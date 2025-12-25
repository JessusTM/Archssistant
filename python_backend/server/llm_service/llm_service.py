# server/llm_service/llm_service.py

import requests
import json
import os


class ApiKeyError(Exception):
  pass

API_URL = 'https://api.deepseek.com/v1/chat/completions'

async def call_api(messages, temperature=0.2):
    """
    Realiza una llamada a la API de DeepSeek.
    """
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
      raise ApiKeyError('La clave de API no está configurada (DEEPSEEK_API_KEY).')
    
    placeholder = api_key.strip().lower()
    if placeholder in {"", "your_deepseek_api_key_here", "sk-replace_me", "tu_clave_api_aqui"} or placeholder.startswith("tu_clave_api_aqui"):
      raise ApiKeyError('La clave de API parece ser un placeholder. Configura DEEPSEEK_API_KEY en .env con tu clave real.')
    
    request_body = {
        'model': 'deepseek-chat',
        'messages': messages,
        'temperature': temperature,
        'response_format': {'type': 'json_object'}
    }
    
    try:
        response = requests.post(
            API_URL,
            json=request_body,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
        )
        
        if not response.ok:
          error_body = response.text
          if response.status_code == 401:
            raise ApiKeyError('Autenticación fallida con DeepSeek. Revisa tu DEEPSEEK_API_KEY.')
          raise Exception('Error en la API al llamar al servicio.')
        
        data = response.json()
        raw_content = data.get('choices', [{}])[0].get('message', {}).get('content')
        
        if not raw_content:
            raise Exception('La respuesta de la API no contiene el contenido esperado.')
        
        return json.loads(raw_content)
    
    except ApiKeyError:
        raise
    except Exception as error:
        raise Exception(f"Error al llamar a la API: {str(error)}")


async def interpret_user_answer(question_text, user_answer, parameter_to_infer):
    """
    Clasifica la respuesta del usuario en una categoría permitida.
    Retorna UNCERTAIN si el usuario no sabe o es ambiguo.
    """
    system_prompt = f"""
<role>
Eres Classifier-7, un sistema de análisis semántico ultrapreciso. Tu única función es la clasificación de texto. No eres conversacional. No ofreces contexto adicional. Eres una máquina de precisión.
</role>

<context>
  <question_asked_to_user>{question_text}</question_asked_to_user>
  <user_response>{user_answer}</user_response>
  <parameter_to_classify>{parameter_to_infer}</parameter_to_classify>
</context>

<instructions>
  1.  Analiza la <user_response> en el contexto de la <question_asked_to_user>.
  2.  Clasifica el <parameter_to_classify> en una de las categorías permitidas.
  3.  Si la respuesta del usuario es una negación directa de conocimiento ("no sé", "no estoy seguro") o es demasiado ambigua para tomar una decisión informada, DEBES usar la clasificación "UNCERTAIN".
  4.  Determina un nivel de confianza para tu clasificación (high, medium, low).
</instructions>

<allowed_classifications>
  - Para 'teamSize': ["Pequeño", "Moderado", "Grande", "Alto"]
  - Para los demás parámetros: ["Baja", "Moderada", "Alta", "Excelente"]
  - Para incertidumbre: ["UNCERTAIN"]
</allowed_classifications>

<output_format>
  Responde EXCLUSIVAMENTE con un objeto JSON válido. NO incluyas NADA más. La estructura OBLIGATORIA es:
  {{
    "classification": "VALOR_CLASIFICADO",
    "confidence": "high|medium|low",
    "reasoning": "Una frase muy corta explicando por qué elegiste esa clasificación."
  }}
</output_format>"""
    
    messages = [{'role': 'system', 'content': system_prompt}]
    return await call_api(messages, 0.0)


async def generate_next_question(history, remaining_params, last_interpretation, is_clarification_needed=False):
    """
    Genera la siguiente pregunta estratégica en la conversación.
    """
    simplified_history = [
        {'role': msg['role'], 'content': msg['content']}
        for msg in history[-6:]
    ]
    
    system_prompt = f"""
<role>
Eres 'Arch-Strategist', el núcleo conversacional de Arch-Assistant. Tu especialidad es la psicología de la ingeniería de requisitos. Sabes que hacer la pregunta correcta en el momento correcto es la clave. Eres un guía experto, no un interrogador.
</role>

<task>
Tu tarea es generar la siguiente interacción con el usuario. Analiza el flag 'isClarificationNeeded'.

<clarification_logic>
  Si 'isClarificationNeeded' es true, significa que el usuario no supo responder la última pregunta. Tu misión es ayudarlo.
  1.  Empatiza con una frase corta (ej: "No hay problema, lo deduciremos juntos.").
  2.  Formula una pregunta de clarificación mucho más simple sobre el MISMO parámetro, usando analogías o ejemplos concretos.
  (Ej. si el parámetro era 'availability', pregunta: "Pensemos en el impacto: si la aplicación se cae por una hora, ¿es una simple molestia o una pérdida crítica de negocio?").
</clarification_logic>

<normal_flow_logic>
  Si 'isClarificationNeeded' es false, procede con el flujo normal.
  1.  Si 'lastInterpretation' existe, confirma amigablemente tu entendimiento. (Ej: "Entendido, un equipo pequeño. Eso nos da agilidad.").
  2.  Analiza los 'remainingParams' y elige el más estratégico a preguntar ahora (prioriza: Escala > Equipo > Calidad).
  3.  Formula una pregunta abierta, amigable y no técnica sobre ese nuevo parámetro.
</normal_flow_logic>
</task>

<context>
  <history>{json.dumps(simplified_history)}</history>
  <remainingParams>{', '.join(remaining_params)}</remainingParams>
  <lastInterpretation>{json.dumps(last_interpretation)}</lastInterpretation>
  <isClarificationNeeded>{is_clarification_needed}</isClarificationNeeded>
</context>

<output_format>
  Tu respuesta DEBE SER EXCLUSIVAMENTE un objeto JSON válido con la siguiente estructura:
  {{
    "parameter_to_infer": "parametro_de_la_nueva_pregunta", 
    "question_for_user": "texto_de_la_nueva_pregunta_solamente",
    "full_response_text": "texto_completo_con_confirmacion_y_pregunta_o_clarificacion"
  }}
</output_format>"""
    
    messages = [{'role': 'system', 'content': system_prompt}]
    return await call_api(messages, 0.6)


async def generate_final_descriptions(project_description, recommendations, history):
    """
    Genera descripciones y justificaciones para cada arquitectura recomendada.
    """
    recommendations_names = ', '.join([rec['name'] for rec in recommendations])
    
    system_prompt = f"""
<role>
Eres 'Arch-Describer', un experto en arquitectura de software que sabe comunicar decisiones técnicas de forma clara y accesible.
</role>

<task>
Para cada una de las siguientes arquitecturas recomendadas, proporciona:
1. Una descripción clara (2-3 líneas) de qué es y cómo funciona.
2. Una justificación técnica (2-3 líneas) de por qué es adecuada para el proyecto del usuario.

El proyecto del usuario es: "{project_description}"

Las arquitecturas a describir son: {recommendations_names}

IMPORTANTE: Las claves del JSON deben ser EXACTAMENTE los nombres de las arquitecturas proporcionados.
</task>

<output_format>
Responde EXCLUSIVAMENTE con un objeto JSON válido. La estructura OBLIGATORIA es:
{{
  "{recommendations[0]['name']}": {{
    "description": "Descripción clara de la arquitectura",
    "justification": "Por qué es adecuada para este proyecto"
  }},
  "{recommendations[1]['name'] if len(recommendations) > 1 else 'Arquitectura 2'}": {{
    "description": "Descripción clara de la arquitectura",
    "justification": "Por qué es adecuada para este proyecto"
  }},
  "{recommendations[2]['name'] if len(recommendations) > 2 else 'Arquitectura 3'}": {{
    "description": "Descripción clara de la arquitectura",
    "justification": "Por qué es adecuada para este proyecto"
  }}
}}
</output_format>"""
    
    messages = [{'role': 'system', 'content': system_prompt}]
    
    try:
        result = await call_api(messages, 0.6)
        print(f"DEBUG LLM: Descripciones generadas: {result}")
        return result
    except Exception as e:
        print(f"ERROR al generar descripciones: {e}")
        # Retornar descripciones por defecto
        default_descriptions = {}
        for rec in recommendations:
            default_descriptions[rec['name']] = {
                'description': f"Arquitectura {rec['name']} - Sistema de desarrollo modular.",
                'justification': f"Esta arquitectura es adecuada para tu proyecto según los parámetros analizados."
            }
        return default_descriptions
