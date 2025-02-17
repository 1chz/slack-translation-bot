import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LOG_DIR = Path("logs")
MAX_BYTES = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 5


def setup_logger(
    name: Optional[str] = None,
    level: int = logging.INFO,
    format_string: str = DEFAULT_FORMAT,
    log_to_file: bool = True,
) -> logging.Logger:
    """
    Creates and configures a logger instance.

    Args:
        name: Logger name (defaults to module name if None)
        level: Logging level (defaults to INFO)
        format_string: Log message format
        log_to_file: Whether to also log to a file

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        formatter = logging.Formatter(format_string)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler
        if log_to_file:
            DEFAULT_LOG_DIR.mkdir(exist_ok=True)
            log_file = DEFAULT_LOG_DIR / f"{name or 'app'}.log"
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=MAX_BYTES,
                backupCount=BACKUP_COUNT,
                encoding="utf-8",
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger
