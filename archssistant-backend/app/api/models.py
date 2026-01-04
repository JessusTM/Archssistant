"""Models for request/response of the Arch-Assistant API.

This module defines the Pydantic models that validate and document
the input and output data of the API endpoints.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any


class ChatRequest(BaseModel):
    """Request model for the chat endpoint.

    Attributes:
        history: Ordered list of conversation messages. Each message is a
            dictionary (or equivalent structure) with at least:
            - `role`: str (e.g. "user", "assistant", or "user_description")
            - `content`: str (message text)

            The orchestrator may also attach `state` in assistant messages.
            This backend validates that `history` is a list; internal content
            is validated tolerantly in the orchestrator.
    """
    
    # model_config      : Configures Pydantic model behavior at the class level.
    # json_schema_extra : Adds extra information to the JSON schema generated for this model,
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "history": [
                    {
                        "role": "user", 
                        "content": "Hola, necesito ayuda con mi proyecto"
                    },
                    {
                        "role": "assistant", 
                        "content": "¡Hola! Estoy aquí para ayudarte..."
                    }
                ]
            }
        }
    )

    history: List[Dict[str, Any]] = Field(
        ...,
        description = "Historial completo de la conversación en orden cronológico",
        min_length  = 0
    )


class ChatResponse(BaseModel):
    """Response model for the chat endpoint.

    Attributes:
        response: Assistant response message with role, content and metadata.
        state: Current conversation state with inferred parameters and status.
    """
    
    # model_config      : Configures Pydantic model behavior at the class level.
    # json_schema_extra : Adds extra information to the JSON schema generated for this model,
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "response": {
                    "role"      : "assistant",
                    "content"   : "¿Cuál es el tipo de proyecto que estás desarrollando?"
                },
                "state": {
                    "inferredParams": {},
                    "status"        : "interviewing"
                }
            }
        }
    )

    response: Dict[str, Any] = Field(
        ...,  # Required field marker - means "this field must be provided"
        description = "Respuesta del asistente con role, content y datos adicionales"
    )
    state: Dict[str, Any] = Field(
        ...,
        description = "Estado de la conversación con inferredParams y status"
    )
