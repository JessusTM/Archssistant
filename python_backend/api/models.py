"""Modelos de request/response para la API de Arch-Assistant.

Este módulo define los modelos Pydantic que validan y documentan
los datos de entrada y salida de los endpoints de la API.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any


class ChatRequest(BaseModel):
    """Modelo de request para el endpoint de chat.

    Attributes:
        history: Lista ordenada de mensajes de la conversación. Cada mensaje es un
            diccionario (o estructura equivalente) con al menos:
            - `role`: str (p.ej. "user", "assistant", o "user_description")
            - `content`: str (texto del mensaje)

            El orquestador también puede adjuntar `state` en mensajes del asistente.
            Este backend valida que `history` sea una lista; el contenido interno se
            valida de forma tolerante en el orquestador.
    """

    history: List[Dict[str, Any]] = Field(
        ...,
        description="Historial completo de la conversación en orden cronológico",
        min_items=0
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "history": [
                    {"role": "user", "content": "Hola, necesito ayuda con mi proyecto"},
                    {"role": "assistant", "content": "¡Hola! Estoy aquí para ayudarte..."}
                ]
            }
        }


class ChatResponse(BaseModel):
    """Modelo de response para el endpoint de chat.

    Attributes:
        response: Mensaje de respuesta del asistente con role, content y metadatos.
        state: Estado actual de la conversación con parámetros inferidos y status.
    """

    response: Dict[str, Any] = Field(
        ...,
        description="Respuesta del asistente con role, content y datos adicionales"
    )
    state: Dict[str, Any] = Field(
        ...,
        description="Estado de la conversación con inferredParams y status"
    )

    class Config:
        """Configuración del modelo Pydantic."""
        json_schema_extra = {
            "example": {
                "response": {
                    "role": "assistant",
                    "content": "¿Cuál es el tipo de proyecto que estás desarrollando?"
                },
                "state": {
                    "inferredParams": {},
                    "status": "interview"
                }
            }
        }
