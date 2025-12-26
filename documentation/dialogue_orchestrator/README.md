# Servicio: dialogue_orchestrator

## 1) Qué es este servicio (idea general)
Este servicio es el **“cerebro” que coordina la conversación** con el usuario.

- Mantiene un **estado** (qué parámetros ya se dedujeron, cuál fue la última pregunta, si se está aclarando, etc.).
- En cada mensaje del usuario decide si:
  1) seguir preguntando (fase de entrevista), o
  2) calcular recomendaciones (fase de recomendación), o
  3) cerrar la conversación (fase final).

En este proyecto, el orquestador vive en:
- Código: `python_backend/server/dialogue_orchestrator/orchestrator.py`

Y depende de estos dos servicios:
- `llm_service`: para interpretar respuestas y generar preguntas/descripciones.
- `recommendation_engine`: para puntuar arquitecturas y devolver las mejores.

---

## 2) Interfaces: entradas y salidas

### Entrada principal
La función principal es `handle_message(history)`.

- `history` es una lista de mensajes (diccionarios). Cada mensaje suele tener:
  - `role`: quién habló (`user`, `assistant`, `user_description`, etc.)
  - `content`: texto del mensaje
  - opcionalmente: `state` (un diccionario con el estado de conversación) *solo en mensajes del asistente*

Ejemplo mínimo de `history`:
```python
history = [
  {"role": "user", "content": "Quiero un sistema para vender cursos online"}
]
```

### Salida
`handle_message` devuelve un diccionario:
- `response`: el mensaje del asistente (dict)
- `state`: el estado actualizado (dict)

Ejemplo:
```python
{
  "response": {"role": "assistant", "content": "..."},
  "state": {
    "inferredParams": {"scalability": "Alta"},
    "lastQuestion": {"parameter_to_infer": "teamSize", "question_text": "..."},
    "isClarifying": False,
    "status": "interviewing"
  }
}
```

---

## 3) Flujo general (muy resumido)

1) El usuario describe el proyecto.
2) El orquestador entra en modo `interviewing`.
3) En cada turno:
   - interpreta la respuesta del usuario (con `interpret_user_answer`),
   - guarda el parámetro deducido,
   - decide si pedir aclaración (`UNCERTAIN`) o seguir,
   - genera la siguiente pregunta (`generate_next_question`).
4) Cuando ya tiene suficientes parámetros (>= 5), cambia a `recommending`.
5) Calcula recomendaciones con `get_recommendation`.
6) Pide al LLM descripciones y justificaciones (`generate_final_descriptions`).
7) Devuelve recomendación enriquecida y finaliza.

---

## 4) Código completo (con números de línea)

A continuación está el contenido de `python_backend/server/dialogue_orchestrator/orchestrator.py` con números de línea (para que la explicación sea exacta):

```python
 1  # server/dialogue_orchestrator/orchestrator.py
 2  
 3  from server.llm_service import interpret_user_answer, generate_next_question, generate_final_descriptions
 4  from server.recommendation_engine import get_recommendation
 5  
 6  ALL_PARAMETERS = [
 7      'complexity', 'scalability', 'teamExperience', 'dataVolume',
 8      'teamSize', 'availability', 'maintainability', 'interoperability'
 9  ]
10  
11  
12  def get_conversation_state(history):
13      """
14      Extrae el estado actual de la conversación del historial.
15      El estado contiene los parámetros ya inferidos y el último estado conocido.
16      """
17      last_assistant_message = None
18      for msg in reversed(history):
19          if msg.get('role') == 'assistant':
20              last_assistant_message = msg
21              break
22      
23      if last_assistant_message:
24          return last_assistant_message.get('state', {
25              'inferredParams': {},
26              'lastQuestion': None,
27              'isClarifying': False,
28              'status': 'interviewing'
29          })
30      
31      return {
32          'inferredParams': {},
33          'lastQuestion': None,
34          'isClarifying': False,
35          'status': 'interviewing'
36      }
37  
38  
39  async def handle_message(history):
40      """
41      Maneja un mensaje del usuario y retorna la respuesta del asistente.
42      Este es el punto de entrada principal del orquestador.
43      """
44      user_message = history[-1]
45      
46      # Busca la descripción inicial del proyecto
47      project_description = None
48      for msg in history:
49          if msg.get('role') == 'user_description':
50              project_description = msg.get('content')
51              break
52      
53      if not project_description:
54          project_description = history[0].get('content', '')
55      
56      # Marca el primer mensaje como descripción del usuario
57      if len(history) == 1:
58          history[0]['role'] = 'user_description'
59      
60      state = get_conversation_state(history)
61      interpretation_result = None
62      
63      # FASE 1: ENTREVISTA (Recopilación de parámetros)
64      if state['status'] == 'interviewing':
65          
66          # Si ya hay una pregunta anterior, interpretar la respuesta del usuario
67          if state.get('lastQuestion'):
68              parameter_to_infer = state['lastQuestion'].get('parameter_to_infer')
69              question_text = state['lastQuestion'].get('question_text')
70              
71              interpretation_result = await interpret_user_answer(
72                  question_text,
73                  user_message.get('content'),
74                  parameter_to_infer
75              )
76              
77              # Lógica de sub-diálogo de clarificación
78              if interpretation_result.get('classification') == 'UNCERTAIN':
79                  state['isClarifying'] = True
80              else:
81                  state['inferredParams'][parameter_to_infer] = interpretation_result.get('classification')
82                  state['isClarifying'] = False
83          
84          # Verificar si hemos recopilado suficientes parámetros
85          inferred_count = len(state['inferredParams'])
86          if inferred_count >= 5:
87              state['status'] = 'recommending'
88          else:
89              # Generar la siguiente pregunta
90              remaining_params = [p for p in ALL_PARAMETERS if p not in state['inferredParams']]
91              
92              next_question = await generate_next_question(
93                  history,
94                  remaining_params,
95                  interpretation_result,
96                  state['isClarifying']
97              )
98              
99              # Si estamos clarificando, mantener el mismo parámetro
100              # Si no, usar el nuevo parámetro sugerido
101              next_param_to_infer = (
102                  state['lastQuestion']['parameter_to_infer']
103                  if state['isClarifying']
104                  else next_question.get('parameter_to_infer')
105              )
106              
107              state['lastQuestion'] = {
108                  'parameter_to_infer': next_param_to_infer,
109                  'question_text': next_question.get('question_for_user')
110              }
111              
112              response = {
113                  'role': 'assistant',
114                  'content': next_question.get('full_response_text')
115              }
116              return {'response': response, 'state': state}
117      
118      # FASE 2: RECOMENDACIÓN
119      if state['status'] == 'recommending':
120          recommendations = get_recommendation(state['inferredParams'])
121          
122          if not recommendations:
123              response = {
124                  'role': 'assistant',
125                  'content': 'No he podido determinar una recomendación con los datos proporcionados.'
126              }
127              state['status'] = 'finished'
128              return {'response': response, 'state': state}
129          
130          print(f"DEBUG: Generando descripciones para {len(recommendations)} arquitecturas")
131          print(f"DEBUG: Arquitecturas: {[r['name'] for r in recommendations]}")
132          
133          # Generar descripciones para cada arquitectura recomendada
134          descriptions = await generate_final_descriptions(
135              project_description,
136              recommendations,
137              history
138          )
139          
140          print(f"DEBUG: Descripciones recibidas con claves: {list(descriptions.keys())}")
141          
142          # Enriquecer las recomendaciones con descripciones y justificaciones
143          enriched_recommendations = []
144          for rec in recommendations:
145              arch_name = rec['name']
146              
147              # Buscar la descripción con el nombre exacto o intentar coincidencias parciales
148              desc_data = descriptions.get(arch_name)
149              
150              if not desc_data:
151                  # Intentar búsqueda case-insensitive
152                  for key in descriptions.keys():
153                      if key.lower() == arch_name.lower():
154                          desc_data = descriptions[key]
155                          break
156              
157              if not desc_data:
158                  print(f"WARNING: No se encontró descripción para '{arch_name}'")
159                  desc_data = {}
160              
161              enriched_recommendations.append({
162                  **rec,
163                  'description': desc_data.get('description', 'Descripción no disponible.'),
164                  'justification': desc_data.get('justification', 'Justificación no disponible.')
165              })
166          
167          response = {
168              'role': 'assistant',
169              'content': '¡Gracias! He analizado tus respuestas.',
170              'recommendation': enriched_recommendations
171          }
172          state['status'] = 'finished'
173          return {'response': response, 'state': state}
174      
175      # FASE 3: FINAL
176      final_response = {
177          'role': 'assistant',
178          'content': 'Si tienes otro proyecto que analizar, simplemente recarga la página.'
179      }
180      return {'response': final_response, 'state': state}
```

---

## 5) Explicación línea por línea (sin omitir detalles)

### Líneas 1-4: imports (dependencias)
- **L1**: comentario con la ruta.
- **L3**: importa 3 funciones del servicio `llm_service`:
  - `interpret_user_answer`: clasifica la respuesta del usuario en categorías (ej. “Alta”, “Baja”, “UNCERTAIN”).
  - `generate_next_question`: decide cuál es la próxima pregunta.
  - `generate_final_descriptions`: genera textos para explicar la recomendación final.
- **L4**: importa `get_recommendation` del motor de recomendación.

**Idea clave**: este archivo no llama a DeepSeek directamente; delega eso en `llm_service`.

### Líneas 6-9: lista de parámetros
- **L6-L9**: `ALL_PARAMETERS` es la lista de “cosas que queremos saber” del proyecto.
  - Por ejemplo: `scalability`, `teamSize`, `availability`, etc.

**Por qué existe**: para saber qué falta por preguntar y evitar repetir.

### Líneas 12-36: `get_conversation_state(history)`
Esta función busca el último estado guardado en el historial.

- **L17**: crea `last_assistant_message = None` (aún no encontró un mensaje del asistente).
- **L18**: recorre el historial al revés con `reversed(history)`.
  - Esto es importante: queremos el **último** mensaje del asistente, no el primero.
- **L19-L21**: si encuentra un mensaje con `role == 'assistant'`, lo guarda y corta el bucle (`break`).

- **L23-L29**: si encontró un mensaje del asistente:
  - devuelve `last_assistant_message.get('state', {...})`
  - o sea: intenta leer la clave `state` del mensaje; si no existe, usa un estado por defecto.

- **L31-L36**: si nunca encontró mensajes del asistente, devuelve un estado por defecto.

**Estructura del estado**:
- `inferredParams`: dict con parámetros deducidos (ej. `{"teamSize": "Moderado"}`).
- `lastQuestion`: última pregunta que se hizo (para saber qué parámetro se estaba preguntando).
- `isClarifying`: si el usuario quedó confundido y hay que re-preguntar más fácil.
- `status`: `interviewing` → `recommending` → `finished`.

### Líneas 39-180: `handle_message(history)` (la función principal)

#### Líneas 44-58: preparar contexto del usuario
- **L44**: `user_message = history[-1]` toma el último mensaje del historial (el mensaje recién llegado).
- **L46-L51**: busca si existe un mensaje especial con `role == 'user_description'`.
  - Esto funciona como “descripción oficial del proyecto”.
- **L53-L54**: si no la encontró, usa el contenido del primer mensaje `history[0]`.
- **L56-L58**: si es el primer turno (historial de longitud 1), marca el primer mensaje como `user_description`.

**Por qué**: el LLM necesita una “descripción del proyecto” estable para generar descripciones finales.

#### Líneas 60-62: cargar estado
- **L60**: llama `get_conversation_state(history)`.
- **L61**: inicializa `interpretation_result = None` (aún no se interpretó nada en este turno).

#### Líneas 63-117: Fase 1 — entrevista
- **L64**: si `state['status']` es `interviewing`, aún estamos recopilando parámetros.

**Interpretación de la respuesta**
- **L67**: si existe `lastQuestion`, significa que el asistente ya había preguntado algo, y ahora el usuario respondió.
- **L68-L69**: extrae:
  - `parameter_to_infer` (qué parámetro estábamos intentando deducir)
  - `question_text` (el texto exacto que se le preguntó)
- **L71-L75**: llama al LLM (mediante `interpret_user_answer`) para clasificar la respuesta.

**Clarificación**
- **L78-L82**:
  - Si el LLM devuelve `classification == 'UNCERTAIN'`, se activa `isClarifying`.
  - Si no, guarda la clasificación en `state['inferredParams'][parameter_to_infer]`.

**Decisión: ¿ya hay suficientes parámetros?**
- **L85**: cuenta cuántos parámetros ya se dedujeron.
- **L86-L88**:
  - si hay 5 o más: cambia a `recommending`.
  - si no: continúa preguntando.

**Generación de la siguiente pregunta**
- **L90**: arma `remaining_params` con comprensión de listas:
  - toma todos los `ALL_PARAMETERS` que todavía NO están en `inferredParams`.
- **L92-L97**: llama `generate_next_question` al LLM.
  - le pasa el historial, lo que falta, la interpretación anterior, y si estamos clarificando.

**Mantener el parámetro si se está clarificando**
- **L101-L105**:
  - si `isClarifying` es `True`, NO cambia de parámetro: vuelve a preguntar por el mismo.
  - si es `False`, usa el parámetro que el LLM sugiere en `next_question`.

**Guardar lastQuestion y responder**
- **L107-L110**: guarda la pregunta actual en el estado.
- **L112-L116**: construye el mensaje de respuesta del asistente y lo devuelve inmediatamente.

#### Líneas 118-174: Fase 2 — recomendación
- **L119**: si el estado ya es `recommending`, se calcula la recomendación.

**Calcular top arquitecturas**
- **L120**: llama al motor `get_recommendation(state['inferredParams'])`.

**Caso sin recomendaciones**
- **L122-L128**: si viene vacío, responde un mensaje de error y termina.

**Pedir descripciones al LLM**
- **L134-L138**: llama `generate_final_descriptions(project_description, recommendations, history)`.

**Enriquecer recomendaciones**
- **L143-L166**: recorre cada recomendación y le agrega:
  - `description`
  - `justification`

Detalles importantes:
- **L148**: intenta buscar `descriptions.get(arch_name)` usando el nombre exacto.
- **L150-L155**: si no existe, intenta una búsqueda “case-insensitive” (ignorando mayúsculas/minúsculas).
- **L157-L165**: si aun así no hay descripción, pone textos por defecto.

**Respuesta final de recomendación**
- **L167-L173**: arma el `response` final con `recommendation` y marca `status = 'finished'`.

#### Líneas 175-180: Fase 3 — final
- Si no está en entrevista ni recomendación, responde un mensaje final y devuelve.

---

## 6) Detalles técnicos y “puntos a notar”

- Este orquestador usa **estado embebido** en el historial (dentro de mensajes del asistente). Eso evita usar base de datos, pero implica que el frontend debe reenviar el historial completo.
- El umbral `>= 5` parámetros (L86) es una regla de negocio: “con 5 ya basta para recomendar”.

---

## 7) Preguntas típicas de novato (y respuestas)

**¿Por qué `async def`?**
Porque el orquestador espera llamadas al LLM (que son lentas). Con `await` (L71 y L92 y L134) el servidor puede manejar otras tareas mientras espera.

**¿Por qué guardar `lastQuestion`?**
Para saber qué parámetro está respondiendo el usuario en el siguiente mensaje.

---

Si quieres, el siguiente paso natural es leer el endpoint HTTP que llama a `handle_message(history)` (normalmente en `python_backend/main.py`), porque eso conecta backend con frontend.
