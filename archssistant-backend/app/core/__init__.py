"""Core module for Arch-Assistant.

Contains global configurations for:
- Centralized logging
- Environment variables
- Application constants
"""

from .config import config, Config

__all__ = [
    "config",
    "Config",
]
