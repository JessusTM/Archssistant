# 🏗️ Arch-Assistant: Asistente de IA para Arquitectura de Software

**Arch-Assistant** es un asistente inteligente basado en IA que ayuda a desarrolladores y arquitectos de software a diseñar la mejor arquitectura para sus proyectos. Mediante una conversación interactiva, el sistema recopila información sobre los requisitos del proyecto y recomienda la arquitectura más adecuada.

---

## 📋 Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Características Principales](#características-principales)
3. [Arquitectura del Proyecto](#arquitectura-del-proyecto)
4. [Requisitos Previos](#requisitos-previos)
5. [Instalación](#instalación)
6. [Configuración](#configuración)
7. [Uso](#uso)
8. [Estructura de Directorios](#estructura-de-directorios)
9. [Componentes Principales](#componentes-principales)
10. [API REST](#api-rest)
11. [Flujo de Conversación](#flujo-de-conversación)
12. [Arquitecturas Soportadas](#arquitecturas-soportadas)
13. [Tecnologías Utilizadas](#tecnologías-utilizadas)
14. [Contribuciones](#contribuciones)
15. [Licencia](#licencia)
16. [Autores](#autores)

---

## 📖 Descripción General

**Arch-Assistant** es una aplicación web que combina un frontend moderno con interfaz de usuario futurista y un backend robusto basado en IA. El sistema:

- **Entrevista al usuario** mediante preguntas inteligentes sobre su proyecto
- **Interpreta respuestas** utilizando análisis de lenguaje natural con IA
- **Infiere parámetros** clave como escalabilidad, complejidad, experiencia del equipo, etc.
- **Recomienda arquitecturas** adaptadas a los requisitos específicos del proyecto
- **Proporciona descripciones detalladas** de cada arquitectura recomendada

El proyecto está diseñado por **J. Tapia** y **Z. Xiao**, como una solución para ayudar a tomar decisiones arquitectónicas fundamentadas.

---

## ✨ Características Principales

### 🤖 **Inteligencia Artificial Avanzada**
- Integración con API de DeepSeek para procesamiento de lenguaje natural
- Sistema de clasificación semántica ultraprecisa
- Generación dinámica de preguntas de clarificación

### 💬 **Interfaz Conversacional Inteligente**
- Diálogo natural y fluido con el usuario
- Recopilación progresiva de parámetros
- Modo de clarificación automático para respuestas ambiguas

### 📊 **Motor de Recomendación**
- Algoritmo de puntuación basado en coincidencia de parámetros
- Recomendación de las 3 mejores arquitecturas
- Justificación detallada de cada recomendación

### 🎨 **Interfaz de Usuario Moderna**
- Diseño futurista con degradados y efectos glassmorphism
- Animaciones suaves y responsivas
- Panel de "Motor de Inferencia" con indicadores visuales en tiempo real
- Visualización circular del progreso de parámetros recopilados

### 🔄 **Gestión de Contexto**
- Seguimiento del estado de conversación
- Mantenimiento del historial de conversación
- Persistencia de parámetros inferidos

---

## 🏛️ Arquitectura del Proyecto

```
┌─────────────────────────────────────────────────────┐
│           Frontend (Public)                          │
│  ┌─────────────────────────────────────────────┐   │
│  │  HTML5 + CSS3 + JavaScript (Vanilla)        │   │
│  │  • index.html - Estructura interactiva      │   │
│  │  • script.js - Lógica de cliente            │   │
│  │  • style.css - Estilos futuristas           │   │
│  └─────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────┘
                     │ HTTP/CORS
┌────────────────────▼────────────────────────────────┐
│        Backend (Python/FastAPI)                      │
│  ┌──────────────────────────────────────────────┐  │
│  │ main.py - Servidor FastAPI + CORS            │  │
│  └───────────────────┬──────────────────────────┘  │
│                      │                              │
│  ┌───────────────────▼──────────────────────────┐  │
│  │  Dialogue Orchestrator                        │  │
│  │  • orchestrator.py - Orquestador principal  │  │
│  │  • Gestión de flujo de conversación          │  │
│  │  • Control de estados                        │  │
│  └───────────────────┬──────────────────────────┘  │
│                      │                              │
│  ┌───────────────────┴──────────────────────────┐  │
│  │         LLM Service (IA)                      │  │
│  │  • llm_service.py - API DeepSeek             │  │
│  │  • Interpretación de respuestas              │  │
│  │  • Generación de preguntas                   │  │
│  │  • Generación de recomendaciones             │  │
│  └────────────────────────────────────────────┘  │
│                      │                              │
│  ┌───────────────────▼──────────────────────────┐  │
│  │  Recommendation Engine                        │  │
│  │  • engine.py - Motor de recomendación        │  │
│  │  • architecture_data.py - Base de datos      │  │
│  │  • Algoritmo de puntuación                   │  │
│  └───────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

---

## 📦 Requisitos Previos

### **Sistema Operativo**
- Windows 10/11, macOS o Linux

### **Software Requerido**
- **Python 3.8+** (recomendado 3.9 o superior)
- **Node.js** (opcional, si deseas usar herramientas complementarias)
- **Git** (para clonar el repositorio)

### **Cuenta en DeepSeek**
- Necesitas una clave API de [DeepSeek](https://www.deepseek.com/) para el funcionamiento de la IA

---

## 🚀 Instalación

### **Paso 1: Clonar el Repositorio**

```bash
git clone https://github.com/JessusTM/Archssistant.git
cd Archssistant
```

### **Paso 2: Configurar el Entorno Python**

#### **En Windows:**
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate
```

#### **En macOS/Linux:**
```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate
```

### **Paso 3: Instalar Dependencias**

```bash
cd python_backend
pip install -r requirements.txt
```

**Dependencias instaladas:**
- `fastapi==0.110.0` - Framework web moderno
- `uvicorn==0.27.1` - Servidor ASGI
- `requests==2.32.3` - Cliente HTTP
- `python-dotenv==1.0.1` - Gestión de variables de entorno
- `pydantic==2.6.4` - Validación de datos

### **Paso 4: Configurar Variables de Entorno**

#### **Opción 1: Renombrar archivo `.env.example` (Recomendado)**

Si existe un archivo `.env.example` en el proyecto:

```bash
# En Windows
copy .env.example .env

# En macOS/Linux
cp .env.example .env
```

Luego, abre el archivo `.env` y reemplaza el valor:

```env
DEEPSEEK_API_KEY=tu_clave_api_real_aqui
```

#### **Opción 2: Crear archivo `.env` manualmente**

Si no existe `.env.example`, crea un archivo `.env` en la raíz del proyecto:

```bash
# En Windows (PowerShell)
@"
DEEPSEEK_API_KEY=tu_clave_api_real_aqui
"@ | Out-File -FilePath .env -Encoding UTF8

# En macOS/Linux
cat > .env << EOF
DEEPSEEK_API_KEY=tu_clave_api_real_aqui
EOF
```

**⚠️ IMPORTANTE:** 
- Reemplaza `tu_clave_api_real_aqui` con tu clave API real de DeepSeek
- **NUNCA** subas el archivo `.env` a GitHub (está en `.gitignore`)
- Mantén tu clave API segura y confidencial

---

## ⚙️ Configuración

### **Variables de Entorno (.env)**

```env
# DeepSeek API Configuration (REQUERIDO)
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Configuración del servidor (Opcional - usa valores por defecto si no se especifica)
PORT=5000
HOST=0.0.0.0
```

**Variables:**
- `DEEPSEEK_API_KEY` *(requerido)* - Tu clave API de DeepSeek
- `PORT` *(opcional, defecto: 5000)* - Puerto donde escuchar
- `HOST` *(opcional, defecto: 0.0.0.0)* - Host/IP donde escuchar

**Obtener la clave API:**
1. Visita [https://www.deepseek.com/](https://www.deepseek.com/)
2. Crea una cuenta o inicia sesión
3. Ve a la sección de API Keys
4. Genera una nueva clave API
5. Copia la clave y pégala en `.env`

### **Configuración de CORS**

El servidor FastAPI está configurado para aceptar peticiones de cualquier origen. Para producción, modifica `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=['https://tudominio.com'],  # Especifica tus dominios
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
```

---

## 💻 Uso

### **Iniciar el Servidor**

Desde la carpeta `python_backend/`:

```bash
python main.py
```

**Output esperado:**
```
Servidor Arch-Assistant iniciando en http://localhost:5000
INFO:     Uvicorn running on http://0.0.0.0:5000
INFO:     Started server process [12345]
```

**Nota:** El puerto por defecto es `5000`. Puedes cambiarlo configurando la variable de entorno `PORT` en `.env`.

### **Acceder a la Aplicación**

Abre tu navegador y ve a:
```
http://localhost:5000
```

La carpeta `public/` se sirve automáticamente desde la raíz.

### **Primer Uso**

1. **Carga la interfaz**: Se mostrará el mensaje de bienvenida del asistente
2. **Describe tu proyecto**: Escribe una descripción inicial de tu proyecto
3. **Responde preguntas**: El sistema hará preguntas sobre 8 parámetros clave:
   - Complejidad del sistema
   - Requisitos de escalabilidad
   - Experiencia del equipo
   - Volumen de datos esperado
   - Tamaño del equipo
   - Disponibilidad requerida
   - Mantenibilidad
   - Interoperabilidad

4. **Recibe recomendación**: Cuando se recopilen 5 parámetros, el sistema generará las 3 mejores arquitecturas recomendadas

### **Ejemplo de Conversación**

```
Usuario: "Necesito construir un sistema de comercio electrónico que pueda 
         manejar millones de transacciones diarias. Tengo un equipo grande 
         y experiencia con sistemas distribuidos."

Sistema: ¿Cuál es tu enfoque en términos de velocidad de desarrollo 
         versus capacidades avanzadas?

Usuario: "Necesitamos capacidades avanzadas, escalabilidad extrema es 
         crítico."

Sistema: [Recomendación: Microservicios, Nube, EDA]
```

---

## 📁 Estructura de Directorios

```
archssistant/
│
├── 📄 README.md                          # Este archivo
├── 📄 .gitignore                         # Archivos a ignorar en Git
├── 📄 .env                               # Variables de entorno (no incluir en Git)
├── 🖼️ diagrama de componentes.png        # Diagrama visual de la arquitectura
│
├── 📂 public/                            # Frontend (Aplicación Web)
│   ├── 📄 index.html                    # Página HTML principal
│   ├── 📄 script.js                     # Lógica de JavaScript del cliente
│   └── 📄 style.css                     # Estilos CSS (diseño futurista)
│
└── 📂 python_backend/                    # Backend (Servidor Python)
    ├── 📄 main.py                       # Punto de entrada del servidor FastAPI
    ├── 📄 requirements.txt               # Dependencias Python
    │
    └── 📂 server/                       # Lógica principal del servidor
        ├── 📄 __init__.py               # Inicializador del paquete
        │
        ├── 📂 dialogue_orchestrator/    # Orquestador de diálogo
        │   ├── 📄 __init__.py           # Importa funciones del orquestador
        │   └── 📄 orchestrator.py       # Lógica principal del flujo
        │
        ├── 📂 llm_service/              # Servicio de IA/LLM
        │   ├── 📄 __init__.py           # Importa funciones del servicio LLM
        │   └── 📄 llm_service.py        # Integración con API DeepSeek
        │
        └── 📂 recommendation_engine/    # Motor de recomendación
            ├── 📄 __init__.py           # Importa funciones del motor
            ├── 📄 engine.py             # Lógica de puntuación y recomendación
            └── 📄 architecture_data.py  # Base de datos de arquitecturas
```

---

## 🔧 Componentes Principales

### **1. Frontend (public/)**

#### `index.html`
- Estructura HTML semántica con soporte multiidioma (ES)
- Elementos interactivos para chat
- Panel lateral con "Motor de Inferencia" visualizado
- Canvas para animaciones de partículas
- Formulario de entrada con validación

#### `script.js`
- Gestión de eventos de formulario
- Comunicación con API backend via fetch
- Manejo del historial de conversación
- Actualización dinámica del DOM
- Animaciones y efectos visuales
- Funciones de escape HTML para seguridad

#### `style.css`
- Variables CSS personalizadas
- Diseño glassmorphism moderno
- Gradientes neón (cyan, azul, púrpura)
- Animaciones con @keyframes
- Responsive design con flexbox y grid
- Tipografía: Orbitron (títulos), Rajdhani (cuerpo), Space Mono (monoespaciada)

### **2. Backend - Dialogue Orchestrator**

#### `orchestrator.py`
**Responsabilidades:**
- Orquesta el flujo completo de conversación
- Gestiona el estado de la entrevista
- Controla las fases: entrevista → clarificación → recomendación
- Interpreta respuestas del usuario
- Genera preguntas siguientes
- Solicita recomendaciones al motor

**Estados principales:**
```
interviewing → (fase de recopilación de parámetros)
recommending → (fase de generación de recomendación)
finished     → (conversación completada)
```

**Parámetros definidos:**
```python
ALL_PARAMETERS = [
    'complexity', 'scalability', 'teamExperience', 'dataVolume',
    'teamSize', 'availability', 'maintainability', 'interoperability'
]
```

**Lógica principal:**
1. Si status="interviewing" y hay pregunta previa:
   - Interpreta respuesta anterior vía LLM
   - Clasifica como CERTAIN o UNCERTAIN
   - Si UNCERTAIN → activa isClarifying=true
   - Si CERTAIN → añade a inferredParams
   
2. Si se han recopilado >= 5 parámetros → status="recommending"

3. Si status="recommending":
   - Obtiene top 3 arquitecturas del motor
   - Genera descripciones vía LLM
   - Retorna respuesta con recomendaciones

### **3. Backend - LLM Service**

#### `llm_service.py`

**Funciones principales:**

1. **`call_api(messages, temperature=0.2)`**
   - Realiza peticiones HTTP a API DeepSeek
   - Usa modelo: `deepseek-chat`
   - Requiere autenticación via Bearer token
   - Retorna respuesta en formato JSON
   - Maneja errores de autenticación y validación de claves

2. **`interpret_user_answer(question_text, user_answer, parameter_to_infer)`**
   - Clasifica respuesta del usuario
   - Retorna: `{"classification": "valor", "confidence": "high|medium|low", "reasoning": "..."}`
   - Clasifica como UNCERTAIN si el usuario es ambiguo o no sabe
   - Temperature: 0.0 (máxima consistencia)

3. **`generate_next_question(history, remaining_params, last_interpretation, is_clarification_needed)`**
   - Genera siguiente pregunta estratégica
   - Analiza si se necesita clarificación o preguntar nuevo parámetro
   - Si es clarificación: reformula pregunta más simple sobre mismo parámetro
   - Si es normal: elige parámetro estratégico (escala > equipo > calidad)
   - Temperature: 0.6
   - Retorna: `{"parameter_to_infer": "...", "question_for_user": "...", "full_response_text": "..."}`

4. **`generate_final_descriptions(project_description, recommendations, history)`**
   - Genera descripción y justificación para cada arquitectura recomendada
   - Temperature: 0.6
   - Retorna objeto JSON con claves exactas a nombres de arquitecturas
   - Si falla, retorna descripciones por defecto

**Validaciones de Clave API:**
- Detecta si la clave es un placeholder ("sk-replace_me", "tu_clave_api_aqui", etc)
- Valida que no esté vacía
- Lanza `ApiKeyError` si hay problemas de autenticación

### **4. Backend - Recommendation Engine**

#### `architecture_data.py`
Base de datos con **7 arquitecturas** predefinidas:

| # | Nombre | Complejidad | Escalabilidad | Disponibilidad |
|---|--------|------------|--------------|----------------|
| 1 | Monolítica | Baja | Baja | Baja |
| 2 | Microservicios | Alta | Alta | Excelente |
| 3 | SOA | Alta | Moderada | Alta |
| 4 | Capas | Alta | Moderada | Moderada |
| 5 | Cliente-Servidor | Moderada | Alta | Moderada |
| 6 | Nube | Alta | Excelente | Excelente |
| 7 | Basada en Eventos (EDA) | Alta | Alta | Alta |

Cada arquitectura tiene 8 parámetros:
- `complexity` - Complejidad técnica
- `scalability` - Capacidad de escalar
- `teamExperience` - Experiencia requerida del equipo  
- `dataVolume` - Volumen de datos que maneja
- `teamSize` - Tamaño de equipo recomendado
- `availability` - Disponibilidad del sistema
- `maintainability` - Facilidad de mantenimiento
- `interoperability` - Interoperabilidad con otros sistemas

#### `engine.py`

**Función: `get_recommendation(user_answers)`**

Algoritmo de puntuación:
```python
VALUE_MAP = {
    'Baja': 1, 'Pequeño': 2, 'Moderado': 3, 'Moderada': 3,
    'Alta': 4, 'Grande': 4, 'Alto': 4, 'Excelente': 5
}

# Para cada parámetro del usuario:
difference = abs(user_score - architecture_score)
if difference == 0:
    score += 2  # Coincidencia exacta
elif difference == 1:
    score += 1  # Coincidencia cercana
```

**Retorna:** Las 3 mejores arquitecturas ordenadas por puntuación descendente

**Ejemplo:**
```
Entrada: {'scalability': 'Alta', 'complexity': 'Alta', 'teamSize': 'Grande'}
Salida: [
  {'name': 'Microservicios', 'score': 6, ...},
  {'name': 'Nube', 'score': 5, ...},
  {'name': 'EDA', 'score': 5, ...}
]
```

### **5. Backend - Main Server**

#### `main.py`

**Inicialización:**
```python
app = FastAPI(title='Arch-Assistant', version='1.0.0')

# CORS habilitado para todos los orígenes
app.add_middleware(CORSMiddleware, allow_origins=['*'], ...)

# Sirve archivos estáticos desde public/
app.mount('/', StaticFiles(directory=public_dir, html=True), name='static')
```

**Endpoint único:**

```python
@app.post('/api/chat')
async def chat(request: ChatRequest):
    """
    Recibe historial de conversación, procesa mensaje final,
    retorna respuesta y estado actualizado.
    """
```

**Validaciones:**
- Verifica que `request.history` sea un array
- Retorna error 400 si es inválido
- Captura `ApiKeyError` → retorna error 401
- Captura excepciones generales → retorna error 500

**Configuración via Entorno:**
```python
PORT = int(os.getenv('PORT', 5000))       # Puerto (defecto: 5000)
HOST = os.getenv('HOST', '0.0.0.0')       # Host (defecto: 0.0.0.0)
```

**Response:**
```json
{
  "response": {
    "role": "assistant",
    "content": "Texto de respuesta",
    "recommendation": [
      {
        "name": "Arquitectura X",
        "description": "...",
        "justification": "...",
        ... (más parámetros arquitectónicos)
      }
    ] // null si aún no hay recomendación
  },
  "state": {
    "inferredParams": {...},
    "lastQuestion": {...},
    "isClarifying": false,
    "status": "interviewing|recommending|finished"
  }
}
```

---

## 🔌 API REST

### **Endpoint: POST /api/chat**

**Descripción:** Procesa un mensaje del usuario y retorna la respuesta del asistente con estado actualizado.

**URL:**
```
POST http://localhost:5000/api/chat
```

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "history": [
    {
      "role": "user",
      "content": "Necesito construir un e-commerce"
    },
    {
      "role": "assistant",
      "content": "Entendido. ¿Cuál es tu escala esperada?",
      "state": {
        "inferredParams": {},
        "lastQuestion": {
          "parameter_to_infer": "scalability",
          "question_text": "..."
        },
        "isClarifying": false,
        "status": "interviewing"
      }
    },
    {
      "role": "user",
      "content": "Millones de usuarios"
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "response": {
    "role": "assistant",
    "content": "Basándome en tus respuestas...",
    "recommendation": {
      "architectures": [
        {
          "name": "Arquitectura en la Nube",
          "score": 18,
          "description": "..."
        },
        {
          "name": "Microservicios",
          "score": 16,
          "description": "..."
        }
      ]
    },
    "state": {
      "inferredParams": {
        "scalability": "Alta",
        "complexity": "Alta"
      },
      "status": "completed"
    }
  },
  "state": {
    "inferredParams": {...},
    "lastQuestion": null,
    "isClarifying": false,
    "status": "completed"
  }
}
```

**Errores Posibles:**

| Código | Descripción |
|--------|-------------|
| 400 | Historial inválido o no es un array |
| 401 | Clave API de DeepSeek no configurada o inválida |
| 500 | Error del servidor |

---

## 🔄 Flujo de Conversación

```
┌──────────────────────────────────────────────────────────────┐
│ FASE 1: INICIALIZACIÓN                                       │
├──────────────────────────────────────────────────────────────┤
│ 1. Usuario describe el proyecto en el primer mensaje         │
│ 2. Sistema marca como "role: user_description"              │
│ 3. Inicia estado "interviewing"                             │
└────────────────────┬─────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────┐
│ FASE 2: ENTREVISTA (status: "interviewing")                 │
├──────────────────────────────────────────────────────────────┤
│ Ciclo iterativo hasta recopilar 5 parámetros:               │
│ 1. Genera pregunta estratégica vía LLM                       │
│ 2. Usuario responde                                          │
│ 3. Interpreta respuesta: CERTAIN o UNCERTAIN                │
│ 4. Si es CERTAIN → infiere parámetro (score +2 o +1)        │
│ 5. Si es UNCERTAIN → modo clarificación                     │
│                                                              │
│ Parámetros disponibles (max 8):                             │
│   - complexity          (Baja, Moderada, Alta, Excelente)   │
│   - scalability         (Baja, Moderada, Alta, Excelente)   │
│   - teamExperience      (Baja, Moderada, Alta, Excelente)   │
│   - dataVolume          (Moderado, Alto, Excelente)         │
│   - teamSize            (Pequeño, Moderado, Grande, Alto)   │
│   - availability        (Baja, Moderada, Alta, Excelente)   │
│   - maintainability     (Baja, Moderada, Alta, Excelente)   │
│   - interoperability    (Baja, Moderada, Alta, Excelente)   │
└────────────────────┬─────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────┐
│ FASE 3: CLARIFICACIÓN (si isClarifying = true)              │
├──────────────────────────────────────────────────────────────┤
│ Si respuesta anterior fue UNCERTAIN:                         │
│ 1. Empatiza con usuario                                      │
│ 2. Genera pregunta más simple sobre el MISMO parámetro       │
│ 3. Intenta clasificación más clara (si falla → mantiene)     │
│ 4. Retorna a ENTREVISTA con nuevo parámetro                 │
└────────────────────┬─────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────┐
│ FASE 4: RECOMENDACIÓN (cuando >= 5 parámetros)             │
├──────────────────────────────────────────────────────────────┤
│ 1. Calcula puntuación para TODAS las 7 arquitecturas         │
│ 2. Ordena por score (descendente)                            │
│ 3. Selecciona TOP 3 arquitecturas                            │
│ 4. Genera descripción y justificación via LLM                │
│ 5. Retorna respuesta con "recommendation" array              │
│ 6. status → "finished"                                       │
└──────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Arquitecturas Soportadas

El sistema recomienda una de estas 7 arquitecturas basada en los parámetros inferidos:

### **1. Monolítica**
- **Complejidad:** Baja
- **Escalabilidad:** Baja
- **Equipo:** Pequeño, poca experiencia
- **Mejor para:** Startups, MVPs, proyectos pequeños

### **2. Microservicios**
- **Complejidad:** Alta
- **Escalabilidad:** Alta
- **Disponibilidad:** Excelente
- **Mejor para:** Sistemas grandes, equipos grandes, alto tráfico

### **3. SOA (Arquitectura Orientada a Servicios)**
- **Complejidad:** Alta
- **Escalabilidad:** Moderada
- **Interoperabilidad:** Excelente
- **Mejor para:** Integraciones empresariales complejas

### **4. Arquitectura de Capas**
- **Complejidad:** Alta
- **Mantenibilidad:** Alta
- **Escalabilidad:** Moderada
- **Mejor para:** Aplicaciones tradicionales, equipos medianos

### **5. Cliente-Servidor**
- **Complejidad:** Moderada
- **Escalabilidad:** Alta
- **Disponibilidad:** Moderada
- **Mejor para:** Aplicaciones web clásicas, escalado horizontal

### **6. Arquitectura en la Nube**
- **Complejidad:** Alta
- **Escalabilidad:** Excelente
- **Disponibilidad:** Excelente
- **Mejor para:** Cualquier proyecto moderno, máxima escalabilidad

### **7. Basada en Eventos (EDA - Event-Driven Architecture)**
- **Complejidad:** Alta
- **Escalabilidad:** Alta
- **Volumen de datos:** Excelente
- **Mejor para:** Sistemas reactivos, streaming de datos, eventos en tiempo real

---

## 🛠️ Tecnologías Utilizadas

### **Frontend**
| Tecnología | Versión | Uso |
|------------|---------|-----|
| HTML5 | - | Estructura semántica |
| CSS3 | - | Estilos y animaciones |
| JavaScript (Vanilla) | ES6+ | Lógica de cliente |
| Canvas API | - | Animación de partículas |

### **Backend**
| Tecnología | Versión | Uso |
|------------|---------|-----|
| Python | 3.8+ | Lenguaje principal |
| FastAPI | 0.110.0 | Framework web |
| Uvicorn | 0.27.1 | Servidor ASGI |
| Pydantic | 2.6.4 | Validación de datos |
| Requests | 2.32.3 | Cliente HTTP |
| python-dotenv | 1.0.1 | Gestión de env vars |

### **APIs Externas**
| Servicio | Uso |
|----------|-----|
| DeepSeek API | Procesamiento de lenguaje natural |

### **Control de Versiones**
| Herramienta | Uso |
|-------------|-----|
| Git | Control de versiones |
| GitHub | Repositorio remoto |

---

## 📝 Desarrollo y Extensión

### **Agregar Nueva Arquitectura**

En [python_backend/server/recommendation_engine/architecture_data.py](python_backend/server/recommendation_engine/architecture_data.py):

```python
# Agregar al final de la lista 'architectures'
architectures.append({
    'name': 'Arquitectura Personalizada',
    'complexity': 'Alta',
    'scalability': 'Moderada',
    'teamExperience': 'Alta',
    'dataVolume': 'Alto',
    'teamSize': 'Grande',
    'availability': 'Alta',
    'maintainability': 'Alta',
    'interoperability': 'Excelente'
})
```

**Valores permitidos:**
- `complexity`, `scalability`, `teamExperience`, `availability`, `maintainability`, `interoperability`: "Baja", "Moderada", "Alta", "Excelente"
- `dataVolume`: "Moderado", "Alto", "Excelente"  
- `teamSize`: "Pequeño", "Moderado", "Grande", "Alto"

### **Agregar Nuevo Parámetro**

Esto requiere cambios en 3 archivos:

**1. En [orchestrator.py](python_backend/server/dialogue_orchestrator/orchestrator.py):**
```python
ALL_PARAMETERS = [
    'complexity', 'scalability', 'teamExperience', 'dataVolume',
    'teamSize', 'availability', 'maintainability', 'interoperability',
    'nuevoParametro'  # ← Agregar aquí
]
```

**2. En [architecture_data.py](python_backend/server/recommendation_engine/architecture_data.py):**
```python
# Agregar a CADA arquitectura en el diccionario:
{
    'name': 'Arquitectura X',
    ...
    'nuevoParametro': 'Valor'  # ← Agregar aquí
}
```

**3. En [script.js](public/script.js):**
```javascript
const PARAMETER_LABELS = {
    complexity: 'Complejidad',
    ...
    nuevoParametro: 'Etiqueta Legible'  // ← Agregar aquí
};
```

### **Modificar Algoritmo de Puntuación**

En [engine.py](python_backend/server/recommendation_engine/engine.py):

```python
def get_recommendation(user_answers):
    """Modificar la lógica aquí"""
    # Actualmente:
    # - +2 puntos por coincidencia exacta (diferencia = 0)
    # - +1 punto por coincidencia cercana (diferencia = 1)
    # - 0 puntos por diferencia > 1
```

### **Cambiar Temperatures de LLM**

En [llm_service.py](python_backend/server/llm_service/llm_service.py):

```python
async def interpret_user_answer(...):
    return await call_api(messages, 0.0)  # ← Cambiar aquí (defecto: 0.0)

async def generate_next_question(...):
    return await call_api(messages, 0.6)  # ← Cambiar aquí (defecto: 0.6)

async def generate_final_descriptions(...):
    return await call_api(messages, 0.6)  # ← Cambiar aquí (defecto: 0.6)
```

**Rango:** 0.0 (determinístico) a 1.0 (creativo)

---

## 🚨 Solución de Problemas

### **Error: "La clave de API no está configurada"**
```
Síntoma: Error 401 en respuesta de /api/chat
Causas posibles:
  1. No existe archivo .env
  2. DEEPSEEK_API_KEY no está configurada
  3. La clave es un placeholder ("sk-replace_me", "tu_clave_api_aqui", etc)

Solución:
  1. Verifica que existe el archivo .env en la raíz del proyecto
  2. Abre .env y verifica DEEPSEEK_API_KEY=sk-[tu_clave_real]
  3. Obtén una clave real en https://www.deepseek.com/
  4. Reinicia el servidor: python main.py
```

### **Error: "No se puede conectar al servidor" / "Conexión rechazada"**
```
Síntoma: El navegador no carga http://localhost:5000
Causas posibles:
  1. El servidor no está corriendo
  2. Puerto 5000 está ocupado por otro programa
  3. Firewall bloquea la conexión

Solución:
  1. Verifica que estés en carpeta python_backend/
  2. Ejecuta: python main.py
  3. Espera el mensaje "Servidor iniciando en http://localhost:5000"
  4. Si el puerto está ocupado, cambia con: PORT=5001 python main.py
  5. Abre http://localhost:5001 en el navegador
```

### **Error: "404 - Archivo no encontrado" en frontend**
```
Síntoma: El servidor corre pero la página muestra 404
Causas posibles:
  1. La carpeta public/ está mal ubicada
  2. El servidor no monta los archivos estáticos correctamente

Solución:
  1. Verifica que exista: c:\...\archssistant\public\index.html
  2. Limpia la caché: Ctrl+Shift+Del en el navegador
  3. Abre en ventana privada/incógnito
  4. Revisa los logs del servidor
```

### **Error: "Error al procesar el mensaje" en chat**
```
Síntoma: Envías un mensaje y recibess error genérico
Causas posibles:
  1. La clave API de DeepSeek es inválida
  2. DeepSeek API está inactiva o límite de requests alcanzado
  3. El formato del historial es incorrecto

Solución:
  1. Verifica en consola del servidor (terminal donde corre python main.py)
  2. Revisa que la clave API sea válida en https://www.deepseek.com/
  3. Abre la consola del navegador (F12) y revisa los errores
  4. Intenta recargar la página (Ctrl+R) y empieza nueva conversación
```

### **Las respuestas de la IA son inconsistentes**
```
Síntoma: El sistema cambia su respuesta frecuentemente para la misma pregunta
Causa: La temperatura de LLM es muy alta

Información:
  - interpret_user_answer: temperature=0.0 (consistencia máxima) ✓
  - generate_next_question: temperature=0.6 (equilibrio)
  - generate_final_descriptions: temperature=0.6 (equilibrio)

Si quieres aumentar consistencia:
  - Disminuye temperature en llm_service.py
  - Valores: 0.0 (determinístico) a 1.0 (creativo)
```

### **El progreso en la barra lateral no avanza**
```
Síntoma: El círculo de progreso no muestra parámetros inferidos
Causas posibles:
  1. JavaScript tiene error en consola
  2. El estado no se está retornando correctamente del servidor

Solución:
  1. Abre F12 → Console y revisa errores
  2. Envía un mensaje y revisa qué retorna en Network → /api/chat
  3. Verifica que la respuesta contenga un campo "state"
```

---

## 📊 Logging y Debugging

### **Logs del Servidor**
El servidor FastAPI/Uvicorn registra automáticamente en consola:

```
INFO:     Uvicorn running on http://0.0.0.0:5000
INFO:     Started server process [12345]
INFO:     Application startup complete
INFO:     127.0.0.1:8000 - "POST /api/chat HTTP/1.1" 200
```

**Logs de Debug en orchestrator.py:**
```python
print(f"DEBUG: Generando descripciones para {len(recommendations)} arquitecturas")
print(f"DEBUG: Arquitecturas: {[r['name'] for r in recommendations]}")
print(f"DEBUG LLM: Descripciones generadas: {result}")
```

Para ver estos logs, observa la terminal donde ejecutas `python main.py`.

### **Debugging en Frontend**
Abre la consola del navegador (F12) para ver:
- Errores de JavaScript
- Solicitudes y respuestas HTTP en la pestaña "Network"
- Estado de variables en "Console"

**Debug útil:**
```javascript
// En console (F12):
conversationHistory   // Ver historial completo
state                 // Ver estado actual
fetch('/api/chat', {...})  // Probar manualmente API
```

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para contribuir:

1. **Fork el repositorio**
2. **Crea una rama de feature** (`git checkout -b feature/MiFeature`)
3. **Commit tus cambios** (`git commit -m 'Agregué MiFeature'`)
4. **Push a la rama** (`git push origin feature/MiFeature`)
5. **Abre un Pull Request**

### **Guía de Estilo**
- Python: Sigue PEP 8
- JavaScript: ESLint (sin punto y coma)
- Commits: Mensajes claros en español o inglés

---

## 📄 Licencia

Este proyecto está bajo la licencia **MIT**. Ver archivo [LICENSE](LICENSE) para más detalles.

**Copyright © 2024 - Diseñado por J. Tapia y Z. Xiao**

---

## 👥 Autores

### **Creadores Principales**
- **J. Tapia** - Arquitecto de Sistemas & Desarrollador Backend
- **Z. Xiao** - Diseñador UX/UI & Desarrollador Frontend

### **Contacto**
- 📧 Email: [contacto@archassistant.com](mailto:contacto@archassistant.com)
- 🌐 Sitio Web: (próximamente)
- 💬 Issues: [GitHub Issues](https://github.com/JessusTM/Archssistant/issues)

---

## 🎓 Recursos Adicionales

### **Arquitectura de Software**
- [Microsoft - Architectural Patterns](https://learn.microsoft.com/en-us/azure/architecture/guide/)
- [AWS - Architecture Center](https://aws.amazon.com/architecture/)
- [Google Cloud - Solution Architecture](https://cloud.google.com/solutions/architecture)

### **DeepSeek API**
- [Documentación oficial](https://www.deepseek.com/docs)
- [API Reference](https://www.deepseek.com/api-docs)

### **FastAPI**
- [Documentación oficial](https://fastapi.tiangolo.com/)
- [Guía completa](https://fastapi.tiangolo.com/learn/)

---

**¡Gracias por usar Arch-Assistant! 🚀**

Si te gusta el proyecto, considera dejar una ⭐ en GitHub.
