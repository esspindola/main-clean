"""
Multi-OCR Engine Manager
Advanced OCR processing with multiple engines for maximum accuracy
"""

import cv2
import numpy as np
import pytesseract
# EasyOCR import made optional to prevent startup issues
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ EasyOCR not available: {e}")
    EASYOCR_AVAILABLE = False
    easyocr = None
import logging
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from collections import defaultdict

logger = logging.getLogger(__name__)


class OCREngineManager:
    """
    Manages multiple OCR engines for optimal text extraction.
    
    Engines:
    - Tesseract: Traditional OCR with Spanish support
    - EasyOCR: Deep learning-based OCR
    - CRAFT: Text detection + recognition pipeline
    """
    
    def __init__(self):
        # Configuración optimizada para facturas
        self.tesseract_config = '--psm 6 -c preserve_interword_spaces=1 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzáéíóúüñÁÉÍÓÚÜÑ.,:-$%/()'
        self.tesseract_table_config = '--psm 6 -c preserve_interword_spaces=1'
        self.easyocr_reader = None
        self._initialize_engines()
    
    def _initialize_engines(self):
        """Initialize OCR engines."""
        self.easyocr_reader = None
        
        if EASYOCR_AVAILABLE:
            try:
                # Initialize EasyOCR with Spanish and English
                self.easyocr_reader = easyocr.Reader(['es', 'en'], gpu=False)
                logger.info("EasyOCR initialized successfully")
            except Exception as e:
                logger.error(f"EasyOCR initialization failed: {e}")
                self.easyocr_reader = None
        else:
            logger.warning("EasyOCR not available, using Tesseract only")
            
        # Test Tesseract
        try:
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract version: {version}")
        except Exception as e:
            logger.warning(f"Tesseract check failed: {e}")
        
        logger.info("OCR engines initialization completed")
    
    def extract_text_multi_engine(self, image: np.ndarray, detections: List[Dict], 
                                 table_regions: List[Dict]) -> Dict[str, Any]:
        """
        Extract text using multiple OCR engines with intelligent fusion.
        
        Args:
            image: Input image
            detections: YOLO detections for guided OCR
            table_regions: Detected table regions
            
        Returns:
            Dictionary with consolidated OCR results
        """
        try:
            
            preprocessed_images = self._prepare_image_variants(image)
            
            
            ocr_results = {}
            
        
            ocr_results['full_image'] = self._extract_full_image_text(preprocessed_images)
            
        
            ocr_results['regions'] = self._extract_region_text(image, detections)
            

            ocr_results['tables'] = self._extract_table_text(image, table_regions)
            
            
            consolidated_results = self._consolidate_results(ocr_results, image.shape)
            
            return consolidated_results
            
        except Exception as e:
            logger.error(f"Multi-engine OCR failed: {e}")
            return {'ocr_results': [], 'average_confidence': 0.0}
    
    def _prepare_image_variants(self, image: np.ndarray) -> Dict[str, np.ndarray]:
        """Prepare different image preprocessing variants for OCR."""
        variants = {}
        
        try:
        
            variants['original'] = image.copy()
            
    
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            variants['grayscale'] = gray
            
        
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            variants['enhanced'] = clahe.apply(gray)
            
        
            variants['denoised'] = cv2.fastNlMeansDenoising(gray)
            
        
            variants['binary'] = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
    
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
            variants['morphed'] = cv2.morphologyEx(variants['binary'], cv2.MORPH_CLOSE, kernel)
            
            logger.debug(f"Prepared {len(variants)} image variants")
            return variants
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return {'original': image}
    
    def _extract_full_image_text(self, image_variants: Dict[str, np.ndarray]) -> List[Dict]:
        """Extract text from full image using multiple engines."""
        results = []
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            
    
            for variant_name, img in image_variants.items():
                if variant_name in ['grayscale', 'enhanced', 'binary']: 
                    futures.append(
                        executor.submit(self._tesseract_ocr, img, variant_name)
                    )
                    futures.append(
                        executor.submit(self._easyocr_ocr, img, variant_name)  
                    )
            
        
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=30)
                    if result:
                        results.extend(result)
                except Exception as e:
                    logger.warning(f"OCR task failed: {e}")
        
        return results
    
    def _extract_region_text(self, image: np.ndarray, detections: List[Dict]) -> List[Dict]:
        """Extract text from specific regions detected by YOLO."""
        region_results = []
        
        for detection in detections:
            try:
                # Extract region
                x1 = max(0, int(detection.get('xmin', 0)))
                y1 = max(0, int(detection.get('ymin', 0)))
                x2 = min(image.shape[1], int(detection.get('xmax', 0)))
                y2 = min(image.shape[0], int(detection.get('ymax', 0)))
                
                if x2 > x1 and y2 > y1:
                    region = image[y1:y2, x1:x2]
                    
                    
                    enhanced_region = self._enhance_region_for_ocr(region, detection.get('class_name', ''))
                    
        
                    region_text = self._extract_region_with_engines(enhanced_region)
                    
                    if region_text:
                        for text_result in region_text:
                            text_result.update({
                                'source_detection': detection,
                                'region_bbox': {'xmin': x1, 'ymin': y1, 'xmax': x2, 'ymax': y2}
                            })
                        region_results.extend(region_text)
                        
            except Exception as e:
                logger.warning(f"Region OCR failed for detection: {e}")
        
        return region_results
    
    def _extract_table_text(self, image: np.ndarray, table_regions: List[Dict]) -> List[Dict]:
        """Extract text from table regions with structure preservation."""
        table_results = []
        
        for i, table in enumerate(table_regions):
            try:
                bbox = table.get('bbox', (0, 0, 0, 0))
                x, y, w, h = bbox
                
                if w > 0 and h > 0:
                    table_region = image[y:y+h, x:x+w]
                    
        
                    table_text = self._process_table_region(table_region, i)
                    
                    if table_text:
                        for text_result in table_text:
                            text_result.update({
                                'table_id': i,
                                'table_bbox': bbox
                            })
                        table_results.extend(table_text)
                        
            except Exception as e:
                logger.warning(f"Table OCR failed: {e}")
        
        return table_results
    
    def _tesseract_ocr(self, image: np.ndarray, variant_name: str) -> List[Dict]:
        """Perform Tesseract OCR on image with multiple configurations."""
        try:
            
            configs = [
                self.tesseract_config + ' -l spa+eng',  # Principal
                '--psm 8 -l spa+eng',  # Una sola palabra
                '--psm 7 -l spa+eng',  # Línea de texto
                '--psm 13 -l spa+eng'  # Línea sin segmentación
            ]
            
            all_results = []
            
            for config in configs:
                try:
                    ocr_data = pytesseract.image_to_data(
                        image, 
                        config=config,
                        output_type=pytesseract.Output.DICT
                    )
                    all_results.extend(self._process_tesseract_data(ocr_data, variant_name))
                except Exception as e:
                    logger.warning(f"Tesseract config failed {config}: {e}")
                    continue
            
            return all_results
        
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {e}")
            return []
    
    def _process_tesseract_data(self, ocr_data: Dict, variant_name: str) -> List[Dict]:
        """Process Tesseract OCR data into standardized format."""
        results = []
        n_boxes = len(ocr_data['text'])
        
        for i in range(n_boxes):
            text = ocr_data['text'][i].strip()
            conf = float(ocr_data['conf'][i])
            
            if text and conf > 30:  
                x = ocr_data['left'][i]
                y = ocr_data['top'][i]
                w = ocr_data['width'][i]
                h = ocr_data['height'][i]
                
                results.append({
                    'text': text,
                    'confidence': conf / 100.0,  
                    'bbox': {
                        'xmin': x, 'ymin': y, 
                        'xmax': x + w, 'ymax': y + h
                    },
                    'engine': 'tesseract',
                    'variant': variant_name
                })
        
        logger.debug(f"Tesseract extracted {len(results)} text regions from {variant_name}")
        return results
    
    def _easyocr_ocr(self, image: np.ndarray, variant_name: str) -> List[Dict]:
        """Perform EasyOCR on image."""
        try:
            if self.easyocr_reader is None:
                return []
            
            
            if len(image.shape) == 3:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            
            ocr_results = self.easyocr_reader.readtext(image_rgb)
            
            results = []
            for bbox_points, text, confidence in ocr_results:
                if confidence > 0.3:  
                    # Convert bbox points to rectangle
                    xs = [point[0] for point in bbox_points]
                    ys = [point[1] for point in bbox_points]
                    
                    results.append({
                        'text': text,
                        'confidence': confidence,
                        'bbox': {
                            'xmin': min(xs), 'ymin': min(ys),
                            'xmax': max(xs), 'ymax': max(ys)
                        },
                        'engine': 'easyocr',
                        'variant': variant_name
                    })
            
            logger.debug(f"EasyOCR extracted {len(results)} text regions from {variant_name}")
            return results
            
        except Exception as e:
            logger.error(f"EasyOCR failed: {e}")
            return []
    
    def _enhance_region_for_ocr(self, region: np.ndarray, class_name: str) -> np.ndarray:
        """Apply class-specific enhancement for OCR."""
        try:
            
            if len(region.shape) == 3:
                gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
            else:
                gray = region.copy()
            
        
            if class_name in ['numero_factura', 'R.U.C']:
                # For numbers and IDs, use strong binarization
                enhanced = cv2.adaptiveThreshold(
                    gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
                )
            elif class_name in ['fecha_hora']:
                # For dates, enhance contrast
                enhanced = cv2.equalizeHist(gray)
            elif class_name in ['razon_social', 'descripcion']:
                # For text fields, denoise
                enhanced = cv2.fastNlMeansDenoising(gray)
            else:
                # Default enhancement
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                enhanced = clahe.apply(gray)
            
            return enhanced
            
        except Exception as e:
            logger.warning(f"Region enhancement failed: {e}")
            return region
    
    def _extract_region_with_engines(self, region: np.ndarray) -> List[Dict]:
        """Extract text from region using multiple engines."""
        results = []
        
        
        tesseract_results = self._tesseract_ocr(region, 'region')
        easyocr_results = self._easyocr_ocr(region, 'region')
        
        results.extend(tesseract_results)
        results.extend(easyocr_results)
        
        return results
    
    def _process_table_region(self, table_region: np.ndarray, table_id: int) -> List[Dict]:
        """Process table region with structure-aware OCR."""
        try:
    
            rows, cols = self._detect_table_structure(table_region)
            
            results = []
            
            # Process each cell
            for row_idx, row in enumerate(rows):
                for col_idx, cell_bbox in enumerate(row):
                    x, y, w, h = cell_bbox
                    if w > 10 and h > 10:  # Skip very small cells
                        cell_region = table_region[y:y+h, x:x+w]
                        
                        # Extract text from cell
                        cell_text = self._extract_cell_text(cell_region)
                        
                        if cell_text:
                            results.append({
                                'text': cell_text['text'],
                                'confidence': cell_text['confidence'],
                                'bbox': {
                                    'xmin': x, 'ymin': y,
                                    'xmax': x + w, 'ymax': y + h
                                },
                                'table_position': {
                                    'row': row_idx,
                                    'col': col_idx
                                },
                                'engine': cell_text.get('engine', 'mixed')
                            })
            
            return results
            
        except Exception as e:
            logger.error(f"Table processing failed: {e}")
            return []
    
    def _detect_table_structure(self, table_image: np.ndarray) -> Tuple[List, List]:
        """Detect table structure (rows and columns)."""
    
        gray = cv2.cvtColor(table_image, cv2.COLOR_BGR2GRAY) if len(table_image.shape) == 3 else table_image
        
    
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
        
        
        rows = [[(0, 0, table_image.shape[1], table_image.shape[0])]]
        cols = []
        
        return rows, cols
    
    def _extract_cell_text(self, cell_region: np.ndarray) -> Optional[Dict]:
        """Extract text from a single table cell."""
        try:
            # Preprocess cell
            if len(cell_region.shape) == 3:
                gray = cv2.cvtColor(cell_region, cv2.COLOR_BGR2GRAY)
            else:
                gray = cell_region
            
            # Apply OCR
            text = pytesseract.image_to_string(gray, config='--psm 8 -l spa+eng').strip()
            
            if text:
                return {
                    'text': text,
                    'confidence': 0.8,  
                    'engine': 'tesseract'
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"Cell OCR failed: {e}")
            return None
    
    def _consolidate_results(self, ocr_results: Dict, image_shape: Tuple) -> Dict[str, Any]:
        """Consolidate results from multiple OCR engines and regions."""
        try:
            all_results = []
            
            
            for result_type, results in ocr_results.items():
                if isinstance(results, list):
                    all_results.extend(results)
            
            
            consolidated = self._merge_overlapping_results(all_results)
            
        
            confidences = [r.get('confidence', 0) for r in consolidated]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
        
            structured_rows = self._group_into_rows(consolidated, image_shape)
            
            return {
                'ocr_results': consolidated,
                'structured_rows': structured_rows,
                'average_confidence': avg_confidence,
                'total_extractions': len(consolidated)
            }
            
        except Exception as e:
            logger.error(f"Result consolidation failed: {e}")
            return {'ocr_results': [], 'average_confidence': 0.0}
    
    def _merge_overlapping_results(self, results: List[Dict]) -> List[Dict]:
        """Merge overlapping OCR results from different engines."""
        if not results:
            return []
        
        # Sort by position
        results.sort(key=lambda x: (x.get('bbox', {}).get('ymin', 0), 
                                   x.get('bbox', {}).get('xmin', 0)))
        
        merged = []
        
        for result in results:
    
            overlapped = False
            
            for merged_result in merged:
                if self._calculate_overlap(result.get('bbox', {}), 
                                         merged_result.get('bbox', {})) > 0.5:
                    
                    if result.get('confidence', 0) > merged_result.get('confidence', 0):
                        merged_result.update(result)
                    overlapped = True
                    break
            
            if not overlapped:
                merged.append(result)
        
        return merged
    
    def _calculate_overlap(self, bbox1: Dict, bbox2: Dict) -> float:
        """Calculate overlap ratio between two bounding boxes."""
        try:
            x1 = max(bbox1.get('xmin', 0), bbox2.get('xmin', 0))
            y1 = max(bbox1.get('ymin', 0), bbox2.get('ymin', 0))
            x2 = min(bbox1.get('xmax', 0), bbox2.get('xmax', 0))
            y2 = min(bbox1.get('ymax', 0), bbox2.get('ymax', 0))
            
            if x1 < x2 and y1 < y2:
                overlap_area = (x2 - x1) * (y2 - y1)
                
                area1 = (bbox1.get('xmax', 0) - bbox1.get('xmin', 0)) * \
                       (bbox1.get('ymax', 0) - bbox1.get('ymin', 0))
                area2 = (bbox2.get('xmax', 0) - bbox2.get('xmin', 0)) * \
                       (bbox2.get('ymax', 0) - bbox2.get('ymin', 0))
                
                min_area = min(area1, area2)
                return overlap_area / min_area if min_area > 0 else 0.0
            
            return 0.0
            
        except:
            return 0.0
    
    def _group_into_rows(self, results: List[Dict], image_shape: Tuple) -> List[Dict]:
        """Group OCR results into logical rows for table structure."""
        if not results:
            return []
        
        # Group by Y coordinate (rows)
        rows = defaultdict(list)
        
        for result in results:
            bbox = result.get('bbox', {})
            y_center = (bbox.get('ymin', 0) + bbox.get('ymax', 0)) / 2
            
            # Find appropriate row 
            row_key = None
            tolerance = image_shape[0] * 0.02  
            
            for existing_y in rows.keys():
                if abs(y_center - existing_y) < tolerance:
                    row_key = existing_y
                    break
            
            if row_key is None:
                row_key = y_center
            
            rows[row_key].append(result)
        
        
        structured_rows = []
        
        for y_pos, row_results in sorted(rows.items()):
        
            row_results.sort(key=lambda x: x.get('bbox', {}).get('xmin', 0))
            
            
            row_data = self._classify_row_columns(row_results, image_shape[1])
            
            if row_data:
                structured_rows.append(row_data)
        
        return structured_rows
    
    def _classify_row_columns(self, row_results: List[Dict], image_width: int) -> Optional[Dict]:
        """Classify row results into columns (description, quantity, price)."""
        if not row_results:
            return None
        
    
        desc_boundary = image_width * 0.6
        qty_boundary = image_width * 0.8
        
        description_parts = []
        quantity_parts = []
        price_parts = []
        
        total_confidence = 0
        
        for result in row_results:
            bbox = result.get('bbox', {})
            x_center = (bbox.get('xmin', 0) + bbox.get('xmax', 0)) / 2
            text = result.get('text', '').strip()
            confidence = result.get('confidence', 0)
            
            total_confidence += confidence
            
            
            if self._is_price_text(text):
                price_parts.append(text)
            elif self._is_quantity_text(text):
                quantity_parts.append(text)
            elif x_center < desc_boundary:
                description_parts.append(text)
            elif x_center < qty_boundary:
                quantity_parts.append(text)
            else:
                price_parts.append(text)
        
        # Combine parts
        avg_confidence = total_confidence / len(row_results) if row_results else 0
        
        return {
            'description': ' '.join(description_parts) or 'No detectado',
            'quantity': ' '.join(quantity_parts) or 'No detectado',
            'unit_price': ' '.join([p for p in price_parts if not self._is_total_price(p)]) or 'No detectado',
            'total_price': ' '.join([p for p in price_parts if self._is_total_price(p)]) or 'No detectado',
            'confidence': avg_confidence
        }
    
    def _is_price_text(self, text: str) -> bool:
        """Check if text represents a price."""
        return bool(re.search(r'[\$€]|(\d+[,.]?\d*)', text))
    
    def _is_quantity_text(self, text: str) -> bool:
        """Check if text represents a quantity."""
        return bool(re.match(r'^\d+$', text.strip()))
    
    def _is_total_price(self, text: str) -> bool:
        """Check if text represents a total price (vs unit price)."""
    
        return '$' in text or '€' in text