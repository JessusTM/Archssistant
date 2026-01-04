"""Centralized logging system configuration for Arch-Assistant.

This module provides:
- Consistent logging configuration across the entire application
- Handlers for console and file output
- Professional formatters with context
- Log file rotation
- Configurable severity levels

Usage:
    from app.core.logging_config import setup_logging
    setup_logging()
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional


# Logs directory
LOGS_DIR = Path(__file__).parent.parent.parent / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Log file paths
LOG_FILE_DEBUG = LOGS_DIR / 'debug.log'
LOG_FILE_INFO = LOGS_DIR / 'info.log'
LOG_FILE_ERROR = LOGS_DIR / 'error.log'

# Detailed format for debugging
DEBUG_FORMAT = (
    '%(asctime)s - %(name)s - %(levelname)s - '
    '[%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s'
)

# Compact format for production
PRODUCTION_FORMAT = (
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Format for log files
FILE_FORMAT = (
    '%(asctime)s | %(name)-30s | %(levelname)-8s | %(message)s'
)


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to console logs."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        """Formats the log record with colors."""
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
            )
        return super().format(record)


def setup_logging(
    debug_mode: bool = False,
    log_level: str = 'INFO'
) -> None:
    """Configures the logging system for the entire application.

    Creates handlers for:
    - Console: logs formatted with colors
    - debug.log file: all logs (DEBUG and above)
    - info.log file: INFO and above logs (without DEBUG)
    - error.log file: only ERROR and CRITICAL logs

    Args:
        debug_mode: If True, shows DEBUG logs in console and file.
        log_level: Minimum log level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')

    Example:
        setup_logging(debug_mode=True, log_level='DEBUG')
    """
    
    # Configure root level
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture all levels
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_level = logging.DEBUG if debug_mode else logging.INFO
    console_handler.setLevel(console_level)
    
    console_formatter = ColoredFormatter(
        DEBUG_FORMAT if debug_mode else PRODUCTION_FORMAT
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Debug file handler (all logs)
    if debug_mode:
        debug_handler = logging.handlers.RotatingFileHandler(
            LOG_FILE_DEBUG,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        debug_handler.setLevel(logging.DEBUG)
        debug_formatter = logging.Formatter(FILE_FORMAT)
        debug_handler.setFormatter(debug_formatter)
        root_logger.addHandler(debug_handler)
    
    # Info file handler (INFO and above)
    info_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE_INFO,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    info_handler.setLevel(logging.INFO)
    info_handler.addFilter(lambda record: record.levelno < logging.ERROR)
    info_formatter = logging.Formatter(FILE_FORMAT)
    info_handler.setFormatter(info_formatter)
    root_logger.addHandler(info_handler)
    
    # Error file handler (ERROR and CRITICAL)
    error_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE_ERROR,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(FILE_FORMAT)
    error_handler.setFormatter(error_formatter)
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
