# Arch-Assistant: Asistente de IA para Arquitectura de Software

Aplicación web que proporciona recomendaciones de arquitectura de software mediante conversación interactiva con IA.

---

## Descripción General

**Arch-Assistant** consta de:
- **Frontend**: Aplicación web HTML/CSS/JavaScript que se sirve desde `public/`
- **Backend**: Servidor FastAPI que ejecuta la lógica de conversación y recomendación

El sistema:
1. Mantiene un historial de conversación
2. Interpreta respuestas del usuario mediante API DeepSeek
3. Genera recomendaciones basadas en parámetros inferidos
4. Retorna las 3 mejores arquitecturas

---

## Requisitos Previos

### Sistema Operativo
- Windows, macOS o Linux (el proyecto tiene scripts de instalación para Windows y Unix)

### Software Requerido
- Python (versión mínima no especificada en el proyecto)
- Git

### Acceso
- Clave API de DeepSeek requerida para funcionamiento

---

## Instalación

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/JessusTM/Archssistant.git
cd Archssistant
```

### Paso 2: Crear Entorno Virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

**Dependencias (según requirements.txt):**
- fastapi==0.110.0
- uvicorn==0.27.1
- requests==2.32.3
- python-dotenv==1.0.1
- pydantic==2.6.4

### Paso 4: Configurar Variables de Entorno

Crea archivo `.env` en la raíz del proyecto:

```env
DEEPSEEK_API_KEY=tu_clave_aqui
PORT=5000
HOST=0.0.0.0
```

O copia desde `.env.example` si existe:

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

Luego edita `.env` con tu clave API de DeepSeek.

---

## Configuración

### Variables de Entorno

El archivo `.env` contiene:
- `DEEPSEEK_API_KEY` - Clave API de DeepSeek (requerida)
- `PORT` - Puerto del servidor (por defecto: 5000)
- `HOST` - Host del servidor (por defecto: 0.0.0.0)

### Archivo .env.example

- Plantilla en la raíz: `.env.example`
- Copia la plantilla a `.env` (no versionar `.env`).

---

## Seguridad y gitignore

- El `.gitignore` en la raíz excluye `.env`, entornos virtuales (`venv/`, `.venv/`), `node_modules/`, logs, temporales y credenciales (`secrets/`, `credentials/`, `*.key`, `*.pem`, `*.cert`).
- No subas nunca `.env` ni llaves; usa `.env.example` como plantilla.
- `python_backend/.gitignore` refuerza las exclusiones dentro del backend.

---

## Uso

### Iniciar el Servidor

Desde `python_backend/`:

```bash
python main.py
```

El servidor se inicia en: `http://localhost:5000`

### Acceder a la Aplicación

Abre navegador en: `http://localhost:5000`

La carpeta `public/` se sirve automáticamente como estática.

### Rutas del API (backend FastAPI)

- `POST /api/chat`
  - **Body**: `{ "history": [ {"role": "user" | "assistant" | "user_description", "content": "..."} ] }`
  - **Flujo**: entrevista hasta inferir ≥5 parámetros; luego recomienda TOP 3 arquitecturas y pide descripciones al LLM.
  - **Respuesta**:
    - `response.content`: texto de la pregunta o agradecimiento final
    - `response.recommendation` (cuando finaliza): lista de 3 arquitecturas con `name`, `description`, `justification` y métricas
    - `state`: `status` (`interviewing` | `recommending` | `finished`), `inferredParams`, `lastQuestion`, `isClarifying`

### Flujo de Interacción

1. Usuario envía descripción del proyecto en el primer mensaje
2. Sistema marca como `role: user_description`
3. Sistema inicia preguntas sobre parámetros
4. Usuario responde las preguntas
5. Sistema interpreta respuestas (CERTAIN o UNCERTAIN)
6. Cuando se recopilan ≥5 parámetros → genera recomendaciones
7. Retorna TOP 3 arquitecturas con descripciones

---

## Estructura de Directorios

```
archssistant/
├── README.md
├── .gitignore
├── .env                          (creado por usuario, no en Git)
├── .env.example
├── requirements.txt
├── diagrama de componentes.png
│
├── public/                       (Frontend)
│   ├── index.html
│   ├── script.js
│   └── style.css
│
└── python_backend/               (Backend)
    ├── main.py
  ├── .gitignore
    │
    └── server/
        ├── __init__.py
        ├── dialogue_orchestrator/
        │   ├── __init__.py
        │   └── orchestrator.py
        ├── llm_service/
        │   ├── __init__.py
        │   └── llm_service.py
        └── recommendation_engine/
            ├── __init__.py
            ├── engine.py
            └── architecture_data.py
```

---

## Componentes Principales

### Frontend (public/)

#### index.html
- Estructura HTML con layout de 2 columnas (sidebar + chat)
- Elemento canvas para animaciones de partículas
- Formulario de entrada de chat
- Divs para mostrar mensajes y progreso

#### script.js
- Event listener para submit del formulario
- Función fetch a `/api/chat`
- Actualiza DOM con respuestas
- Calcula y muestra progreso de parámetros (0-5)
- Escapa HTML para seguridad
- Animaciones de partículas en canvas

#### style.css
- Variables CSS para colores y fuentes
- Definiciones de glassmorphism, gradientes, animaciones
- Responsive design con media queries
- 1073 líneas de estilos

### Backend - Dialogue Orchestrator (server/dialogue_orchestrator/)

#### orchestrator.py
- Función `handle_message(history)` - punto de entrada
- Función `get_conversation_state(history)` - extrae estado
- Estados posibles: `interviewing`, `recommending`, `finished`
- Parámetros: complexity, scalability, teamExperience, dataVolume, teamSize, availability, maintainability, interoperability
- Lógica:
  - Si estado "interviewing": genera preguntas hasta ≥5 parámetros
  - Si estado "recommending": obtiene TOP 3 y genera descripciones
  - Maneja UNCERTAIN con modo clarificación

### Backend - LLM Service (server/llm_service/)

#### llm_service.py
- `call_api(messages, temperature)` - petición HTTP a DeepSeek
- `interpret_user_answer(question_text, user_answer, parameter_to_infer)` - clasifica respuesta
- `generate_next_question(history, remaining_params, last_interpretation, is_clarification_needed)` - genera pregunta
- `generate_final_descriptions(project_description, recommendations, history)` - describe arquitecturas
- URL API: `https://api.deepseek.com/v1/chat/completions`
- Modelo: `deepseek-chat`
- Validación de claves API

### Backend - Recommendation Engine (server/recommendation_engine/)

#### architecture_data.py
Contiene lista `architectures` con 7 arquitecturas:
1. Arquitectura Monolítica
2. Arquitectura de Microservicios
3. Arquitectura Orientada a Servicios (SOA)
4. Arquitectura de Capas
5. Arquitectura Cliente-Servidor
6. Arquitectura en la Nube
7. Arquitectura Basada en Eventos (EDA)

Cada una tiene estos parámetros:
- complexity, scalability, teamExperience, dataVolume, teamSize, availability, maintainability, interoperability

#### engine.py
- Función `get_recommendation(user_answers)`
- VALUE_MAP: mapea valores a números (Baja→1, Alta→4, Excelente→5, etc.)
- Algoritmo: +2 puntos si diferencia=0, +1 si diferencia=1
- Retorna TOP 3 arquitecturas ordenadas por score

#### Editar Arquitecturas (Tutorial)

Esta sección te guía para personalizar las arquitecturas que el sistema considera al recomendar.

- **Ubicación:** Ver [python_backend/server/recommendation_engine/architecture_data.py](python_backend/server/recommendation_engine/architecture_data.py)
- **Estructura:** Lista `architectures` de objetos con claves:
  - `name`, `complexity`, `scalability`, `teamExperience`, `dataVolume`, `teamSize`, `availability`, `maintainability`, `interoperability`
- **Valores permitidos:**
  - Para la mayoría: Baja, Moderada, Alta, Excelente
  - `teamSize`: Pequeño, Moderado, Grande, Alto
  - `dataVolume`: Moderado, Alto, Excelente

Pasos comunes:

1) Añadir una arquitectura

Inserta un nuevo objeto dentro de la lista `architectures` en el archivo indicado.

Ejemplo:

```python
{
    'name': 'Arquitectura Hexagonal (Ports & Adapters)',
    'complexity': 'Alta',
    'scalability': 'Moderada',
    'teamExperience': 'Alta',
    'dataVolume': 'Moderado',
    'teamSize': 'Moderado',
    'availability': 'Alta',
    'maintainability': 'Excelente',
    'interoperability': 'Alta'
}
```

2) Eliminar una arquitectura

Borra el objeto correspondiente de la lista `architectures` (asegúrate de mantener la sintaxis válida de Python).

3) Modificar una arquitectura

Edita los valores de las claves existentes usando las categorías permitidas arriba. Cambios inválidos (valores fuera de catálogo) no puntuarán al calcular el ranking.

Notas importantes:

- **Nombre exacto:** El módulo de descripciones usa el `name` como clave para generar textos; mantén nombres únicos y bien escritos para que coincidan en la salida.
- **Impacto en el ranking:** `engine.py` toma automáticamente todas las entradas en `architectures`. Añadir o quitar elementos afecta el TOP 3.
- **Prueba rápida:** Reinicia el backend y ejecuta una conversación que infiera al menos 5 parámetros; verás la nueva arquitectura competir en el ranking.

Comandos útiles (Windows):

```powershell
cd python_backend
python .\main.py
```

#### Catálogo de valores permitidos (VALUE_MAP)

Para que el motor de puntuación funcione, usa exactamente estas palabras (con mayúsculas y tildes) al editar las arquitecturas en [python_backend/server/recommendation_engine/architecture_data.py](python_backend/server/recommendation_engine/architecture_data.py). Se aceptan formas de género donde se indica.

- Escalas generales: Baja (1), Moderada/Moderado (3), Alta/Alto (4), Excelente (5)
- Tamaño del equipo (`teamSize`): Pequeño (2), Moderado (3), Grande (4), Alto (4)
- Volumen de datos (`dataVolume`): Moderado (3), Alto (4), Excelente (5)

Notas:
- Los valores deben coincidir exactamente con el catálogo anterior; otros valores no puntúan.
- `Moderada` y `Moderado` se tratan igual (3); `Alta` y `Alto` se tratan igual (4).
- `Grande` y `Alto` se mapean ambos a 4 para `teamSize`.

### Backend - Main Server (main.py)

- FastAPI app con titulo 'Arch-Assistant' version '1.0.0'
- CORS habilitado para todos los orígenes (`allow_origins=['*']`)
- Endpoint `POST /api/chat` recibe `ChatRequest` con campo `history` (lista)
- Sirve archivos estáticos desde carpeta `public/`
- Manejo de excepciones: 400, 401, 500
- Lee variables de entorno: PORT (defecto 5000), HOST (defecto 0.0.0.0)

---

## API REST

### Endpoint: POST /api/chat

**URL:** `http://localhost:5000/api/chat`

**Request:**
```json
{
  "history": [
    {"role": "user", "content": "texto"},
    {"role": "assistant", "content": "respuesta", "state": {...}}
  ]
}
```

**Response (200):**
```json
{
  "response": {
    "role": "assistant",
    "content": "texto",
    "recommendation": [...]  // null si no hay recomendación
  },
  "state": {
    "inferredParams": {...},
    "lastQuestion": {...},
    "isClarifying": boolean,
    "status": "string"
  }
}
```

**Errores:**
- 400: historial no es array
- 401: problema con clave API DeepSeek
- 500: error interno

---

## Arquitecturas Soportadas

El sistema recomienda de estas 7 opciones:

1. **Arquitectura Monolítica** - Baja complejidad, baja escalabilidad
2. **Arquitectura de Microservicios** - Alta complejidad, alta escalabilidad
3. **Arquitectura Orientada a Servicios (SOA)** - Alta complejidad, escalabilidad moderada
4. **Arquitectura de Capas** - Alta complejidad, escalabilidad moderada
5. **Arquitectura Cliente-Servidor** - Complejidad moderada, alta escalabilidad
6. **Arquitectura en la Nube** - Alta complejidad, escalabilidad excelente
7. **Arquitectura Basada en Eventos (EDA)** - Alta complejidad, alta escalabilidad

Cada una tiene valores para: complexity, scalability, teamExperience, dataVolume, teamSize, availability, maintainability, interoperability.

---

## Tecnologías Utilizadas

### Frontend
- HTML5
- CSS3
- JavaScript (Vanilla ES6+)
- Canvas API (para animaciones)
- Google Fonts (Orbitron, Rajdhani, Space Mono)

### Backend
- Python
- FastAPI 0.110.0
- Uvicorn 0.27.1
- Pydantic 2.6.4
- Requests 2.32.3
- python-dotenv 1.0.1

### APIs Externas
- DeepSeek API (https://api.deepseek.com/v1/chat/completions)

---

## Parámetros Inferidos

El sistema intenta inferir estos 8 parámetros:

1. `complexity` - Baja, Moderada, Alta, Excelente
2. `scalability` - Baja, Moderada, Alta, Excelente
3. `teamExperience` - Baja, Moderada, Alta, Excelente
4. `dataVolume` - Moderado, Alto, Excelente
5. `teamSize` - Pequeño, Moderado, Grande, Alto
6. `availability` - Baja, Moderada, Alta, Excelente
7. `maintainability` - Baja, Moderada, Alta, Excelente
8. `interoperability` - Baja, Moderada, Alta, Excelente

Cuando se recopilan ≥5, el sistema genera recomendación.

---

## Flujo de Ejecución

1. Usuario abre http://localhost:5000
2. Carga index.html + script.js + style.css
3. script.js inicia conversationHistory = []
4. Usuario escribe mensaje y hace submit
5. script.js hace POST /api/chat con {history: [...]}
6. main.py recibe, llama handle_message()
7. orchestrator.py procesa según estado:
   - Si primera vez: marca como user_description, inicia entrevista
   - Si interviewing: interpreta respuesta, genera siguiente pregunta
   - Si >= 5 parámetros: status = recommending
   - Si recommending: obtiene TOP 3 y genera descripciones
8. Retorna response + state actualizado
9. script.js actualiza DOM con respuesta
10. Muestra progreso (parámetros recopilados / 5)

---

## Notas Importantes

- El archivo `.env` NO se sube a Git (está en .gitignore)
- La carpeta `python_backend/venv` está en .gitignore
- El proyecto usa async/await en Python
- DeepSeek API requiere autenticación con Bearer token
- Las respuestas de DeepSeek deben ser JSON válido

---

## Autores

- J. Tapia
- Z. Xiao

---

## Referencias

- Repositorio: https://github.com/JessusTM/Archssistant
- FastAPI docs: https://fastapi.tiangolo.com/
- DeepSeek API: https://www.deepseek.com/
