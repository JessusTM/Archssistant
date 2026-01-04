# API Gateway - Documentación Técnica

## Descripción

El **API Gateway** es un componente arquitectónico centralizado que actúa como punto de entrada para todas las solicitudes HTTP a la aplicación. Implementa el patrón API Gateway, proporcionando validación, logging, manejo de errores y delegación a servicios especializados.

**Ubicación:** `python_backend/api/gateway.py`

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

## Clases y Funciones

### `process_chat_message(request: ChatRequest) -> ChatResponse`

Función principal que procesa un mensaje de chat a través del Gateway.

**Parámetros:**
- `request` (ChatRequest): Objeto validado por Pydantic con historial

**Retorna:**
- `ChatResponse`: Respuesta con mensaje del asistente y estado

**Excepciones lanzadas:**
- `ValidationError`: Si la solicitud no cumple requisitos
- `AuthenticationError`: Si hay error de credenciales LLM
- `InternalServerError`: Si ocurre error no controlado

**Flujo:**
1. Valida entrada con `_validate_chat_request()`
2. Genera Request ID único
3. Registra solicitud con logging
4. Delega a `handle_message()` del Orchestrator
5. Registra respuesta exitosa
6. Retorna resultado

**Ejemplo:**
```python
result = await process_chat_message(request)
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
    _validate_chat_request(request)
except ValidationError as ve:
    # Manejo del error
    raise HTTPException(status_code=400, detail=ve.detail)
```

---

## Excepciones Personalizadas

### `GatewayError`

Base para todas las excepciones del Gateway.

```python
class GatewayError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
```

### `ValidationError` (HTTP 400)

Se lanza cuando la solicitud no cumple validación.

```python
raise ValidationError("El historial no puede estar vacío")
```

### `AuthenticationError` (HTTP 401)

Se lanza cuando hay error de credenciales LLM.

```python
raise AuthenticationError("API key inválida o expirada")
```

### `InternalServerError` (HTTP 500)

Se lanza cuando ocurre error interno no controlado.

```python
raise InternalServerError("Error inesperado al procesar")
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
[REQUEST_ID] Solicitud de chat recibida. Historial: 3 mensajes.
[REQUEST_ID] Respuesta generada exitosamente. Estado: interviewing
```

**DEBUG (delegación):**
```
[REQUEST_ID] Delegando a Dialogue Orchestrator...
```

**WARNING (validación):**
```
[REQUEST_ID] Error de validación: El historial no puede estar vacío
```

**ERROR (excepciones):**
```
[REQUEST_ID] Error de autenticación LLM: DEEPSEEK_API_KEY no configurada
[REQUEST_ID] Error interno no controlado: AttributeError en orchestrator
```

Todos los logs van a:
- **Consola** (INFO y superiores)
- **logs/info.log** (INFO y WARNING)
- **logs/error.log** (ERROR y CRITICAL)

---

## Integración con Routes

El Gateway se integra en `routes.py`:

```python
@router.post('/chat', response_model=ChatResponse)
async def chat(request: ChatRequest) -> Dict[str, Any]:
    try:
        result = await process_chat_message(request)
        return result
    except ValidationError as ve:
        raise HTTPException(status_code=400, detail=ve.detail)
    except AuthenticationError as ae:
        raise HTTPException(status_code=401, detail=ae.detail)
    except InternalServerError as ise:
        raise HTTPException(status_code=500, detail=ise.detail)
```

El endpoint actúa como adaptador entre FastAPI y el Gateway.

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
Gateway → Valida ❌ → Lanza ValidationError
Routes → Captura → Retorna 400 Bad Request
Logs → "Error de validación: El historial no puede estar vacío"
```

### Caso 3: Error de Autenticación

```
Cliente → POST /api/chat
Gateway → Valida ✅ → Delega al Orchestrator
LLM Service → Llama a DeepSeek → API KEY inválida ❌
Orchestrator → Lanza ApiKeyError
Gateway → Captura → Lanza AuthenticationError
Routes → Captura → Retorna 401 Unauthorized
```

### Caso 4: Error Interno

```
Cliente → POST /api/chat
Gateway → Valida ✅ → Delega al Orchestrator
Orchestrator → Error inesperado ❌
Gateway → Captura en try/except → Lanza InternalServerError
Routes → Captura → Retorna 500 Internal Server Error
Logs → Exception completo con stack trace
```

---

## Mejores Prácticas

### ✅ DO

```python
# Usar request ID para trazabilidad
logger.info(f"[{request_id}] Solicitud procesada")

# Incluir contexto en validaciones
raise ValidationError("El campo 'history' debe ser un array de mensajes")

# Registrar tanto entrada como salida
logger.info(f"[{request_id}] Solicitud recibida. Mensajes: {len(request.history)}")
logger.info(f"[{request_id}] Respuesta generada. Estado: {result['state']['status']}")
```

### ❌ DON'T

```python
# No crear nuevos loggers
logger = logging.getLogger(__name__)  # Usar get_logger() en su lugar

# No omitir contexto
logger.error("Error")  # Poco informativo

# No capturar todas las excepciones
try:
    ...
except:  # Evitar, ser específico
    ...
```

---

## Testing

### Test de Validación

```python
async def test_empty_history():
    request = ChatRequest(history=[])
    with pytest.raises(ValidationError):
        await process_chat_message(request)
```

### Test de Autenticación

```python
async def test_invalid_api_key():
    os.environ.pop('DEEPSEEK_API_KEY', None)
    request = ChatRequest(history=[{"role": "user", "content": "test"}])
    with pytest.raises(AuthenticationError):
        await process_chat_message(request)
```

### Test de Éxito

```python
async def test_valid_request(mock_orchestrator):
    mock_orchestrator.return_value = {
        "response": {"role": "assistant", "content": "..."},
        "state": {"status": "interviewing"}
    }
    request = ChatRequest(history=[{"role": "user", "content": "test"}])
    result = await process_chat_message(request)
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
- [Sistema de Logging](../config/README.md)
- [Routes (Endpoints)](./routes.py)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Versión:** 1.0.0
**Última actualización:** 28 de Diciembre, 2025
