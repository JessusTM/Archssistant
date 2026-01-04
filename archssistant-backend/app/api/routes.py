"""Definition of routes and endpoints of the Arch-Assistant API.

Define the HTTP endpoints that expose the application. Here, each endpoint
acts as an entry point for client requests, delegating all validation and
validation and processing to the API Gateway.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from .models import ChatRequest, ChatResponse
from .gateway import ApiGateway
from .exceptions import GatewayError

router  = APIRouter(prefix='/api', tags=['chat'])
gateway = ApiGateway() # Create a single instance of the API Gateway


@router.post('/chat', response_model=ChatResponse)
def chat(request: ChatRequest) -> Dict[str, Any]:
    """
    Entry point for chat requests. All validation, logging, and processing logic is delegated to the API Gateway.

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
        This function acts as an HTTP adapter that:
        1. Receives the validated HTTP request by FastAPI/Pydantic
        2. Delegates to the Gateway for complete processing
        3. Converts Gateway exceptions to HTTPException
        4. Returns a normalized response
    """
    try:
        # Delegate to the API Gateway for complete processing
        result = gateway.process_chat_message(request)
        return result
    
    except GatewayError as ge:
        # Convert GatewayError to HTTPException
        # The GatewayError already contains status_code and detail appropriate
        raise HTTPException(
            status_code=ge.status_code,
            detail=ge.detail
        ) from ge
    
    except Exception as error:
        # Capture unexpected errors that were not handled by the Gateway
        raise HTTPException(
            status_code=500,
            detail='Unexpected internal error processing the message...'
        ) from error