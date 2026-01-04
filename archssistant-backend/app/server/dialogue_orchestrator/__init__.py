"""Paquete de orquestación de diálogo.

Exports:
	- `handle_message`: punto de entrada del flujo conversacional.
"""
from .orchestrator import handle_message

__all__ = ['handle_message']
