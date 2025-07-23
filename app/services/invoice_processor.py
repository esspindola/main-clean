"""
Advanced Invoice Processing Service
Professional-grade invoice OCR processing with multiple engines
"""

import cv2
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Any
from PIL import Image
from pdf2image import convert_from_bytes
import pytesseract
import easyocr
import base64
import io
import re
from collections import Counter

from app.services.ocr_engines import OCREngineManager
from app.services.image_processor import ImageProcessor
from app.services.table_detector import TableDetector
from app.services.enhanced_ocr import EnhancedOCRService
from app.utils.text_processing import TextProcessor
from app.core.ml_models import ModelManager

logger = logging.getLogger(__name__)


class InvoiceProcessor:
    """
    Advanced invoice processing with multiple OCR engines and AI-powered field detection.
    
    Features:
    - YOLOv5 custom model for field detection
    - Multi-OCR engines (Tesseract, EasyOCR, CRAFT)
    - Advanced image preprocessing
    - Table detection and structure analysis
    - Intelligent text grouping and classification
    - Rotation and skew correction
    """
    
    def __init__(self, model_manager: ModelManager, enhance_ocr: bool = True, 
                 rotation_correction: bool = True, confidence_threshold: float = 0.25):
        self.model_manager = model_manager
        self.enhance_ocr = enhance_ocr
        self.rotation_correction = rotation_correction
        self.confidence_threshold = confidence_threshold
        
        # Initialize service components
        self.ocr_manager = OCREngineManager()
        self.image_processor = ImageProcessor()
        self.table_detector = TableDetector()
        self.enhanced_ocr = EnhancedOCRService()  # New enhanced OCR service
        self.text_processor = TextProcessor()
        
        logger.info("InvoiceProcessor initialized")
    
    def process_document(self, file) -> Dict[str, Any]:
        """
        Process invoice document (PDF or image) and extract structured data.
        
        Args:
            file: Uploaded file object
            
        Returns:
            Dictionary containing extracted invoice data
        """
        try:
            
            images = self._convert_to_images(file)
            
            if not images:
                raise ValueError("No valid images found in document")
            
    
            primary_image = images[0]
            
        
            if self.enhance_ocr:
                enhanced_image = self.image_processor.enhance_for_ocr(primary_image)
            else:
                enhanced_image = primary_image.copy()
            

            if self.rotation_correction:
                corrected_image = self.image_processor.correct_rotation(enhanced_image)
            else:
                corrected_image = enhanced_image
            
            logger.info("Starting YOLOv5 object detection...")
            detections = self.model_manager.detect_objects(corrected_image)
            logger.info(f"YOLOv5 detected {len(detections)} objects")
            
        
            logger.info("Detecting table regions...")
            table_regions = self.table_detector.detect_tables(corrected_image)
            logger.info(f"Found {len(table_regions)} table regions")
            

            logger.info("Starting enhanced OCR extraction...")
            line_items = self.enhanced_ocr.extract_invoice_data(corrected_image, detections)
            logger.info(f"Enhanced OCR extracted {len(line_items)} line items")
            
            
            logger.info("Extracting metadata from detections...")
            metadata = self._extract_metadata_from_detections(detections, corrected_image)
            logger.info(f"Extracted metadata fields: {len(metadata)}")
            

            logger.info("Structuring invoice data...")
            structured_data = {
                'metadata': metadata,
                'line_items': line_items
            }
            logger.info(f"Structured data: metadata={len(structured_data.get('metadata', {}))}, line_items={len(structured_data.get('line_items', []))}")
            
            
            processed_image_b64 = self._create_visualization(
                corrected_image, detections, table_regions
            )
            
        
            avg_confidence = 0.0
            if line_items:
                total_confidence = sum(item.get('confidence', 0.0) for item in line_items)
                avg_confidence = total_confidence / len(line_items)
            
            return {
                'metadata': structured_data.get('metadata', {}),
                'line_items': self._format_line_items(structured_data.get('line_items', [])),
                'detections': self._format_detections(detections),
                'processed_image': processed_image_b64,
                'table_regions': len(table_regions),
                'ocr_confidence': avg_confidence
            }
            
        except Exception as e:
            logger.error(f"Invoice processing failed: {e}", exc_info=True)
            raise
    
    def _convert_to_images(self, file) -> List[np.ndarray]:
        """Convert uploaded file to list of images."""
        try:
            filename = file.filename.lower()
            
            if filename.endswith('.pdf'):
                # Convert PDF to images
                file.seek(0)
                pdf_images = convert_from_bytes(
                    file.read(),
                    dpi=300,
                    fmt='RGB'
                )
                
                
                images = []
                for pil_image in pdf_images:
                    image_array = np.array(pil_image)
                    image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
                    images.append(image_bgr)
                
                logger.info(f"Converted PDF to {len(images)} images")
                return images
                
            else:
            
                file.seek(0)
                pil_image = Image.open(file.stream).convert('RGB')
                image_array = np.array(pil_image)
                image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
                
                logger.info("Loaded single image")
                return [image_bgr]
                
        except Exception as e:
            logger.error(f"File conversion failed: {e}")
            raise ValueError(f"Cannot convert file to image: {e}")
    
    def _extract_metadata_from_detections(self, detections: List[Dict], image: np.ndarray) -> Dict:
        """Extract invoice metadata from YOLO detections using OCR on detected regions."""
        metadata = {}
        
        try:
            
            class_mapping = {
                'R.U.C': 'ruc',
                'numero_factura': 'invoice_number',
                'fecha_hora': 'date',
                'razon_social': 'company_name',
                'subtotal': 'subtotal',
                'iva': 'iva',
                'precio_total': 'total'
            }
            
        
            for detection in detections:
                class_name = detection.get('class_name', '')
                if class_name in class_mapping:
                    field_name = class_mapping[class_name]
                    
            
                    x1, y1 = int(detection.get('xmin', 0)), int(detection.get('ymin', 0))
                    x2, y2 = int(detection.get('xmax', 0)), int(detection.get('ymax', 0))
                    
                    if x2 > x1 and y2 > y1:
                        region = image[y1:y2, x1:x2]
                        
                    
                        region_boxes = self.enhanced_ocr.easyocr_text_regions(region)
                        region_text = ' '.join([box['text'] for box in region_boxes if box.get('confidence', 0) > 0.5])
                        
                        if region_text.strip():
                    
                            cleaned_text = self._postprocess_metadata_field(field_name, region_text)
                            metadata[field_name] = cleaned_text
            
            logger.debug(f"Extracted metadata: {metadata}")
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            return {}
    
    def _postprocess_metadata_field(self, field_name: str, text: str) -> str:
        """Post-process metadata field for cleanup and standardization."""
        # Clean up text
        cleaned_value = re.sub(r'[^\w\s\-\.\/:$]', '', text).strip()
        
        
        if field_name == 'ruc':
            # Extract RUC number
            ruc_match = re.search(r'\d{10,13}', cleaned_value)
            return ruc_match.group() if ruc_match else cleaned_value
        
        elif field_name in ['subtotal', 'iva', 'total']:
    
            money_match = re.search(r'[\$]?[\d,]+\.?\d*', cleaned_value)
            return money_match.group() if money_match else cleaned_value
        
        elif field_name == 'date':
            
            date_match = re.search(r'\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}', cleaned_value)
            return date_match.group() if date_match else cleaned_value
        
        else:
            return cleaned_value
    
    def _format_line_items(self, line_items: List[Dict]) -> List[Dict]:
        """Format line items from enhanced OCR for API response."""
        formatted_items = []
        
        for item in line_items:
        
            formatted_item = {
                'description': item.get('descripcion', 'No detectado'),
                'quantity': item.get('cantidad', 'No detectado'),
                'unit_price': 'No detectado',  
                'total_price': item.get('precio', 'No detectado'),
                'confidence': item.get('confidence', 0.0)
            }
            
    
            try:
                if (formatted_item['total_price'] != 'No detectado' and 
                    formatted_item['quantity'] != 'No detectado'):
                    
                    # Extract numeric values
                    total_match = re.search(r'[\d,]+\.?\d*', formatted_item['total_price'])
                    qty_match = re.search(r'\d+', formatted_item['quantity'])
                    
                    if total_match and qty_match:
                        total_val = float(total_match.group().replace(',', ''))
                        qty_val = float(qty_match.group())
                        
                        if qty_val > 0:
                            unit_price = total_val / qty_val
                            formatted_item['unit_price'] = f"{unit_price:.2f}"
            except:
                pass  
            
            formatted_items.append(formatted_item)
        
        return formatted_items
    
    
    def _format_detections(self, detections: List[Dict]) -> List[Dict]:
        """Format detections for API response."""
        formatted = []
        
        for detection in detections:
            formatted.append({
                'field_type': detection.get('class_name', ''),
                'text': detection.get('text', ''),
                'confidence': detection.get('confidence', 0.0),
                'bbox': {
                    'xmin': detection.get('xmin', 0),
                    'ymin': detection.get('ymin', 0),
                    'xmax': detection.get('xmax', 0),
                    'ymax': detection.get('ymax', 0)
                },
                'ocr_confidence': detection.get('ocr_confidence')
            })
        
        return formatted
    
    def _create_visualization(self, image: np.ndarray, detections: List[Dict], 
                            table_regions: List[Dict]) -> Optional[str]:
        """Create visualization of processing results."""
        try:
            vis_image = image.copy()
            
            # Draw YOLO detections
            for detection in detections:
                x1 = int(detection.get('xmin', 0))
                y1 = int(detection.get('ymin', 0))
                x2 = int(detection.get('xmax', 0))
                y2 = int(detection.get('ymax', 0))
                
                # Draw bounding box
                cv2.rectangle(vis_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Draw label
                label = f"{detection.get('class_name', '')} ({detection.get('confidence', 0):.2f})"
                cv2.putText(vis_image, label, (x1, y1-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            # Draw table regions
            for i, region in enumerate(table_regions):
                x, y, w, h = region.get('bbox', (0, 0, 0, 0))
                cv2.rectangle(vis_image, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.putText(vis_image, f"Table {i+1}", (x, y-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            
            # Convert to base64
            _, buffer = cv2.imencode('.jpg', vis_image, [cv2.IMWRITE_JPEG_QUALITY, 95])
            img_b64 = base64.b64encode(buffer).decode('utf-8')
            
            return img_b64
            
        except Exception as e:
            logger.error(f"Visualization creation failed: {e}")
            return None