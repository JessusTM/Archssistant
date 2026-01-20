"""LLM client for DeepSeek chat-completions.

Single responsibility:
- Send a chat-completions request and return parsed JSON content.
- Load prompt templates from the local prompt directory.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional
import requests
from app.api.exceptions import ApiKeyError
from app.core import get_logger


class DeepSeekLLMClient:
    """DeepSeek HTTP client that returns JSON objects from model output."""

    API_URL = "https://api.deepseek.com/v1/chat/completions"

    def __init__(self, prompt_dir: Optional[Path] = None) -> None:
        self.prompt_dir = prompt_dir or (Path(__file__).parent / "prompt")
        self.logger     = get_logger(__name__)

    def load_prompt(self, filename: str) -> str:
        """Load a prompt template from disk (UTF-8)."""
        prompt_path = self.prompt_dir / filename
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def call_json(self, messages: list[dict[str, Any]], temperature: float = 0.2) -> Any:
        """Call DeepSeek and parse the returned message content as JSON."""
        api_key = self._get_api_key()
        request_body = self._build_request_body(messages, temperature)

        try:
            response    = self._post_request(api_key, request_body)
            raw_content = self._extract_raw_content(response)
            parsed_json = self._parse_json_content(raw_content)
            return parsed_json
        except ApiKeyError:
            raise
        except json.JSONDecodeError as json_error:
            self.logger.error(f"Failed to parse JSON response from DeepSeek API: {str(json_error)}")
            raise Exception(f"Error parsing API response: {str(json_error)}")
        except Exception as error:
            self.logger.error(f"Error calling DeepSeek API: {str(error)}", exc_info=True)
            raise Exception(f"Error al llamar a la API: {str(error)}")

    def _get_api_key(self) -> str:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            self.logger.error("DEEPSEEK_API_KEY not found in environment variables")
            raise ApiKeyError("La clave de API no está configurada (DEEPSEEK_API_KEY).")

        placeholder             = api_key.strip().lower()
        invalid_placeholders    = {
            "", 
            "your_deepseek_api_key_here", 
            "sk-replace_me", 
            "tu_clave_api_aqui"
        }
        if placeholder in invalid_placeholders or placeholder.startswith("tu_clave_api_aqui"):
            self.logger.error("DEEPSEEK_API_KEY appears to be a placeholder value")
            raise ApiKeyError(
                "La clave de API parece ser un placeholder. Configura DEEPSEEK_API_KEY en .env con tu clave real."
            )
        return api_key

    def _build_request_body(self, messages: list[dict[str, Any]], temperature: float) -> dict[str, Any]:
        request_body = {
            "model"             : "deepseek-chat",
            "messages"          : messages,
            "temperature"       : temperature,
            "response_format"   : {"type": "json_object"},
        }
        return request_body

    def _post_request(self, api_key: str, request_body: dict[str, Any]):
        response = requests.post(
            self.API_URL,
            json    = request_body,
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        )
        if not response.ok:
            if response.status_code == 401:
                self.logger.error("DeepSeek API authentication failed (401)")
                raise ApiKeyError("Autenticación fallida con DeepSeek. Revisa tu DEEPSEEK_API_KEY.")
            self.logger.error(f"DeepSeek API request failed with status {response.status_code}")
            raise Exception("Error en la API al llamar al servicio.")
        return response

    def _extract_raw_content(self, response) -> str:
        data        = response.json()
        raw_content = data.get("choices", [{}])[0].get("message", {}).get("content")
        if not raw_content:
            self.logger.error("DeepSeek API response missing expected content")
            raise Exception("La respuesta de la API no contiene el contenido esperado.")
        return raw_content

    def _parse_json_content(self, raw_content: str) -> Any:
        parsed_json = json.loads(raw_content)
        return parsed_json