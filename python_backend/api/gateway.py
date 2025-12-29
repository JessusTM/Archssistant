"""API Gateway: componente de enrutamiento, validación y manejo de errores.

Este módulo implementa el patrón API Gateway, actuando como punto de entrada
centralizado que:
- Valida y normaliza las solicitudes entrantes
- Registra eventos y errores (logging)
- Maneja errores de manera consistente
- Delega la lógica de negocio a servicios especializados
- Proporciona respuestas normalizadas

Esta capa permite separar las políticas transversales (validación, logging,
autenticación) de la lógica de negocio específica del orquestador.
"""

from typing import Dict, Any
from datetime import datetime

from .models import ChatRequest, ChatResponse
from ..server.dialogue_orchestrator import handle_message
from ..server.llm_service.llm_service import ApiKeyError
from ..config import get_logger

# Obtener logger desde configuración centralizada
logger = get_logger(__name__)


class GatewayError(Exception):
    """Error base del Gateway para manejo de errores específicos."""
    
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class ValidationError(GatewayError):
    """Error de validación de entrada."""
    
    def __init__(self, detail: str):
        super().__init__(400, detail)


class AuthenticationError(GatewayError):
    """Error de autenticación (API keys, credenciales)."""
    
    def __init__(self, detail: str):
        super().__init__(401, detail)


class InternalServerError(GatewayError):
    """Error interno del servidor."""
    
    def __init__(self, detail: str = "Error interno al procesar la solicitud"):
        super().__init__(500, detail)


def process_chat_message(request: ChatRequest) -> ChatResponse:
    """Procesa un mensaje de chat a través del Gateway.

    Este método actúa como punto de entrada centralizado para todas las solicitudes
    de chat. Implementa las siguientes políticas transversales:

    1. Validación de entrada
    2. Logging de solicitud
    3. Delegación al orquestador
    4. Manejo de errores
    5. Logging de respuesta

    Args:
        request: Objeto ChatRequest validado por Pydantic. Contiene el historial
            completo de la conversación.

    Returns:
        ChatResponse: Respuesta del sistema con mensaje y estado conversacional.

    Raises:
        ValidationError: Si la solicitud no cumple los requisitos mínimos.
        AuthenticationError: Si hay problemas de autenticación (API keys).
        InternalServerError: Si ocurre un error no controlado.
    """
    request_id = f"{datetime.now().isoformat()}"
    
    try:
        # 1. VALIDACIÓN DE ENTRADA
        _validate_chat_request(request)
        logger.info(
            f"[{request_id}] Solicitud de chat recibida. "
            f"Historial: {len(request.history)} mensajes."
        )
        
        # 2. DELEGACIÓN AL ORQUESTADOR
        logger.debug(
            f"[{request_id}] Delegando a Dialogue Orchestrator..."
        )
        result = handle_message(request.history)
        
        # 3. LOGGING DE RESPUESTA
        logger.info(
            f"[{request_id}] Respuesta generada exitosamente. "
            f"Estado: {result.get('state', {}).get('status', 'unknown')}"
        )
        
        return result
    
    except ValidationError as ve:
        logger.warning(f"[{request_id}] Error de validación: {ve.detail}")
        raise
    
    except ApiKeyError as ake:
        logger.error(f"[{request_id}] Error de autenticación LLM: {str(ake)}")
        raise AuthenticationError(
            f"Error de autenticación con el proveedor LLM: {str(ake)}"
        )
    
    except Exception as e:
        logger.exception(
            f"[{request_id}] Error interno no controlado: {str(e)}"
        )
        raise InternalServerError(
            "Error interno al procesar el mensaje de chat."
        )


def _validate_chat_request(request: ChatRequest) -> None:
    """Valida que la solicitud de chat cumpla los requisitos mínimos.

    Args:
        request: Objeto ChatRequest a validar.

    Raises:
        ValidationError: Si la validación falla.
    """
    # Validar que history sea una lista
    if not isinstance(request.history, list):
        raise ValidationError(
            "El campo 'history' debe ser un array de mensajes."
        )
    
    # Validar que no esté vacía
    if len(request.history) == 0:
        raise ValidationError(
            "El historial no puede estar vacío. Debe contener al menos un mensaje."
        )
    
    # Validar estructura básica de los mensajes
    for i, message in enumerate(request.history):
        if not isinstance(message, dict):
            raise ValidationError(
                f"Mensaje {i} no es un objeto: {type(message)}"
            )
        
        if 'role' not in message or 'content' not in message:
            raise ValidationError(
                f"Mensaje {i} debe contener 'role' y 'content'."
            )
    
    logger.debug(f"Validación de solicitud exitosa. {len(request.history)} mensajes válidos.")
