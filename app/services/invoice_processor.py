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

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ EasyOCR not available: {e}")
    EASYOCR_AVAILABLE = False
    easyocr = None
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
        
      
        self.ocr_manager = OCREngineManager()
        self.image_processor = ImageProcessor()
        self.table_detector = TableDetector()
        self.enhanced_ocr = EnhancedOCRService() 
        self.text_processor = TextProcessor()
        
        logger.info("InvoiceProcessor initialized")


    #modo prueba para ver si me trae los datos de archivos que lle ocr 
    def process_document(self, file) -> Dict[str, Any]:
        """
        Process invoice document (PDF or image) and extract structured data.
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

            logger.info("🚀 Starting ROBUST MULTI-ENGINE processing...")
            detections = []
            try:
                logger.info("🎯 Attempting YOLOv5 detection with robust handling...")
                detections = self._robust_yolo_detection(corrected_image)
                logger.info(f"🎯 YOLOv5 detected {len(detections)} objects")
            except Exception as e:
                logger.warning(f"⚠️ YOLOv5 failed: {e}, continuing with backup methods...")

            logger.info("🧠 Executing robust multi-engine extraction...")
            robust_result = self._execute_robust_extraction(corrected_image, detections)
            metadata = robust_result.get('metadata', {})
            line_items = robust_result.get('line_items', [])

    
           
            logger.info(f"🔧 RAW METADATA FROM ROBUST SYSTEM: {metadata}")
            
            robust_metadata = {}
            for field, value in metadata.items():
                if value and str(value).strip():
                    robust_metadata[field] = str(value).strip()
                    logger.info(f"  ✅ DIRECT MAPPING {field}: {value}")
                else:
                    robust_metadata[field] = 'No detectado'
            
            robust_line_items = line_items if isinstance(line_items, list) else []
            robust_detections = self._format_detections(detections)
            robust_processed_image = self._create_visualization(corrected_image, detections, [])

            logger.info("📊 Detecting table regions...")
            table_regions = []
            try:
                table_regions = self.table_detector.detect_tables(corrected_image)
                logger.info(f"📊 Found {len(table_regions)} table regions")
            except Exception as e:
                logger.warning(f"⚠️ Table detection failed: {e}")

            logger.info(f"✅ Robust processing completed - Metadata: {len(metadata)}, Items: {len(line_items)}")
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

            final_metadata = robust_metadata  
            final_line_items = robust_line_items
            final_detections = robust_detections
            final_processed_image = robust_processed_image if robust_processed_image else processed_image_b64
            
            logger.info(f"🎯 FINAL DATA READY: metadata={len(final_metadata)}, items={len(final_line_items)}")
            logger.info("📋 FINAL METADATA TO SEND:")
            for field, value in final_metadata.items():
                logger.info(f"  🔹 {field}: '{value}'")

            return {
                'metadata': final_metadata,
                'line_items': final_line_items,
                'detections': final_detections,
                'processed_image': final_processed_image,
                'table_regions': len(table_regions),
                'ocr_confidence': avg_confidence,
                'yolo_detections': len(detections),
                'model_status': self.model_manager.get_model_info(),
            
                
                'original_metadata': self._format_metadata(structured_data.get('metadata', {})),
                'original_line_items': self._format_line_items(structured_data.get('line_items', [])),
                'robust_metadata': robust_metadata,
                'robust_line_items': robust_line_items,
                'robust_detections': robust_detections,
                'robust_processed_image': robust_processed_image
            }

        except Exception as e:
            logger.error(f"Invoice processing failed: {e}", exc_info=True)
            raise



    def _convert_to_images(self, file) -> List[np.ndarray]:
        """Convert uploaded file to list of images."""
        try:
            filename = file.filename.lower()
            
            if filename.endswith('.pdf'):
             
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
        """Extract invoice metadata from YOLO detections using enhanced OCR."""
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
                    
                   
                    extracted_text = detection.get('extracted_text', '')
                    ocr_confidence = detection.get('ocr_confidence', 0.0)
                    
                    if extracted_text and ocr_confidence > 0.3:
                        cleaned_text = self._postprocess_metadata_field(field_name, extracted_text)
                        metadata[field_name] = {
                            'value': cleaned_text,
                            'confidence': ocr_confidence,
                            'bbox': {
                                'xmin': detection.get('xmin', 0),
                                'ymin': detection.get('ymin', 0),
                                'xmax': detection.get('xmax', 0),
                                'ymax': detection.get('ymax', 0)
                            }
                        }
                    else:
                      
                        x1, y1 = int(detection.get('xmin', 0)), int(detection.get('ymin', 0))
                        x2, y2 = int(detection.get('xmax', 0)), int(detection.get('ymax', 0))
                        
                        if x2 > x1 and y2 > y1:
                            region = image[y1:y2, x1:x2]
                            
                           
                            region_boxes = self.enhanced_ocr.easyocr_text_regions(region)
                            if not region_boxes:
                                region_boxes = self.enhanced_ocr.tesseract_text_regions(region)
                            
                            best_text = ''
                            best_conf = 0.0
                            
                            for box in region_boxes:
                                if box.get('confidence', 0) > best_conf:
                                    best_text = box['text']
                                    best_conf = box.get('confidence', 0)
                            
                            if best_text.strip() and best_conf > 0.2:
                                cleaned_text = self._postprocess_metadata_field(field_name, best_text)
                                metadata[field_name] = {
                                    'value': cleaned_text,
                                    'confidence': best_conf,
                                    'bbox': {
                                        'xmin': x1, 'ymin': y1, 'xmax': x2, 'ymax': y2
                                    }
                                }
            
            logger.info(f"Extracted metadata for {len(metadata)} fields")
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            return {}
    
    def _postprocess_metadata_field(self, field_name: str, text: str) -> str:
        """Post-process metadata field for cleanup and standardization."""
        # Clean up text
        cleaned_value = re.sub(r'[^\w\s\-\.\/:$]', '', text).strip()
        
        
        if field_name == 'ruc':
           
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
    
    def _format_metadata(self, metadata: Dict) -> Dict:
        """Format metadata for API response."""
        formatted = {}
        
        for field, data in metadata.items():
            if isinstance(data, dict) and 'value' in data:
                formatted[field] = data['value']
            else:
                formatted[field] = str(data) if data else 'No detectado'
        
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
    
    # ========== MÉTODOS DEL SISTEMA ROBUSTO ==========
    
    def _robust_yolo_detection(self, image: np.ndarray) -> List[Dict]:
        """Detección YOLO robusta con manejo de errores mejorado"""
        try:
            # Configurar umbrales muy bajos
            if hasattr(self.model_manager.yolo_model, 'conf'):
                self.model_manager.yolo_model.conf = 0.05
            if hasattr(self.model_manager.yolo_model, 'iou'):
                self.model_manager.yolo_model.iou = 0.3
            if hasattr(self.model_manager.yolo_model, 'max_det'):
                self.model_manager.yolo_model.max_det = 1000
                
            logger.info("🎯 Configured YOLO with low thresholds (conf=0.05)")
            
            # Usar el método del model_manager pero capturar errores
            try:
                detections = self.model_manager.detect_objects(image)
                logger.info(f"🎯 YOLO successful: {len(detections)} objects detected")
                return detections
            except Exception as yolo_error:
                logger.error(f"❌ YOLO model_manager failed: {yolo_error}")
                # Intentar acceso directo al modelo
                return self._direct_yolo_inference(image)
                
        except Exception as e:
            logger.error(f"❌ Robust YOLO detection failed: {e}")
            return []
    
    def _direct_yolo_inference(self, image: np.ndarray) -> List[Dict]:
        """Inferencia YOLO directa como fallback"""
        try:
            if not hasattr(self.model_manager, 'yolo_model') or self.model_manager.yolo_model is None:
                logger.warning("⚠️ No YOLO model available")
                return []
            
            # Preprocesar imagen
            if len(image.shape) == 3:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            
            # Redimensionar si es necesario
            height, width = image_rgb.shape[:2]
            if width > 1280 or height > 1280:
                scale = min(1280/width, 1280/height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                image_rgb = cv2.resize(image_rgb, (new_width, new_height))
            
            # Inferencia directa
            results = self.model_manager.yolo_model(image_rgb)
            
            # Procesar resultados con múltiples formatos
            detections = []
            
            # Formato pandas (YOLOv5 clásico)
            if hasattr(results, 'pandas'):
                try:
                    df = results.pandas().xyxy[0]
                    for _, detection in df.iterrows():
                        detections.append({
                            'xmin': float(detection['xmin']),
                            'ymin': float(detection['ymin']),
                            'xmax': float(detection['xmax']),
                            'ymax': float(detection['ymax']),
                            'confidence': float(detection['confidence']),
                            'class_id': int(detection['class']),
                            'class_name': detection['name']
                        })
                    logger.info(f"✅ Direct YOLO pandas: {len(detections)} detections")
                except Exception as e:
                    logger.debug(f"Pandas format failed: {e}")
            
            # Formato xyxy
            elif hasattr(results, 'xyxy') and len(results.xyxy) > 0:
                try:
                    tensor_results = results.xyxy[0]
                    for detection in tensor_results:
                        if len(detection) >= 6:
                            class_id = int(detection[5])
                            confidence = float(detection[4])
                            class_name = self.model_manager.classes.get(class_id, f'class_{class_id}')
                            
                            if confidence >= 0.05:
                                detections.append({
                                    'xmin': float(detection[0]),
                                    'ymin': float(detection[1]),
                                    'xmax': float(detection[2]),
                                    'ymax': float(detection[3]),
                                    'confidence': confidence,
                                    'class_id': class_id,
                                    'class_name': class_name
                                })
                    logger.info(f"✅ Direct YOLO xyxy: {len(detections)} detections")
                except Exception as e:
                    logger.debug(f"xyxy format failed: {e}")
            
            return [d for d in detections if d['confidence'] >= 0.05]
            
        except Exception as e:
            logger.error(f"❌ Direct YOLO inference failed: {e}")
            return []
    
    def _execute_robust_extraction(self, image: np.ndarray, yolo_detections: List[Dict]) -> Dict:
        """Ejecutar extracción robusta multi-motor"""
        try:
            # Importar sistema robusto
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            
            from robust_multi_engine_ocr import RobustMultiEngineOCR
            
            # Inicializar sistema robusto
            robust_system = RobustMultiEngineOCR(
                yolo_model=self.model_manager.yolo_model,
                model_classes=self.model_manager.classes
            )
            
            # Procesar con sistema robusto
            result = robust_system.process_invoice_robust(image)
            
            if result.get('success', False):
                # Convertir formato para compatibilidad
                metadata = result.get('metadata', {})
                line_items = result.get('line_items', [])
                
                # Formatear metadatos
                formatted_metadata = {}
                for field, value in metadata.items():
                    if value and str(value).strip():
                        formatted_metadata[field] = {
                            'value': str(value).strip(),
                            'confidence': 0.8,
                            'bbox': {'xmin': 0, 'ymin': 0, 'xmax': 100, 'ymax': 100}
                        }
                
                # Formatear líneas de items
                formatted_items = []
                for item in line_items:
                    formatted_items.append({
                        'descripcion': item.get('description', 'No detectado'),
                        'cantidad': item.get('quantity', '1'),
                        'precio': item.get('total_price', '0.00'),
                        'confidence': item.get('confidence', 0.75)
                    })
                
                logger.info(f"🧠 Robust system extracted {len(formatted_metadata)} metadata fields, {len(formatted_items)} items")
                
                return {
                    'metadata': formatted_metadata,
                    'line_items': formatted_items,
                    'success': True
                }
            else:
                logger.error(f"❌ Robust system failed: {result.get('message', 'Unknown error')}")
                return self._fallback_extraction(image, yolo_detections)
                
        except ImportError as e:
            logger.error(f"❌ Cannot import robust system: {e}")
            return self._fallback_extraction(image, yolo_detections)
        except Exception as e:
            logger.error(f"❌ Robust extraction failed: {e}")
            return self._fallback_extraction(image, yolo_detections)
    
    def _fallback_extraction(self, image: np.ndarray, yolo_detections: List[Dict]) -> Dict:
        """Sistema de extracción de respaldo usando solo patrones"""
        logger.info("🔄 Using fallback pattern-based extraction...")
        
        try:
            # Extraer texto completo con Tesseract básico
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Mejorar imagen
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            
            # OCR básico
            try:
                text = pytesseract.image_to_string(enhanced, config='--psm 6 -l spa+eng')
                logger.info(f"📄 Extracted {len(text)} characters with Tesseract")
            except:
                text = ""
            
            # Patrones ecuatorianos básicos
            patterns = {
                'ruc': r'(?:R\.?U\.?C\.?|RUC)[\s:]*(\d{10,13})',
                'company_name': r'([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ\s\.&,-]{15,50})',
                'invoice_number': r'(?:FACTURA|FACT)[\s#:Nº]*(\d{3}-\d{3}-\d{9})',
                'date': r'(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})',
                'subtotal': r'(?:SUBTOTAL|SUB[\s\-]*TOTAL)[\s:$]*(\d+[.,]\d{2})',
                'iva': r'(?:I\.?V\.?A\.?|12%)[\s:$]*(\d+[.,]\d{2})',
                'total': r'(?:TOTAL)[\s:$]*(\d+[.,]\d{2})'
            }
            
            metadata = {}
            for field, pattern in patterns.items():
                try:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        value = match.group(1) if match.groups() else match.group(0)
                        metadata[field] = {
                            'value': value.strip(),
                            'confidence': 0.6,
                            'bbox': {'xmin': 0, 'ymin': 0, 'xmax': 100, 'ymax': 100}
                        }
                        logger.info(f"🔍 Pattern found {field}: '{value.strip()}'")
                except:
                    continue
            
            # Productos básicos
            line_items = []
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if len(line) > 15:
                    # Patrón básico para productos
                    product_match = re.search(r'(.{10,40})\s+(\d+)\s+(\d+[.,]\d{2})', line)
                    if product_match:
                        line_items.append({
                            'descripcion': product_match.group(1).strip(),
                            'cantidad': product_match.group(2),
                            'precio': product_match.group(3),
                            'confidence': 0.5
                        })
            
            logger.info(f"🔍 Fallback extracted {len(metadata)} metadata, {len(line_items)} items")
            
            return {
                'metadata': metadata,
                'line_items': line_items[:10],  # Limitar
                'success': True
            }
            
        except Exception as e:
            logger.error(f"❌ Fallback extraction failed: {e}")
            return {
                'metadata': {},
                'line_items': [],
                'success': False
            }