# Arquitectura de Arch-Assistant

Documento que describe la arquitectura general del sistema, componentes y patrones utilizados.

---

## Descripción General

**Arch-Assistant** es una aplicación web de recomendación de arquitecturas de software que utiliza inteligencia artificial para asesorar a equipos de desarrollo.

**Stack Tecnológico:**
- **Frontend:** HTML5, CSS3, JavaScript vanilla
- **Backend:** Python, FastAPI, DeepSeek API
- **Arquitectura:** Monolítica modular con separación clara de responsabilidades

---

## Arquitectura General

```
┌──────────────────────────────────────────────────────────────┐
│                    Navegador Web (Cliente)                   │
└──────────────────────┬───────────────────────────────────────┘
                       │ HTTP/JSON
                       ↓
┌──────────────────────────────────────────────────────────────┐
│                      FastAPI Server                          │
│                   (app/main.py, Port 5000)                   │
├──────────────────────────────────────────────────────────────┤
│ Middleware:                                                   │
│ - CORS (Allow All Origins)                                   │
│ - Static Files Mounting                                      │
└──────────────────────┬───────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Static Files │ │ API Routes   │ │ API Gateway  │
│ (archssistant-frontend/) │ (/api/chat)  │ (Validación) │
└──────────────┘ └──────┬───────┘ └──────┬───────┘
                        │                │
                        └────────┬───────┘
                                 ↓
                     ┌──────────────────────┐
                     │ Dialogue Orchestrator│
                     │  (Control de flujo)  │
                     └──────────┬───────────┘
                                │
                ┌───────────────┼───────────────┐
                ↓               ↓               ↓
          ┌─────────┐    ┌─────────┐    ┌─────────┐
          │ LLM     │    │Recommend │    │ Config  │
          │Service  │    │ Engine   │    │ (Logs)  │
          └────┬────┘    └────┬─────┘    └─────────┘
               │              │
               │ (DeepSeek)   │ (Scoring)
               ↓              ↓
          ┌─────────────────────────┐
          │ Datos de Arquitecturas  │
          └─────────────────────────┘
```

---

## Componentes Principales

### 1. Frontend (`archssistant-frontend/`)

**Responsabilidad:** Interfaz de usuario para interacción conversacional

**Componentes:**
- `index.html` - Estructura HTML
- `style.css` - Estilos (glassmorphism, animaciones)
- `script.js` - Lógica de cliente

**Características:**
- Chat interactivo en tiempo real
- Progreso visual de parámetros inferidos
- Animaciones con canvas (partículas)
- Responsive design
- Seguridad: escapado de HTML

**Flujo de Cliente:**
```
Usuario escribe mensaje
    ↓
JavaScript captura submit
    ↓
POST /api/chat con historial completo
    ↓
Actualiza DOM con respuesta
    ↓
Calcula progreso (parámetros/5)
    ↓
Si es recomendación: muestra TOP 3
```

### 2. Servidor FastAPI (`app/main.py`)

**Responsabilidad:** Punto de entrada y configuración de aplicación

**Funciones:**
- Inicializar aplicación FastAPI
- Configurar CORS
- Registrar routers de API
- Montar archivos estáticos
- Inicializar sistema de logging

**Configuración:**
```python
app = FastAPI(
    title='Arch-Assistant',
    version='1.0.0'
)

# CORS: Todos los orígenes permitidos
app.add_middleware(CORSMiddleware, allow_origins=['*'])

# Logging centralizado
setup_logging(debug_mode=False)

# Montar frontend desde archssistant-frontend/
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
frontend_dir = project_root / 'archssistant-frontend'
app.mount('/', StaticFiles(directory=frontend_dir, html=True))
```

### 3. API Routes (`python_backend/api/routes.py`)

**Responsabilidad:** Definir endpoints HTTP

**Endpoints:**
- `POST /api/chat` - Procesa mensajes de chat

**Estructura:**
```python
@router.post('/api/chat')
async def chat(request: ChatRequest) -> ChatResponse:
    # Delegado al Gateway
    # El Gateway maneja:
    # - Validación
    # - Logging
    # - Manejo de errores
```

**Modelos Pydantic:**
- `ChatRequest` - Contiene historial de mensajes
- `ChatResponse` - Contiene respuesta del asistente y estado

### 4. API Gateway (`python_backend/api/gateway.py`)

**Responsabilidad:** Validación centralizada y manejo de errores transversales

**Funciones Principales:**
- `process_chat_message()` - Procesa solicitud con pipeline completo
- `_validate_chat_request()` - Valida estructura de entrada

**Pipeline:**
```
1. Validación de entrada
    ↓
2. Crear Request ID (trazabilidad)
    ↓
3. Loguear solicitud
    ↓
4. Delegar al Orchestrator
    ↓
5. Loguear respuesta
    ↓
6. Retornar ChatResponse
```

**Excepciones:**
- `ValidationError` (400) - Entrada inválida
- `AuthenticationError` (401) - Credenciales inválidas
- `InternalServerError` (500) - Error no controlado

### 5. Dialogue Orchestrator (`orchestrator.py`)

**Responsabilidad:** Control del flujo conversacional

**Funciones Principales:**
- `handle_message()` - Punto de entrada principal
- `get_conversation_state()` - Extrae estado del historial

**Estados:**
- `interviewing` - Recopilando parámetros (fase 1)
- `recommending` - Generando recomendaciones (fase 2)
- `finished` - Conversación completada

**Parámetros Inferidos:**
```
complexity, scalability, teamExperience, dataVolume,
teamSize, availability, maintainability, interoperability
```

**Lógica:**
```
Si parámetros < 5:
    ├─ Generar siguiente pregunta
    └─ Interpretar respuesta del usuario
Si parámetros >= 5 y estado = "interviewing":
    ├─ Cambiar a "recommending"
    └─ Obtener TOP 3 recomendaciones
Si estado = "recommending":
    ├─ Generar descripciones del LLM
    └─ Retornar con recomendaciones
```

### 6. LLM Service (`llm_service.py`)

**Responsabilidad:** Integración con DeepSeek API

**Funciones:**
- `interpret_user_answer()` - Clasifica respuesta en categoría
- `generate_next_question()` - Genera pregunta estratégica
- `generate_final_descriptions()` - Describe arquitecturas
- `call_api()` - Llamada HTTP a DeepSeek

**Configuración:**
- URL: `https://api.deepseek.com/v1/chat/completions`
- Modelo: `deepseek-chat`
- Requiere: `DEEPSEEK_API_KEY` en `.env`

**Prompts:**
- `prompt/interpret_user_answer_prompt.txt`
- `prompt/generate_next_question_prompt.txt`
- `prompt/generate_final_descriptions_prompt.txt`

### 7. Recommendation Engine (`engine.py`)

**Responsabilidad:** Scoring y ranking de arquitecturas

**Función Principal:**
- `get_recommendation()` - Calcula TOP 3 arquitecturas

**Algoritmo:**
```
Para cada arquitectura:
    score = 0
    Para cada parámetro del usuario:
        diferencia = |score_usuario - score_arquitectura|
        Si diferencia == 0: score += 2
        Si diferencia == 1: score += 1
        Si diferencia > 1:  score += 0

Ordenar por score descendente
Retornar TOP 3
```

**Base de Datos (En Memoria):**
- Ubicación: `architecture_data.py`
- 7 arquitecturas predefinidas
- Catálogo estático (no es una BD real)

### 8. Config/Logging (`python_backend/config/`)

**Responsabilidad:** Configuración centralizada

**Módulos:**
- `logging_config.py` - Configuración de logging
- `logging_utils.py` - Decoradores y funciones auxiliares
- `__init__.py` - Exports

**Características:**
- Configuración en un lugar
- Múltiples handlers (consola, archivo)
- Rotación automática
- Decoradores para instrumentación

**Archivos de Log:**
- `logs/debug.log` - Todos los logs (modo debug)
- `logs/info.log` - INFO y superiores
- `logs/error.log` - ERROR y CRITICAL

---

## Flujo de Conversación Completo

```
1. Usuario abre http://localhost:5000
   ├─ Carga archssistant-frontend/index.html
   ├─ Carga archssistant-frontend/script.js
   └─ Carga archssistant-frontend/style.css

2. Usuario envía primer mensaje: "Quiero una API REST"
   ├─ JavaScript crea historial con role: "user_description"
   ├─ Envía POST /api/chat
   └─ Cuerpo: { "history": [...] }

3. Servidor recibe solicitud
   ├─ Routes (/api/chat) recibe ChatRequest
   ├─ Gateway valida entrada
   ├─ Gateway crea Request ID para trazabilidad
   ├─ Gateway delega a Orchestrator

4. Orchestrator procesa
   ├─ Extrae estado del historial
   ├─ Status = "interviewing" (primer mensaje)
   ├─ Parámetros inferidos: {}
   ├─ Delega a LLM Service para generar pregunta
   └─ LLM Service llama a DeepSeek
       ├─ Prompt: "Genera una pregunta sobre..." 
       └─ Retorna: "¿Cuántos usuarios concurrentes esperas?"

5. Orchestrator retorna ChatResponse
   ├─ response.role: "assistant"
   ├─ response.content: "¿Cuántos usuarios concurrentes esperas?"
   └─ state.status: "interviewing"

6. Gateway registra éxito
   ├─ Log INFO en console (verde)
   ├─ Log en logs/info.log
   └─ Retorna HTTP 200

7. JavaScript recibe respuesta
   ├─ Actualiza DOM con pregunta
   ├─ Calcula progreso: 0/5 parámetros
   ├─ Habilita input para siguiente respuesta
   └─ Guarda estado en memoria

8. Usuario responde: "Unos 10,000 usuarios"
   ├─ Historial ahora tiene 4 mensajes
   ├─ Envía POST /api/chat con historial completo
   ├─ Loop vuelve a paso 3

9. Después de 5+ preguntas respondidas
   ├─ Orchestrator detecta parámetros >= 5
   ├─ Cambia status a "recommending"
   ├─ Llama a Recommendation Engine
   ├─ Engine.get_recommendation() calcula scores
   ├─ Retorna TOP 3 arquitecturas
   ├─ LLM Service genera descripciones para cada una
   └─ Retorna ChatResponse con recomendations[]

10. JavaScript muestra recomendaciones
    ├─ Tarjetas con TOP 3 arquitecturas
    ├─ Nombre, descripción, justificación
    └─ Progreso: 5/5 parámetros ✅
```

---

## Patrones de Diseño

### 1. API Gateway Pattern
- Validación centralizada
- Manejo de errores consistente
- Logging transversal

### 2. Orchestrator Pattern
- Coordinación de servicios
- Gestión de estado conversacional
- Control de flujo

### 3. Service Layer
- Servicios especializados desacoplados
- LLM Service independiente
- Recommendation Engine independiente

### 4. Repository Pattern (Implicit)
- `architecture_data.py` actúa como "repositorio" de arquitecturas
- En el futuro: fácil migración a BD real

---

## Principios de Diseño

### ✅ Separación de Responsabilidades
- Cada componente tiene responsabilidad clara
- No hay lógica duplicada

### ✅ Bajo Acoplamiento
- Gateway no conoce detalles de Orchestrator
- Orchestrator no conoce detalles de LLM
- Fácil reemplazar componentes

### ✅ Escalabilidad
- Arquitectura preparada para:
  - Más componentes
  - Base de datos real
  - Autenticación de usuario
  - Rate limiting

### ✅ Observabilidad
- Logging completo en todos los puntos
- Request IDs para trazabilidad
- Decoradores para instrumentación automática

---

## Mejoras Potenciales

### Corto Plazo
- [ ] Tests unitarios e integración
- [ ] Validación de entrada más robusta
- [ ] Caching de respuestas

### Mediano Plazo
- [ ] Base de datos (PostgreSQL)
- [ ] Autenticación y autorización
- [ ] Rate limiting
- [ ] Circuit breaker para LLM

### Largo Plazo
- [ ] Microservicios (¡usar la propia arquitectura!)
- [ ] Machine learning para mejorar recomendaciones
- [ ] Análisis de costos
- [ ] Integración con herramientas DevOps

---

## Seguridad

### ✅ Implementado
- CORS configurado (todos los orígenes por ahora)
- Escapado de HTML en frontend
- Validación de input
- Manejo seguro de excepciones

### ⚠️ Por Implementar
- [ ] HTTPS en producción
- [ ] Rate limiting
- [ ] Autenticación de usuario
- [ ] Sanitización de prompts
- [ ] Secrets management

---

## Performance

### Optimizaciones
- FastAPI (async/await)
- Validación con Pydantic
- Caché potencial en LLM

### Métricas
- Tiempo de respuesta típico: 2-5 segundos (LLM)
- Tamaño de solicitud: < 100 KB (historial)
- Tamaño de respuesta: < 10 KB (mensaje)

---

## Despliegue

### Desarrollo Local
```bash
python -m app.main
# Servidor en http://localhost:5000
```

### Producción (Recomendado)
```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
# O usar Docker
```

---

## Referencias

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [DeepSeek API](https://platform.deepseek.com/)
- [Microservices Patterns](https://microservices.io/)