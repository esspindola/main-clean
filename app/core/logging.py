"""
Logging Configuration
Professional logging setup for the OCR backend
"""

import logging
import logging.handlers
import os
from pathlib import Path
from flask import Flask


def setup_logging(app: Flask):
    """Configure application logging with rotating file handler."""
    
  
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
   
    logging.basicConfig(level=getattr(logging, app.config['LOG_LEVEL']))
    
  
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
  
    file_handler = logging.handlers.RotatingFileHandler(
        filename=app.config['LOG_FILE'],
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
  
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
    
   
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
    
    
    loggers = [
        'werkzeug',
        'gunicorn.error',
        'gunicorn.access',
        'app.services.ocr',
        'app.services.ml',
        'app.api'
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.addHandler(file_handler)
        logger.setLevel(logging.INFO)
    
    app.logger.info("Logging system initialized")