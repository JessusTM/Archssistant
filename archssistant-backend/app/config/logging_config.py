"""Configuración centralizada del sistema de logging para Arch-Assistant.

Este módulo proporciona:
- Configuración de logging consistente en toda la aplicación
- Handlers para consola y archivo
- Formatters profesionales con contexto
- Rotación de archivos de log
- Niveles de severidad configurables

Uso:
    from app.config.logging_config import setup_logging
    setup_logging()
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional


# Directorio de logs
LOGS_DIR = Path(__file__).parent.parent.parent / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Rutas de archivos de log
LOG_FILE_DEBUG = LOGS_DIR / 'debug.log'
LOG_FILE_INFO = LOGS_DIR / 'info.log'
LOG_FILE_ERROR = LOGS_DIR / 'error.log'

# Formato detallado para debugging
DEBUG_FORMAT = (
    '%(asctime)s - %(name)s - %(levelname)s - '
    '[%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s'
)

# Formato compacto para producción
PRODUCTION_FORMAT = (
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Formato para archivo
FILE_FORMAT = (
    '%(asctime)s | %(name)-30s | %(levelname)-8s | %(message)s'
)


class ColoredFormatter(logging.Formatter):
    """Formatter personalizado que agrega colores a los logs en consola."""
    
    # Códigos ANSI para colores
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        """Formatea el registro con colores."""
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
    """Configura el sistema de logging para toda la aplicación.

    Crea handlers para:
    - Consola: logs formateados con colores
    - Archivo debug.log: todos los logs (DEBUG y superior)
    - Archivo info.log: logs INFO y superior (sin DEBUG)
    - Archivo error.log: solo logs ERROR y CRITICAL

    Args:
        debug_mode: Si True, muestra logs DEBUG en consola y archivo.
        log_level: Nivel mínimo de log ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')

    Example:
        setup_logging(debug_mode=True, log_level='DEBUG')
    """
    
    # Configurar nivel raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capturar todos los niveles
    
    # Limpiar handlers existentes
    root_logger.handlers.clear()
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_level = logging.DEBUG if debug_mode else logging.INFO
    console_handler.setLevel(console_level)
    
    console_formatter = ColoredFormatter(
        DEBUG_FORMAT if debug_mode else PRODUCTION_FORMAT
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Handler para archivo debug (todos los logs)
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
    
    # Handler para archivo info (INFO y superior)
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
    
    # Handler para archivo error (ERROR y CRITICAL)
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
    
    # Log de inicialización
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("Sistema de logging inicializado")
    logger.info(f"Directorio de logs: {LOGS_DIR.absolute()}")
    logger.info(f"Nivel de consola: {logging.getLevelName(console_level)}")
    logger.info("=" * 80)


def get_logger(name: str) -> logging.Logger:
    """Obtiene un logger configurado para un módulo.

    Args:
        name: Nombre del módulo (típicamente __name__)

    Returns:
        logging.Logger: Logger configurado

    Example:
        from app.config.logging_config import get_logger
        logger = get_logger(__name__)
        logger.info("Mensaje informativo")
    """
    return logging.getLogger(name)
