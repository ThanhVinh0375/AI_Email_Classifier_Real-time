"""Logging configuration"""
import logging
import sys
from pathlib import Path
from src.config import settings

def get_logger(name: str) -> logging.Logger:
    """Get configured logger instance"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(getattr(logging, settings.log_level))
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, settings.log_level))
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
    
    return logger
