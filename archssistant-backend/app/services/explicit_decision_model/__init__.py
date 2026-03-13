"""Explicit Decision Model component.

Provides the explicit architecture catalog and the logic that instantiates
decision tables from inferred criteria.
"""

from .architecture_catalog import VALUE_MAP, architectures
from .model import ExplicitDecisionModel

__all__ = ["ExplicitDecisionModel", "architectures", "VALUE_MAP"]
