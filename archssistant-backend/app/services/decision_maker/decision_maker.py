"""Decision Maker.

Implements deterministic evaluation rules over symbolic knowledge to produce
a ranked list of recommended architectures.
"""

import logging
from typing import Any


logger = logging.getLogger(__name__)


class DecisionMaker:
    """Scores candidate architectures and returns the top matches."""

    def __init__(self) -> None:
        # Local mapping so this component depends only on the decision table instance.
        self.value_map = {
            "Low": 1,
            "Small": 2,
            "Moderate": 3,
            "High": 4,
            "Large": 4,
            "Excellent": 5,
        }

    def get_recommendation(
        self, decision_table: dict[str, Any], top_n: int = 3
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Score a decision table and return recommendations.

        The input table is expected to be already instantiated (values filled).
        This method enriches the same table with numeric scores.

        Args:
            decision_table: Instantiated decision table with inferred criteria and rows
            top_n: Number of top architectures to return

        Returns:
            (recommendations, evaluated_decision_table)

            recommendations: Top N architectures with `score` added
            evaluated_decision_table: Same table enriched with per-architecture `score`
        """
        inferred_criteria: dict[str, str] = decision_table.get("inferred_criteria", {})
        rows: list[dict[str, Any]] = decision_table.get("rows", [])

        logger.debug(
            f"Calculating recommendations for {len(inferred_criteria)} parameters"
        )

        for row in rows:
            score = 0
            criteria_values: dict[str, Any] = row.get("criteria_values", {})

            for parameter, user_answer in inferred_criteria.items():
                arch_value = criteria_values.get(parameter)
                user_score = self.value_map.get(user_answer)
                if not isinstance(arch_value, str):
                    continue

                arch_score = self.value_map.get(arch_value)

                if user_score is None or arch_score is None:
                    continue

                difference = abs(user_score - arch_score)
                if difference == 0:
                    score += 2
                elif difference == 1:
                    score += 1

            row["score"] = score

        rows.sort(key=lambda r: int(r.get("score") or 0), reverse=True)
        top_rows = rows[:top_n]

        recommendations: list[dict[str, Any]] = []
        for row in top_rows:
            arch = row.get("architecture") or {}
            recommendations.append({**arch, "score": row.get("score", 0)})

        logger.info(
            f"Recommendations generated - top architectures: {[r['name'] for r in recommendations]}"
        )
        return recommendations, decision_table
