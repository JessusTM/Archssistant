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
                        "content": "Hello, I need help with my project"
                    },
                    {
                        "role": "assistant", 
                        "content": "Hello! I'm here to help you..."
                    }
                ]
            }
        }
    )

    history: List[Dict[str, Any]] = Field(
        ..., # Required Field
        description = "Complete conversation history in chronological order",
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
                    "content"   : "What type of project are you developing?"
                },
                "state": {
                    "inferredParams": {},
                    "status"        : "interviewing"
                }
            }
        }
    )

    response: Dict[str, Any] = Field(
        ..., # Required Field
        description = "Assistant response with role, content and additional data"
    )
    state: Dict[str, Any] = Field(
        ..., # Required Field
        description = "Conversation state with inferredParams and status"
    )
