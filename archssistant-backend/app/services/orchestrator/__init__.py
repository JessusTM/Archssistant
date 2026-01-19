"""Orchestrator component.

Coordinates the conversation flow across:
- ElicitationMachine
- SymbolicKnowledgeBase (via DecisionMaker)
- RecommendationExplainer
"""

from .orchestrator import Orchestrator

__all__ = ["Orchestrator"]