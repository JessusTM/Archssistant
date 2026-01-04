"""LLM Service: integration with DeepSeek for classification and generation.

This module encapsulates 3 capabilities (all via `call_api`):
- `interpret_user_answer`: classifies a user response into allowed categories.
- `generate_next_question`: produces the next strategic question (or clarification).
- `generate_final_descriptions`: generates description and justification per architecture.

Configuration:
- Requires environment variable `DEEPSEEK_API_KEY`.

Technical note:
- `call_api` is declared as `async`, but currently uses `requests` (blocking).
  Kept this way to not alter logic; in high loads it might be convenient to migrate
  to an async HTTP client.
"""

import requests
import json
import os
from pathlib import Path

from app.api.exceptions import ApiKeyError


class LLMService:
    """Service for interacting with the DeepSeek LLM API.
    
    This class handles all LLM-related operations including interpretation,
    question generation, and description generation.
    """
    
    API_URL = 'https://api.deepseek.com/v1/chat/completions'
    
    def __init__(self):
        """Initialize the LLM Service."""
        self.prompt_dir = Path(__file__).parent / 'prompt'
    
    def load_prompt(self, prompt_filename):
        """Loads a prompt from a text file.
        
        Args:
            prompt_filename (str): Prompt file name (e.g. 'interpret_user_answer_prompt.txt')
        
        Returns:
            str: Prompt content
        
        Raises:
            FileNotFoundError: If the prompt file doesn't exist
        """
        prompt_path = self.prompt_dir / prompt_filename
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def call_api(self, messages, temperature=0.2):
        """Makes a call to the DeepSeek API and parses content as JSON.

        Args:
            messages (list[dict]): List of Chat Completions-style messages, for example:
              [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
              This service normally sends only a `system` message with instructions.
            temperature (float, optional): Model randomness control. Low values
              favor determinism. Default 0.2.

        Behavior:
            - Reads `DEEPSEEK_API_KEY` from environment variables.
            - Rejects common placeholders to avoid confusion in deployments.
            - Sends request to `API_URL` requesting `response_format=json_object`.
            - Takes `choices[0].message.content` and interprets it as JSON (string).

        Returns:
            dict | list: Parsed JSON object from the `content` returned by the model.

        Raises:
            ApiKeyError: If API key doesn't exist, seems like placeholder, or server responds 401.
            Exception: For network errors, non-OK responses, missing content, or invalid JSON.

        Notes:
            This function is synchronous and uses `requests.post` (blocking).
        """
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            raise ApiKeyError('La clave de API no está configurada (DEEPSEEK_API_KEY).')

        placeholder = api_key.strip().lower()
        if placeholder in {"", "your_deepseek_api_key_here", "sk-replace_me", "tu_clave_api_aqui"} or placeholder.startswith("tu_clave_api_aqui"):
            raise ApiKeyError('La clave de API parece ser un placeholder. Configura DEEPSEEK_API_KEY en .env con tu clave real.')

        request_body = {
            'model': 'deepseek-chat',
            'messages': messages,
            'temperature': temperature,
            'response_format': {'type': 'json_object'}
        }

        try:
            response = requests.post(
                self.API_URL,
                json=request_body,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {api_key}'
                }
            )

            if not response.ok:
                if response.status_code == 401:
                    raise ApiKeyError('Autenticación fallida con DeepSeek. Revisa tu DEEPSEEK_API_KEY.')
                raise Exception('Error en la API al llamar al servicio.')

            data = response.json()
            raw_content = data.get('choices', [{}])[0].get('message', {}).get('content')

            if not raw_content:
                raise Exception('La respuesta de la API no contiene el contenido esperado.')

            return json.loads(raw_content)

        except ApiKeyError:
            raise
        except Exception as error:
            raise Exception(f"Error al llamar a la API: {str(error)}")
    
    def interpret_user_answer(self, question_text, user_answer, parameter_to_infer):
        """Classifies the user's response for a specific parameter.

        Args:
            question_text (str): Question previously asked to the user (context).
            user_answer (str): User's textual response.
            parameter_to_infer (str): Name of parameter to infer (e.g. "scalability",
              "teamSize", etc.).

        Behavior:
            - Builds a classification prompt (not conversational) with allowed categories.
            - If response is ambiguous or user declares ignorance, must produce
              `classification == "UNCERTAIN"`.

        Returns:
            dict: JSON object with keys:
              - `classification`: str (one of allowed categories or "UNCERTAIN")
              - `confidence`: "high" | "medium" | "low"
              - `reasoning`: str (short phrase justifying)

        Raises:
            ApiKeyError / Exception: Propagated from `call_api`.
        """
        prompt_template = self.load_prompt('interpret_user_answer_prompt.txt')
        system_prompt   = prompt_template.format(
            question_text       = question_text,
            user_answer         = user_answer,
            parameter_to_infer  = parameter_to_infer
        )

        messages = [{'role': 'system', 'content': system_prompt}]
        return self.call_api(messages, 0.0)
    
    def generate_next_question(self, history, remaining_params, last_interpretation, is_clarification_needed=False):
        """Generates the next interaction (confirmation + question or clarification).

        Args:
            history (list[dict]): Complete conversational history. Uses a window
              of the last 6 messages for context.
            remaining_params (list[str]): Parameters not yet inferred; model decides which
              is most strategic to ask next.
            last_interpretation (dict | None): Previous result from `interpret_user_answer`.
              If exists, model can confirm what was understood before asking.
            is_clarification_needed (bool, optional): If `True`, requests clarification
              about the SAME parameter (simplifying the question). Default `False`.

        Returns:
            dict: JSON object with:
              - `parameter_to_infer`: str
              - `question_for_user`: str (only the question)
              - `full_response_text`: str (confirmation + question/clarification)

        Raises:
            ApiKeyError / Exception: Propagated from `call_api`.
        """
        simplified_history = [
            {'role': msg['role'], 'content': msg['content']}
            for msg in history[-6:]
        ]

        prompt_template = self.load_prompt('generate_next_question_prompt.txt')
        system_prompt   = prompt_template.format(
            history                 = json.dumps(simplified_history),
            remaining_params        = ', '.join(remaining_params),
            last_interpretation     = json.dumps(last_interpretation),
            is_clarification_needed = is_clarification_needed
        )

        messages = [{'role': 'system', 'content': system_prompt}]
        return self.call_api(messages, 0.6)
    
    def generate_final_descriptions(self, project_description, recommendations, history):
        """Generates description and justification per recommended architecture.

        Args:
            project_description (str): Initial project description from user.
            recommendations (list[dict]): List of recommended architectures (dicts). Each
              dict is expected to have at least the `name` key.
            history (list[dict]): Conversational history. Currently not used for the
              prompt, but kept in signature for orchestrator compatibility.

        Behavior:
            - Asks LLM to return a JSON whose keys are EXACTLY the names
              of recommended architectures.
            - On error (API/network/parse), returns default descriptions to not
              interrupt recommendation flow.

        Returns:
            dict[str, dict]: Map:
              {
                "Architecture Name": {
                  "description": "...",
                  "justification": "..."
                },
                ...
              }

        Side Effects:
            Prints debug/error logs to stdout.
        """
        recommendations_names = ', '.join([rec['name'] for rec in recommendations])

        prompt_template = self.load_prompt('generate_final_descriptions_prompt.txt')
        system_prompt   = prompt_template.format(
            project_description     = project_description,
            recommendations_names   = recommendations_names,
            architecture_1_name     = recommendations[0]['name'] if len(recommendations) > 0 else 'Arquitectura 1',
            architecture_2_name     = recommendations[1]['name'] if len(recommendations) > 1 else 'Arquitectura 2',
            architecture_3_name     = recommendations[2]['name'] if len(recommendations) > 2 else 'Arquitectura 3'
        )

        messages = [{'role': 'system', 'content': system_prompt}]

        try:
            result = self.call_api(messages, 0.6)
            print(f"DEBUG LLM: Descripciones generadas: {result}")
            return result
        except Exception as e:
            print(f"ERROR al generar descripciones: {e}")
            # Return default descriptions
            default_descriptions = {}
            for rec in recommendations:
                default_descriptions[rec['name']] = {
                    'description': f"Arquitectura {rec['name']} - Sistema de desarrollo modular.",
                    'justification': "Esta arquitectura es adecuada para tu proyecto según los parámetros analizados."
                }
            return default_descriptions