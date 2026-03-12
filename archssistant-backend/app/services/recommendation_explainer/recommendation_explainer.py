"""Recommendation Explainer.

Uses the LLM to generate descriptions and justifications for each recommended architecture.
"""

import json
import logging
from typing import Any
from app.services.elicitation_machine.llm_client import DeepSeekLLMClient


logger = logging.getLogger(__name__)


class RecommendationExplainer:
    """Generates auditable explanations (description + justification) for recommendations."""

    def __init__(self, llm_client: DeepSeekLLMClient | None = None) -> None:
        self.llm_client = llm_client or DeepSeekLLMClient()

    def generate_final_descriptions(
        self,
        project_description: str,
        recommendations: list[dict[str, Any]],
        history: list[dict[str, Any]],
        decision_table: dict[str, Any],
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
        conversation_history = "\n".join(
            [f"{msg['role'].upper()}: {msg['content']}" for msg in history]
        )

        decision_table_summary: dict[str, Any] = {
            "inferred_criteria": decision_table.get("inferred_criteria", {}),
            "architectures": [],
        }

        rows = decision_table.get("rows", [])
        rows_by_name: dict[str, Any] = {}
        for row in rows:
            name = row.get("architecture_name")
            if isinstance(name, str):
                rows_by_name[name] = row

        for rec in recommendations:
            name = rec.get("name")
            if not isinstance(name, str):
                continue
            row = rows_by_name.get(name, {})
            decision_table_summary["architectures"].append(
                {
                    "name": name,
                    "score": row.get("score", rec.get("score")),
                    "criteria_values": row.get("criteria_values", {}),
                }
            )

        decision_table_json = json.dumps(decision_table_summary, ensure_ascii=True)

        recommendation_names_list: list[str] = []
        for recommendation in recommendations:
            recommendation_names_list.append(recommendation["name"])
        recommendations_names = ", ".join(recommendation_names_list)

        prompt_template = self.llm_client.load_prompt(
            "generate_final_descriptions_prompt.txt"
        )
        system_prompt = prompt_template.format(
            project_description=project_description,
            conversation_history=conversation_history,
            decision_table=decision_table_json,
            recommendations_names=recommendations_names,
            architecture_1_name=recommendations[0]["name"]
            if len(recommendations) > 0
            else "Arquitectura 1",
            architecture_2_name=recommendations[1]["name"]
            if len(recommendations) > 1
            else "Arquitectura 2",
            architecture_3_name=recommendations[2]["name"]
            if len(recommendations) > 2
            else "Arquitectura 3",
        )

        messages = [{"role": "system", "content": system_prompt}]
        try:
            result = self.llm_client.call_json(messages, temperature=0.6)
            logger.debug(
                f"Architecture descriptions generated - keys: {list(result.keys())}"
            )
            return result
        except Exception as e:
            logger.error(
                f"Failed to generate architecture descriptions: {str(e)}", exc_info=True
            )
            logger.warning(
                "Returning default descriptions to continue recommendation flow"
            )
            default_descriptions: dict[str, dict[str, str]] = {}
            for rec in recommendations:
                default_descriptions[rec["name"]] = {
                    "description": f"{rec['name']} Architecture - Modular development system.",
                    "justification": "This architecture is suitable for your project based on the analyzed parameters.",
                }
            return default_descriptions
