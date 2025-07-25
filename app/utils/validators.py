"""
File and Data Validation Utilities
Comprehensive validation functions for the OCR backend
"""

import os
import logging
from typing import Dict, Any, Optional
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from flask import current_app
from PIL import Image
import fitz  # PyMuPDF for PDF validation

logger = logging.getLogger(__name__)


def validate_file(file: FileStorage) -> Dict[str, Any]:
    """
    Comprehensive file validation for uploaded documents.
    
    Args:
        file: Uploaded file object
        
    Returns:
        Dictionary with validation results
    """
    try:
        result = {
            'valid': False,
            'error': None,
            'details': {}
        }
        
        # Check if file exists
        if not file or not file.filename:
            result['error'] = 'No file provided or empty filename'
            return result
        
        # Secure filename
        filename = secure_filename(file.filename)
        if not filename:
            result['error'] = 'Invalid filename'
            return result
        
        result['details']['filename'] = filename
        
        # Check file extension
        if not allowed_file_extension(filename):
            result['error'] = f'File type not supported. Allowed: {current_app.config["ALLOWED_EXTENSIONS"]}'
            result['details']['allowed_extensions'] = list(current_app.config['ALLOWED_EXTENSIONS'])
            return result
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        max_size = current_app.config['MAX_CONTENT_LENGTH']
        if file_size > max_size:
            result['error'] = f'File too large. Maximum size: {max_size // (1024*1024)}MB'
            result['details']['file_size'] = file_size
            result['details']['max_size'] = max_size
            return result
        
        result['details']['file_size'] = file_size
        
        # Validate file content/magic number
        file_content = file.read(1024)  # Read first 1KB for magic number detection
        file.seek(0)
        
        content_validation = validate_file_content(file_content, filename)
        if not content_validation['valid']:
            result['error'] = content_validation['error']
            result['details'].update(content_validation['details'])
            return result
        
        result['details']['content_type'] = content_validation['content_type']
        
        # Additional format-specific validation
        if filename.lower().endswith('.pdf'):
            pdf_validation = validate_pdf_file(file)
            if not pdf_validation['valid']:
                result['error'] = pdf_validation['error']
                result['details'].update(pdf_validation['details'])
                return result
            result['details'].update(pdf_validation['details'])
            
        elif any(filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']):
            image_validation = validate_image_file(file)
            if not image_validation['valid']:
                result['error'] = image_validation['error']
                result['details'].update(image_validation['details'])
                return result
            result['details'].update(image_validation['details'])
        
        # All validations passed
        result['valid'] = True
        logger.debug(f"File validation successful: {filename}")
        return result
        
    except Exception as e:
        logger.error(f"File validation error: {e}")
        return {
            'valid': False,
            'error': f'Validation failed: {str(e)}',
            'details': {}
        }


def allowed_file_extension(filename: str) -> bool:
    """Check if file extension is allowed."""
    return ('.' in filename and 
            filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS'])


def validate_file_content(content: bytes, filename: str) -> Dict[str, Any]:
    """
    Validate file content using magic numbers.
    
    Args:
        content: First bytes of the file
        filename: Original filename
        
    Returns:
        Validation result with content type
    """
    try:
        result = {
            'valid': False,
            'error': None,
            'content_type': None,
            'details': {}
        }
        
        # Detect MIME type using file extension and magic numbers
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        mime_mapping = {
            'pdf': 'application/pdf',
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'tiff': 'image/tiff',
            'bmp': 'image/bmp'
        }
        mime_type = mime_mapping.get(ext, 'unknown')
        result['content_type'] = mime_type
        result['details']['detected_mime'] = mime_type
        
        # Validate content matches expected format
        filename_ext = filename.lower().split('.')[-1] if '.' in filename else ''
        
        if filename_ext == 'pdf':
            if not (content.startswith(b'%PDF') or 'pdf' in mime_type.lower()):
                result['error'] = 'File does not appear to be a valid PDF'
                return result
                
        elif filename_ext in ['jpg', 'jpeg']:
            if not (content.startswith(b'\xff\xd8\xff') or 'jpeg' in mime_type.lower()):
                result['error'] = 'File does not appear to be a valid JPEG'
                return result
                
        elif filename_ext == 'png':
            if not (content.startswith(b'\x89PNG\r\n\x1a\n') or 'png' in mime_type.lower()):
                result['error'] = 'File does not appear to be a valid PNG'
                return result
                
        elif filename_ext == 'tiff':
            if not (content.startswith((b'II*\x00', b'MM\x00*')) or 'tiff' in mime_type.lower()):
                result['error'] = 'File does not appear to be a valid TIFF'
                return result
                
        elif filename_ext == 'bmp':
            if not (content.startswith(b'BM') or 'bmp' in mime_type.lower()):
                result['error'] = 'File does not appear to be a valid BMP'
                return result
        
        result['valid'] = True
        return result
        
    except Exception as e:
        logger.warning(f"Content validation failed: {e}")
        return {
            'valid': True,  # Be lenient on content validation errors
            'error': None,
            'content_type': 'unknown',
            'details': {'content_validation_error': str(e)}
        }


def validate_pdf_file(file: FileStorage) -> Dict[str, Any]:
    """
    Validate PDF file structure and readability.
    
    Args:
        file: PDF file object
        
    Returns:
        Validation result with PDF metadata
    """
    try:
        result = {
            'valid': False,
            'error': None,
            'details': {}
        }
        

        file.seek(0)
        pdf_content = file.read()
        file.seek(0)
        
        
        try:
            pdf_doc = fitz.open(stream=pdf_content, filetype="pdf")
            
        
            page_count = pdf_doc.page_count
            if page_count == 0:
                result['error'] = 'PDF has no pages'
                return result
            
            result['details']['page_count'] = page_count
            
            
            if pdf_doc.needs_pass:
                result['error'] = 'PDF is password protected'
                return result
            

            first_page = pdf_doc[0]
            page_rect = first_page.rect
            
            result['details']['page_dimensions'] = {
                'width': page_rect.width,
                'height': page_rect.height
            }
            
        
            text_content = first_page.get_text()
            result['details']['has_text'] = len(text_content.strip()) > 0
            result['details']['text_length'] = len(text_content)
            
        
            image_list = first_page.get_images()
            result['details']['has_images'] = len(image_list) > 0
            result['details']['image_count'] = len(image_list)
            
            pdf_doc.close()
            
        except Exception as e:
            result['error'] = f'Invalid or corrupted PDF: {str(e)}'
            return result
        
        # Additional size validation
        if pdf_content.__sizeof__() < 100: 
            result['error'] = 'PDF file appears to be too small or empty'
            return result
        
        result['valid'] = True
        logger.debug(f"PDF validation successful: {page_count} pages")
        return result
        
    except Exception as e:
        logger.error(f"PDF validation error: {e}")
        return {
            'valid': False,
            'error': f'PDF validation failed: {str(e)}',
            'details': {}
        }


def validate_image_file(file: FileStorage) -> Dict[str, Any]:
    """
    Validate image file structure and properties.
    
    Args:
        file: Image file object
        
    Returns:
        Validation result with image metadata
    """
    try:
        result = {
            'valid': False,
            'error': None,
            'details': {}
        }
        
        file.seek(0)
        try:
            with Image.open(file) as img:
                # Basic image properties
                result['details']['format'] = img.format
                result['details']['mode'] = img.mode
                result['details']['size'] = img.size
                result['details']['width'] = img.width
                result['details']['height'] = img.height
                
    
                if img.width < 50 or img.height < 50:
                    result['error'] = 'Image too small (minimum 50x50 pixels)'
                    return result
                
                if img.width > 10000 or img.height > 10000:
                    result['error'] = 'Image too large (maximum 10000x10000 pixels)'
                    return result
                
        
                aspect_ratio = img.width / img.height
                if aspect_ratio > 20 or aspect_ratio < 0.05:
                    result['error'] = 'Invalid aspect ratio (too wide or too narrow)'
                    return result
                
                result['details']['aspect_ratio'] = aspect_ratio
                
                
                try:
                    img.load()
                except Exception as e:
                    result['error'] = f'Corrupted image data: {str(e)}'
                    return result
                
        
                supported_modes = ['RGB', 'RGBA', 'L', 'LA', 'P']
                if img.mode not in supported_modes:
                    result['error'] = f'Unsupported color mode: {img.mode}'
                    return result
                
        
                dpi = img.info.get('dpi', (72, 72))
                if isinstance(dpi, (list, tuple)):
                    avg_dpi = sum(dpi) / len(dpi)
                else:
                    avg_dpi = dpi
                
                result['details']['dpi'] = avg_dpi
                result['details']['quality_estimate'] = 'high' if avg_dpi >= 150 else 'medium' if avg_dpi >= 100 else 'low'
                
        except Exception as e:
            result['error'] = f'Invalid or corrupted image: {str(e)}'
            return result
        
        file.seek(0)
        
        result['valid'] = True
        logger.debug(f"Image validation successful: {result['details']['size']}")
        return result
        
    except Exception as e:
        logger.error(f"Image validation error: {e}")
        return {
            'valid': False,
            'error': f'Image validation failed: {str(e)}',
            'details': {}
        }


def validate_processing_parameters(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate processing parameters.
    
    Args:
        params: Processing parameters dictionary
        
    Returns:
        Validation result
    """
    try:
        result = {
            'valid': True,
            'error': None,
            'sanitized_params': {}
        }
        
    
        confidence = params.get('confidence_threshold', 0.25)
        if not isinstance(confidence, (int, float)) or confidence < 0.1 or confidence > 0.9:
            result['valid'] = False
            result['error'] = 'confidence_threshold must be a number between 0.1 and 0.9'
            return result
        result['sanitized_params']['confidence_threshold'] = float(confidence)
        
    
        bool_params = ['enhance_ocr', 'rotation_correction']
        for param in bool_params:
            value = params.get(param, True)
            if not isinstance(value, bool):
               
                if isinstance(value, str):
                    value = value.lower() in ['true', '1', 'yes', 'on']
                else:
                    value = bool(value)
            result['sanitized_params'][param] = value
        
        return result
        
    except Exception as e:
        logger.error(f"Parameter validation error: {e}")
        return {
            'valid': False,
            'error': f'Parameter validation failed: {str(e)}',
            'sanitized_params': {}
        }