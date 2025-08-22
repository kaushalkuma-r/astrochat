import logging
import sys
from pathlib import Path
from app.config import settings

def setup_logging():
    """Setup logging configuration for the application."""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "astrochat.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific loggers
    loggers = [
        "uvicorn",
        "fastapi",
        "sqlalchemy",
        "chromadb",
        "app"
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Create main application logger
    logger = logging.getLogger("astrochat")
    logger.info("Logging configured successfully")
    
    return logger
