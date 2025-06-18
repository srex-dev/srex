# core/logger.py
import logging
import sys
from pathlib import Path
from typing import Optional
from core.config import config_manager

class CustomFormatter(logging.Formatter):
    """Custom formatter with colors."""
    
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    
    format_template = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    FORMATS = {
        logging.DEBUG: grey + format_template + reset,
        logging.INFO: grey + format_template + reset,
        logging.WARNING: yellow + format_template + reset,
        logging.ERROR: red + format_template + reset,
        logging.CRITICAL: bold_red + format_template + reset
    }
    
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def setup_logger(name: str, level: Optional[str] = None, log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up a logger with the given name and configuration.
    
    Args:
        name: Logger name
        level: Logging level (defaults to config)
        log_file: Log file path (defaults to config)
    
    Returns:
        Configured logger instance
    """
    # Get configuration
    config = config_manager.get_config()
    log_level = level or config.logging.level
    log_file = log_file or config.logging.file
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create handlers
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(CustomFormatter())
    handlers.append(console_handler)
    
    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(config.logging.format))
        handlers.append(file_handler)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Add new handlers
    for handler in handlers:
        logger.addHandler(handler)
    
    return logger

# Create default logger
logger = setup_logger("srex")