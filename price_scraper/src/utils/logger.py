import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


def setup_logger(
    name: str = "moto_price_compare",
    log_file: Optional[str] = None,
    log_level: str = "INFO",
    max_file_size_mb: int = 10,
    backup_count: int = 5,
) -> logging.Logger:
    """Set up logger with file and console handlers."""
    
    # Create logger
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if logger already configured
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log_file specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size_mb * 1024 * 1024,
            backupCount=backup_count,
            encoding="utf-8"
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "moto_price_compare") -> logging.Logger:
    """Get configured logger instance."""
    log_file = os.getenv("LOG_FILE", "logs/app.log")
    log_level = os.getenv("LOG_LEVEL", "INFO")
    
    return setup_logger(
        name=name,
        log_file=log_file,
        log_level=log_level
    )