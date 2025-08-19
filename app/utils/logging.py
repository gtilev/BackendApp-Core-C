import logging
import sys
from pathlib import Path
from loguru import logger
import json
from datetime import datetime

from app.core.config import settings


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentation.
    See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


class JsonFormatter:
    """
    Formatter for JSON logs
    """
    def __init__(self):
        self.format_dict = {
            "level": "{level}",
            "timestamp": "{time:YYYY-MM-DD HH:mm:ss.SSS}",
            "message": "{message}",
            "module": "{name}",
            "function": "{function}",
            "line": "{line}",
        }
    
    def format(self, record):
        record["extra"]["serialized"] = json.dumps(self.format_dict)
        return "{extra[serialized]}"


def setup_logging():
    """
    Configure logging for the application
    """
    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    
    # Remove all loggers configured before
    logger.remove()
    
    # Create logs directory if it doesn't exist
    logs_path = Path("logs")
    logs_path.mkdir(exist_ok=True)
    
    # Configure loguru logger
    logger.configure(
        handlers=[
            # Console handler
            {
                "sink": sys.stdout, 
                "level": "DEBUG" if settings.DEBUG else "INFO",
                "format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
            },
            # File handler for all logs
            {
                "sink": logs_path / f"accounting_api_{datetime.now().strftime('%Y-%m-%d')}.log",
                "level": "INFO",
                "rotation": "00:00",  # Rotate at midnight
                "retention": "30 days",  # Keep logs for 30 days
                "format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{line} - {message}",
            },
            # File handler for errors only
            {
                "sink": logs_path / f"accounting_api_errors_{datetime.now().strftime('%Y-%m-%d')}.log",
                "level": "ERROR",
                "rotation": "00:00",  # Rotate at midnight
                "retention": "30 days",  # Keep logs for 30 days
                "format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{line} - {message}",
            },
            # JSON formatter for structured logging (optional)
            # {
            #     "sink": logs_path / f"accounting_api_json_{datetime.now().strftime('%Y-%m-%d')}.json",
            #     "level": "INFO",
            #     "format": JsonFormatter().format,
            #     "rotation": "00:00",
            #     "retention": "30 days",
            # },
        ]
    )
    
    # Replace stdlib handlers with loguru
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True
    
    # Add DEBUG flag to config
    if not hasattr(settings, "DEBUG"):
        settings.DEBUG = False
    
    return logger