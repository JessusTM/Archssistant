# Sistema de Logging de Arch-Assistant

## Descripción General

Arch-Assistant implementa un sistema de logging profesional y centralizado que proporciona visibilidad completa del comportamiento de la aplicación en desarrollo y producción.

## Características

### ✅ Logging Centralizado
- **Configuración única** en `python_backend/config/logging_config.py`
- **Inicialización en punto de entrada** (`main.py`)
- **Coherencia en toda la aplicación**

### ✅ Múltiples Handlers
- **Consola**: Salida en tiempo real con colores
- **Archivo debug.log**: Todos los logs (modo debug)
- **Archivo info.log**: INFO y superior
- **Archivo error.log**: Solo ERROR y CRITICAL

### ✅ Rotación de Logs
- Archivos limitan a **10 MB** cada uno
- Mantiene **5 backups** de cada archivo
- Evita llenar el disco

### ✅ Decoradores Automáticos
- `@log_function_call`: Rastrea entrada/salida
- `@log_performance`: Mide tiempo de ejecución
- Útiles para debugging y profiling

### ✅ Funciones de Dominio
- `log_orchestration_event()`: Eventos de flujo conversacional
- `log_llm_call()`: Llamadas a LLM con contexto
- `log_recommendation_event()`: Eventos del motor de recomendación
- `log_api_request()`: Solicitudes HTTP

## Estructura de Directorios

```
python_backend/
├── config/
│   ├── __init__.py
│   ├── logging_config.py      # Configuración central
│   └── logging_utils.py        # Decoradores y utilidades
├── api/
│   ├── gateway.py             # Usa get_logger()
│   └── routes.py
├── server/
│   ├── dialogue_orchestrator/
│   │   └── orchestrator.py    # Usa log_orchestration_event()
│   ├── llm_service/
│   │   └── llm_service.py     # Usa log_llm_call()
│   └── recommendation_engine/
│       └── engine.py          # Usa log_recommendation_event()
└── main.py                    # setup_logging() + get_logger()

logs/
├── debug.log                  # Todos los logs (DEBUG+)
├── info.log                   # INFO y superior (sin DEBUG)
└── error.log                  # Solo ERROR y CRITICAL
```

## Uso

### Inicialización (main.py)
```python
from python_backend.config import setup_logging, get_logger

# Configurar logging (se hace automáticamente en main.py)
setup_logging(debug_mode=False)  # False en producción

# Obtener logger para el módulo
logger = get_logger(__name__)
logger.info("Mensaje informativo")
```

### En Módulos
```python
from python_backend.config import get_logger

logger = get_logger(__name__)

# Logging básico
logger.debug("Información de debugging")
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
    return x + y

@log_performance
def expensive_operation():
    # Mide automáticamente el tiempo
    pass
```

### Eventos de Dominio
```python
from python_backend.config import (
    log_orchestration_event,
    log_llm_call,
    log_recommendation_event
)

# En orchestrator.py
log_orchestration_event(
    event_type='answer_received',
    phase='interviewing',
    message='Usuario respondió sobre scalability',
    extra_data={'parameter': 'scalability', 'value': 'Alta'}
)

# En llm_service.py
log_llm_call(
    operation='interpret',
    input_summary='Usuario respondió: "Startup pequeña"',
    output_summary='teamSize=Pequeño'
)

# En engine.py
log_recommendation_event(
    stage='scoring',
    message='Calculando puntajes',
    extra_data={'architectures_count': 5}
)
```

## Niveles de Log

| Nivel | Uso | Ejemplo |
|-------|-----|---------|
| **DEBUG** | Información detallada para debugging | Valores de variables, detalles de ejecución |
| **INFO** | Eventos importantes | Inicio de proceso, cambio de estado, solicitudes HTTP |
| **WARNING** | Situaciones inesperadas | API key vacía, parámetro inválido |
| **ERROR** | Error que no detiene la aplicación | Fallo de llamada LLM, validación fallida |
| **CRITICAL** | Error grave que detiene la aplicación | Crash del servidor, error fatal |

## Formatos

### Consola (Coloreado)
```
2025-12-28 10:30:45,123 - __main__ - INFO - Inicializando Arch-Assistant API...
2025-12-28 10:30:45,234 - gateway - ERROR - Error de validación: El historial no puede estar vacío
```

### Archivo
```
2025-12-28 10:30:45,123 | orchestrator                     | INFO     | [ORQ] ANSWER_RECEIVED (interviewing) - Usuario respondió sobre scalability
2025-12-28 10:30:45,234 | llm_service                      | INFO     | [LLM] INTERPRET (deepseek) | Input: "Startup pequeña"
```

## Archivos de Log

Los logs se guardan en `logs/`:

### `debug.log` (Modo Debug)
- Contiene **todos** los logs (DEBUG y superior)
- Solo se crea en `debug_mode=True`
- Útil para desarrollo local

### `info.log`
- Logs INFO y WARNING (sin DEBUG)
- Excluye logs ERROR/CRITICAL
- Ideal para monitoreo en producción

### `error.log`
- Solo ERROR y CRITICAL
- Facilita identificar problemas
- Ideal para alertas

## Rotación de Archivos

Cada archivo de log:
- **Límite de tamaño**: 10 MB
- **Backups**: 5 archivos (debug.log.1, debug.log.2, etc.)
- **Codificación**: UTF-8
- **Automática**: Se rota sin intervención manual

## Ejemplo Completo

```python
# En python_backend/server/dialogue_orchestrator/orchestrator.py

from python_backend.config import (
    get_logger,
    log_function_call,
    log_orchestration_event
)

logger = get_logger(__name__)

@log_function_call
async def handle_message(history):
    """Maneja un mensaje conversacional."""
    logger.info(f"Procesando mensaje #{len(history)}")
    
    try:
        state = get_conversation_state(history)
        
        if state['status'] == 'interviewing':
            log_orchestration_event(
                event_type='question_asked',
                phase='interviewing',
                message=f"Preguntando sobre {next_param}",
                extra_data={'parameters_pending': len(remaining_params)}
            )
        elif state['status'] == 'recommending':
            log_orchestration_event(
                event_type='recommendation_ready',
                phase='recommendation',
                message='Generando recomendaciones'
            )
            
    except Exception as e:
        logger.error(f"Error procesando mensaje: {str(e)}", exc_info=True)
        raise
```

## Mejores Prácticas

### ✅ DO
```python
# Usar get_logger(__name__)
logger = get_logger(__name__)

# Loguear eventos importantes
logger.info("Usuario inició sesión")

# Incluir contexto en errores
logger.error(f"Falló llamada LLM para {param}: {error_msg}", exc_info=True)

# Usar funciones de dominio para eventos específicos
log_orchestration_event(...)
```

### ❌ DON'T
```python
# No crear loggers manualmente
import logging
logger = logging.getLogger(__name__)  # Evitar esto

# No omitir contexto
logger.error("Error")  # Poco informativo

# No loguear sin contexto
logger.debug("x")  # Inútil
```

## Debugging

### Ver logs en tiempo real
```bash
# En Windows PowerShell
Get-Content logs/info.log -Tail 20 -Wait

# En Linux/Mac
tail -f logs/info.log
```

### Filtrar logs por nivel
```bash
# Solo errores
Select-String "ERROR|CRITICAL" logs/error.log

# Solo eventos de orquestación
Select-String "\[ORQ\]" logs/info.log
```

## Configuración Avanzada

### Cambiar nivel de consola
En `main.py`:
```python
setup_logging(debug_mode=True)  # Muestra DEBUG en consola
```

### Agregar handlers personalizados
En `logging_config.py`, agregar al final de `setup_logging()`:
```python
# Handler para Slack, Datadog, etc.
# sentry_handler = ...
# root_logger.addHandler(sentry_handler)
```

## Monitoreo y Alertas

En producción, pueden monitorearse:
1. **Archivo `error.log`** para errores críticos
2. **Líneas con `[CRITICAL]`** para alertas automáticas
3. **Duración de operaciones** en logs `[PERF]`
4. **Tasa de errores** en intervalos regulares

---

**Documentación**: [Sistema de Logging](.)
