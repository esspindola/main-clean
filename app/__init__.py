"""
OCR Backend Application
Professional Invoice Processing System with YOLOv5 + Multi-OCR
Author: AI System Architecture
Version: 2.0.0
"""

from flask import Flask
from flask_cors import CORS
from flask_restx import Api
from app.core.config import Config
from app.core.logging import setup_logging
import logging


def create_app(config_class=Config):
    """Application factory pattern for Flask app creation."""
    
    # Initialize Flask app
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Setup logging
    setup_logging(app)
    logger = logging.getLogger(__name__)
    
    # Initialize CORS with comprehensive settings
    CORS(app, 
         origins=app.config['CORS_ORIGINS'],
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
         expose_headers=["Content-Range", "X-Content-Range"])
    
    # Initialize Swagger API documentation
    api = Api(app,
              title='OCR Invoice Processing API',
              version='2.0.0',
              description='''
              Professional Invoice Processing System using YOLOv5 + Multi-OCR
              
              Features:
              - YOLOv5 custom trained model for invoice field detection
              - Multi-OCR engines (Tesseract, EasyOCR, CRAFT)
              - Automatic table detection and text extraction
              - PDF and image processing support
              - Real-time invoice data extraction
              - Professional REST API with Swagger documentation
              ''',
              doc='/docs/',
              prefix='/api/v1')
    
    # Register blueprints/namespaces
    from app.api.v1.invoice import invoice_ns
    from app.api.v1.health import health_ns
    from app.api.v1.orders import orders_ns
    from app.api.v1.database import db_ns
    
    api.add_namespace(health_ns, path='/health')
    api.add_namespace(invoice_ns, path='/invoice')
    api.add_namespace(orders_ns, path='/orders')
    api.add_namespace(db_ns, path='/database')
    
    # Initialize core services
    from app.core.ml_models import ModelManager
    app.model_manager = ModelManager()
    
    # Load ML models on startup
    try:
        app.model_manager.load_models()
        logger.info("ML models loaded successfully during app initialization")
    except Exception as e:
        logger.error(f"Failed to load ML models during startup: {e}")
        # Continue with dummy models for debugging
    
    # Add simple health check route for Docker
    @app.route('/health')
    def simple_health():
        return {'status': 'ok', 'message': 'OCR Backend is running'}, 200
    
    logger.info("OCR Backend Application initialized successfully")
    
    return app