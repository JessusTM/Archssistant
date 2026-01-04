"""Centralized logging system configuration for Arch-Assistant.

This module provides:
- Consistent logging configuration across the entire application
- Handlers for console and file output
- Professional formatters with colors (using colorlog)
- Log file rotation
- Configurable severity levels

Usage:
    from app.core.logging_config import setup_logging
    setup_logging(log_level='INFO')
"""

import logging
import logging.handlers
import colorlog
from pathlib import Path
from typing import Optional, Callable


# ------ LOGS DIRECTORY ------
LOGS_DIR = Path(__file__).parent.parent.parent / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

LOG_FILE_DEBUG  = LOGS_DIR / 'debug.log'
LOG_FILE_INFO   = LOGS_DIR / 'info.log'
LOG_FILE_ERROR  = LOGS_DIR / 'error.log'

# ------ FORMAT ------
DEBUG_FORMAT = (
    '%(asctime)s - %(name)s - %(log_color)s%(levelname)s%(reset)s - '
    '[%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s'
)

PRODUCTION_FORMAT = (
    '%(asctime)s - %(name)s - %(log_color)s%(levelname)s%(reset)s - %(message)s'
)

FILE_FORMAT = (
    '%(asctime)s | %(name)-30s | %(levelname)-8s | %(message)s'
)


def _parse_log_level(log_level: str) -> int:
    """Converts log level string to logging constant.
    
    Args:
        log_level: Log level string ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    
    Returns:
        int: Logging level constant
    
    Raises:
        ValueError: If log_level is invalid
    """
    level_map = {
        'DEBUG'     : logging.DEBUG,
        'INFO'      : logging.INFO,
        'WARNING'   : logging.WARNING,
        'ERROR'     : logging.ERROR,
        'CRITICAL'  : logging.CRITICAL
    }
    
    upper_level = log_level.upper()
    if upper_level not in level_map:
        raise ValueError(
            f"Invalid log level '{log_level}'. "
            f"Must be one of: {list(level_map.keys())}"
        )
    
    return level_map[upper_level]


def _create_file_handler(
    log_file: Path,
    level: int,
    filter_func: Optional[Callable] = None
) -> logging.handlers.RotatingFileHandler:
    """Creates a rotating file handler with common configuration.
    
    Args:
        log_file    : Path to the log file
        level       : Logging level for this handler
        filter_func : Optional filter function to apply to records
    
    Returns:
        RotatingFileHandler: Configured file handler
    """
    handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes    = 10 * 1024 * 1024,  # 10 MB
        backupCount = 5,
        encoding    = 'utf-8'
    )
    handler.setLevel(level)
    
    if filter_func:
        handler.addFilter(filter_func)
    
    formatter = logging.Formatter(FILE_FORMAT)
    handler.setFormatter(formatter)
    
    return handler


def setup_logging(log_level: str = 'INFO') -> None:
    """Configures the logging system for the entire application.

    Creates handlers for:
    - Console: logs formatted with colors (using colorlog)
      - Level controlled by log_level parameter
      - Uses DEBUG_FORMAT if log_level='DEBUG', otherwise PRODUCTION_FORMAT
    - debug.log file: all logs (DEBUG and above) - only created if log_level='DEBUG'
    - info.log file : INFO and WARNING logs
    - error.log file: ERROR and CRITICAL logs

    Args:
        log_level: Minimum log level for console ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
                  Default: 'INFO'
                  File handlers use fixed levels regardless of this parameter

    Example:
        setup_logging(log_level='DEBUG')  # Development
        setup_logging(log_level='INFO')   # Production
    """
    
    # Parse and validate log level
    console_level = _parse_log_level(log_level)
    is_debug_mode = (console_level == logging.DEBUG)
    
    # Configure root level
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture all levels
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler with colors (using colorlog)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    
    # Choose format based on log level
    console_format = DEBUG_FORMAT if is_debug_mode else PRODUCTION_FORMAT
    
    # Use colorlog for automatic color detection and TTY safety
    console_formatter = colorlog.ColoredFormatter(
        console_format,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Debug file handler (all logs) - only in debug mode
    if is_debug_mode:
        debug_handler = _create_file_handler(LOG_FILE_DEBUG, logging.DEBUG)
        root_logger.addHandler(debug_handler)
    
    # Info file handler (INFO and WARNING)
    info_handler = _create_file_handler(
        LOG_FILE_INFO,
        logging.INFO,
        filter_func=lambda record: record.levelno < logging.ERROR
    )
    root_logger.addHandler(info_handler)
    
    # Error file handler (ERROR and CRITICAL)
    error_handler = _create_file_handler(LOG_FILE_ERROR, logging.ERROR)
    root_logger.addHandler(error_handler)
    
    # Initialization log
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("Logging system initialized")
    logger.info(f"Logs directory: {LOGS_DIR.absolute()}")
    logger.info(f"Console level: {logging.getLevelName(console_level)}")
    logger.info("=" * 80)


def get_logger(name: str) -> logging.Logger:
    """Gets a configured logger for a module.

    Args:
        name: Module name (typically __name__)

    Returns:
        logging.Logger: Configured logger

    Example:
        from app.core.logging_config import get_logger
        logger = get_logger(__name__)
        logger.info("Informative message")
    """
    return logging.getLogger(name)