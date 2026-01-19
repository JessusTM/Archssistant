"""Elicitation Machine.

Encapsulates the interview loop behaviors driven by the LLM:
- interpret user's answer for a parameter
- generate the next question (or clarification)
"""

from __future__ import annotations
import json
from typing import Any
from app.core import get_logger
from .llm_client import DeepSeekLLMClient


class ElicitationMachine:
    """LLM-driven elicitation of project variables."""

    def __init__(self, llm_client: DeepSeekLLMClient | None = None) -> None:
        self.llm_client = llm_client or DeepSeekLLMClient()
        self.logger     = get_logger(__name__)

    def interpret_user_answer(self, question_text: str, user_answer: str, parameter_to_infer: str) -> dict[str, Any]:
        prompt_template = self.llm_client.load_prompt("interpret_user_answer_prompt.txt")
        system_prompt   = prompt_template.format(
            question_text       = question_text,
            user_answer         = user_answer,
            parameter_to_infer  = parameter_to_infer,
        )
        messages = [{"role": "system", "content": system_prompt}]
        return self.llm_client.call_json(messages, temperature=0.0)

    def generate_next_question(
        self,
        history                 : list[dict[str, Any]],
        remaining_params        : list[str],
        last_interpretation     : dict[str, Any] | None,
        is_clarification_needed : bool = False,
    ) -> dict[str, Any]:
        simplified_history: list[dict[str, Any]] = []
        for msg in history[-6:]:
            simplified_entry = {
                "role"      : msg["role"],
                "content"   : msg["content"],
            }
            simplified_history.append(simplified_entry)

        prompt_template = self.llm_client.load_prompt("generate_next_question_prompt.txt")
        system_prompt   = prompt_template.format(
            history                 = json.dumps(simplified_history),
            remaining_params        = ", ".join(remaining_params),
            last_interpretation     = json.dumps(last_interpretation),
            is_clarification_needed = is_clarification_needed,
        )

        messages = [{"role": "system", "content": system_prompt}]
        return self.llm_client.call_json(messages, temperature=0.6)