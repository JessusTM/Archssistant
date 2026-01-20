"""Symbolic Knowledge Base component.

Holds static / symbolic knowledge used for decision making (rules, catalog, mappings).
"""

from .architecture_catalog import architectures, VALUE_MAP

__all__ = ["architectures", "VALUE_MAP"]