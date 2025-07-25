#!/usr/bin/env python3
"""
OCR Backend - Production Runner
Optimized startup script for production deployment
"""

import os
import sys
import signal
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from main import app

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def signal_handler(signum, frame):
    """Graceful shutdown handler."""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)


def main():
    """Main entry point for production deployment."""
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Environment configuration
    env = os.environ.get('FLASK_ENV', 'production')
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    
    logger.info(f"Starting OCR Backend in {env} mode")
    logger.info(f"Server will be available at http://{host}:{port}")
    logger.info("API Documentation available at http://localhost:8001/docs/")
    
    try:
        # For production, use gunicorn instead of Flask dev server
        if env == 'production':
            logger.info("Production mode detected - use gunicorn for deployment")
            logger.info("Example: gunicorn --bind 0.0.0.0:5000 --workers 2 main:app")
        else:
            # Development mode
            app.run(
                host=host,
                port=port,
                debug=(env == 'development'),
                threaded=True
            )
            
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()