# Archssistant: Asistente de IA para Arquitectura de Software

Aplicación web que proporciona recomendaciones de arquitectura de software mediante conversación interactiva con IA.

**Status**: ✅ Sistema completo con arquitectura modular y logging profesional

---

## 📋 Tabla de Contenidos

- [Descripción General](#descripción-general)
- [Características](#características)
- [Arquitectura del Sistema](#arquitectura-del-sistema)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Requisitos Previos](#requisitos-previos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Ejecución](#ejecución)
- [API REST](#api-rest)
- [Sistema de Logging](#sistema-de-logging)
- [Documentación Detallada](#documentación-detallada)
- [Troubleshooting](#troubleshooting)

---

## Descripción General

**Archssistant** es un asistente de IA que ayuda a equipos de desarrollo a encontrar la arquitectura de software más adecuada para sus proyectos mediante una conversación interactiva.

### Características

✅ **Conversación Interactiva**: Diálogo natural que recopila información del proyecto  
✅ **Inferencia Inteligente**: Interpreta respuestas usando DeepSeek LLM  
✅ **Recomendaciones Personalizadas**: Top 3 arquitecturas basadas en parámetros inferidos  
✅ **Justificaciones Detalladas**: Explica por qué cada arquitectura es recomendada  
✅ **Historial Persistente**: Mantiene contexto completo de la conversación  
✅ **API RESTful**: Interfaz HTTP moderna y escalable  
✅ **Sistema de Logging Profesional**: Visibilidad completa con niveles configurables  
✅ **Arquitectura Modular**: Separación clara de responsabilidades con clases e interfaces  

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Cliente)                       │
│    archssistant-frontend/index.html | style.css | script.js  │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP REST
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                  app/main.py (FastAPI)                       │
│              Punto de entrada del servidor                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│          API Routes (app/api/routes.py)                      │
│                 POST /api/chat                               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│               Orchestrator                                  │
│        (app/services/orchestrator/Orchestrator)              │
└───────────────┬───────────────────────┬─────────────────────┘
                │                       │
                ↓                       ↓
┌──────────────────────────┐   ┌──────────────────────────────┐
│   Elicitation Machine    │   │        Decision Maker         │
│ (infer variables w/ LLM) │   │ (evaluate rules / scoring)    │
└──────────────┬───────────┘   └──────────────┬───────────────┘
               │                              │
               ↓                              ↓
┌──────────────────────────┐   ┌──────────────────────────────┐
│ Recommendation Explainer │   │  Symbolic Knowledge Base      │
│ (LLM descriptions)       │   │ (catalog + mappings)          │
└──────────────────────────┘   └──────────────────────────────┘
```

---

## Estructura del Proyecto

```
Archssistant/
├── archssistant-backend/          # Backend Python
│   ├── pyproject.toml             # Dependencias Python
│   ├── .env                       # Variables de entorno (NO versionar)
│   ├── .gitignore                 # Archivos ignorados por git
│   │
│   └── app/                       # Paquete principal
│       ├── main.py                # Punto de entrada FastAPI
│       ├── api/                   # Capa API HTTP
│       │   ├── __init__.py
│       │   ├── models.py          # Modelos Pydantic (ChatRequest, ChatResponse)
│       │   ├── routes.py          # Endpoints (/api/chat)
│       │   └── exceptions.py      # Excepciones personalizadas
│       │
│       ├── core/                  # Configuración centralizada
│       │   ├── __init__.py
│       │   ├── config.py          # Config (BaseSettings) con APP_NAME, LOG_LEVEL, PORT, HOST
│       │   ├── logging_config.py  # Sistema de logging
│       │   └── logging_utils.py   # Funciones de dominio
│       │
│       └── services/              # Lógica de negocio
│           ├── orchestrator/                # Orchestrator (flujo conversacional)
│           ├── elicitation_machine/         # Inferencia + preguntas (LLM)
│           │   └── prompt/                  # Prompts del LLM
│           ├── recommendation_explainer/    # Descripciones/justificaciones (LLM)
│           ├── decision_maker/              # Scoring/ranking determinístico
│           └── symbolic_knowledge_base/     # Catálogo + mapeos simbólicos
│
├── archssistant-frontend/         # Frontend estático
│   ├── index.html                 # Interfaz HTML
│   ├── style.css                  # Estilos
│   └── script.js                  # Lógica del cliente
│
├── docs/                          # Documentación técnica
│   ├── ARCHITECTURE.md            # Arquitectura general del sistema
│   ├── LOGGING.md                 # Documentación del sistema de logging
│   ├── api_gateway/
│   │   └── README.md
│   ├── dialogue_orchestrator/
│   │   └── README.md
│   ├── llm_service/
│   │   └── README.md
│   └── recommendation_engine/
│       └── README.md
│
├── logs/                          # Archivos de log (NO versionar)
│   ├── debug.log                  # Todos los logs (solo si LOG_LEVEL=DEBUG)
│   ├── info.log                   # INFO y WARNING
│   └── error.log                  # ERROR y CRITICAL
│
└── README.md                      # Este archivo
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

### Paso 2: Navegar al Backend

```bash
cd archssistant-backend
```

### Paso 3: Crear Entorno Virtual

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

### Paso 4: Instalar Dependencias

```bash
pip install .
```

**Dependencias principales (pyproject.toml):**
- `fastapi==0.110.0` - Framework web moderno
- `uvicorn==0.27.1` - Servidor ASGI
- `requests==2.32.3` - Cliente HTTP
- `python-dotenv==1.0.1` - Gestión de variables de entorno
- `pydantic==2.6.4` - Validación de datos
- `pydantic-settings==2.1.0` - Configuración con BaseSettings
- `colorlog==6.8.0` - Colores automáticos en logs

---

## Configuración

### Paso 1: Crear Archivo .env

Crea un archivo `.env` en el directorio `archssistant-backend/`:

**Windows:**
```bash
cd archssistant-backend
copy .env.example .env
```

**macOS/Linux:**
```bash
cd archssistant-backend
cp .env.example .env
```

### Paso 2: Configurar Variables de Entorno

Edita el archivo `.env` con tus credenciales:

```env
# Clave API de DeepSeek (REQUERIDA)
DEEPSEEK_API_KEY=sk_your_api_key_here

# Configuración del servidor
HOST=0.0.0.0
PORT=5000

# Nivel de logging
# Valores válidos: DEBUG, INFO, WARNING, ERROR, CRITICAL
# DEBUG: Todos los logs (desarrollo)
# INFO: Logs informativos y superiores (producción por defecto)
LOG_LEVEL=INFO
```

### Variables de Entorno

| Variable | Descripción | Requerida | Valor por Defecto |
|----------|-------------|-----------|-------------------|
| `DEEPSEEK_API_KEY` | Clave API de DeepSeek | ✅ Sí | - |
| `HOST` | Host del servidor | ❌ No | `0.0.0.0` |
| `PORT` | Puerto del servidor | ❌ No | `5000` |
| `LOG_LEVEL` | Nivel de logging | ❌ No | `INFO` |

### Seguridad

⚠️ **Importante**: Nunca versionar estos archivos:
- `.env` - Contiene credenciales
- `venv/` - Entorno virtual
- `logs/` - Archivos de log
- `__pycache__/` - Caché de Python

El `.gitignore` excluye automáticamente estos archivos.

---

## Ejecución

### Paso 1: Activar el Entorno Virtual

Asegúrate de que el entorno virtual esté activado:

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### Paso 2: Verificar Configuración

Asegúrate de estar en el directorio `archssistant-backend/`:

```bash
cd archssistant-backend
```

### Paso 3: Iniciar el Servidor

```bash
python -m app.main
# o con autoreload explícito:
uvicorn app.main:app --reload --host 0.0.0.0 --port 5000
```

**Salida esperada:**
```
================================================================================
2025-01-XX 10:30:45,123 - app.core.config - INFO - Configuration initialized for Archssistant
2025-01-XX 10:30:45,234 - app.core.config - INFO - Log level : INFO
2025-01-XX 10:30:45,345 - app.core.config - INFO - Host      : 0.0.0.0
2025-01-XX 10:30:45,456 - app.core.config - INFO - Port      : 5000
================================================================================
2025-01-XX 10:30:45,567 - __main__ - INFO - Initializing API: Archssistant
2025-01-XX 10:30:45,678 - __main__ - INFO - CORS middleware enabled for all origins
2025-01-XX 10:30:45,789 - __main__ - INFO - API routers registered
2025-01-XX 10:30:45,890 - __main__ - INFO - Static files mounted from: .../archssistant-frontend
2025-01-XX 10:30:45,901 - __main__ - INFO - API Archssistant ready to receive requests
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
```

### Paso 4: Acceder a la Aplicación

Abre el navegador en:
```
http://localhost:5000
```

### Detener el Servidor

Presiona `CTRL+C` en la terminal donde se está ejecutando el servidor.

---

## API REST

### Endpoint: POST /api/chat

**URL:** `http://localhost:5000/api/chat`

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
      "content": "¿Cuál es la complejidad esperada de tu proyecto?",
      "state": {
        "inferredParams": {},
        "lastQuestion": {
          "parameter_to_infer": "complexity",
          "question_text": "¿Cuál es la complejidad esperada de tu proyecto?"
        },
        "isClarifying": false,
        "status": "interviewing"
      }
    },
    {
      "role": "user",
      "content": "Moderada, queremos empezar simple pero crecer con el tiempo"
    }
  ]
}
```

**Response (200) - En fase de entrevista:**
```json
{
  "response": {
    "role": "assistant",
    "content": "Entendido, una complejidad moderada. ¿Cuántas personas componen tu equipo de desarrollo?"
  },
  "state": {
    "status": "interviewing",
    "inferredParams": {
      "complexity": "Moderada"
    },
    "lastQuestion": {
      "parameter_to_infer": "teamSize",
      "question_text": "¿Cuántas personas componen tu equipo de desarrollo?"
    },
    "isClarifying": false
  }
}
```

**Response (200) - Con recomendaciones:**
```json
{
  "response": {
    "role": "assistant",
    "content": "¡Gracias! He analizado tus respuestas.",
    "recommendation": [
      {
        "name": "Arquitectura de Microservicios",
        "description": "Divide tu aplicación en servicios independientes...",
        "justification": "Es ideal para escalabilidad y equipos distribuidos...",
        "complexity": "Alta",
        "scalability": "Alta",
        "score": 18
      },
      {
        "name": "Arquitectura en la Nube",
        "description": "Aprovecha servicios cloud para tu infraestructura...",
        "justification": "Ofrece elasticidad y manejo automático de carga...",
        "score": 17
      },
      {
        "name": "Arquitectura de Capas",
        "description": "Organiza tu aplicación en capas...",
        "justification": "Simple de entender para equipos pequeños...",
        "score": 14
      }
    ]
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
  }
}
```

**Errores:**
- `400`: Request inválida (historial vacío, estructura incorrecta)
- `401`: Error de autenticación con DeepSeek API
- `500`: Error interno del servidor

---

## Sistema de Logging

Archssistant incluye un sistema de logging profesional y centralizado.

### Características

✅ **Configuración centralizada** en `app/core/`  
✅ **Colores automáticos** con `colorlog` (solo en terminal)  
✅ **Niveles configurables** vía `.env` (DEBUG, INFO, WARNING, ERROR, CRITICAL)  
✅ **Múltiples handlers** (consola, info.log, error.log)  
✅ **Rotación automática** de logs (10 MB por archivo, 5 backups)  
✅ **Logging estructurado** con mensajes en inglés  

### Configuración

El nivel de logging se configura en `.env`:

```env
# Desarrollo: ver todos los logs
LOG_LEVEL=DEBUG

# Producción: solo logs importantes
LOG_LEVEL=INFO
```

### Archivos de Log

Los logs se guardan en `archssistant-backend/logs/`:

```
logs/
├── debug.log       # Todos los logs (solo si LOG_LEVEL=DEBUG)
├── info.log        # INFO y WARNING (siempre)
└── error.log       # ERROR y CRITICAL (siempre)
```

### Ver Logs en Tiempo Real

**Windows PowerShell:**
```powershell
Get-Content archssistant-backend\logs\info.log -Tail 20 -Wait
```

**Linux/Mac:**
```bash
tail -f archssistant-backend/logs/info.log
```

Para más información, consulta [docs/LOGGING.md](docs/LOGGING.md).

---

## Documentación Detallada

Para documentación técnica detallada de cada componente, consulta:

- **[Arquitectura General](docs/ARCHITECTURE.md)** - Visión general del sistema
- **[Sistema de Logging](docs/LOGGING.md)** - Documentación completa del logging
- **[Dialogue Orchestrator](docs/dialogue_orchestrator/README.md)** - Orquestación conversacional
- **[LLM Service](docs/llm_service/README.md)** - Integración con DeepSeek
- **[Recommendation Engine](docs/recommendation_engine/README.md)** - Motor de recomendaciones

---

## Troubleshooting

### Error: ModuleNotFoundError

**Problema:** `ModuleNotFoundError: No module named 'app'`

**Solución:**
1. Asegúrate de estar en el directorio `archssistant-backend/`
2. Verifica que el venv está activado
3. Ejecuta: `pip install .`

### Error: DEEPSEEK_API_KEY no encontrada

**Problema:** `ApiKeyError: La clave de API no está configurada (DEEPSEEK_API_KEY).`

**Solución:**
1. Crea `.env` en `archssistant-backend/`
2. Añade tu clave API: `DEEPSEEK_API_KEY=sk_...`
3. Reinicia el servidor

### Error: Puerto en uso

**Problema:** `Address already in use 0.0.0.0:5000`

**Solución:**
1. Cambia el puerto en `.env`: `PORT=5001`
2. O mata el proceso en ese puerto:
   - **Windows:** `netstat -ano | findstr :5000` luego `taskkill /PID <PID> /F`
   - **Linux/Mac:** `lsof -ti:5000 | xargs kill`

### Error: LOG_LEVEL inválido

**Problema:** Logging no funciona correctamente

**Solución:**
- Verifica que `LOG_LEVEL` en `.env` sea uno de: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- Si no está configurado, usa `INFO` por defecto

### Error: No se pueden cargar los prompts

**Problema:** `FileNotFoundError: prompt/interpret_user_answer_prompt.txt`

**Solución:**
- Verifica que los archivos de prompt existan en `app/services/llm_service/prompt/`
- Si faltan, clona nuevamente el repositorio

---

## Tecnologías Utilizadas

### Frontend
- HTML5
- CSS3
- JavaScript (Vanilla ES6+)
- Canvas API (para animaciones)

### Backend
- **Python 3.8+**
- **FastAPI 0.110.0** - Framework web moderno
- **Uvicorn 0.27.1** - Servidor ASGI
- **Pydantic 2.6.4** - Validación de datos
- **Pydantic Settings 2.1.0** - Configuración con BaseSettings
- **Requests 2.32.3** - Cliente HTTP
- **python-dotenv 1.0.1** - Gestión de variables de entorno
- **colorlog 6.8.0** - Colores automáticos en logs

### APIs Externas
- **DeepSeek API** - https://api.deepseek.com/v1/chat/completions

---

## Parámetros Inferidos

El sistema intenta inferir estos 8 parámetros durante la conversación:

1. `complexity` - Baja, Moderada, Alta, Excelente
2. `scalability` - Baja, Moderada, Alta, Excelente
3. `teamExperience` - Baja, Moderada, Alta, Excelente
4. `dataVolume` - Moderado, Alto, Excelente
5. `teamSize` - Pequeño, Moderado, Grande, Alto
6. `availability` - Baja, Moderada, Alta, Excelente
7. `maintainability` - Baja, Moderada, Alta, Excelente
8. `interoperability` - Baja, Moderada, Alta, Excelente

Cuando se recopilan ≥5 parámetros, el sistema genera recomendaciones.

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
**GitHub:** https://github.com/JessusTM/Archssistant

---

**Versión:** 2.0.0  
**Última actualización:** Enero 2025
