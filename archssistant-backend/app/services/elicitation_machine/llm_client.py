"""LLM client for DeepSeek chat-completions.

Single responsibility:
- Send a chat-completions request and return parsed JSON content.
- Load prompt templates from the local prompt directory.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Optional
import requests


logger = logging.getLogger(__name__)


class DeepSeekLLMClient:
    """DeepSeek HTTP client that returns JSON objects from model output."""

    API_URL = "https://api.deepseek.com/v1/chat/completions"

    def __init__(self, prompt_dir: Optional[Path] = None) -> None:
        self.prompt_dir = prompt_dir or (Path(__file__).parent / "prompt")

    def load_prompt(self, filename: str) -> str:
        """Load a prompt template from disk.

        Args:
            filename: Name of the prompt template file

        Returns:
            Prompt template content as a string

        Raises:
            FileNotFoundError   : If the prompt file does not exist
            IOError             : If the file cannot be read
        """
        prompt_path = self.prompt_dir / filename
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def call_json(
        self, messages: list[dict[str, Any]], temperature: float = 0.2
    ) -> Any:
        """Call DeepSeek API and parse the returned message content as JSON.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature for the model (default: 0.2)

        Returns:
            Parsed JSON object from the API response

        Raises:
            PermissionError     : If API key is missing or invalid
            json.JSONDecodeError: If response is not valid JSON
            Exception           : For other API or network errors
        """
        api_key = self._get_api_key()
        request_body = self._build_request_body(messages, temperature)

        try:
            response = self._post_request(api_key, request_body)
            raw_content = self._extract_raw_content(response)
            parsed_json = self._parse_json_content(raw_content)
            return parsed_json
        except PermissionError:
            raise
        except json.JSONDecodeError as json_error:
            logger.error(
                f"Failed to parse JSON response from DeepSeek API: {str(json_error)}"
            )
            raise Exception(f"Error parsing API response: {str(json_error)}")
        except Exception as error:
            logger.error(f"Error calling DeepSeek API: {str(error)}", exc_info=True)
            raise Exception(f"Error al llamar a la API: {str(error)}")

    def _get_api_key(self) -> str:
        """Retrieves and validates the DeepSeek API key from environment.

        Returns:
            Validated API key string

        Raises:
            PermissionError: If API key is missing or appears to be a placeholder
        """
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            logger.error("DEEPSEEK_API_KEY not found in environment variables")
            raise PermissionError(
                "La clave de API no está configurada (DEEPSEEK_API_KEY)."
            )

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
            logger.error("DEEPSEEK_API_KEY appears to be a placeholder value")
            raise PermissionError(
                "La clave de API parece ser un placeholder. Configura DEEPSEEK_API_KEY en .env con tu clave real."
            )
        return api_key

    def _build_request_body(
        self, messages: list[dict[str, Any]], temperature: float
    ) -> dict[str, Any]:
        """Builds the request body for the DeepSeek API call.

        Args:
            messages    : List of message dictionaries
            temperature : Sampling temperature

        Returns:
            Dictionary with API request parameters
        """
        request_body = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }
        return request_body

    def _post_request(self, api_key: str, request_body: dict[str, Any]):
        """Sends a POST request to the DeepSeek API.

        Args:
            api_key     : DeepSeek API key for authentication
            request_body: Request payload dictionary

        Returns:
            Response object from requests library

        Raises:
            PermissionError : If authentication fails (401)
            Exception   : For other HTTP errors
        """
        response = requests.post(
            self.API_URL,
            json=request_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )
        if not response.ok:
            if response.status_code == 401:
                logger.error("DeepSeek API authentication failed (401)")
                raise PermissionError(
                    "Autenticación fallida con DeepSeek. Revisa tu DEEPSEEK_API_KEY."
                )
            logger.error(
                f"DeepSeek API request failed with status {response.status_code}"
            )
            raise Exception("Error en la API al llamar al servicio.")
        return response

    def _extract_raw_content(self, response) -> str:
        """Extracts the message content from the API response.

        Args:
            response: Response object from requests library

        Returns:
            Raw content string from the response

        Raises:
            Exception: If the expected content structure is not found
        """
        data = response.json()
        raw_content = data.get("choices", [{}])[0].get("message", {}).get("content")
        if not raw_content:
            logger.error("DeepSeek API response missing expected content")
            raise Exception("La respuesta de la API no contiene el contenido esperado.")
        return raw_content

    def _parse_json_content(self, raw_content: str) -> Any:
        """Parses JSON content from the raw response string.

        Args:
            raw_content: JSON string to parse

        Returns:
            Parsed JSON object (dict, list, etc.)

        Raises:
            json.JSONDecodeError: If the content is not valid JSON
        """
        parsed_json = json.loads(raw_content)
        return parsed_json
