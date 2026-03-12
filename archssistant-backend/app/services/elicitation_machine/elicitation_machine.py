"""Elicitation Machine.

Encapsulates the interview loop behaviors driven by the LLM:
- interpret user's answer for a parameter
- generate the next question (or clarification)
"""

import logging
import json
from typing import Any
from .llm_client import DeepSeekLLMClient


logger = logging.getLogger(__name__)


class ElicitationMachine:
    """LLM-driven elicitation of project variables."""

    def __init__(self, llm_client: DeepSeekLLMClient | None = None) -> None:
        self.llm_client = llm_client or DeepSeekLLMClient()

    def interpret_user_answer(
        self, question_text: str, user_answer: str, parameter_to_infer: str
    ) -> dict[str, Any]:
        """Interprets the user's answer to classify a parameter value.

        Uses an LLM to analyze the user's response and determine the
        appropriate classification for the target parameter.

        Args:
            question_text: The question that was asked to the user
            user_answer: The user's response text
            parameter_to_infer: The parameter name being inferred

        Returns:
            Dictionary with classification result, typically containing:
                - classification: Inferred parameter value or 'UNCERTAIN'
                - confidence: Confidence level (optional)
        """
        prompt_template = self.llm_client.load_prompt(
            "interpret_user_answer_prompt.txt"
        )
        system_prompt = prompt_template.format(
            question_text=question_text,
            user_answer=user_answer,
            parameter_to_infer=parameter_to_infer,
        )
        messages = [{"role": "system", "content": system_prompt}]
        return self.llm_client.call_json(messages, temperature=0.0)

    def generate_next_question(
        self,
        history: list[dict[str, Any]],
        remaining_params: list[str],
        last_interpretation: dict[str, Any] | None,
        is_clarification_needed: bool = False,
    ) -> dict[str, Any]:
        """Generates the next question to ask the user.

        Uses an LLM to generate contextually appropriate questions based on
        the conversation history, remaining parameters to infer, and whether
        clarification is needed from the previous answer.

        Args:
            history: Recent conversation messages (last 6 messages are used)
            remaining_params: List of parameter names still to be inferred
            last_interpretation: Result from interpreting the last answer, if any
            is_clarification_needed: Whether a clarification question is needed

        Returns:
            Dictionary containing:
                - full_response_text: The complete question text
                - parameter_to_infer: The parameter this question targets
                - question_for_user: Formatted question text
        """
        simplified_history: list[dict[str, Any]] = []
        for msg in history[-6:]:
            simplified_entry = {
                "role": msg["role"],
                "content": msg["content"],
            }
            simplified_history.append(simplified_entry)

        prompt_template = self.llm_client.load_prompt(
            "generate_next_question_prompt.txt"
        )
        system_prompt = prompt_template.format(
            history=json.dumps(simplified_history),
            remaining_params=", ".join(remaining_params),
            last_interpretation=json.dumps(last_interpretation),
            is_clarification_needed=is_clarification_needed,
        )

        messages = [{"role": "system", "content": system_prompt}]
        return self.llm_client.call_json(messages, temperature=0.6)
