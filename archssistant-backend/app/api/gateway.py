"""API Gateway: Routing Component

- Validates and normalizes incoming requests
- Delegates business logic to specialized services
- Provides normalized responses
"""

from datetime import datetime

from .models import ChatRequest, ChatResponse
from .exceptions import GatewayError
from ..server.dialogue_orchestrator import handle_message
from ..server.llm_service.llm_service import ApiKeyError
from ..config import get_logger


class ApiGateway:
    """API Gateway class for handling chat message processing.
    
    This class implements the API Gateway pattern, acting as a centralized entry point
    that validates requests, handles errors, and delegates business logic to specialized services.
    """
    
    def __init__(self):
        """Initialize the API Gateway with required dependencies."""
        self.logger = get_logger(__name__)
    
    def process_chat_message(self, request: ChatRequest) -> ChatResponse:
        """Processes a chat message through the Gateway.

        1. Validation of input
        2. Logging of request
        3. Delegation to the orchestrator
        4. Error handling
        5. Logging of response

        Args:
            request: Validated ChatRequest by Pydantic. Contains the complete conversation history.

        Returns:
            ChatResponse: Response from the system with message and conversational state.

        Raises:
            GatewayError: If an error occurs during processing.
                - status_code 400: Validation error
                - status_code 401: Authentication error
                - status_code 500: Internal server error
        """
        request_id = f"{datetime.now().isoformat()}"
        
        try:
            # 1. Validation of input
            self._validate_chat_request(request)
            self.logger.info(
                f"[{request_id}] Chat request received. "
                f"History: {len(request.history)} messages."
            )
            
            # 2. Delegation to the Orchestrator
            self.logger.debug(
                f"[{request_id}] Delegating to the Dialogue Orchestrator..."
            )
            result = handle_message(request.history)
            
            # 3. Logging of response
            self.logger.info(
                f"[{request_id}] Response generated successfully. "
                f"State: {result.get('state', {}).get('status', 'unknown')}"
            )
            
            return result
        
        except ApiKeyError as ake:
            self.logger.error(f"[{request_id}] LLM authentication error: {str(ake)}")
            raise GatewayError(
                status_code = 401,
                detail      = f"Authentication error with the LLM provider: {str(ake)}"
            )
        
        except Exception as e:
            self.logger.exception(
                f"[{request_id}] Uncontrolled internal error: {str(e)}"
            )
            raise GatewayError(
                status_code = 500,
                detail      = "Internal error processing the chat message."
            )
    
    def _validate_chat_request(self, request: ChatRequest) -> None:
        """Validates that the chat request meets the minimum requirements.

        Args:
            request: ChatRequest to validate.

        Raises:
            GatewayError: If validation fails (status_code=400).
        """
        # Validate that history is a list
        if not isinstance(request.history, list):
            raise GatewayError(
                status_code = 400,
                detail      = "The 'history' field must be an array of messages."
            )
        
        # Validate that history is not empty
        if len(request.history) == 0:
            raise GatewayError(
                status_code = 400,
                detail      = "The history cannot be empty. It must contain at least one message."
            )
        
        # Validate the basic structure of the messages
        for i, message in enumerate(request.history):
            if not isinstance(message, dict):
                raise GatewayError(
                    status_code = 400,
                    detail      = f"Message {i} is not an object: {type(message)}"
                )
            
            if 'role' not in message or 'content' not in message:
                raise GatewayError(
                    status_code = 400,
                    detail      = f"Message {i} must contain 'role' and 'content'."
                )
        
        self.logger.debug(f"Validation of request successful. {len(request.history)} valid messages.")