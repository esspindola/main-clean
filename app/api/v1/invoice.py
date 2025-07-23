"""
Invoice Processing API
Main endpoints for invoice OCR processing
"""

from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import time
import logging
from typing import Dict, Any

from app.models.invoice import (
    ProcessDocumentResponse, 
    ErrorResponse, 
    InvoiceRow, 
    InvoiceMetadata,
    DetectionResult
)
from app.services.invoice_processor import InvoiceProcessor
from app.utils.file_handler import FileHandler
from app.utils.validators import validate_file

logger = logging.getLogger(__name__)

invoice_ns = Namespace('invoice', description='Invoice processing operations')

upload_parser = invoice_ns.parser()
upload_parser.add_argument('file', location='files', type=FileStorage, required=True, 
                          help='Invoice file (PDF or image)')
upload_parser.add_argument('enhance_ocr', type=bool, default=True, 
                          help='Enable OCR enhancement')
upload_parser.add_argument('rotation_correction', type=bool, default=True, 
                          help='Enable rotation correction')
upload_parser.add_argument('confidence_threshold', type=float, default=0.25, 
                          help='Detection confidence threshold (0.1-0.9)')

bbox_model = invoice_ns.model('BoundingBox', {
    'xmin': fields.Float(required=True, description='Left coordinate'),
    'ymin': fields.Float(required=True, description='Top coordinate'),
    'xmax': fields.Float(required=True, description='Right coordinate'),
    'ymax': fields.Float(required=True, description='Bottom coordinate')
})

detection_model = invoice_ns.model('Detection', {
    'field_type': fields.String(required=True, description='Detected field type'),
    'text': fields.String(required=True, description='Extracted text'),
    'confidence': fields.Float(required=True, description='Detection confidence'),
    'bbox': fields.Nested(bbox_model),
    'ocr_confidence': fields.Float(description='OCR confidence')
})

invoice_row_model = invoice_ns.model('InvoiceRow', {
    'description': fields.String(required=True, description='Product/service description'),
    'quantity': fields.String(required=True, description='Quantity'),
    'unit_price': fields.String(required=True, description='Unit price'),
    'total_price': fields.String(required=True, description='Total price'),
    'confidence': fields.Float(required=True, description='Extraction confidence')
})

metadata_model = invoice_ns.model('InvoiceMetadata', {
    'ruc': fields.String(description='RUC number'),
    'invoice_number': fields.String(description='Invoice number'),
    'date': fields.String(description='Invoice date'),
    'company_name': fields.String(description='Company name'),
    'subtotal': fields.String(description='Subtotal amount'),
    'iva': fields.String(description='IVA amount'),
    'total': fields.String(description='Total amount')
})

process_response_model = invoice_ns.model('ProcessResponse', {
    'success': fields.Boolean(required=True, description='Processing success'),
    'message': fields.String(required=True, description='Processing message'),
    'metadata': fields.Nested(metadata_model),
    'line_items': fields.List(fields.Nested(invoice_row_model)),
    'detections': fields.List(fields.Nested(detection_model)),
    'processed_image': fields.String(description='Base64 encoded processed image'),
    'processing_time': fields.Float(required=True, description='Processing time in seconds')
})

error_model = invoice_ns.model('Error', {
    'success': fields.Boolean(default=False, description='Always false for errors'),
    'error': fields.String(required=True, description='Error message'),
    'error_code': fields.String(description='Error code'),
    'details': fields.Raw(description='Additional error details')
})


@invoice_ns.route('/process')
class ProcessInvoice(Resource):
    """Process invoice documents for data extraction."""
    
    @invoice_ns.expect(upload_parser)
    @invoice_ns.marshal_with(process_response_model, code=200)
    @invoice_ns.marshal_with(error_model, code=400)
    @invoice_ns.marshal_with(error_model, code=500)
    def post(self):
        """
        Process invoice document
        
        Upload an invoice (PDF or image) for automated data extraction using:
        - YOLOv5 custom model for field detection
        - Multi-OCR engines (Tesseract, EasyOCR, CRAFT)
        - Advanced table detection and text extraction
        - Automatic rotation correction
        
        Returns extracted invoice data including line items and metadata.
        """
        start_time = time.time()
        
        try:
        
            args = upload_parser.parse_args()
            file = args['file']
            enhance_ocr = args.get('enhance_ocr', True)
            rotation_correction = args.get('rotation_correction', True)
            confidence_threshold = args.get('confidence_threshold', 0.25)
            
        
            if not file:
                return {
                    'success': False,
                    'error': 'No file provided',
                    'error_code': 'MISSING_FILE'
                }, 400
            
    
            validation_result = validate_file(file)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['error'],
                    'error_code': 'INVALID_FILE',
                    'details': validation_result.get('details', {})
                }, 400
            
            logger.info(f"Processing invoice: {file.filename}")
            
            processor = InvoiceProcessor(
                model_manager=current_app.model_manager,
                enhance_ocr=enhance_ocr,
                rotation_correction=rotation_correction,
                confidence_threshold=confidence_threshold
            )
            
            result = processor.process_document(file)
            
            processing_time = time.time() - start_time
            
        
            response = {
                'success': True,
                'message': 'Invoice processed successfully',
                'metadata': result.get('metadata', {}),
                'line_items': result.get('line_items', []),
                'detections': result.get('detections', []),
                'processed_image': result.get('processed_image'),
                'processing_time': round(processing_time, 2)
            }
            
            logger.info(f"Invoice processed successfully in {processing_time:.2f}s")
            return response, 200
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Invoice processing failed: {e}", exc_info=True)
            
            return {
                'success': False,
                'error': f'Processing failed: {str(e)}',
                'error_code': 'PROCESSING_ERROR',
                'details': {
                    'processing_time': round(processing_time, 2),
                    'file_name': file.filename if file else None
                }
            }, 500


@invoice_ns.route('/validate')
class ValidateInvoice(Resource):
    """Validate invoice file without processing."""
    
    @invoice_ns.expect(upload_parser)
    def post(self):
        """
        Validate invoice file
        
        Check if the uploaded file is valid for processing without
        actually performing the OCR extraction.
        """
        try:
            args = upload_parser.parse_args()
            file = args['file']
            
            if not file:
                return {
                    'valid': False,
                    'error': 'No file provided'
                }, 400
            
            validation_result = validate_file(file)
            
            if validation_result['valid']:
                return {
                    'valid': True,
                    'message': 'File is valid for processing',
                    'file_info': {
                        'filename': secure_filename(file.filename),
                        'size': len(file.read()),
                        'content_type': file.content_type
                    }
                }, 200
            else:
                return {
                    'valid': False,
                    'error': validation_result['error'],
                    'details': validation_result.get('details', {})
                }, 400
                
        except Exception as e:
            logger.error(f"File validation failed: {e}")
            return {
                'valid': False,
                'error': f'Validation failed: {str(e)}'
            }, 500


@invoice_ns.route('/supported-formats')
class SupportedFormats(Resource):
    """Get supported file formats and limitations."""
    
    def get(self):
        """
        Get supported file formats
        
        Returns information about supported file formats,
        size limitations, and processing capabilities.
        """
        return {
            'supported_formats': list(current_app.config['ALLOWED_EXTENSIONS']),
            'max_file_size_mb': current_app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024),
            'ocr_languages': current_app.config['OCR_LANGUAGES'],
            'capabilities': {
                'pdf_processing': True,
                'image_processing': True,
                'table_detection': True,
                'rotation_correction': True,
                'multi_ocr_engines': True,
                'yolo_field_detection': True
            },
            'optimal_conditions': {
                'dpi': 'Minimum 150 DPI for images',
                'format': 'PDF preferred for multi-page documents',
                'quality': 'High contrast, clear text',
                'orientation': 'Portrait orientation preferred'
            }
        }, 200


@invoice_ns.route('/debug')
class DebugInvoice(Resource):
    """Debug endpoint for OCR testing."""
    
    def get(self):
        """
        Debug information about the OCR system.
        
        Returns detailed information about model loading,
        OCR engines status, and system capabilities.
        """
        import cv2
        import numpy as np
        import pytesseract
        
        debug_info = {
            'model_status': {
                'yolo_loaded': current_app.model_manager.is_loaded if hasattr(current_app, 'model_manager') else False,
                'classes_count': len(current_app.model_manager.classes) if hasattr(current_app, 'model_manager') else 0
            },
            'ocr_engines': {},
            'simple_test': {}
        }
        
        # Test Tesseract
        try:
            version = pytesseract.get_tesseract_version()
            debug_info['ocr_engines']['tesseract'] = {
                'status': 'OK',
                'version': str(version)
            }
            
    
            img = np.ones((100, 400, 3), dtype=np.uint8) * 255
            cv2.putText(img, 'FACTURA 001-001-12345', (10, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            
            text = pytesseract.image_to_string(img, config='--psm 8 -l spa+eng')
            debug_info['simple_test']['tesseract_text'] = text.strip()
            
        except Exception as e:
            debug_info['ocr_engines']['tesseract'] = {
                'status': 'ERROR',
                'error': str(e)
            }
        
        # Test model detection
        if hasattr(current_app, 'model_manager') and current_app.model_manager.is_loaded:
            try:
                # Create test image más realista para facturas
                test_img = np.ones((800, 600, 3), dtype=np.uint8) * 255
                
                # Simular header de factura
                cv2.putText(test_img, 'EMPRESA S.A.', (50, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
                cv2.putText(test_img, 'RUC: 1791354400001', (50, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                cv2.putText(test_img, 'FACTURA No: 001-001-123456', (50, 150), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                cv2.putText(test_img, 'FECHA: 15/02/2024', (50, 200), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                
                # Simular tabla de items
                cv2.rectangle(test_img, (50, 250), (550, 450), (0, 0, 0), 2)
                cv2.putText(test_img, 'DESCRIPCION', (60, 280), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                cv2.putText(test_img, 'CANTIDAD', (250, 280), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                cv2.putText(test_img, 'PRECIO', (400, 280), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                
                # Items
                cv2.putText(test_img, 'Producto A', (60, 320), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                cv2.putText(test_img, '2', (270, 320), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                cv2.putText(test_img, '$25.00', (410, 320), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                
                # Totales
                cv2.putText(test_img, 'SUBTOTAL: $50.00', (350, 500), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                cv2.putText(test_img, 'IVA: $6.00', (350, 550), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                cv2.putText(test_img, 'TOTAL: $56.00', (350, 600), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                
                detections = current_app.model_manager.detect_objects(test_img)
                debug_info['simple_test']['yolo_detections'] = len(detections)
                debug_info['simple_test']['detected_classes'] = [d.get('class_name', 'unknown') for d in detections]
                
            except Exception as e:
                debug_info['simple_test']['yolo_error'] = str(e)
        
        return debug_info, 200


@invoice_ns.route('/switch-model/<string:model_name>')
class SwitchModel(Resource):
    """Switch between trained models."""
    
    def post(self, model_name):
        """
        Switch between available trained models.
        
        Available models: exp4, exp_retrain
        """
        try:
            from pathlib import Path
            
            if model_name not in ['exp4', 'exp_retrain']:
                return {
                    'success': False,
                    'error': 'Invalid model name. Available: exp4, exp_retrain'
                }, 400
            
    
            model_path = Path(f'yolov5/runs/train/{model_name}/weights/best.pt')
            
            if not model_path.exists():
                return {
                    'success': False,
                    'error': f'Model {model_name} not found at {model_path}'
                }, 404
            
            
            import shutil
            shutil.copy2(model_path, 'models/best.pt')
            
            # Reload model manager
            current_app.model_manager._load_yolo_model()
            
            return {
                'success': True,
                'message': f'Switched to model {model_name}',
                'model_path': str(model_path),
                'classes_count': len(current_app.model_manager.classes)
            }, 200
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to switch model: {str(e)}'
            }, 500