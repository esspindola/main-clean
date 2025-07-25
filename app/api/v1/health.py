"""
Health Check API
System health monitoring endpoints
"""

from flask_restx import Namespace, Resource
from flask import current_app
import psutil
import torch
import cv2
import pytesseract
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

health_ns = Namespace('health', description='System health monitoring')


@health_ns.route('')
class HealthCheck(Resource):
    """Basic health check endpoint."""
    
    def get(self):
        """
        Basic health check
        Returns system status and timestamp
        """
        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'OCR Invoice Processing API',
            'version': '2.0.0'
        }, 200


@health_ns.route('/detailed')
class DetailedHealthCheck(Resource):
    """Detailed health check with system information."""
    
    def get(self):
        """
        Detailed health check
        Returns comprehensive system status including dependencies
        """
        try:
            health_data = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'service': 'OCR Invoice Processing API',
                'version': '2.0.0',
                'system': {
                    'cpu_percent': psutil.cpu_percent(interval=1),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_percent': psutil.disk_usage('/').percent
                },
                'dependencies': {}
            }
            
            try:
                health_data['dependencies']['torch'] = {
                    'status': 'available',
                    'version': torch.__version__,
                    'cuda_available': torch.cuda.is_available()
                }
            except Exception as e:
                health_data['dependencies']['torch'] = {
                    'status': 'error',
                    'error': str(e)
                }
            
            try:
                health_data['dependencies']['opencv'] = {
                    'status': 'available',
                    'version': cv2.__version__
                }
            except Exception as e:
                health_data['dependencies']['opencv'] = {
                    'status': 'error',
                    'error': str(e)
                }
            

            try:
                version = pytesseract.get_tesseract_version()
                health_data['dependencies']['tesseract'] = {
                    'status': 'available',
                    'version': str(version)
                }
            except Exception as e:
                health_data['dependencies']['tesseract'] = {
                    'status': 'error',
                    'error': str(e)
                }
            
        
            try:
                model_manager = current_app.model_manager
                health_data['ml_model'] = {
                    'status': 'loaded' if model_manager.is_loaded else 'not_loaded',
                    'model_path': str(current_app.config['MODEL_PATH'])
                }
            except Exception as e:
                health_data['ml_model'] = {
                    'status': 'error',
                    'error': str(e)
                }
            
            
            error_count = sum(1 for dep in health_data['dependencies'].values() 
                            if dep.get('status') == 'error')
            
            if error_count > 0:
                health_data['status'] = 'degraded'
                
            if health_data.get('ml_model', {}).get('status') == 'error':
                health_data['status'] = 'unhealthy'
            
            status_code = 200 if health_data['status'] == 'healthy' else 503
            
            return health_data, status_code
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }, 503


@health_ns.route('/ready')
class ReadinessCheck(Resource):
    """Readiness check for container orchestration."""
    
    def get(self):
        """
        Readiness check
        Returns 200 if service is ready to accept requests
        """
        try:
        
            model_manager = current_app.model_manager
            if not model_manager.is_loaded:
                return {
                    'ready': False,
                    'reason': 'ML model not loaded'
                }, 503
            
            return {
                'ready': True,
                'timestamp': datetime.utcnow().isoformat()
            }, 200
            
        except Exception as e:
            logger.error(f"Readiness check failed: {e}")
            return {
                'ready': False,
                'reason': str(e)
            }, 503


@health_ns.route('/live')
class LivenessCheck(Resource):
    """Liveness check for container orchestration."""
    
    def get(self):
        """
        Liveness check
        Returns 200 if service is alive
        """
        return {
            'alive': True,
            'timestamp': datetime.utcnow().isoformat()
        }, 200