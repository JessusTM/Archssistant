"""API module for Arch-Assistant.

This package contains HTTP route definitions, request/response models,
and endpoint configuration for the application.
"""

from .routes import router

__all__ = ["router"]
