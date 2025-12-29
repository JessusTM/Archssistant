"""Módulo de configuración de Arch-Assistant.

Contiene configuraciones globales para:
- Logging centralizado
- Variables de entorno
- Constantes de la aplicación
"""

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
    'setup_logging',
    'get_logger',
    'log_function_call',
    'log_performance',
    'log_orchestration_event',
    'log_llm_call',
    'log_recommendation_event',
    'log_api_request'
]
