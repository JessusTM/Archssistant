"""Paquete del motor de recomendación.

Exports:
	- `get_recommendation`: calcula top-3 arquitecturas según scoring.
"""
from .engine import get_recommendation

__all__ = ['get_recommendation']
