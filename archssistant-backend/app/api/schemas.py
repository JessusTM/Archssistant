"""Schemas for request/response of the Arch-Assistant API.

This module defines the Pydantic models that validate and document
the input and output data of the API endpoints.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any


class ChatMessage(BaseModel):
    """Single chat message schema.

    The API contract requires `role` and `content`. Extra fields are allowed
    because the backend may attach metadata (e.g. `state`) to messages.
    """

    model_config = ConfigDict(extra="allow")

    role: str
    content: str


class ChatRequest(BaseModel):
    """Request model for the chat endpoint.

    Attributes:
        history: Ordered list of conversation messages. Each message has at least:
            - `role`: str (e.g. "user", "assistant", or "user_description")
            - `content`: str (message text)

            The orchestrator may also attach `state` in assistant messages.
            This backend validates the message shape in the HTTP layer.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "history": [
                    {"role": "user", "content": "Hello, I need help with my project"},
                    {"role": "assistant", "content": "Hello! I'm here to help you..."},
                ]
            }
        }
    )

    history: List[ChatMessage] = Field(
        ...,
        description="Complete conversation history in chronological order",
        min_length=1,
    )


class ChatResponse(BaseModel):
    """Response model for the chat endpoint.

    Attributes:
        response: Assistant response message with role, content and metadata.
        state: Current conversation state with inferred parameters and status.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "response": {
                    "role": "assistant",
                    "content": "What type of project are you developing?",
                },
                "state": {"inferredParams": {}, "status": "interviewing"},
            }
        }
    )

    response: Dict[str, Any] = Field(
        ..., description="Assistant response with role, content and additional data"
    )
    state: Dict[str, Any] = Field(
        ..., description="Conversation state with inferredParams and status"
    )
