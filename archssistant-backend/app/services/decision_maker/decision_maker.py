"""Decision Maker.

Implements deterministic evaluation rules over symbolic knowledge to produce
a ranked list of recommended architectures.
"""

from __future__ import annotations
from typing import Any
from app.core import get_logger
from app.services.symbolic_knowledge_base import VALUE_MAP, architectures


class DecisionMaker:
    """Scores candidate architectures and returns the top matches."""

    def __init__(self) -> None:
        self.architectures  = architectures
        self.value_map      = VALUE_MAP
        self.logger         = get_logger(__name__)

    def get_recommendation(self, user_answers: dict[str, str]) -> list[dict[str, Any]]:
        """Scores candidate architectures and returns the top 3 matches.
        
        Evaluates all architectures in the catalog against the user's
        inferred parameters using a scoring algorithm. Each parameter match
        contributes points based on how close the architecture's value is
        to the user's requirement.
        
        Args:
            user_answers: Dictionary mapping parameter names to their inferred values
            
        Returns:
            List of top 3 recommended architectures, each containing:
                - All original architecture attributes
                - score: Total match score
            Sorted by score in descending order
        """
        self.logger.debug(f"Calculating recommendations for {len(user_answers)} parameters")
        scored_architectures: list[dict[str, Any]] = []

        for arch in self.architectures:
            score = 0
            for parameter, user_answer in user_answers.items():
                arch_value = arch.get(parameter)
                user_score = self.value_map.get(user_answer)
                arch_score = self.value_map.get(arch_value)

                if user_score and arch_score:
                    difference = abs(user_score - arch_score)
                    if difference == 0:
                        score += 2
                    elif difference == 1:
                        score += 1

            scored_architectures.append({**arch, "score": score})

        scored_architectures.sort(key=lambda x: x["score"], reverse=True)
        top_3 = scored_architectures[:3]

        self.logger.info(f"Recommendations generated - top architectures: {[arch['name'] for arch in top_3]}")
        return top_3