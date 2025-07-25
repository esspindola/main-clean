"""
OCR Invoice Processing Backend - Main Application
Professional-grade invoice OCR system with YOLOv5 + Multi-OCR engines

Author: AI System Architecture  
Version: 2.0.0
License: MIT

Features:
- YOLOv5 custom trained model for invoice field detection
- Multi-OCR engines (Tesseract, EasyOCR, CRAFT)
- Advanced image preprocessing and rotation correction
- Professional REST API with Swagger documentation
- Docker containerization support
- Comprehensive logging and monitoring
"""

import os
import sys
from pathlib import Path


project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


from app import create_app
from app.core.config import config


config_name = os.environ.get('FLASK_ENV', 'production')
app = create_app(config[config_name])


with app.app_context():
    app.logger.info("Application started successfully - models will be loaded on demand")

if __name__ == '__main__':

    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )