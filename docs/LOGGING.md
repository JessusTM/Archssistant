# Sistema de Logging de Arch-Assistant

## Descripción General

Arch-Assistant implementa un sistema de logging profesional y centralizado que proporciona visibilidad completa del comportamiento de la aplicación en desarrollo y producción.

El sistema utiliza `colorlog` para colores automáticos en terminal, soporta múltiples niveles configurables vía `.env`, y genera logs separados por nivel en archivos rotativos.

## Características

### ✅ Logging Centralizado
- **Configuración única** en `app/core/logging_config.py`
- **Inicialización automática** en `app/core/config.py` al importar
- **Coherencia en toda la aplicación**

### ✅ Colores Automáticos
- **colorlog** para colores en terminal (solo si es TTY)
- **Detección automática** de soporte de colores
- **Seguro** para archivos (sin códigos ANSI en logs)

### ✅ Niveles Configurables
- **LOG_LEVEL** configurable vía `.env`
- Valores válidos: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- Por defecto: `INFO` (producción)
- `DEBUG` para desarrollo completo

### ✅ Múltiples Handlers
- **Consola**: Salida en tiempo real con colores (nivel según LOG_LEVEL)
- **Archivo debug.log**: Todos los logs (solo si LOG_LEVEL=DEBUG)
- **Archivo info.log**: INFO y WARNING (siempre)
- **Archivo error.log**: Solo ERROR y CRITICAL (siempre)

### ✅ Rotación de Logs
- Archivos limitan a **10 MB** cada uno
- Mantiene **5 backups** de cada archivo
- Evita llenar el disco

### ✅ Funciones de Dominio
- `log_orchestration_event()`: Eventos de flujo conversacional
- `log_llm_call()`: Llamadas a LLM con contexto
- `log_recommendation_event()`: Eventos del motor de recomendación
- `log_api_request()`: Solicitudes HTTP

**Nota:** Los decoradores `@log_function_call` y `@log_performance` fueron eliminados por no ser utilizados.

## Estructura de Directorios

```
archssistant-backend/
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Configuración con Config (BaseSettings)
│   │   ├── logging_config.py      # Configuración central de logging
│   │   └── logging_utils.py       # Funciones de dominio
│   ├── main.py                    # Punto de entrada
│   ├── api/
│   │   ├── gateway.py             # Usa get_logger()
│   │   └── routes.py              # Usa get_logger()
│   └── services/
│       ├── dialogue_orchestrator/
│       │   └── orchestrator.py    # Usa get_logger()
│       ├── llm_service/
│       │   └── llm_service.py     # Usa get_logger()
│       └── recommendation_engine/
│           └── engine.py          # Usa get_logger()
├── pyproject.toml
└── logs/

logs/
├── debug.log                       # Todos los logs (solo si LOG_LEVEL=DEBUG)
├── info.log                        # INFO y WARNING (siempre)
└── error.log                       # Solo ERROR y CRITICAL (siempre)
```

## Configuración

### Variables de Entorno (.env)

```env
# Nivel de logging
LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Por defecto: INFO (producción)
# Para desarrollo: LOG_LEVEL=DEBUG
```

### Inicialización Automática

El logging se inicializa automáticamente al importar `app.core.config`:

```python
# En app/main.py
from app.core import config, get_logger

# El logging ya está configurado automáticamente
logger = get_logger(__name__)
logger.info("Mensaje informativo")
```

## Uso

### Obtener Logger en Módulos

```python
from app.core import get_logger

logger = get_logger(__name__)

# Logging básico
logger.debug("Información detallada de debugging")
logger.info("Evento importante")
logger.warning("Advertencia")
logger.error("Error no crítico")
logger.exception("Error con stack trace completo")  # Para excepciones
logger.critical("Error crítico")
```

### Eventos de Dominio

```python
from app.core import (
    log_orchestration_event,
    log_llm_call,
    log_recommendation_event,
    log_api_request
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
    output_summary='teamSize=Pequeño',
    model='deepseek'
)

# En engine.py
log_recommendation_event(
    stage='scoring',
    message='Calculando puntajes',
    extra_data={'architectures_count': 5}
)

# En routes.py
log_api_request(
    method='POST',
    endpoint='/api/chat',
    status_code=200,
    duration_ms=125.5,
    message='Chat procesado exitosamente'
)
```

## Niveles de Log

| Nivel | Uso | Ejemplo | Incluye |
|-------|-----|---------|---------|
| **DEBUG** | Información detallada para debugging | Valores de variables, detalles de ejecución | DEBUG, INFO, WARNING, ERROR, CRITICAL |
| **INFO** | Eventos importantes | Inicio de proceso, cambio de estado, solicitudes HTTP | INFO, WARNING, ERROR, CRITICAL |
| **WARNING** | Situaciones inesperadas | API key vacía, parámetro inválido | WARNING, ERROR, CRITICAL |
| **ERROR** | Error que no detiene la aplicación | Fallo de llamada LLM, validación fallida | ERROR, CRITICAL |
| **CRITICAL** | Error grave que detiene la aplicación | Crash del servidor, error fatal | CRITICAL |

### Jerarquía de Niveles

```
DEBUG < INFO < WARNING < ERROR < CRITICAL
```

Cuando configuras un nivel, incluye ese nivel y todos los superiores.

## Formatos

### Consola (Coloreado con colorlog)

**Formato DEBUG (LOG_LEVEL=DEBUG):**
```
2025-12-28 10:30:45,123 - __main__ - INFO - Initializing API: Archssistant
2025-12-28 10:30:45,234 - gateway - ERROR - [REQUEST_ID] LLM authentication error: ...
2025-12-28 10:30:45,345 - orchestrator - DEBUG - [main.py:123] - handle_message() - Generating descriptions for 3 architectures
```

**Formato Producción (LOG_LEVEL=INFO):**
```
2025-12-28 10:30:45,123 - __main__ - INFO - Initializing API: Archssistant
2025-12-28 10:30:45,234 - gateway - ERROR - [REQUEST_ID] LLM authentication error: ...
```

### Archivo

```
2025-12-28 10:30:45,123 | orchestrator                     | INFO     | Generating descriptions for 3 architectures: ['Microservicios', 'SOA', 'Nube']
2025-12-28 10:30:45,234 | llm_service                      | ERROR    | DeepSeek API authentication failed (401)
2025-12-28 10:30:45,345 | recommendation_engine             | INFO     | Recommendations generated - top architectures: ['Microservicios', 'SOA', 'Nube']
```

## Archivos de Log

Los logs se guardan en `archssistant-backend/logs/`:

### `debug.log` (Solo si LOG_LEVEL=DEBUG)
- Contiene **todos** los logs (DEBUG y superior)
- Solo se crea en desarrollo (`LOG_LEVEL=DEBUG`)
- Útil para debugging local detallado

### `info.log` (Siempre)
- Logs INFO y WARNING (sin DEBUG ni ERROR)
- Excluye DEBUG y ERROR/CRITICAL
- Ideal para monitoreo en producción

### `error.log` (Siempre)
- Solo ERROR y CRITICAL
- Facilita identificar problemas
- Ideal para alertas y monitoreo de errores

## Rotación de Archivos

Cada archivo de log:
- **Límite de tamaño**: 10 MB
- **Backups**: 5 archivos (debug.log.1, debug.log.2, etc.)
- **Codificación**: UTF-8
- **Automática**: Se rota sin intervención manual

Cuando un archivo alcanza 10 MB:
1. Se renombra a `debug.log.1`
2. El anterior `debug.log.1` se convierte en `debug.log.2`
3. Y así sucesivamente hasta 5 backups
4. Se crea un nuevo `debug.log`

## Ejemplo Completo

```python
# En app/services/dialogue_orchestrator/orchestrator.py

from app.core import get_logger

logger = get_logger(__name__)

class DialogueOrchestrator:
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def handle_message(self, history):
        """Maneja un mensaje conversacional."""
        self.logger.info(f"Processing message - history contains {len(history)} messages")
        
        try:
            state = self.get_conversation_state(history)
            
            if state['status'] == 'recommending':
                self.logger.debug(
                    f"Generating descriptions for {len(recommendations)} architectures: "
                    f"{[r['name'] for r in recommendations]}"
                )
                
        except Exception as e:
            self.logger.exception(f"Error processing message: {str(e)}")
            raise
```

## Mejores Prácticas

### ✅ DO

```python
# Usar get_logger(__name__)
logger = get_logger(__name__)

# Loguear eventos importantes
logger.info("Initializing API: Archssistant")

# Incluir contexto en errores
logger.error(f"Failed to call LLM API: {error_msg}", exc_info=True)

# Usar niveles apropiados
logger.debug("Detailed debugging info")  # Solo para desarrollo
logger.info("Important business event")   # Producción
logger.warning("Unusual situation")       # Atención necesaria
logger.error("Error occurred")            # Requiere atención
logger.critical("Critical failure")       # Sistema en peligro

# Usar funciones de dominio para eventos específicos
log_orchestration_event(...)
log_llm_call(...)
```

### ❌ DON'T

```python
# No crear loggers manualmente
import logging
logger = logging.getLogger(__name__)  # Evitar esto

# No omitir contexto
logger.error("Error")  # Poco informativo

# No usar print() en lugar de logging
print("DEBUG: algo")  # Usar logger.debug() en su lugar

# No loguear sin contexto útil
logger.debug("x")  # Inútil

# No usar niveles incorrectos
logger.error("Todo está bien")  # Usar logger.info() en su lugar
```

## Debugging

### Ver logs en tiempo real

```bash
# Windows PowerShell
Get-Content logs/info.log -Tail 20 -Wait

# Linux/Mac
tail -f logs/info.log
```

### Filtrar logs por nivel

```bash
# Solo errores
Select-String "ERROR|CRITICAL" logs/error.log  # Windows
grep "ERROR\|CRITICAL" logs/error.log          # Linux/Mac

# Solo eventos de orquestación
Select-String "orchestrator" logs/info.log
```

### Filtrar por Request ID

```bash
# Buscar todos los logs de una solicitud específica
Select-String "\[2025-12-28T10:30:45" logs/info.log
```

## Configuración Avanzada

### Cambiar nivel de logging

En `.env`:
```env
# Desarrollo
LOG_LEVEL=DEBUG

# Producción
LOG_LEVEL=INFO

# Solo errores
LOG_LEVEL=WARNING
```

### Agregar handlers personalizados

En `app/core/logging_config.py`, agregar al final de `setup_logging()`:
```python
# Handler para servicios externos (Slack, Datadog, Sentry, etc.)
# external_handler = logging.handlers.HTTPHandler(...)
# root_logger.addHandler(external_handler)
```

## Monitoreo y Alertas

En producción, pueden monitorearse:

1. **Archivo `error.log`** para errores críticos
2. **Líneas con `CRITICAL`** para alertas automáticas
3. **Tasa de errores** en intervalos regulares
4. **Request IDs** para rastrear solicitudes completas

### Alertas Recomendadas

```bash
# Alertar si hay más de 10 errores por minuto
grep -c "ERROR" logs/error.log | tail -n 1

# Alertar si hay errores críticos
grep "CRITICAL" logs/error.log
```

## Dependencias

```txt
colorlog==6.8.0          # Colores automáticos en terminal
python-dotenv==1.0.1     # Carga de variables de entorno
pydantic-settings==2.1.0 # Configuración con BaseSettings
```

## Cambios Recientes

### Mejoras Implementadas

1. **Reemplazo de DEBUG booleano por LOG_LEVEL string**
   - Configuración más flexible
   - Soporte para WARNING, ERROR, CRITICAL

2. **Integración de colorlog**
   - Colores automáticos y seguros
   - Detección de TTY
   - Sin códigos ANSI en archivos

3. **Eliminación de decoradores no usados**
   - `@log_function_call` eliminado
   - `@log_performance` eliminado

4. **Mejora de logging en servicios**
   - LLM Service: logging completo para API calls
   - Recommendation Engine: logging agregado
   - Gateway: mensajes mejorados

5. **Traducción a inglés**
   - Todos los mensajes de logging en inglés
   - Docstrings en inglés
   - Mensajes de usuario siguen en español

---

**Documentación**: [Sistema de Logging](./LOGGING.md)
**Versión**: 2.0.0
**Última actualización**: Diciembre 2025

