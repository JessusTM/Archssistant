"""Definición de rutas y endpoints de la API de Arch-Assistant.

Este módulo define los endpoints HTTP que expone la aplicación. Cada endpoint
actúa como punto de entrada para solicitudes del cliente, delegando toda la
validación y procesamiento al API Gateway.

El API Gateway (gateway.py) es responsable de:
- Validar las solicitudes entrantes
- Registrar logs de eventos
- Manejar errores de manera centralizada
- Delegar la lógica de negocio a servicios especializados
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from .models import ChatRequest, ChatResponse
from .gateway import (
    process_chat_message,
    ValidationError,
    AuthenticationError,
    InternalServerError
)


router = APIRouter(prefix='/api', tags=['chat'])


@router.post('/chat', response_model=ChatResponse)
def chat(request: ChatRequest) -> Dict[str, Any]:
    """Endpoint de chat para procesamiento de mensajes conversacionales.

    Este endpoint actúa como punto de entrada HTTP para solicitudes de chat.
    Toda la lógica de validación, logging y procesamiento es delegada al
    API Gateway (gateway.process_chat_message).

    Args:
        request: Cuerpo JSON validado por Pydantic (ChatRequest). Debe contener
            `history` como una lista con el historial completo de la conversación
            en orden cronológico.

    Returns:
        ChatResponse: Respuesta JSON con:
            - response: Mensaje del asistente
            - state: Estado conversacional (parámetros inferidos, status, etc.)

    Raises:
        HTTPException:
            - 400: Solicitud inválida (validación fallida)
            - 401: Error de autenticación (API key inválida del LLM)
            - 500: Error interno del servidor

    Notes:
        Esta función actúa como adaptador HTTP que:
        1. Recibe la solicitud HTTP validada por FastAPI/Pydantic
        2. Delega al Gateway para procesamiento completo
        3. Convierte excepciones del Gateway a HTTPException
        4. Devuelve respuesta normalizada
    """
    try:
        # Delegar al API Gateway para procesamiento completo
        result = process_chat_message(request)
        return result
    
    except ValidationError as ve:
        # Error de validación: request inválida
        raise HTTPException(
            status_code=ve.status_code,
            detail=ve.detail
        ) from ve
    
    except AuthenticationError as ae:
        # Error de autenticación: credenciales inválidas
        raise HTTPException(
            status_code=ae.status_code,
            detail=ae.detail
        ) from ae
    
    except InternalServerError as ise:
        # Error interno: fallo en procesamiento
        raise HTTPException(
            status_code=ise.status_code,
            detail=ise.detail
        ) from ise
    
    except Exception as error:
        # Capturar errores inesperados que no fueron manejados por el Gateway
        raise HTTPException(
            status_code=500,
            detail='Error interno inesperado al procesar el mensaje.'
        ) from error
