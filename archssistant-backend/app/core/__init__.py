"""Core module for Arch-Assistant.

Contains global configurations for:
- Centralized logging
- Environment variables
- Application constants
"""

from .config import config, Config
from .logging_config import setup_logging, get_logger
from .logging_utils import (
    log_orchestration_event,
    log_llm_call,
    log_recommendation_event,
    log_api_request
)

__all__ = [
    'config',
    'Config',
    'setup_logging',
    'get_logger',
    'log_orchestration_event',
    'log_llm_call',
    'log_recommendation_event',
    'log_api_request'
]