"""Servicio LLM: integración con DeepSeek para clasificación y generación.

Este módulo encapsula 3 capacidades (todas vía `call_api`):
- `interpret_user_answer`: clasifica una respuesta del usuario en categorías permitidas.
- `generate_next_question`: produce la siguiente pregunta estratégica (o clarificación).
- `generate_final_descriptions`: genera descripción y justificación por arquitectura.

Configuración:
- Requiere variable de entorno `DEEPSEEK_API_KEY`.

Nota técnica:
- `call_api` está declarado como `async`, pero actualmente usa `requests` (bloqueante).
  Se mantiene así para no alterar la lógica; en cargas altas podría convenir migrar a
  un cliente HTTP asíncrono.
"""

import requests
import json
import os
from pathlib import Path


class ApiKeyError(Exception):
    """Error de configuración/autenticación relacionado con la API key del LLM.

    Se usa para distinguir fallos de credenciales (p.ej. ausencia de `DEEPSEEK_API_KEY`
    o autenticación 401) de errores de red/servidor. El API HTTP lo traduce a `401`.
    """

    pass

API_URL = 'https://api.deepseek.com/v1/chat/completions'

# Directorio donde se encuentran los prompts
PROMPT_DIR = Path(__file__).parent / 'prompt'

def load_prompt(prompt_filename):
    """Carga un prompt desde un archivo de texto.
    
    Args:
        prompt_filename (str): Nombre del archivo de prompt (ej: 'interpret_user_answer_prompt.txt')
    
    Returns:
        str: Contenido del prompt
    
    Raises:
        FileNotFoundError: Si el archivo de prompt no existe
    """
    prompt_path = PROMPT_DIR / prompt_filename
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()

async def call_api(messages, temperature=0.2):
    """Realiza una llamada a la API de DeepSeek y parsea el contenido como JSON.

    Args:
        messages (list[dict]): Lista de mensajes estilo Chat Completions, por ejemplo:
          [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
          Este servicio normalmente envía solo un mensaje `system` con instrucciones.
        temperature (float, optional): Control de aleatoriedad del modelo. Valores bajos
          favorecen determinismo. Por defecto 0.2.

    Behavior:
        - Lee `DEEPSEEK_API_KEY` de variables de entorno.
        - Rechaza placeholders comunes para evitar confusión en despliegues.
        - Envia la solicitud a `API_URL` solicitando `response_format=json_object`.
        - Toma el `choices[0].message.content` y lo interpreta como JSON (string).

    Returns:
        dict | list: Objeto JSON ya parseado desde el `content` retornado por el modelo.

    Raises:
        ApiKeyError: Si la API key no existe, parece placeholder, o el servidor responde 401.
        Exception: Para errores de red, respuestas no-OK, ausencia de contenido, o JSON inválido.

    Notes:
        Aunque la función es `async`, la llamada HTTP usa `requests.post` (bloqueante).
        Si se ejecuta bajo un loop asíncrono con alta concurrencia, puede bloquear workers.
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
    """Clasifica la respuesta del usuario para un parámetro específico.

    Args:
        question_text (str): Pregunta previamente hecha al usuario (contexto).
        user_answer (str): Respuesta textual del usuario.
        parameter_to_infer (str): Nombre del parámetro a inferir (p.ej. "scalability",
          "teamSize", etc.).

    Behavior:
        - Construye un prompt de clasificación (no conversacional) con categorías permitidas.
        - Si la respuesta es ambigua o el usuario declara desconocimiento, debe producir
          `classification == "UNCERTAIN"`.

    Returns:
        dict: Objeto JSON con claves:
          - `classification`: str (una de las categorías permitidas o "UNCERTAIN")
          - `confidence`: "high" | "medium" | "low"
          - `reasoning`: str (frase corta justificando)

    Raises:
        ApiKeyError / Exception: Propagados desde `call_api`.
    """

    prompt_template = load_prompt('interpret_user_answer_prompt.txt')
    system_prompt = prompt_template.format(
        question_text=question_text,
        user_answer=user_answer,
        parameter_to_infer=parameter_to_infer
    )

    messages = [{'role': 'system', 'content': system_prompt}]
    return await call_api(messages, 0.0)


async def generate_next_question(history, remaining_params, last_interpretation, is_clarification_needed=False):
    """Genera la siguiente interacción (confirmación + pregunta o clarificación).

    Args:
        history (list[dict]): Historial conversacional completo. Se usa una ventana
          de los últimos 6 mensajes para contexto.
        remaining_params (list[str]): Parámetros aún no inferidos; el modelo decide cuál
          es más estratégico preguntar a continuación.
        last_interpretation (dict | None): Resultado anterior de `interpret_user_answer`.
          Si existe, el modelo puede confirmar lo entendido antes de preguntar.
        is_clarification_needed (bool, optional): Si `True`, se solicita clarificación
          sobre el MISMO parámetro (simplificando la pregunta). Por defecto `False`.

    Returns:
        dict: Objeto JSON con:
          - `parameter_to_infer`: str
          - `question_for_user`: str (solo la pregunta)
          - `full_response_text`: str (confirmación + pregunta/clarificación)

    Raises:
        ApiKeyError / Exception: Propagados desde `call_api`.
    """

    simplified_history = [
        {'role': msg['role'], 'content': msg['content']}
        for msg in history[-6:]
    ]

    prompt_template = load_prompt('generate_next_question_prompt.txt')
    system_prompt = prompt_template.format(
        history=json.dumps(simplified_history),
        remaining_params=', '.join(remaining_params),
        last_interpretation=json.dumps(last_interpretation),
        is_clarification_needed=is_clarification_needed
    )

    messages = [{'role': 'system', 'content': system_prompt}]
    return await call_api(messages, 0.6)


async def generate_final_descriptions(project_description, recommendations, history):
    """Genera descripción y justificación por arquitectura recomendada.

    Args:
        project_description (str): Descripción inicial del proyecto del usuario.
        recommendations (list[dict]): Lista de arquitecturas recomendadas (dicts). Se
          espera que cada dict tenga al menos la clave `name`.
        history (list[dict]): Historial conversacional. Actualmente no se usa para el
          prompt, pero se conserva en la firma por compatibilidad del orquestador.

    Behavior:
        - Pide al LLM que devuelva un JSON cuyas claves sean EXACTAMENTE los nombres
          de las arquitecturas recomendadas.
        - En error (API/network/parse), retorna descripciones por defecto para no
          interrumpir el flujo de recomendación.

    Returns:
        dict[str, dict]: Mapa:
          {
            "Nombre Arquitectura": {
              "description": "...",
              "justification": "..."
            },
            ...
          }

    Side Effects:
        Imprime logs de depuración/errores a stdout.
    """

    recommendations_names = ', '.join([rec['name'] for rec in recommendations])

    prompt_template = load_prompt('generate_final_descriptions_prompt.txt')
    system_prompt = prompt_template.format(
        project_description=project_description,
        recommendations_names=recommendations_names,
        architecture_1_name=recommendations[0]['name'] if len(recommendations) > 0 else 'Arquitectura 1',
        architecture_2_name=recommendations[1]['name'] if len(recommendations) > 1 else 'Arquitectura 2',
        architecture_3_name=recommendations[2]['name'] if len(recommendations) > 2 else 'Arquitectura 3'
    )

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
                'justification': "Esta arquitectura es adecuada para tu proyecto según los parámetros analizados."
            }
        return default_descriptions
