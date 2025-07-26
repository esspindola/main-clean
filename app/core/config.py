"""
Application Configuration
Centralized configuration management for the OCR backend
"""

import os
from pathlib import Path
from typing import List

class Config:
    """Base configuration class with common settings."""
    
   
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
 
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
   
    CORS_ORIGINS = [
       
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173",  # Vite dev server
        "http://localhost:4444",  # Node.js backend
        "http://127.0.0.1:4444",  # Node.js backend
        # Docker and production
        "http://localhost:8001",  # Docker OCR backend
        "http://127.0.0.1:8001",  # Docker OCR backend
        "http://localhost:8080",  # Docker nginx
        "http://127.0.0.1:8080",  # Docker nginx
        # External
        "https://web-navy-nine.vercel.app",
        "https://*.ngrok-free.app"
    ]
  
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  
    UPLOAD_FOLDER = Path('uploads')
    OUTPUT_FOLDER = Path('outputs')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tiff', 'bmp', 'pdf'}
    
   
    TESSERACT_CMD = os.environ.get('TESSERACT_CMD', 'tesseract')
    TESSDATA_PREFIX = os.environ.get('TESSDATA_PREFIX', '/usr/share/tesseract-ocr/5/tessdata')
    OCR_LANGUAGES = ['spa', 'eng']
    
    MODEL_PATH = Path('models/best.pt')
    YOLO_CONFIDENCE_THRESHOLD = 0.25
    YOLO_IOU_THRESHOLD = 0.45
    YOLO_INPUT_SIZE = 640
    
  
    POPPLER_PATH = os.environ.get('POPPLER_PATH', None)
    PDF_DPI = 300
    
   
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = Path('logs/ocr_backend.log')
    
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///ocr_backend.db')
    
   
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
    CACHE_TYPE = 'redis'
    CACHE_DEFAULT_TIMEOUT = 300
    
    @staticmethod
    def init_app(app):
        """Initialize application with config-specific settings."""
        # Create necessary directories
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)
        os.makedirs(Config.LOG_FILE.parent, exist_ok=True)
        os.makedirs(Config.MODEL_PATH.parent, exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration with debug enabled."""
    DEBUG = True
    FLASK_ENV = 'development'
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration with optimized settings."""
    DEBUG = False
    FLASK_ENV = 'production'
    LOG_LEVEL = 'WARNING'
    
   
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class TestingConfig(Config):
    """Testing configuration for unit tests."""
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}