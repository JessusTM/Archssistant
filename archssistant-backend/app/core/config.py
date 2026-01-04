"""Core configuration for Arch-Assistant.

This module centralizes application configuration using Pydantic BaseSettings,
handling environment variables, logging setup, and application-wide settings.

Configuration values are loaded from environment variables (via .env file)
or use the default values if not specified. BaseSettings automatically loads
values from the .env file when configured with env_file.
"""

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from .logging_config import setup_logging, get_logger


load_dotenv()


class Config(BaseSettings):
    """Application configuration using Pydantic BaseSettings.
    
    This class defines all application configuration settings that are
    loaded from environment variables (via .env file) or use sensible defaults.
    
    BaseSettings automatically reads from .env file when env_file is set.
    Values in .env will override the default values below.
    
    Attributes:
        APP_NAME    : Application name (hardcoded, not configurable via .env)
        LOG_LEVEL   : Logging level (loaded from .env LOG_LEVEL variable, default: INFO)
                      Valid values: DEBUG, INFO, WARNING, ERROR, CRITICAL
                        - DEBUG for development
                        - INFO for production 
        PORT        : Server port (loaded from .env PORT variable, default: 5000)
        HOST        : Server host (loaded from .env HOST variable, default: 0.0.0.0)
    """
    
    model_config = SettingsConfigDict(
        env_file        = ".env",
        case_sensitive  = False
    )
    
    APP_NAME    : str   = "Archssistant"
    LOG_LEVEL   : str   = "INFO"
    PORT        : int   = 5000
    HOST        : str   = "0.0.0.0"


config = Config()
setup_logging(log_level=config.LOG_LEVEL)
logger = get_logger(__name__)

logger.info("=" * 80)
logger.info(f"Configuration initialized for {config.APP_NAME}")
logger.info(f"Log level : {config.LOG_LEVEL}")
logger.info(f"Host      : {config.HOST}")
logger.info(f"Port      : {config.PORT}")
logger.info("=" * 80)