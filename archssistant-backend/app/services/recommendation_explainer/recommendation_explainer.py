"""Recommendation Explainer.

Uses the LLM to generate descriptions and justifications for each recommended architecture.
"""

from __future__ import annotations
from typing import Any
from app.core import get_logger
from app.services.elicitation_machine.llm_client import DeepSeekLLMClient


class RecommendationExplainer:
    """Generates auditable explanations (description + justification) for recommendations."""

    def __init__(self, llm_client: DeepSeekLLMClient | None = None) -> None:
        self.llm_client = llm_client or DeepSeekLLMClient()
        self.logger     = get_logger(__name__)

    def generate_final_descriptions(
        self,
        project_description : str,
        recommendations     : list[dict[str, Any]],
        history             : list[dict[str, Any]],
    ) -> dict[str, dict[str, str]]:
        """Generates descriptions and justifications for recommended architectures.
        
        Uses an LLM to create personalized descriptions and justifications
        for each recommended architecture based on the project description
        and conversation history.
        
        Args:
            project_description : User's project description
            recommendations     : List of recommended architectures with scores
            history             : Complete conversation history
            
        Returns:
            Dictionary mapping architecture names to dictionaries containing:
                - description   : Detailed description of the architecture
                - justification : Explanation of why it's recommended
            
        Note:
            If LLM call fails, returns default descriptions to allow the
            recommendation flow to continue.
        """
        conversation_history = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}" 
            for msg in history
        ])

        recommendation_names_list: list[str] = []
        for recommendation in recommendations:
            recommendation_names_list.append(recommendation["name"])
        recommendations_names = ", ".join(recommendation_names_list)

        prompt_template = self.llm_client.load_prompt("generate_final_descriptions_prompt.txt")
        system_prompt   = prompt_template.format(
            project_description     = project_description,
            conversation_history    = conversation_history,
            recommendations_names   = recommendations_names,
            architecture_1_name     = recommendations[0]["name"] if len(recommendations) > 0 else "Arquitectura 1",
            architecture_2_name     = recommendations[1]["name"] if len(recommendations) > 1 else "Arquitectura 2",
            architecture_3_name     = recommendations[2]["name"] if len(recommendations) > 2 else "Arquitectura 3",
        )

        messages = [{"role": "system", "content": system_prompt}]
        try:
            result = self.llm_client.call_json(messages, temperature=0.6)
            self.logger.debug(f"Architecture descriptions generated - keys: {list(result.keys())}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to generate architecture descriptions: {str(e)}", exc_info=True)
            self.logger.warning("Returning default descriptions to continue recommendation flow")
            default_descriptions: dict[str, dict[str, str]] = {}
            for rec in recommendations:
                default_descriptions[rec["name"]] = {
                    "description"   : f"{rec['name']} Architecture - Modular development system.",
                    "justification" : "This architecture is suitable for your project based on the analyzed parameters.",
                }
            return default_descriptions