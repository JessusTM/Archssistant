"""Definition of routes and endpoints of the Archssistant API.

HTTP adapter layer:
- Validates minimal request shape (history)
- Delegates business logic to the Orchestrator
- Translates domain exceptions into HTTP status codes
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from .models import ChatRequest, ChatResponse
from .exceptions import GatewayError, ApiKeyError
from ..core import get_logger
from ..services.orchestrator import Orchestrator

router  = APIRouter(prefix='/api', tags=['chat'])
orchestrator = Orchestrator()
logger  = get_logger(__name__) 


@router.post('/chat', response_model=ChatResponse)
def chat(request: ChatRequest) -> Dict[str, Any]:
    """
    Entry point for chat requests.

    Args:
        request: Validated JSON body by Pydantic (ChatRequest). Must contain
                `history` as a list with the complete conversation history
                in chronological order.

    Returns:
        ChatResponse: JSON response with:
            - response  : Assistant message
            - state     : Conversational state (inferred parameters, status, etc.)

    Raises:
        HTTPException:
            - 400: Invalid request (validation failed)
            - 401: Authentication error (invalid API key for LLM)
            - 500: Internal server error

    Notes:
        This function acts as an HTTP adapter that keeps orchestration and domain logic
        inside `app.services.orchestrator`.
    """
    try:
        _validate_chat_request(request)
        result = orchestrator.handle_message(request.history)
        return result
    
    except ApiKeyError as ake:
        raise HTTPException(status_code=401, detail=str(ake)) from ake

    except GatewayError as ge:
        raise HTTPException(
            status_code=ge.status_code,
            detail=ge.detail
        ) from ge
    
    except Exception as error:
        logger.exception("Unexpected error in chat endpoint")
        raise HTTPException(
            status_code=500,
            detail='Unexpected internal error processing the message...'
        ) from error


def _validate_chat_request(request: ChatRequest) -> None:
    """Minimal validation of the chat request (kept from previous adapter behavior)."""
    if not isinstance(request.history, list):
        raise GatewayError(status_code=400, detail="The 'history' field must be an array of messages.")
    if len(request.history) == 0:
        raise GatewayError(status_code=400, detail="The history cannot be empty. It must contain at least one message.")

    for i, message in enumerate(request.history):
        if not isinstance(message, dict):
            raise GatewayError(status_code=400, detail=f"Message {i} is not an object: {type(message)}")
        if "role" not in message or "content" not in message:
            raise GatewayError(status_code=400, detail=f"Message {i} must contain 'role' and 'content'.")