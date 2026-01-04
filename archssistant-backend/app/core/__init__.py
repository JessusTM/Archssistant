"""Core module for Arch-Assistant.

Contains global configurations for:
- Centralized logging
- Environment variables
- Application constants
"""

# Import configuration (this initializes logging automatically)
from .config import config, Config

# Import logging utilities
from .logging_config import setup_logging, get_logger
from .logging_utils import (
    log_function_call,
    log_performance,
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
    'log_function_call',
    'log_performance',
    'log_orchestration_event',
    'log_llm_call',
    'log_recommendation_event',
    'log_api_request'
]
