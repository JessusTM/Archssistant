# API Gateway - Documentación Técnica

## Descripción

El **API Gateway** es un componente arquitectónico centralizado que actúa como punto de entrada para todas las solicitudes HTTP a la aplicación. Implementa el patrón API Gateway, proporcionando validación, logging, manejo de errores y delegación a servicios especializados.

**Ubicación:** `archssistant-backend/app/api/gateway.py`

---

## Responsabilidades

### ✅ Validación de Entrada
- Verifica que el historial sea una lista válida
- Valida la estructura de cada mensaje (roles y contenido)
- Rechaza solicitudes malformadas con código 400

### ✅ Logging Centralizado
- Registra todas las solicitudes entrantes
- Crea un Request ID para trazabilidad
- Registra respuestas exitosas y errores
- Usa timestamps para análisis temporal

### ✅ Manejo de Errores
- **Validación (400)**: Request inválida
- **Autenticación (401)**: Error de API key del LLM
- **Servidor (500)**: Error interno no controlado

### ✅ Delegación a Servicios
- Delega procesamiento al Dialogue Orchestrator
- Traduce excepciones internas a respuestas HTTP

---

## Arquitectura del Gateway

```
Solicitud HTTP
      ↓
┌─────────────────────────────────┐
│  API Gateway                    │
├─────────────────────────────────┤
│ 1. Validar entrada              │
│ 2. Crear Request ID             │
│ 3. Loguear solicitud            │
│ 4. Delegar a Orchestrator       │
│ 5. Loguear respuesta            │
│ 6. Retornar resultado           │
└──────────────┬──────────────────┘
               ↓
      Dialogue Orchestrator
               ↓
    LLM Service + Recommendation Engine
               ↓
            Respuesta HTTP
```

---

## Clases y Métodos

### `ApiGateway`

Clase que implementa el patrón API Gateway para manejo centralizado de solicitudes.

**Inicialización:**
```python
gateway = ApiGateway()
```

### `process_chat_message(request: ChatRequest) -> ChatResponse`

Método principal que procesa un mensaje de chat a través del Gateway.

**Parámetros:**
- `request` (ChatRequest): Objeto validado por Pydantic con historial

**Retorna:**
- `ChatResponse`: Respuesta con mensaje del asistente y estado

**Excepciones lanzadas:**
- `GatewayError`: Excepción unificada con status_code y detail
  - status_code 400: Error de validación
  - status_code 401: Error de autenticación (API key LLM)
  - status_code 500: Error interno no controlado

**Flujo:**
1. Valida entrada con `_validate_chat_request()`
2. Genera Request ID único
3. Registra solicitud con logging
4. Delega a `handle_message()` del Orchestrator
5. Registra respuesta exitosa
6. Retorna resultado

**Ejemplo:**
```python
gateway = ApiGateway()
result = gateway.process_chat_message(request)
return result  # ChatResponse
```

---

### `_validate_chat_request(request: ChatRequest) -> None`

Valida que la solicitud cumpla los requisitos mínimos.

**Validaciones:**
- ✅ Historial es una lista
- ✅ Historial no está vacío
- ✅ Cada mensaje es un diccionario
- ✅ Cada mensaje tiene `role` y `content`

**Lanza `ValidationError` si:**
- `history` no es lista
- `history` está vacío
- Algún mensaje no es diccionario
- Algún mensaje falta `role` o `content`

**Ejemplo:**
```python
try:
    self._validate_chat_request(request)
except GatewayError as ge:
    # Manejo del error (ya tiene status_code y detail)
    raise ge
```

---

## Excepciones Personalizadas

### `GatewayError`

Excepción unificada para todos los errores del Gateway. Permite especificar el código HTTP y el mensaje de error de forma clara y consistente.

**Ubicación:** `app/api/exceptions.py`

```python
class GatewayError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)
```

**Uso:**
```python
# Error de validación (400)
raise GatewayError(
    status_code=400,
    detail="El historial no puede estar vacío"
)

# Error de autenticación (401)
raise GatewayError(
    status_code=401,
    detail="Error de autenticación con el proveedor LLM: ..."
)

# Error interno (500)
raise GatewayError(
    status_code=500,
    detail="Error interno al procesar el mensaje de chat."
)
```

### `ApiKeyError`

Excepción específica para errores relacionados con la API key del LLM. El Gateway la captura y la convierte a `GatewayError` con status_code 401.

**Ubicación:** `app/api/exceptions.py`

```python
class ApiKeyError(Exception):
    """Error de autenticación relacionado con la API key del LLM."""
    pass
```

---

## Request ID y Trazabilidad

Cada solicitud recibe un ID único basado en timestamp ISO:

```
[2025-12-28T10:30:45.123456] Solicitud de chat recibida
[2025-12-28T10:30:45.234567] Delegando a Dialogue Orchestrator...
[2025-12-28T10:30:45.456789] Respuesta generada exitosamente
```

Esto permite:
- Rastrear una solicitud a través de todos los componentes
- Correlacionar logs en diferentes módulos
- Debuggear problemas específicos

---

## Logging

### Logs Generados

**INFO (solicitud exitosa):**
```
[REQUEST_ID] Chat request received - history contains 3 messages
[REQUEST_ID] Response generated successfully - state: interviewing
```

**DEBUG (delegación y validación):**
```
[REQUEST_ID] Delegating to Dialogue Orchestrator
Request validation successful - 3 valid messages
```

**ERROR (excepciones):**
```
[REQUEST_ID] LLM authentication error: DEEPSEEK_API_KEY not found in environment variables
[REQUEST_ID] Unexpected internal error in gateway: AttributeError in orchestrator
```

Todos los logs van a:
- **Consola** (INFO y superiores)
- **logs/info.log** (INFO y WARNING)
- **logs/error.log** (ERROR y CRITICAL)

---

## Integración con Routes

El Gateway se integra en `app/api/routes.py`:

```python
from .gateway import ApiGateway
from .exceptions import GatewayError

gateway = ApiGateway()

@router.post('/chat', response_model=ChatResponse)
def chat(request: ChatRequest) -> Dict[str, Any]:
    try:
        result = gateway.process_chat_message(request)
        return result
    except GatewayError as ge:
        # GatewayError ya contiene status_code y detail
        raise HTTPException(
            status_code=ge.status_code,
            detail=ge.detail
        ) from ge
    except Exception as error:
        # Errores inesperados no manejados por Gateway
        logger.exception("Unexpected error in chat endpoint...")
        raise HTTPException(
            status_code=500,
            detail='Unexpected internal error processing the message...'
        ) from error
```

El endpoint actúa como adaptador entre FastAPI y el Gateway. La simplificación a una única excepción `GatewayError` hace el manejo de errores más claro y mantenible.

---

## Casos de Uso

### Caso 1: Solicitud Válida

```
Cliente → POST /api/chat con historial válido
Gateway → Valida ✅ → Delega al Orchestrator
Orchestrator → Procesa → Retorna respuesta
Gateway → Registra éxito → Retorna 200
```

### Caso 2: Validación Fallida

```
Cliente → POST /api/chat con historial vacío
Gateway → Valida ❌ → Lanza GatewayError(status_code=400, ...)
Routes → Captura GatewayError → Retorna 400 Bad Request
Logs → "Request validation failed"
```

### Caso 3: Error de Autenticación

```
Cliente → POST /api/chat
Gateway → Valida ✅ → Delega al Orchestrator
LLM Service → Llama a DeepSeek → API KEY inválida ❌
LLM Service → Lanza ApiKeyError
Gateway → Captura ApiKeyError → Lanza GatewayError(status_code=401, ...)
Routes → Captura GatewayError → Retorna 401 Unauthorized
```

### Caso 4: Error Interno

```
Cliente → POST /api/chat
Gateway → Valida ✅ → Delega al Orchestrator
Orchestrator → Error inesperado ❌
Gateway → Captura Exception → Lanza GatewayError(status_code=500, ...)
Routes → Captura GatewayError → Retorna 500 Internal Server Error
Logs → Exception completo con stack trace (logger.exception)
```

---

## Mejores Prácticas

### ✅ DO

```python
# Usar request ID para trazabilidad
self.logger.info(f"[{request_id}] Chat request received - history contains {len(request.history)} messages")

# Incluir contexto en validaciones
raise GatewayError(
    status_code=400,
    detail="The 'history' field must be an array of messages."
)

# Registrar tanto entrada como salida
state_status = result.get('state', {}).get('status', 'unknown')
self.logger.info(f"[{request_id}] Response generated successfully - state: {state_status}")

# Logging de errores con stack trace
self.logger.exception(f"[{request_id}] Unexpected internal error in gateway: {str(e)}")
```

### ❌ DON'T

```python
# No crear nuevos loggers manualmente
import logging
logger = logging.getLogger(__name__)  # Usar get_logger() en su lugar

# Usar get_logger() del core
from app.core import get_logger
self.logger = get_logger(__name__)

# No omitir contexto
self.logger.error("Error")  # Poco informativo
# Mejor:
self.logger.error(f"[{request_id}] LLM authentication error: {str(ake)}")

# Capturar excepciones específicas cuando sea posible
try:
    ...
except ApiKeyError as ake:  # Específico
    ...
except Exception as e:  # Genérico solo para casos no esperados
    ...
```

---

## Testing

### Test de Validación

```python
def test_empty_history():
    gateway = ApiGateway()
    request = ChatRequest(history=[])
    with pytest.raises(GatewayError) as exc_info:
        gateway.process_chat_message(request)
    assert exc_info.value.status_code == 400
```

### Test de Autenticación

```python
def test_invalid_api_key():
    os.environ.pop('DEEPSEEK_API_KEY', None)
    gateway = ApiGateway()
    request = ChatRequest(history=[{"role": "user", "content": "test"}])
    with pytest.raises(GatewayError) as exc_info:
        gateway.process_chat_message(request)
    assert exc_info.value.status_code == 401
```

### Test de Éxito

```python
def test_valid_request(mock_orchestrator):
    mock_orchestrator.handle_message.return_value = {
        "response": {"role": "assistant", "content": "..."},
        "state": {"status": "interviewing"}
    }
    gateway = ApiGateway()
    gateway.orchestrator = mock_orchestrator
    request = ChatRequest(history=[{"role": "user", "content": "test"}])
    result = gateway.process_chat_message(request)
    assert result['response']['role'] == 'assistant'
```

---

## Evolución Futura

### Políticas Transversales Potenciales

El Gateway puede extenderse para:

1. **Autenticación de Usuario**
   ```python
   # Validar JWT token
   def _validate_auth_header(request):
       ...
   ```

2. **Rate Limiting**
   ```python
   # Limitar solicitudes por IP/usuario
   def _check_rate_limit(request_id):
       ...
   ```

3. **Transformación de Datos**
   ```python
   # Normalizar datos de entrada/salida
   def _normalize_request(request):
       ...
   ```

4. **Caching**
   ```python
   # Cache de respuestas frecuentes
   if request.history in cache:
       return cache[request.history]
   ```

---

## Diagnóstico

### Ver logs en tiempo real

```bash
# Windows PowerShell
Get-Content logs/info.log -Tail 20 -Wait

# Linux/Mac
tail -f logs/info.log
```

### Filtrar por errores

```bash
# Windows
Select-String "ERROR|CRITICAL" logs/error.log

# Linux
grep "ERROR\|CRITICAL" logs/error.log
```

### Filtrar por Request ID

```bash
# Buscar todos los logs de una solicitud
Select-String "\[2025-12-28T10:30:45" logs/info.log
```

---

## Referencias

- [Patrón API Gateway](https://microservices.io/patterns/apigateway.html)
- [Sistema de Logging](./LOGGING.md)
- [Routes (Endpoints)](../archssistant-backend/app/api/routes.py)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Versión:** 2.0.0
**Última actualización:** Diciembre 2025
