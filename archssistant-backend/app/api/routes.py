"""Definition of routes and endpoints of the Archssistant API.

HTTP adapter layer:
- Validates minimal request shape (history)
- Delegates business logic to the Orchestrator
- Translates domain exceptions into HTTP status codes
"""

import os
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.schemas import ChatRequest, ChatResponse
from app.services.orchestrator import Orchestrator


router = APIRouter(prefix="/api", tags=["chat"])


def get_orchestrator() -> Orchestrator:
    return Orchestrator()


def require_deepseek_key() -> None:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise PermissionError("La clave de API no está configurada (DEEPSEEK_API_KEY).")

    placeholder = api_key.strip().lower()
    invalid_placeholders = {
        "",
        "your_deepseek_api_key_here",
        "sk-replace_me",
        "tu_clave_api_aqui",
    }
    if placeholder in invalid_placeholders or placeholder.startswith(
        "tu_clave_api_aqui"
    ):
        raise PermissionError(
            "La clave de API parece ser un placeholder. Configura DEEPSEEK_API_KEY en .env con tu clave real."
        )


@router.post("/chat", response_model=ChatResponse)
def chat(
    _: Annotated[None, Depends(require_deepseek_key)],
    request: ChatRequest,
    orchestrator: Annotated[Orchestrator, Depends(get_orchestrator)],
) -> dict:
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
            - 401: Authentication error (invalid API key for LLM)
            - 500: Internal server error

        RequestValidationError:
            - 422: Invalid request body (validation failed)

    Notes:
        This function acts as an HTTP adapter that keeps orchestration and domain logic
        inside `app.services.orchestrator`.
    """
    history_dicts: list[dict] = []
    for message in request.history:
        history_dicts.append(message.model_dump())

    result = orchestrator.handle_message(history_dicts)
    return result
