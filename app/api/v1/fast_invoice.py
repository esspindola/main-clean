"""
ENDPOINT ULTRA RÁPIDO SIN DEPENDENCIAS PESADAS
Diseñado para procesar facturas en menos de 5 segundos
"""

from flask import request
from flask_restx import Namespace, Resource, fields
from werkzeug.datastructures import FileStorage
import time
import logging
import cv2
import numpy as np
from PIL import Image
from pdf2image import convert_from_bytes
import pytesseract
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = logging.getLogger(__name__)

fast_ns = Namespace('fast-invoice', description='Ultra fast invoice processing')

upload_parser = fast_ns.parser()
upload_parser.add_argument('file', location='files', type=FileStorage, required=True)

fast_response_model = fast_ns.model('FastResponse', {
    'success': fields.Boolean(required=True),
    'message': fields.String(required=True),
    'metadata': fields.Raw(),
    'line_items': fields.List(fields.Raw()),
    'processing_time': fields.Float(required=True)
})

@fast_ns.route('/process')
class FastProcessInvoice(Resource):
    """Ultra fast invoice processing - No YOLO, No Redis, No Heavy Dependencies"""
    
    @fast_ns.expect(upload_parser)
    @fast_ns.marshal_with(fast_response_model, code=200)
    def post(self):
        """
        Ultra fast invoice processing
        
        Processes invoices in under 5 seconds using:
        - Direct Tesseract OCR only
        - Pattern recognition for known invoice types
        - Pre-defined product database
        - No machine learning models
        """
        start_time = time.time()
        
        logger.info("⚡ ULTRA FAST PROCESSING STARTED")
        
        try:
            args = upload_parser.parse_args()
            file = args['file']
            
            if not file:
                return {
                    'success': False,
                    'message': 'No file provided',
                    'processing_time': time.time() - start_time
                }, 400
            
            logger.info("📷 Converting file to image...")
            image = self._quick_file_to_image(file)
            
            if image is None:
                return {
                    'success': False,
                    'message': 'Cannot convert file to image',
                    'processing_time': time.time() - start_time
                }, 400
            
            logger.info("🔍 Quick OCR extraction...")
            text = self._quick_ocr(image)
            
            if len(text) < 20:
                return {
                    'success': False,
                    'message': 'No text extracted from image',
                    'processing_time': time.time() - start_time
                }, 400
            logger.info("⚡ Ultra light processing...")
            from ultra_light_processor import process_invoice_ultra_fast
            
            result = process_invoice_ultra_fast(text)
            
            processing_time = time.time() - start_time
            result['processing_time'] = processing_time
            
            logger.info(f"✅ Fast processing completed in {processing_time:.2f}s")
            
            return result, 200
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"❌ Fast processing failed: {e}")
            
            return {
                'success': False,
                'message': f'Fast processing failed: {str(e)}',
                'processing_time': processing_time
            }, 500
    
    def _quick_file_to_image(self, file) -> np.ndarray:
        """Conversión rápida de archivo a imagen"""
        try:
            filename = file.filename.lower()
            
            if filename.endswith('.pdf'):
            
                file.seek(0)
                pdf_images = convert_from_bytes(
                    file.read(),
                    dpi=150,  
                    first_page=1,
                    last_page=1
                )
                
                if pdf_images:
                    image_array = np.array(pdf_images[0])
                    return cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            else:
        
                file.seek(0)
                pil_image = Image.open(file.stream).convert('RGB')
                image_array = np.array(pil_image)
                return cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        except Exception as e:
            logger.error(f"File conversion error: {e}")
            return None
    
    def _quick_ocr(self, image: np.ndarray) -> str:
        """OCR rápido solo con Tesseract básico"""
        try:
        
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
        
            text = pytesseract.image_to_string(
                gray, 
                config='--psm 6 -l eng',  
                timeout=10  
            )
            
            logger.info(f"📄 OCR extracted {len(text)} characters")
            return text
            
        except Exception as e:
            logger.error(f"OCR error: {e}")
            return ""