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
# DeepSeek API Configuration
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

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

O alternativamente:

```bash
uvicorn main:app --reload
```

**Output esperado:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
```

### **Acceder a la Aplicación**

Abre tu navegador y ve a:
```
http://127.0.0.1:8000
```

### **Primer Uso**

1. **Carga la interfaz**: Se mostrará el mensaje de bienvenida
2. **Describe tu proyecto**: Escribe una descripción detallada de lo que necesitas
3. **Responde preguntas**: El sistema hará preguntas sobre:
   - Complejidad del sistema
   - Requisitos de escalabilidad
   - Experiencia del equipo
   - Volumen de datos esperado
   - Tamaño del equipo
   - Disponibilidad requerida
   - Mantenibilidad
   - Interoperabilidad

4. **Recibe recomendación**: El sistema mostrará las 3 mejores arquitecturas con puntuaciones

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
interviewing → (recopilación de parámetros)
clarifying   → (preguntas de aclaración)
recommending → (generación de recomendación)
completed    → (finalizado)
```

### **3. Backend - LLM Service**

#### `llm_service.py`
**Funciones principales:**
- `call_api()` - Realiza peticiones a API DeepSeek
- `interpret_user_answer()` - Clasifica respuestas en categorías
- `generate_next_question()` - Genera preguntas dinámicas
- `generate_final_descriptions()` - Describe arquitecturas recomendadas

**Características:**
- Manejo robusto de errores de API
- Validación de claves API
- Respuestas en formato JSON estruturado
- Temperature bajo (0.2) para respuestas consistentes

### **4. Backend - Recommendation Engine**

#### `architecture_data.py`
Base de datos con 8 arquitecturas predefinidas:
1. **Monolítica** - Simple, baja complejidad
2. **Microservicios** - Altamente escalable, compleja
3. **SOA** - Servicios empresariales
4. **Capas** - Tradicional, moderada complejidad
5. **Cliente-Servidor** - Clásica, escalable
6. **Nube** - Escalabilidad extrema
7. **Basada en Eventos (EDA)** - Altamente reactiva

Cada arquitectura tiene 8 parámetros evaluados:
- `complexity` - Complejidad del sistema
- `scalability` - Capacidad de escalar
- `teamExperience` - Experiencia requerida del equipo
- `dataVolume` - Volumen de datos manejado
- `teamSize` - Tamaño de equipo recomendado
- `availability` - Disponibilidad
- `maintainability` - Mantenibilidad
- `interoperability` - Interoperabilidad

#### `engine.py`
- Algoritmo de puntuación: compara parámetros del usuario con cada arquitectura
- Sistema de scoring:
  - +2 puntos por coincidencia exacta
  - +1 punto por coincidencia cercana (diferencia de 1)
- Retorna las 3 arquitecturas mejor puntuadas

### **5. Backend - Main Server**

#### `main.py`
**Endpoints:**
- `POST /api/chat` - Recibe mensaje del usuario y retorna respuesta del asistente

**Respuesta:**
```json
{
  "response": {
    "role": "assistant",
    "content": "Texto de respuesta",
    "recommendation": null  // O estructura con recomendaciones
  },
  "state": {
    "inferredParams": {...},
    "lastQuestion": {...},
    "isClarifying": false,
    "status": "interviewing"
  }
}
```

---

## 🔌 API REST

### **Endpoint: POST /api/chat**

**Descripción:** Procesa un mensaje del usuario y retorna la respuesta del asistente con estado actualizado.

**URL:**
```
POST http://localhost:8000/api/chat
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
┌─────────────────────────────────────────────────────────────┐
│ FASE 1: INICIALIZACIÓN                                      │
├─────────────────────────────────────────────────────────────┤
│ 1. Usuario describe el proyecto                             │
│ 2. Sistema guarda como "user_description"                   │
│ 3. Inicia recopilación de parámetros                        │
└───────────────────┬─────────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────────┐
│ FASE 2: ENTREVISTA (status: "interviewing")                │
├─────────────────────────────────────────────────────────────┤
│ Ciclo para cada parámetro no inferido:                      │
│ 1. Genera pregunta específica para el parámetro             │
│ 2. Guarda pregunta en estado                                │
│ 3. Interpreta respuesta del usuario                         │
│ 4. Clasifica como CERTAIN, UNCERTAIN, o UNKNOWN            │
│ 5. Infiere valor del parámetro                              │
│ Parámetros: complexity, scalability, teamExperience...      │
└───────────────────┬─────────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────────┐
│ FASE 3: CLARIFICACIÓN (si status: "clarifying")            │
├─────────────────────────────────────────────────────────────┤
│ Si respuesta anterior fue UNCERTAIN:                        │
│ 1. Genera pregunta de clarificación                         │
│ 2. Intenta obtener clasificación más clara                  │
│ 3. Vuelve a interpretar                                     │
└───────────────────┬─────────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────────┐
│ FASE 4: RECOMENDACIÓN (cuando params completos)            │
├─────────────────────────────────────────────────────────────┤
│ 1. Envía parámetros al motor de recomendación              │
│ 2. Calcula puntuaciones para cada arquitectura              │
│ 3. Genera descripciones detalladas                          │
│ 4. Retorna top 3 arquitecturas                              │
│ 5. status → "completed"                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Arquitecturas Soportadas

### **1. Monolítica**
- **Mejor para:** Proyectos pequeños, startups
- **Ventajas:** Simple, fácil de desplegar
- **Desventajas:** Difícil de escalar
- **Parámetros:**
  - Complejidad: Baja
  - Escalabilidad: Baja
  - Experiencia: Baja

### **2. Microservicios**
- **Mejor para:** Sistemas grandes, equipos grandes
- **Ventajas:** Altamente escalable, flexible
- **Desventajas:** Compleja de gestionar
- **Parámetros:**
  - Complejidad: Alta
  - Escalabilidad: Alta
  - Experiencia: Alta
  - Disponibilidad: Excelente

### **3. SOA (Orientada a Servicios)**
- **Mejor para:** Empresas grandes, integraciones complejas
- **Ventajas:** Interoperabilidad excelente
- **Desventajas:** Implementación compleja
- **Parámetros:**
  - Complejidad: Alta
  - Interoperabilidad: Excelente

### **4. Capas**
- **Mejor para:** Aplicaciones tradicionales
- **Ventajas:** Bien comprendida, mantenible
- **Desventajas:** Escalabilidad limitada
- **Parámetros:**
  - Complejidad: Alta
  - Mantenibilidad: Alta

### **5. Cliente-Servidor**
- **Mejor para:** Aplicaciones web tradicionales
- **Ventajas:** Escalable horizontalmente
- **Desventajas:** Acoplamiento cliente-servidor
- **Parámetros:**
  - Escalabilidad: Alta

### **6. Nube**
- **Mejor para:** Cualquier proyecto moderno
- **Ventajas:** Escalabilidad extrema, flexible
- **Desventajas:** Dependencia de proveedor
- **Parámetros:**
  - Escalabilidad: Excelente
  - Disponibilidad: Excelente

### **7. Basada en Eventos (EDA)**
- **Mejor para:** Sistemas altamente reactivos
- **Ventajas:** Escalable, desacoplada
- **Desventajas:** Complejidad operacional
- **Parámetros:**
  - Escalabilidad: Alta
  - Volumen de datos: Excelente

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

En `python_backend/server/recommendation_engine/architecture_data.py`:

```python
architectures.append({
    'name': 'Mi Arquitectura',
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

### **Agregar Nuevo Parámetro**

1. En `orchestrator.py`, agrega a `ALL_PARAMETERS`:
```python
ALL_PARAMETERS = [
    'complexity', 'scalability', ..., 'nuevoParametro'
]
```

2. En `architecture_data.py`, agrega a cada arquitectura:
```python
'nuevoParametro': 'Valor'
```

3. En `script.js`, agrega label en `PARAMETER_LABELS`:
```javascript
const PARAMETER_LABELS = {
    ...
    nuevoParametro: 'Mi Parámetro'
};
```

### **Modificar Algoritmo de Puntuación**

En `python_backend/server/recommendation_engine/engine.py`:

```python
def get_recommendation(user_answers):
    # Personaliza la lógica de puntuación aquí
    # Actualmente: +2 exacta, +1 cercana
```

---

## 🚨 Solución de Problemas

### **Error: "La clave de API no está configurada"**
```
Solución:
1. Verifica que existe el archivo .env
2. La variable se llama DEEPSEEK_API_KEY
3. Copia tu clave real de https://www.deepseek.com/
4. Reinicia el servidor
```

### **Error: "No se puede conectar al servidor"**
```
Solución:
1. Verifica que estés en la carpeta python_backend/
2. Ejecuta: python main.py
3. Abre: http://127.0.0.1:8000 en el navegador
4. Revisa los logs en la terminal
```

### **El frontend no se carga**
```
Solución:
1. Verifica que el servidor FastAPI está corriendo
2. La carpeta public/ está al mismo nivel que python_backend/
3. Limpia la caché del navegador (Ctrl+Shift+Del)
4. Revisa la consola de desarrollador (F12)
```

### **La IA devuelve respuestas inconsistentes**
```
Solución:
1. Verifica la temperatura en llm_service.py (está en 0.2)
2. Asegúrate de que el modelo es 'deepseek-chat'
3. Revisa que el formato de respuesta sea JSON válido
4. Aumenta la temperatura para más creatividad, disminuye para más consistencia
```

---

## 📊 Métricas y Monitoreo

### **Logging**
El servidor FastAPI registra automáticamente:
- Peticiones HTTP
- Errores y excepciones
- Cambios de estado

Para ver los logs, revisa la salida de la terminal donde corre `python main.py`.

### **Debugging**
Habilita modo debug en `script.js`:
```javascript
// Descomenta para ver logs detallados
console.log('Historial:', conversationHistory);
console.log('Estado:', state);
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
