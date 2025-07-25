
"""
Sistema Inteligente de Análisis de Facturas - Nivel PhD
Análisis adaptativo para múltiples formatos de facturas con IA avanzada

Autor: Sistema IA Avanzado
Versión: 3.0.0 - Adaptativo e Inteligente
"""

import re
import cv2
import numpy as np
import pandas as pd
import pytesseract
from pathlib import Path
import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class InvoiceField:
    """Representa un campo de factura detectado"""
    field_type: str
    text: str
    confidence: float
    bbox: Dict[str, int]
    ocr_confidence: float
    source: str  # 'yolo', 'pattern', 'hybrid'

@dataclass
class InvoiceAnalysisResult:
    """Resultado completo del análisis de factura"""
    success: bool
    message: str
    metadata: Dict[str, str]
    line_items: List[Dict[str, Any]]
    detections: List[Dict[str, Any]]
    processed_image: Optional[str]
    processing_time: float
    statistics: Dict[str, Any]
    class_regions: Dict[str, List[Dict]]
    confidence_score: float
    format_detected: str

class IntelligentInvoiceAnalyzer:
    """Analizador inteligente de facturas con capacidades adaptativas"""
    
    def __init__(self):
        # Patrones inteligentes para diferentes tipos de facturas
        self.patterns = {
            'ruc': [
                r'R\.?U\.?C\.?\s*:?\s*(\d{11,13})',
                r'RUC[\s:]*(\d{11,13})',
                r'CI/RUC[\s:]*(\d{8,13})',
                r'(?:CEDULA|CÉDULA|CI)[\s:]*(\d{8,13})',
            ],
            'fecha': [
                r'FECHA[\s:]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'(\d{4}-\d{2}-\d{2})',
                r'(\d{2}/\d{2}/\d{4})',
                r'EMISION[\s:]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            ],
            'numero_factura': [
                r'FACTURA[\s#:Nº]*(\d{3,15})',
                r'(?:FACT|FAC)[\s#:Nº]*(\d{3,15})',
                r'(?:INVOICE|INV)[\s#:Nº]*(\d{3,15})',
                r'N[ºo°]\.?\s*(\d{3,15})',
                r'(\d{3}-\d{3}-\d{6,9})',
                r'DOCUMENTO[\s#:]*(\d{3,15})',
            ],
            'razon_social': [
                r'(?:RAZON SOCIAL|RAZÓN SOCIAL)[\s:]*([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ\s]{5,50})',
                r'(?:EMPRESA|COMPANY)[\s:]*([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ\s]{5,50})',
                r'(?:CLIENTE|CLIENT)[\s:]*([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ\s]{5,50})',
            ],
            'subtotal': [
                r'SUBTOTAL[\s:$]*(\d+[.,]\d{2})',
                r'SUB[\s\-]*TOTAL[\s:$]*(\d+[.,]\d{2})',
                r'BASE[\s]*IMPONIBLE[\s:$]*(\d+[.,]\d{2})',
            ],
            'iva': [
                r'I\.?V\.?A\.?[\s:$%]*(\d+[.,]\d{2})',
                r'IMPUESTO[\s:$]*(\d+[.,]\d{2})',
                r'TAX[\s:$]*(\d+[.,]\d{2})',
                r'(?:12%|15%)[\s:$]*(\d+[.,]\d{2})',
            ],
            'total': [
                r'TOTAL[\s:$]*(\d+[.,]\d{2})',
                r'TOTAL\s*A\s*PAGAR[\s:$]*(\d+[.,]\d{2})',
                r'IMPORTE[\s]*TOTAL[\s:$]*(\d+[.,]\d{2})',
                r'GRAN[\s]*TOTAL[\s:$]*(\d+[.,]\d{2})',
                r'VALOR[\s]*TOTAL[\s:$]*(\d+[.,]\d{2})',
            ]
        }
        
       
        self.ocr_configs = {
            'general': '--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzáéíóúñÁÉÍÓÚÑ0123456789.,:/- ',
            'numbers': '--psm 8 -c tessedit_char_whitelist=0123456789.,',
            'dates': '--psm 8 -c tessedit_char_whitelist=0123456789/-',
            'text_only': '--psm 7',
            'single_line': '--psm 8',
            'sparse_text': '--psm 11',
        }
        
        # Clases esperadas para detección YOLO
        self.expected_classes = [
            'logo', 'razon_social', 'R.U.C', 'numero_factura', 'fecha_hora',
            'descripcion', 'cantidad', 'precio_unitario', 'precio_total',
            'subtotal', 'iva', 'total_amount', 'product_table', 'header',
            'footer', 'barcode', 'qr_code', 'signature'
        ]

    def preprocess_image_intelligent(self, image: np.ndarray) -> Dict[str, np.ndarray]:
        """Preprocesa la imagen con múltiples técnicas para mejorar OCR"""
        preprocessed = {}
        
  
        preprocessed['original'] = image.copy()
        

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        preprocessed['gray'] = gray
        
        # Binarización adaptativa
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        preprocessed['binary'] = binary
        
        # Reducción de ruido
        denoised = cv2.medianBlur(gray, 3)
        preprocessed['denoised'] = denoised
        
        # Mejora de contraste
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        preprocessed['enhanced'] = enhanced
        
  
        kernel = np.ones((1,1), np.uint8)
        dilated = cv2.dilate(gray, kernel, iterations=1)
        preprocessed['dilated'] = dilated
        
        return preprocessed

    def extract_text_with_multiple_strategies(self, image: np.ndarray, field_type: str = 'general') -> List[Tuple[str, float]]:
        """Extrae texto usando múltiples estrategias OCR"""
        results = []
        
        # Preprocesar imagen
        preprocessed_images = self.preprocess_image_intelligent(image)
        
       
        for prep_name, prep_image in preprocessed_images.items():
            for config_name, config in self.ocr_configs.items():
                try:
                 
                    if field_type in ['ruc', 'numero_factura'] and config_name in ['numbers', 'single_line']:
                        text = pytesseract.image_to_string(prep_image, config=config, lang='spa+eng')
                    elif field_type == 'fecha' and config_name in ['dates', 'single_line']:
                        text = pytesseract.image_to_string(prep_image, config=config, lang='spa+eng')
                    elif config_name == 'general':
                        text = pytesseract.image_to_string(prep_image, config=config, lang='spa+eng')
                    else:
                        continue
                    
                    if text.strip():
                      
                        confidence = min(0.9, len(text.strip()) / 50 + 0.3)
                        results.append((text.strip(), confidence))
                        
                except Exception as e:
                    logger.debug(f"OCR falló para {prep_name} + {config_name}: {e}")
                    continue
        
        # EasyOCR como respaldo
        try:
            import easyocr
            reader = easyocr.Reader(['es', 'en'])
            easy_results = reader.readtext(image)
            for (bbox, text, conf) in easy_results:
                if conf > 0.3 and text.strip():
                    results.append((text.strip(), conf))
        except Exception as e:
            logger.debug(f"EasyOCR falló: {e}")
        
      
        unique_results = {}
        for text, conf in results:
            clean_text = re.sub(r'\s+', ' ', text).strip()
            if clean_text and len(clean_text) > 1:
                if clean_text not in unique_results or unique_results[clean_text] < conf:
                    unique_results[clean_text] = conf
        
        return [(text, conf) for text, conf in sorted(unique_results.items(), key=lambda x: x[1], reverse=True)]

    def apply_intelligent_patterns(self, full_text: str) -> Dict[str, InvoiceField]:
        """Aplica patrones inteligentes para extraer campos específicos"""
        detected_fields = {}
        
        logger.info(f"📝 Aplicando patrones inteligentes a texto de {len(full_text)} caracteres")
        
        for field_type, patterns in self.patterns.items():
            best_match = None
            best_confidence = 0
            
            for pattern in patterns:
                try:
                    matches = re.finditer(pattern, full_text, re.IGNORECASE | re.MULTILINE)
                    for match in matches:
                        text = match.group(1) if match.groups() else match.group(0)
                        
                       
                        confidence = 0.7  
                        
                      
                        context_before = full_text[max(0, match.start()-20):match.start()]
                        context_after = full_text[match.end():min(len(full_text), match.end()+20)]
                        
                        if field_type in context_before.lower() or field_type in context_after.lower():
                            confidence += 0.2
                        
                        if confidence > best_confidence:
                            best_match = text
                            best_confidence = confidence
                            
                except Exception as e:
                    logger.debug(f"Error aplicando patrón {pattern}: {e}")
                    continue
            
            if best_match:
                detected_fields[field_type] = InvoiceField(
                    field_type=field_type,
                    text=best_match,
                    confidence=best_confidence,
                    bbox={'xmin': 0, 'ymin': 0, 'xmax': 100, 'ymax': 100},
                    ocr_confidence=best_confidence,
                    source='pattern'
                )
                logger.info(f"🎯 {field_type}: '{best_match}' (confianza: {best_confidence:.2f})")
        
        return detected_fields

    def detect_invoice_format(self, text: str) -> str:
        """Detecta el formato/tipo de factura basado en el texto"""
        text_lower = text.lower()
        
        # Facturas electrónicas ecuatorianas
        if re.search(r'\d{49}', text) or 'autorizacion' in text_lower:
            return 'factura_electronica_ecuador'
        
        # Recibos/tickets
        if any(word in text_lower for word in ['ticket', 'recibo', 'comprobante']):
            return 'ticket_recibo'
        
        # Facturas comerciales
        if any(word in text_lower for word in ['factura', 'invoice', 'bill']):
            return 'factura_comercial'
        
        # Presupuestos
        if any(word in text_lower for word in ['presupuesto', 'cotizacion', 'quote']):
            return 'presupuesto'
        
        return 'formato_desconocido'

    def extract_product_lines_intelligent(self, text: str, format_type: str) -> List[Dict[str, Any]]:
        """Extrae líneas de productos de manera inteligente según el formato"""
        products = []
        
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if len(line) < 5:  
                continue
            
          
        
            pattern1 = r'(\d+(?:[.,]\d+)?)\s+(.+?)\s+(\d+[.,]\d{2})'
            # Patrón: descripción + cantidad + precio unitario + total
            pattern2 = r'(.+?)\s+(\d+)\s+(\d+[.,]\d{2})\s+(\d+[.,]\d{2})'
            
            match1 = re.search(pattern1, line)
            match2 = re.search(pattern2, line)
            
            if match1:
                products.append({
                    'description': match1.group(2).strip(),
                    'quantity': match1.group(1),
                    'unit_price': match1.group(3),
                    'total_price': match1.group(3),
                    'confidence': 0.8,
                    'source': 'pattern1'
                })
            elif match2:
                products.append({
                    'description': match2.group(1).strip(),
                    'quantity': match2.group(2),
                    'unit_price': match2.group(3),
                    'total_price': match2.group(4),
                    'confidence': 0.85,
                    'source': 'pattern2'
                })
            else:
             
                if any(word in line.lower() for word in ['producto', 'item', 'art', 'serv']):
                    products.append({
                        'description': line,
                        'quantity': '1',
                        'unit_price': '0.00',
                        'total_price': '0.00',
                        'confidence': 0.5,
                        'source': 'heuristic'
                    })
        
        logger.info(f"📦 Productos extraídos: {len(products)}")
        return products

    def analyze_with_yolo_integration(self, image: np.ndarray, yolo_detections: pd.DataFrame) -> Dict[str, InvoiceField]:
        """Integra detecciones YOLO con análisis inteligente"""
        yolo_fields = {}
        
        if yolo_detections.empty:
            logger.warning("⚠️ No hay detecciones YOLO disponibles")
            return yolo_fields
        
        logger.info(f"🔍 Procesando {len(yolo_detections)} detecciones YOLO")
        
        for _, detection in yolo_detections.iterrows():
            try:
                class_name = detection['name']
                confidence = float(detection['confidence'])
                
                if confidence < 0.25:
                    continue
                
            
                x_min, y_min = int(detection['xmin']), int(detection['ymin'])
                x_max, y_max = int(detection['xmax']), int(detection['ymax'])
                
              
                h, w = image.shape[:2]
                x_min = max(0, min(x_min, w-1))
                y_min = max(0, min(y_min, h-1))
                x_max = max(x_min+1, min(x_max, w))
                y_max = max(y_min+1, min(y_max, h))
                
                region = image[y_min:y_max, x_min:x_max]
                
                if region.size == 0:
                    continue
                
            
                text_results = self.extract_text_with_multiple_strategies(region, class_name)
                
                if text_results:
                    best_text, ocr_conf = text_results[0]
                    
                    yolo_fields[class_name] = InvoiceField(
                        field_type=class_name,
                        text=best_text,
                        confidence=confidence,
                        bbox={'xmin': x_min, 'ymin': y_min, 'xmax': x_max, 'ymax': y_max},
                        ocr_confidence=ocr_conf,
                        source='yolo'
                    )
                    
                    logger.info(f"🎯 YOLO {class_name}: '{best_text}' (YOLO: {confidence:.2f}, OCR: {ocr_conf:.2f})")
                
            except Exception as e:
                logger.error(f"Error procesando detección YOLO {detection.get('name', 'unknown')}: {e}")
                continue
        
        return yolo_fields

    def merge_and_validate_fields(self, yolo_fields: Dict[str, InvoiceField], pattern_fields: Dict[str, InvoiceField]) -> Dict[str, InvoiceField]:
        """Combina y valida campos de YOLO y patrones, eligiendo los mejores"""
        merged_fields = {}
        
        # Mapeo de nombres de clases
        class_mapping = {
            'R.U.C': 'ruc',
            'razon_social': 'razon_social',
            'numero_factura': 'numero_factura',
            'fecha_hora': 'fecha',
            'total_amount': 'total',
            'subtotal': 'subtotal',
            'iva': 'iva'
        }
        
       
        for yolo_class, field in yolo_fields.items():
            mapped_name = class_mapping.get(yolo_class, yolo_class)
            merged_fields[mapped_name] = field
        
     
        for pattern_name, field in pattern_fields.items():
            if pattern_name in merged_fields:
             
                existing = merged_fields[pattern_name]
                combined_conf_existing = (existing.confidence + existing.ocr_confidence) / 2
                combined_conf_new = (field.confidence + field.ocr_confidence) / 2
                
                if combined_conf_new > combined_conf_existing or len(field.text) > len(existing.text):
                    merged_fields[pattern_name] = field
                    logger.info(f"🔄 Reemplazado {pattern_name} con mejor resultado de patrones")
            else:
                merged_fields[pattern_name] = field
                logger.info(f"➕ Agregado {pattern_name} desde patrones")
        
        return merged_fields

    def analyze_invoice_intelligent(self, image: np.ndarray, yolo_detections: pd.DataFrame = None) -> InvoiceAnalysisResult:
        """Análisis principal inteligente de factura"""
        start_time = datetime.now()
        
        logger.info("🚀 Iniciando análisis inteligente de factura")
        
    
        full_text_results = self.extract_text_with_multiple_strategies(image, 'general')
        full_text = full_text_results[0][0] if full_text_results else ""
        
        logger.info(f"📄 Texto extraído: {len(full_text)} caracteres")
        
    
        format_type = self.detect_invoice_format(full_text)
        logger.info(f"📋 Formato detectado: {format_type}")
        
   
        pattern_fields = self.apply_intelligent_patterns(full_text)
        
        # 4. Análisis con YOLO (si disponible)
        yolo_fields = {}
        if yolo_detections is not None and not yolo_detections.empty:
            yolo_fields = self.analyze_with_yolo_integration(image, yolo_detections)
        
        # 5. Combinar y validar resultados
        final_fields = self.merge_and_validate_fields(yolo_fields, pattern_fields)
        
        # 6. Extraer productos/líneas de items
        line_items = self.extract_product_lines_intelligent(full_text, format_type)
        
        # 7. Calcular confianza general
        if final_fields:
            confidence_score = sum(field.confidence for field in final_fields.values()) / len(final_fields)
        else:
            confidence_score = 0.1
        
        # 8. Preparar metadatos
        metadata = {}
        for field_name, field in final_fields.items():
            if field_name in ['ruc', 'razon_social', 'numero_factura', 'fecha', 'subtotal', 'iva', 'total']:
                metadata[field_name] = field.text
        
        # Mapear nombres para compatibilidad con frontend
        metadata_mapped = {
            'company_name': metadata.get('razon_social', ''),
            'ruc': metadata.get('ruc', ''),
            'invoice_number': metadata.get('numero_factura', ''),
            'date': metadata.get('fecha', ''),
            'subtotal': metadata.get('subtotal', ''),
            'iva': metadata.get('iva', ''),
            'total': metadata.get('total', '')
        }
        
        # 9. Preparar detecciones para frontend
        detections = []
        for field in final_fields.values():
            detections.append({
                'field_type': field.field_type,
                'text': field.text,
                'confidence': field.confidence,
                'bbox': field.bbox,
                'ocr_confidence': field.ocr_confidence
            })
        
        # 10. Estadísticas
        processing_time = (datetime.now() - start_time).total_seconds()
        
        statistics = {
            'yolo_detections': len(yolo_fields),
            'pattern_detections': len(pattern_fields),
            'total_fields': len(final_fields),
            'table_regions': 1 if line_items else 0,
            'ocr_confidence': confidence_score,
            'model_status': {
                'yolo_loaded': yolo_detections is not None,
                'classes_count': len(self.expected_classes),
                'is_loaded': True
            }
        }
        
        # 11. Regiones por clase
        class_regions = {}
        for field_name, field in final_fields.items():
            class_regions[field_name] = [{
                'text': field.text,
                'bbox': field.bbox,
                'confidence': field.confidence
            }]
        
        result = InvoiceAnalysisResult(
            success=True,
            message=f"Factura analizada exitosamente - Formato: {format_type}",
            metadata=metadata_mapped,
            line_items=line_items,
            detections=detections,
            processed_image=None,  # Se genera por separado
            processing_time=processing_time,
            statistics=statistics,
            class_regions=class_regions,
            confidence_score=confidence_score,
            format_detected=format_type
        )
        
        logger.info(f"✅ Análisis completado en {processing_time:.2f}s - Confianza: {confidence_score:.2f}")
        return result

# Crear instancia global
intelligent_analyzer = IntelligentInvoiceAnalyzer()