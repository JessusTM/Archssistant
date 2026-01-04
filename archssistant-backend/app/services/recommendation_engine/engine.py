"""Recommendation Engine based on scoring.

Compares user-inferred classifications with a predefined architectures table
and assigns a similarity score.
"""

from .architecture_data import architectures, VALUE_MAP
from app.core import get_logger


class RecommendationEngine:
    """Engine for calculating architecture recommendations based on scoring.
    
    This class compares user requirements with predefined architectures
    and returns the top matches based on similarity scoring.
    """
    
    def __init__(self):
        """Initialize the Recommendation Engine."""
        self.architectures = architectures
        self.value_map = VALUE_MAP
        self.logger = get_logger(__name__)
    
    def get_recommendation(self, user_answers):
        """Calculates architecture recommendations from inferred parameters.

        Args:
            user_answers (dict[str, str]): Map `parameter -> classification` inferred by the
                orchestrator. Example values:
                - For `teamSize`: "Pequeño" | "Moderado" | "Grande" | "Alto"
                - For other parameters: "Baja" | "Moderada" | "Alta" | "Excelente"

        Behavior:
            - For each base architecture (see `architecture_data.architectures`), compares
              each parameter present in `user_answers`.
            - Converts categorical values to numeric scale with `VALUE_MAP`.
            - Sums score by proximity:
                - difference 0: +2
                - difference 1: +1
                - difference >1 or unmapped values: +0
            - Sorts from highest to lowest score.

        Returns:
            list[dict]: Up to 3 architectures (top-3), each as a dict that includes
                its attributes and an additional `score` (int) key.

        Notes:
            This engine is deterministic and doesn't use the LLM. If `VALUE_MAP` doesn't
            contain some value (e.g. new entries), that parameter doesn't contribute to the score.
        """
        self.logger.debug(
            f"Calculating recommendations for {len(user_answers)} parameters"
        )
        
        scored_architectures = []
        
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
            
            scored_architectures.append({**arch, 'score': score})
        
        scored_architectures.sort(key=lambda x: x['score'], reverse=True)
        top_3 = scored_architectures[:3]
        
        self.logger.info(
            f"Recommendations generated - top architectures: "
            f"{[arch['name'] for arch in top_3]}"
        )
        
        return top_3