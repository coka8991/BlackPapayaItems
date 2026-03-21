"""
Logger configuration module
"""
import logging
import sys
from typing import Optional

APP_LOGGER_NAME = "my_app"


def configure_logging(
    level: str = "INFO",
    format_string: Optional[str] = None
) -> None:
    """
    Configure logging so that only internal modules emit INFO/DEBUG logs.
    External libraries will log only WARNING+.
    """
    if format_string is None:
        format_string = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

    # 1️⃣ Root logger: silencia librerías externas
    logging.basicConfig(
        level=logging.INFO,
        format=format_string,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )
    logging.getLogger("sqlalchemy.engine.Engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("msal").setLevel(logging.WARNING)
    

    # 2️⃣ Logger raíz de la aplicación
    app_logger = logging.getLogger(APP_LOGGER_NAME)
    app_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

configure_logging()

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a given module name.
    Use __name__ when calling this function.
    """

    return logging.getLogger(f"{APP_LOGGER_NAME}.{name}")
