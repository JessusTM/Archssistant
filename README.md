# Arch-Assistant: Asistente de IA para Arquitectura de Software

Aplicación web que proporciona recomendaciones de arquitectura de software mediante conversación interactiva con IA.

**Status**: ✅ Arquitectura implementada con API Gateway y sistema de logging centralizado

---

## 📋 Tabla de Contenidos

- [Descripción General](#descripción-general)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Requisitos Previos](#requisitos-previos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [API REST](#api-rest)
- [Sistema de Logging](#sistema-de-logging)
- [Documentación Detallada](#documentación-detallada)

---

## Descripción General

**Arch-Assistant** es un asistente de IA que ayuda a equipos de desarrollo a encontrar la arquitectura de software más adecuada para sus proyectos mediante una conversación interactiva.

### Características Principales

✅ **Conversación Interactiva**: Diálogo natural que recopila información del proyecto
✅ **Inferencia Inteligente**: Interpreta respuestas usando DeepSeek LLM
✅ **Recomendaciones Personalizadas**: Top 3 arquitecturas basadas en parámetros inferidos
✅ **Justificaciones Detalladas**: Explica por qué cada arquitectura es recomendada
✅ **Historial Persistente**: Mantiene contexto completo de la conversación
✅ **API RESTful**: Interfaz HTTP moderna y escalable
✅ **Sistema de Logging Profesional**: Visibilidad completa del comportamiento

### Componentes Principales

- **Frontend**: Aplicación web interactiva (HTML/CSS/JavaScript)
- **Backend FastAPI**: Servidor HTTP escalable y moderno
- **API Gateway**: Validación centralizada y manejo de errores
- **Dialogue Orchestrator**: Orquestación inteligente del flujo conversacional
- **LLM Service**: Integración con DeepSeek para procesamiento semántico
- **Recommendation Engine**: Motor de scoring para arquitecturas

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Cliente)                       │
│              public/index.html | style.css | script.js       │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP REST
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                      main.py (FastAPI)                       │
│                   Punto de entrada                           │
└──────────────────────┬────────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│            API Routes (python_backend/api/routes.py)         │
│                 POST /api/chat                               │
└──────────────────────┬────────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│          API Gateway (python_backend/api/gateway.py)         │
│     ✓ Validación de entrada                                  │
│     ✓ Logging centralizado                                   │
│     ✓ Manejo de errores                                      │
│     ✓ Request ID para trazabilidad                           │
└──────────────────────┬────────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│   Dialogue Orchestrator (dialogue_orchestrator/orchestrator) │
│     - Mantiene estado conversacional                         │
│     - Interpreta respuestas del usuario                      │
│     - Decide cuándo pasar a recomendación                    │
└────┬──────────────────────┬────────────────────────────────┘
     │                      │
     ↓                      ↓
┌─────────────────────┐  ┌─────────────────────┐
│   LLM Service       │  │ Recommendation      │
│ (llm_service.py)    │  │ Engine (engine.py)  │
│                     │  │                     │
│ • interpret_answer  │  │ • scoring           │
│ • generate_question │  │ • ranking           │
│ • generate_desc     │  │ • top 3 results     │
└─────────────────────┘  └─────────────────────┘
```

---

## Estructura del Proyecto

```
Arch-Assistant/
├── main.py                              # Punto de entrada FastAPI
├── README.md                            # Este archivo
├── requirements.txt                     # Dependencias Python
├── .env                                 # Variables de entorno (NO versionar)
├── .env.example                         # Plantilla de .env
├── .gitignore                           # Archivos ignorados por git
│
├── public/                              # Frontend estático
│   ├── index.html                       # Interfaz HTML
│   ├── style.css                        # Estilos
│   └── script.js                        # Lógica del cliente
│
├── python_backend/                      # Backend Python
│   ├── config/                          # Configuración centralizada
│   │   ├── __init__.py
│   │   ├── logging_config.py           # Sistema de logging
│   │   ├── logging_utils.py            # Decoradores y utilidades
│   │   └── README.md                    # Documentación de logging
│   │
│   ├── api/                             # Capa API HTTP
│   │   ├── __init__.py
│   │   ├── models.py                   # Modelos Pydantic (ChatRequest, ChatResponse)
│   │   ├── routes.py                   # Endpoints (/api/chat)
│   │   ├── gateway.py                  # API Gateway (validación, logging)
│   │   └── __init__.py
│   │
│   └── server/                          # Lógica de negocio
│       ├── dialogue_orchestrator/       # Orquestador conversacional
│       │   ├── __init__.py
│       │   ├── orchestrator.py          # Flujo conversacional
│       │   └── __pycache__/
│       │
│       ├── llm_service/                 # Servicio LLM (DeepSeek)
│       │   ├── __init__.py
│       │   ├── llm_service.py           # Integración DeepSeek
│       │   ├── prompt/                  # Archivos de prompt
│       │   │   ├── interpret_user_answer_prompt.txt
│       │   │   ├── generate_next_question_prompt.txt
│       │   │   └── generate_final_descriptions_prompt.txt
│       │   └── __pycache__/
│       │
│       └── recommendation_engine/       # Motor de recomendación
│           ├── __init__.py
│           ├── engine.py                # Scoring y ranking
│           ├── architecture_data.py     # Catálogo de arquitecturas
│           └── __pycache__/
│
├── documentation/                       # Documentación técnica
│   ├── dialogue_orchestrator/README.md
│   ├── llm_service/README.md
│   └── recommendation_engine/README.md
│
├── logs/                                # Archivos de log (NO versionar)
│   ├── debug.log                        # Todos los logs (modo debug)
│   ├── info.log                         # INFO y superiores
│   └── error.log                        # Solo ERROR y CRITICAL
│
└── venv/                                # Entorno virtual (NO versionar)
```

---

## Requisitos Previos

### Sistema Operativo
- Windows, macOS o Linux

### Software Requerido
- **Python 3.8+**
- **Git**
- **pip** (incluido con Python)

### Acceso
- **Clave API de DeepSeek** (obtener en https://platform.deepseek.com/)

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

**Dependencias principales:**
- `fastapi==0.110.0` - Framework web moderno
- `uvicorn==0.27.1` - Servidor ASGI
- `requests==2.32.3` - Cliente HTTP
- `python-dotenv==1.0.1` - Gestión de variables de entorno
- `pydantic==2.6.4` - Validación de datos

### Paso 4: Configurar Variables de Entorno

Crea archivo `.env` en la raíz del proyecto:

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

Edita `.env` con tus credenciales:

```env
DEEPSEEK_API_KEY=sk_your_api_key_here
PORT=5000
HOST=0.0.0.0
```

---

## Configuración

### Variables de Entorno

El archivo `.env` debe contener:

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DEEPSEEK_API_KEY` | Clave API de DeepSeek | `sk_...` |
| `PORT` | Puerto del servidor | `5000` |
| `HOST` | Host del servidor | `0.0.0.0` |

### Seguridad (gitignore)

⚠️ **Importante**: Nunca versionar estos archivos:
- `.env` - Credenciales
- `venv/` - Entorno virtual
- `logs/` - Archivos de log
- `__pycache__/` - Caché de Python
- `*.key`, `*.pem`, `*.cert` - Claves privadas

El `.gitignore` excluye automáticamente estos archivos.

---

## Uso

### Iniciar el Servidor

```bash
# Asegúrate de que el venv está activado
python main.py
```

**Salida esperada:**
```
================================================================================
2025-12-28 10:30:45,123 - __main__ - INFO - Inicializando Arch-Assistant API...
2025-12-28 10:30:45,234 - __main__ - INFO - CORS habilitado para todos los orígenes
2025-12-28 10:30:45,345 - __main__ - INFO - Routers de API registrados
2025-12-28 10:30:45,456 - __main__ - INFO - Archivos estáticos montados desde: ...
2025-12-28 10:30:45,567 - __main__ - INFO - Arch-Assistant API lista para recibir solicitudes
================================================================================
```

### Acceder a la Aplicación

Abre el navegador en:
```
http://localhost:5000
```

---

## API REST
### Endpoint: POST /api/chat

**URL:** `POST /api/chat`

**Request:**
```json
{
  "history": [
    {
      "role": "user",
      "content": "Quiero construir una plataforma de streaming de videos"
    },
    {
      "role": "assistant",
      "content": "¿Cuál es la complejidad esperada de tu proyecto?"
    },
    {
      "role": "user",
      "content": "Moderada, queremos empezar simple pero crecer con el tiempo"
    }
  ]
}
```

**Response (en fase de entrevista):**
```json
{
  "response": {
    "role": "assistant",
    "content": "¿Cuántas personas componen tu equipo de desarrollo?"
  },
  "state": {
    "status": "interviewing",
    "inferredParams": {
      "complexity": "Moderada"
    },
    "lastQuestion": "complexity",
    "isClarifying": false
  }
}
```

**Response (cuando se generan recomendaciones):**
```json
{
  "response": {
    "role": "assistant",
    "content": "He analizado tu proyecto y aquí están las 3 arquitecturas más recomendadas..."
  },
  "state": {
    "status": "finished",
    "inferredParams": {
      "complexity": "Moderada",
      "scalability": "Alta",
      "teamSize": "Moderado",
      "availability": "Alta",
      "dataVolume": "Alto"
    }
  },
  "recommendation": [
    {
      "name": "Arquitectura de Microservicios",
      "description": "Divide tu aplicación en servicios independientes...",
      "justification": "Es ideal para escalabilidad y équipos distribuidos...",
      "score": 18
    },
    {
      "name": "Arquitectura en la Nube",
      "description": "Aprovecha servicios cloud para tu infraestructura...",
      "justification": "Oferece elasticidad y manejo automático de carga...",
      "score": 17
    },
    {
      "name": "Arquitectura de Capas",
      "description": "Organiza tu aplicación en capas (presentación, lógica, datos)...",
      "justification": "Simple de entender para equipos pequeños...",
      "score": 14
    }
  ]
}
```

---

## Sistema de Logging

Arch-Assistant incluye un sistema de logging profesional y centralizado para debugging, monitoreo y auditoría.

### Características

✅ **Configuración centralizada** en `python_backend/config/`
✅ **Múltiples handlers** (consola, archivo info, archivo error)
✅ **Rotación automática** de logs (10 MB por archivo)
✅ **Decoradores** para rastrear funciones automáticamente
✅ **Eventos de dominio** para operaciones específicas
✅ **Colores en consola** para fácil lectura

### Archivos de Log

Los logs se guardan en el directorio `logs/`:

```
logs/
├── debug.log       # Todos los logs (modo debug únicamente)
├── info.log        # INFO, WARNING (excluye DEBUG y ERROR)
└── error.log       # Solo ERROR y CRITICAL
```

### Usando el Logger

En cualquier módulo:

```python
from python_backend.config import get_logger

logger = get_logger(__name__)

logger.info("Evento importante")
logger.warning("Advertencia")
logger.error("Error no crítico")
logger.critical("Error crítico")
```

### Decoradores

```python
from python_backend.config import log_function_call, log_performance

@log_function_call
def process_data(x, y):
    """Se registra entrada y salida automáticamente"""
    return x + y

@log_performance
def expensive_operation():
    """Se mide el tiempo de ejecución"""
    pass
```

### Funciones de Dominio

```python
from python_backend.config import (
    log_orchestration_event,
    log_llm_call,
    log_recommendation_event
)

# En orchestrator
log_orchestration_event(
    event_type='answer_received',
    phase='interviewing',
    message='Usuario respondió sobre scalability',
    extra_data={'parameter': 'scalability', 'value': 'Alta'}
)

# En llm_service
log_llm_call(
    operation='interpret',
    input_summary='Usuario: "Startup pequeña"',
    output_summary='teamSize=Pequeño'
)

# En engine
log_recommendation_event(
    stage='scoring',
    message='Calculando puntajes',
    extra_data={'architectures_count': 5}
)
```

Para documentación completa del sistema de logging, consulta [python_backend/config/README.md](python_backend/config/README.md).

---

## Personalizar Arquitecturas

Las arquitecturas recomendadas se definen en [python_backend/server/recommendation_engine/architecture_data.py](python_backend/server/recommendation_engine/architecture_data.py).

### Agregar una Arquitectura

```python
{
    'name': 'Arquitectura Hexagonal',
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

### Valores Permitidos

| Parámetro | Valores Permitidos |
|-----------|-------------------|
| `complexity` | Baja, Moderada, Alta, Excelente |
| `scalability` | Baja, Moderada, Alta, Excelente |
| `teamExperience` | Baja, Moderada, Alta, Excelente |
| `dataVolume` | Moderado, Alto, Excelente |
| `teamSize` | Pequeño, Moderado, Grande, Alto |
| `availability` | Baja, Moderada, Alta, Excelente |
| `maintainability` | Baja, Moderada, Alta, Excelente |
| `interoperability` | Baja, Moderada, Alta, Excelente |

---

## Documentación Detallada

Para documentación técnica detallada de cada componente, consulta:

- [Dialogue Orchestrator](documentation/dialogue_orchestrator/README.md)
- [LLM Service](documentation/llm_service/README.md)
- [Recommendation Engine](documentation/recommendation_engine/README.md)
- [Sistema de Logging](python_backend/config/README.md)

---

## Troubleshooting

### Error: ModuleNotFoundError

**Problema:** `ModuleNotFoundError: No module named 'python_backend'`

**Solución:**
1. Asegúrate que estás en la carpeta raíz del proyecto
2. Verifica que el venv está activado
3. Ejecuta: `pip install -r requirements.txt`

### Error: DEEPSEEK_API_KEY no encontrada

**Problema:** `ApiKeyError: DEEPSEEK_API_KEY no configurada`

**Solución:**
1. Crea `.env` en la raíz del proyecto
2. Añade tu clave API: `DEEPSEEK_API_KEY=sk_...`
3. Reinicia el servidor

### Error: Puerto en uso

**Problema:** `Address already in use 0.0.0.0:5000`

**Solución:**
1. Cambia el puerto en `.env`: `PORT=5001`
2. O mata el proceso en ese puerto

---

## Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## Licencia

Este proyecto está bajo licencia MIT. Ver archivo `LICENSE` para más detalles.

---

## Contacto

**Autor:** JessusTM
**Email:** [tu-email@example.com]
**GitHub:** https://github.com/JessusTM/Archssistant

---

## Roadmap

- [ ] Autenticación de usuarios
- [ ] Persistencia de conversaciones en BD
- [ ] Más arquitecturas (DDD, CQRS, Event Sourcing)
- [ ] Exportar recomendaciones a PDF
- [ ] Integración con figma para diagramas
- [ ] Análisis de costos por arquitectura
- [ ] Soporte multiidioma

---

**Última actualización:** 28 de Diciembre, 2025
**Versión:** 1.0.0
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
