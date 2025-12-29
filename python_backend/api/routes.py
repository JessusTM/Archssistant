"""Definición de rutas y endpoints de la API de Arch-Assistant.

Este módulo contiene los endpoints HTTP que expone la aplicación,
delegando la lógica de negocio a los componentes correspondientes
del servidor (orquestador, LLM service, recommendation engine).
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from .models import ChatRequest, ChatResponse
from ..server.dialogue_orchestrator import handle_message
from ..server.llm_service.llm_service import ApiKeyError


router = APIRouter(prefix='/api', tags=['chat'])


@router.post('/chat', response_model=ChatResponse)
async def chat(request: ChatRequest) -> Dict[str, Any]:
    """Procesa el último mensaje del usuario y responde como asistente.

    Args:
        request: Cuerpo JSON validado por Pydantic. Debe contener `history` como una
            lista con el historial completo de la conversación en orden cronológico.
            Se asume que el último elemento corresponde al mensaje actual del usuario.

    Behavior:
        - Valida que `request.history` sea una lista (validado por Pydantic).
        - Delega el flujo conversacional al orquestador `handle_message(history)`.
        - Traduce errores de autenticación de LLM a un `HTTP 401`.
        - En errores inesperados, responde con `HTTP 500`.

    Returns:
        dict: Respuesta JSON con la forma:
            {
              "response": {"role": "assistant", "content": "...", ...},
              "state": {"inferredParams": {...}, "status": "...", ...}
            }
            El contenido exacto depende del estado de la entrevista (preguntas) o de
            la fase de recomendación (incluye `recommendation`).

    Raises:
        HTTPException:
            - 400 si `history` no es una lista (manejado por Pydantic).
            - 401 si falta/es inválida la API key del proveedor LLM.
            - 500 para fallos internos no controlados.
    """
    try:
        # Validación ya realizada por Pydantic
        if not isinstance(request.history, list):
            raise HTTPException(
                status_code=400,
                detail='El historial de la conversación es obligatorio y debe ser un array.'
            )
        
        # Delegar al orquestador
        result = await handle_message(request.history)
        return result
    
    except ApiKeyError as api_error:
        # Error de autenticación con el proveedor LLM
        raise HTTPException(
            status_code=401,
            detail=str(api_error)
        ) from api_error
    
    except HTTPException:
        # Re-lanzar excepciones HTTP ya definidas
        raise
    
    except Exception as error:
        # Capturar errores inesperados
        raise HTTPException(
            status_code=500,
            detail='Error interno al procesar el mensaje.'
        ) from error
