# Servicio: llm_service

## 1) Qué es este servicio
Este servicio encapsula **todas las llamadas al LLM (DeepSeek)**.

En este proyecto se usa para 3 tareas concretas:
1) Interpretar la respuesta del usuario y clasificarla (función `interpret_user_answer`).
2) Decidir la siguiente pregunta (función `generate_next_question`).
3) Generar descripciones y justificaciones finales (función `generate_final_descriptions`).

Código: `archssistant-backend/app/services/llm_service/llm_service.py`

---

## 2) Conceptos mínimos (para entender el código)

### 2.1 API Key (clave secreta)
La API externa requiere autenticación. La clave se lee desde una variable de entorno:
- `DEEPSEEK_API_KEY`

### 2.2 “messages” (formato chat)
La API recibe una lista de mensajes con estructura típica:
```python
messages = [
  {"role": "system", "content": "Instrucciones"},
  {"role": "user", "content": "Pregunta"}
]
```

### 2.3 “temperature”
Es un número que controla aleatoriedad:
- 0.0: máximo determinismo (muy consistente)
- 0.6: más flexible/creativo

---

## 3) Código completo (con números de línea)

```python
  # app/services/llm_service/llm_service.py

  import requests
  import json
  import os
  from pathlib import Path

  from app.api.exceptions import ApiKeyError
  from app.core import get_logger


  class LLMService:
      """Service for interacting with the DeepSeek LLM API."""
      
      API_URL = 'https://api.deepseek.com/v1/chat/completions'
      
      def __init__(self):
          """Initialize the LLM Service."""
          self.prompt_dir = Path(__file__).parent / 'prompt'
          self.logger = get_logger(__name__)
      
      def load_prompt(self, prompt_filename):
          """Loads a prompt from a text file."""
          # ...
      
      def call_api(self, messages, temperature=0.2):
 14      """
 15      Realiza una llamada a la API de DeepSeek.
 16      """
 17      api_key = os.getenv('DEEPSEEK_API_KEY')
 18      if not api_key:
 19        raise ApiKeyError('La clave de API no está configurada (DEEPSEEK_API_KEY).')
 20      
 21      placeholder = api_key.strip().lower()
 22      if placeholder in {"", "your_deepseek_api_key_here", "sk-replace_me", "tu_clave_api_aqui"} or placeholder.startswith("tu_clave_api_aqui"):
 23        raise ApiKeyError('La clave de API parece ser un placeholder. Configura DEEPSEEK_API_KEY en .env con tu clave real.')
 24      
 25      request_body = {
 26          'model': 'deepseek-chat',
 27          'messages': messages,
 28          'temperature': temperature,
 29          'response_format': {'type': 'json_object'}
 30      }
 31      
 32      try:
 33          response = requests.post(
 34              API_URL,
 35              json=request_body,
 36              headers={
 37                  'Content-Type': 'application/json',
 38                  'Authorization': f'Bearer {api_key}'
 39              }
 40          )
 41          
 42          if not response.ok:
 43            error_body = response.text
 44            if response.status_code == 401:
 45              raise ApiKeyError('Autenticación fallida con DeepSeek. Revisa tu DEEPSEEK_API_KEY.')
 46            raise Exception('Error en la API al llamar al servicio.')
 47          
 48          data = response.json()
 49          raw_content = data.get('choices', [{}])[0].get('message', {}).get('content')
 50          
 51          if not raw_content:
 52              raise Exception('La respuesta de la API no contiene el contenido esperado.')
 53          
 54          return json.loads(raw_content)
 55      
 56      except ApiKeyError:
 57          raise
 58      except Exception as error:
 59          raise Exception(f"Error al llamar a la API: {str(error)}")
 60  
 61  
 62      def interpret_user_answer(self, question_text, user_answer, parameter_to_infer):
 63      """
 64      Clasifica la respuesta del usuario en una categoría permitida.
 65      Retorna UNCERTAIN si el usuario no sabe o es ambiguo.
 66      """
 67      system_prompt = f"""
 68  <role>
 69  Eres Classifier-7, un sistema de análisis semántico ultrapreciso. Tu única función es la clasificación de texto. No eres conversacional. No ofreces contexto adicional. Eres una máquina de precisión.
 70  </role>
 71  
 72  <context>
 73    <question_asked_to_user>{question_text}</question_asked_to_user>
 74    <user_response>{user_answer}</user_response>
 75    <parameter_to_classify>{parameter_to_infer}</parameter_to_classify>
 76  </context>
 77  
 78  <instructions>
 79    1.  Analiza la <user_response> en el contexto de la <question_asked_to_user>.
 80    2.  Clasifica el <parameter_to_classify> en una de las categorías permitidas.
 81    3.  Si la respuesta del usuario es una negación directa de conocimiento ("no sé", "no estoy seguro") o es demasiado ambigua para tomar una decisión informada, DEBES usar la clasificación "UNCERTAIN".
 82    4.  Determina un nivel de confianza para tu clasificación (high, medium, low).
 83  </instructions>
 84  
 85  <allowed_classifications>
 86    - Para 'teamSize': ["Pequeño", "Moderado", "Grande", "Alto"]
 87    - Para los demás parámetros: ["Baja", "Moderada", "Alta", "Excelente"]
 88    - Para incertidumbre: ["UNCERTAIN"]
 89  </allowed_classifications>
 90  
 91  <output_format>
 92    Responde EXCLUSIVAMENTE con un objeto JSON válido. NO incluyas NADA más. La estructura OBLIGATORIA es:
 93    {{
 94      "classification": "VALOR_CLASIFICADO",
 95      "confidence": "high|medium|low",
 96      "reasoning": "Una frase muy corta explicando por qué elegiste esa clasificación."
 97    }}
 98  </output_format>"""
 99      
100      messages = [{'role': 'system', 'content': system_prompt}]
101      return await call_api(messages, 0.0)
102  
103  
104      def generate_next_question(self, history, remaining_params, last_interpretation, is_clarification_needed=False):
105      """
106      Genera la siguiente pregunta estratégica en la conversación.
107      """
108      simplified_history = [
109          {'role': msg['role'], 'content': msg['content']}
110          for msg in history[-6:]
111      ]
112      
113      system_prompt = f"""
114  <role>
115  Eres 'Arch-Strategist', el núcleo conversacional de Arch-Assistant. Tu especialidad es la psicología de la ingeniería de requisitos. Sabes que hacer la pregunta correcta en el momento correcto es la clave. Eres un guía experto, no un interrogador.
116  </role>
117  
118  <task>
119  Tu tarea es generar la siguiente interacción con el usuario. Analiza el flag 'isClarificationNeeded'.
120  
121  <clarification_logic>
122    Si 'isClarificationNeeded' es true, significa que el usuario no supo responder la última pregunta. Tu misión es ayudarlo.
123    1.  Empatiza con una frase corta (ej: "No hay problema, lo deduciremos juntos.").
124    2.  Formula una pregunta de clarificación mucho más simple sobre el MISMO parámetro, usando analogías o ejemplos concretos.
125    (Ej. si el parámetro era 'availability', pregunta: "Pensemos en el impacto: si la aplicación se cae por una hora, ¿es una simple molestia o una pérdida crítica de negocio?").
126  </clarification_logic>
127  
128  <normal_flow_logic>
129    Si 'isClarificationNeeded' es false, procede con el flujo normal.
130    1.  Si 'lastInterpretation' existe, confirma amigablemente tu entendimiento. (Ej: "Entendido, un equipo pequeño. Eso nos da agilidad.").
131    2.  Analiza los 'remainingParams' y elige el más estratégico a preguntar ahora (prioriza: Escala > Equipo > Calidad).
132    3.  Formula una pregunta abierta, amigable y no técnica sobre ese nuevo parámetro.
133  </normal_flow_logic>
134  </task>
135  
136  <context>
137    <history>{json.dumps(simplified_history)}</history>
138    <remainingParams>{', '.join(remaining_params)}</remainingParams>
139    <lastInterpretation>{json.dumps(last_interpretation)}</lastInterpretation>
140    <isClarificationNeeded>{is_clarification_needed}</isClarificationNeeded>
141  </context>
142  
143  <output_format>
144    Tu respuesta DEBE SER EXCLUSIVAMENTE un objeto JSON válido con la siguiente estructura:
145    {{
146      "parameter_to_infer": "parametro_de_la_nueva_pregunta", 
147      "question_for_user": "texto_de_la_nueva_pregunta_solamente",
148      "full_response_text": "texto_completo_con_confirmacion_y_pregunta_o_clarificacion"
149    }}
150  </output_format>"""
151      
152      messages = [{'role': 'system', 'content': system_prompt}]
153      return await call_api(messages, 0.6)
154  
155  
156      def generate_final_descriptions(self, project_description, recommendations, history):
157      """
158      Genera descripciones y justificaciones para cada arquitectura recomendada.
159      """
160      recommendations_names = ', '.join([rec['name'] for rec in recommendations])
161      
162      system_prompt = f"""
163  <role>
164  Eres 'Arch-Describer', un experto en arquitectura de software que sabe comunicar decisiones técnicas de forma clara y accesible.
165  </role>
166  
167  <task>
168  Para cada una de las siguientes arquitecturas recomendadas, proporciona:
169  1. Una descripción clara (2-3 líneas) de qué es y cómo funciona.
170  2. Una justificación técnica (2-3 líneas) de por qué es adecuada para el proyecto del usuario.
171  
172  El proyecto del usuario es: "{project_description}"
173  
174  Las arquitecturas a describir son: {recommendations_names}
175  
176  IMPORTANTE: Las claves del JSON deben ser EXACTAMENTE los nombres de las arquitecturas proporcionados.
177  </task>
178  
179  <output_format>
180  Responde EXCLUSIVAMENTE con un objeto JSON válido. La estructura OBLIGATORIA es:
181  {{
182    "{recommendations[0]['name']}": {{
183      "description": "Descripción clara de la arquitectura",
184      "justification": "Por qué es adecuada para este proyecto"
185    }},
186    "{recommendations[1]['name'] if len(recommendations) > 1 else 'Arquitectura 2'}": {{
187      "description": "Descripción clara de la arquitectura",
188      "justification": "Por qué es adecuada para este proyecto"
189    }},
190    "{recommendations[2]['name'] if len(recommendations) > 2 else 'Arquitectura 3'}": {{
191      "description": "Descripción clara de la arquitectura",
192      "justification": "Por qué es adecuada para este proyecto"
193    }}
194  }}
195  </output_format>"""
196      
197      messages = [{'role': 'system', 'content': system_prompt}]
198      
199      try:
200          result = await call_api(messages, 0.6)
201          print(f"DEBUG LLM: Descripciones generadas: {result}")
202          return result
203      except Exception as e:
204          print(f"ERROR al generar descripciones: {e}")
205          # Retornar descripciones por defecto
206          default_descriptions = {}
207          for rec in recommendations:
208              default_descriptions[rec['name']] = {
209                  'description': f"Arquitectura {rec['name']} - Sistema de desarrollo modular.",
210                  'justification': f"Esta arquitectura es adecuada para tu proyecto según los parámetros analizados."
211              }
212          return default_descriptions
```

---

## 4) Uso

```python
from app.services.llm_service import LLMService

# Crear instancia
llm_service = LLMService()

# Interpretar respuesta
result = llm_service.interpret_user_answer(
    question_text="¿Cuál es el tamaño de tu equipo?",
    user_answer="Somos un equipo pequeño de 3 personas",
    parameter_to_infer="teamSize"
)
# Retorna: {"classification": "Pequeño", "confidence": "high", "reasoning": "..."}

# Generar siguiente pregunta
question = llm_service.generate_next_question(
    history=[...],
    remaining_params=['complexity', 'scalability'],
    last_interpretation=result,
    is_clarification_needed=False
)
# Retorna: {"parameter_to_infer": "complexity", "question_for_user": "...", "full_response_text": "..."}

# Generar descripciones finales
descriptions = llm_service.generate_final_descriptions(
    project_description="Sistema para vender cursos online",
    recommendations=[...],
    history=[...]
)
# Retorna: {"Arquitectura Monolítica": {"description": "...", "justification": "..."}, ...}
```

## 5) Logging

El servicio LLM usa logging estructurado:

```python
# Error: API key no encontrada
self.logger.error("DEEPSEEK_API_KEY not found in environment variables")

# Error: Autenticación fallida
self.logger.error("DeepSeek API authentication failed (401)")

# Error: Request fallido
self.logger.error(f"DeepSeek API request failed with status {response.status_code}")

# Error: Parsing JSON
self.logger.error(f"Failed to parse JSON response from DeepSeek API: {str(je)}")

# Error: Error general con stack trace
self.logger.error(f"Error calling DeepSeek API: {str(error)}", exc_info=True)

# Debug: Descripciones generadas
self.logger.debug(f"Architecture descriptions generated - keys: {list(result.keys())}")

# Warning: Usando descripciones por defecto
self.logger.warning("Returning default descriptions to continue recommendation flow")
```

Todos los mensajes de logging están en inglés para consistencia.

## 6) Explicación detallada

### Estructura de la Clase

**Clase `LLMService`:**
- `__init__()`: Inicializa el servicio con `prompt_dir` y `logger`
- `load_prompt()`: Carga prompts desde archivos de texto
- `call_api()`: Método principal para llamar a la API de DeepSeek
- `interpret_user_answer()`: Clasifica respuestas del usuario
- `generate_next_question()`: Genera la siguiente pregunta
- `generate_final_descriptions()`: Genera descripciones de arquitecturas

**Importaciones:**
- `requests`: librería HTTP para hacer llamadas a la API
- `json`: convertir texto JSON ↔ estructuras Python
- `os`: leer variables de entorno (`DEEPSEEK_API_KEY`)
- `pathlib.Path`: manejo de rutas de archivos
- `ApiKeyError`: excepción definida en `app/api/exceptions.py`
- `get_logger`: función de logging de `app.core`

### `call_api(messages, temperature)`
Esta función hace el “trabajo pesado”: validación de clave, request HTTP, parsing JSON.

#### Validación de API key
- Lee `DEEPSEEK_API_KEY` del sistema.
- Si no existe, registra error con `self.logger.error()` y lanza `ApiKeyError`.
- Normaliza la key con `strip()` y `lower()` para detectar placeholders.
- Si es un placeholder típico, registra error y lanza `ApiKeyError`.

#### Preparación del request
- **L25-L30**: arma el `request_body` con:
  - modelo: `deepseek-chat`
  - mensajes
  - temperatura
  - `response_format`: pide que el contenido sea un JSON.

#### Request HTTP
- **L32**: `try` para capturar errores.
- **L33-L40**: envía POST a `API_URL`.
  - `json=request_body` hace que `requests` serialice el body como JSON.
  - `Authorization: Bearer <api_key>` autentica.

#### Manejo de errores HTTP
- Si la respuesta no fue 2xx:
  - Si es 401: registra error con `self.logger.error()` y lanza `ApiKeyError`.
  - Para otros casos: registra error con `self.logger.error()` y lanza excepción genérica.

#### Parsing de la respuesta
- `response.json()` convierte la respuesta a dict.
- Navega por `choices[0].message.content`.
  - Si faltan claves, usa valores por defecto (`[{}]` y `{}`) para evitar `KeyError`.
- Si no hay `content`, registra error con `self.logger.error()` y lanza excepción.
- `json.loads(raw_content)` convierte el contenido (string JSON) a dict Python.

#### Manejo de excepciones
- Si es `ApiKeyError`: se vuelve a lanzar igual (ya está logueado).
- Si es `json.JSONDecodeError`: registra error específico y lanza excepción.
- Cualquier otro error: registra error con stack trace (`exc_info=True`) y re-lanza.

> **Nota técnica importante**: `call_api` es síncrono y usa `requests.post` (bloqueante). Funciona correctamente, pero en el futuro podría migrarse a un cliente HTTP async para mejorar la concurrencia.

### `interpret_user_answer(question_text, user_answer, parameter_to_infer)`
- Objetivo: **clasificar** la respuesta del usuario para un parámetro.

Paso a paso:
- Carga el prompt desde `prompt/interpret_user_answer_prompt.txt`.
- Formatea el prompt con `question_text`, `user_answer`, `parameter_to_infer`.
- Crea `messages` con un solo mensaje `system`.
- Llama `self.call_api(messages, 0.0)` (temperatura 0: más determinista).

Salida esperada:
```json
{"classification": "Alta", "confidence": "high", "reasoning": "..."}
```

### `generate_next_question(history, remaining_params, last_interpretation, is_clarification_needed)`
- Objetivo: decidir la **siguiente pregunta**.

Paso a paso:
- Crea `simplified_history` con los últimos 6 mensajes.
  - Esto reduce tokens y evita enviar estructuras innecesarias.
- Carga el prompt desde `prompt/generate_next_question_prompt.txt`.
- Formatea el prompt con historial, parámetros restantes, última interpretación, y flag de clarificación.
- Llama `self.call_api(messages, 0.6)`.

Salida esperada:
```json
{
  "parameter_to_infer": "teamSize",
  "question_for_user": "...",
  "full_response_text": "..."
}
```

### `generate_final_descriptions(project_description, recommendations, history)`
- Objetivo: para cada arquitectura recomendada generar:
  - `description`
  - `justification`

Paso a paso:
- Construye string con nombres de arquitecturas.
- Carga el prompt desde `prompt/generate_final_descriptions_prompt.txt`.
- Formatea el prompt con descripción del proyecto y nombres de arquitecturas.
- Intenta llamar al LLM y devolver resultado.
  - Registra debug con `self.logger.debug()` cuando tiene éxito.
- Si falla el LLM:
  - Registra error con `self.logger.error()` y stack trace.
  - Registra warning con `self.logger.warning()` sobre usar descripciones por defecto.
  - Crea `default_descriptions` para no romper el flujo del backend.

---

## 7) Qué debes revisar para que funcione

- Debes tener `DEEPSEEK_API_KEY` configurada en el archivo `.env`.
- Debe existir acceso a internet desde el backend.
- La API debe devolver `choices[0].message.content` conteniendo un JSON válido.
- Los archivos de prompt deben existir en `app/services/llm_service/prompt/`:
  - `interpret_user_answer_prompt.txt`
  - `generate_next_question_prompt.txt`
  - `generate_final_descriptions_prompt.txt`

## 8) Excepciones

**ApiKeyError:**
- Ubicación: `app/api/exceptions.py`
- Se lanza cuando:
  - `DEEPSEEK_API_KEY` no está configurada
  - `DEEPSEEK_API_KEY` es un placeholder
  - La API responde con 401 (autenticación fallida)
- El Gateway la captura y la convierte a `GatewayError` con status_code 401.

---

Si quieres, el siguiente paso es documentar cómo `DialogueOrchestrator` usa estos métodos en un flujo real de conversación (ya está en su README).
