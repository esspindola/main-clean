"""
Advanced Text Processing Utilities
Intelligent text analysis and structure extraction
"""

import re
import logging
from typing import Dict, List, Any, Tuple, Optional
import numpy as np
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


class TextProcessor:
    """
    Advanced text processing for invoice data extraction.
    
    Features:
    - Intelligent text grouping and classification
    - Field type detection using patterns and context
    - Data validation and cleaning
    - Confidence scoring for extracted data
    """
    
    def __init__(self):
      
        self.patterns = {
            'ruc': [
                r'\b\d{10,13}\b',  # RUC numbers
                r'R\.?U\.?C\.?\s*:?\s*(\d{10,13})',
                r'RUC\s*:?\s*(\d{10,13})'
            ],
            'invoice_number': [
                r'\b\d{3}-\d{3}-\d{9}\b',  # Format: 005-002-000002389
                r'N[UÚ]MERO\s+DE\s+FACTURA\s*:?\s*([\d\-]+)',
                r'FACTURA\s*N[°º]?\s*:?\s*([\d\-]+)',
                r'No\.\s*FACTURA\s*:?\s*([\d\-]+)'
            ],
            'date': [
                r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b',
                r'FECHA\s*:?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
                r'(\d{1,2})\s+de\s+\w+\s+de\s+(\d{4})',
                r'EMISI[OÓ]N\s*:?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})'
            ],
            'monetary': [
                r'\$\s*[\d,]+\.?\d{0,2}',
                r'USD\s*[\d,]+\.?\d{0,2}',
                r'\b[\d,]+\.\d{2}\b'
            ],
            'quantity': [
                r'^\d+$',
                r'^\d+\.\d+$',
                r'CANTIDAD\s*:?\s*(\d+)',
                r'CANT\.\s*:?\s*(\d+)'
            ]
        }
        
        # Field classification rules
        self.field_keywords = {
            'company_name': ['empresa', 'razón social', 'compañía', 'sociedad'],
            'description': ['descripción', 'producto', 'servicio', 'concepto', 'detalle'],
            'quantity': ['cantidad', 'cant', 'qty', 'unidades', 'pcs'],
            'unit_price': ['precio unitario', 'precio unit', 'p. unit', 'valor unit'],
            'total_price': ['precio total', 'total', 'importe', 'valor total'],
            'subtotal': ['subtotal', 'sub total', 'base imponible'],
            'tax': ['iva', 'impuesto', 'tax', 'igv'],
            'total': ['total', 'total a pagar', 'total factura', 'importe total']
        }
        
        logger.info("TextProcessor initialized")
    
    def process_extracted_text(self, ocr_results: Dict[str, Any], 
                              detections: List[Dict], image_shape: Tuple) -> Dict[str, Any]:
        """
        Process and structure extracted text from OCR results.
        
        Args:
            ocr_results: OCR extraction results
            detections: YOLO detection results
            image_shape: Original image dimensions
            
        Returns:
            Processed and structured text data
        """
        try:
            
            all_text_results = ocr_results.get('ocr_results', [])
            structured_rows = ocr_results.get('structured_rows', [])
            
         
            enhanced_rows = self._enhance_row_classification(structured_rows, image_shape)
            
           
            key_value_pairs = self._extract_key_value_pairs(all_text_results)
            
          
            cleaned_data = self._clean_extracted_data(key_value_pairs)
            
          
            confidence_scores = [result.get('confidence', 0) for result in all_text_results]
            average_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
            
            return {
                'structured_rows': enhanced_rows,
                'key_value_pairs': cleaned_data,
                'all_extractions': all_text_results,
                'average_confidence': average_confidence,
                'extraction_stats': {
                    'total_texts': len(all_text_results),
                    'structured_rows': len(enhanced_rows),
                    'confidence_distribution': self._analyze_confidence_distribution(confidence_scores)
                }
            }
            
        except Exception as e:
            logger.error(f"Text processing failed: {e}")
            return {
                'structured_rows': [],
                'key_value_pairs': {},
                'all_extractions': [],
                'average_confidence': 0.0
            }
    
    def _enhance_row_classification(self, rows: List[Dict], image_shape: Tuple) -> List[Dict]:
        """Enhance row classification with better field detection."""
        enhanced_rows = []
        
        for row in rows:
            enhanced_row = row.copy()
            
          
            description = row.get('description', '')
            enhanced_row['description'] = self._clean_description_text(description)
            
          
            quantity = row.get('quantity', '')
            enhanced_row['quantity'] = self._clean_quantity_text(quantity)
            
          
            unit_price = row.get('unit_price', '')
            total_price = row.get('total_price', '')
            
            enhanced_row['unit_price'] = self._clean_price_text(unit_price)
            enhanced_row['total_price'] = self._clean_price_text(total_price)
            
         
            enhanced_row['field_types'] = self._classify_row_fields(enhanced_row)
            
         
            enhanced_row['confidence'] = self._calculate_row_confidence(enhanced_row)
            
            enhanced_rows.append(enhanced_row)
        
        return enhanced_rows
    
    def _extract_key_value_pairs(self, text_results: List[Dict]) -> Dict[str, str]:
        """Extract key-value pairs from text results."""
        key_value_pairs = {}
        
    
        all_text = ' '.join([result.get('text', '') for result in text_results])
        
        # Extract RUC
        ruc_value = self._extract_pattern_value(all_text, self.patterns['ruc'])
        if ruc_value:
            key_value_pairs['ruc'] = ruc_value
        
        # Extract invoice number
        invoice_number = self._extract_pattern_value(all_text, self.patterns['invoice_number'])
        if invoice_number:
            key_value_pairs['invoice_number'] = invoice_number
        
        # Extract date
        date_value = self._extract_pattern_value(all_text, self.patterns['date'])
        if date_value:
            key_value_pairs['date'] = date_value
        
      
        company_name = self._extract_company_name(text_results)
        if company_name:
            key_value_pairs['company_name'] = company_name
        
     
        monetary_values = self._extract_monetary_values(all_text)
        key_value_pairs.update(monetary_values)
        
        return key_value_pairs
    
    def _extract_pattern_value(self, text: str, patterns: List[str]) -> Optional[str]:
        """Extract value using regex patterns."""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
              
                return match.group(1) if match.groups() else match.group(0)
        return None
    
    def _extract_company_name(self, text_results: List[Dict]) -> Optional[str]:
        """Extract company name using position and context."""
       
        company_candidates = []
        
        for result in text_results:
            text = result.get('text', '').strip()
            bbox = result.get('bbox', {})
            y_pos = bbox.get('ymin', 0)
            
         
            if y_pos < 0.3 and len(text) > 5:
              
                if not any(keyword in text.lower() for keyword in 
                          ['factura', 'ruc', 'fecha', 'número', 'autorización']):
                    company_candidates.append({
                        'text': text,
                        'y_pos': y_pos,
                        'confidence': result.get('confidence', 0)
                    })
        
       
        if company_candidates:
            best_candidate = max(company_candidates, 
                               key=lambda x: x['confidence'] * (1 - x['y_pos']))
            return best_candidate['text']
        
        return None
    
    def _extract_monetary_values(self, text: str) -> Dict[str, str]:
        """Extract monetary values (subtotal, tax, total)."""
        monetary_values = {}
        
      
        monetary_patterns = {
            'subtotal': [
                r'SUBTOTAL\s*:?\s*\$?\s*([\d,]+\.?\d{0,2})',
                r'SUB\s*TOTAL\s*:?\s*\$?\s*([\d,]+\.?\d{0,2})',
                r'BASE\s*IMPONIBLE\s*:?\s*\$?\s*([\d,]+\.?\d{0,2})'
            ],
            'iva': [
                r'IVA\s*\d*%?\s*:?\s*\$?\s*([\d,]+\.?\d{0,2})',
                r'IMPUESTO\s*:?\s*\$?\s*([\d,]+\.?\d{0,2})',
                r'TAX\s*:?\s*\$?\s*([\d,]+\.?\d{0,2})'
            ],
            'total': [
                r'TOTAL\s*:?\s*\$?\s*([\d,]+\.?\d{0,2})',
                r'TOTAL\s*A\s*PAGAR\s*:?\s*\$?\s*([\d,]+\.?\d{0,2})',
                r'IMPORTE\s*TOTAL\s*:?\s*\$?\s*([\d,]+\.?\d{0,2})',
                r'VALOR\s*TOTAL\s*:?\s*\$?\s*([\d,]+\.?\d{0,2})'
            ]
        }
        
        for field_name, patterns in monetary_patterns.items():
            value = self._extract_pattern_value(text, patterns)
            if value:
              
                formatted_value = self._format_monetary_value(value)
                if formatted_value:
                    monetary_values[field_name] = formatted_value
        
        return monetary_values
    
    def _clean_description_text(self, text: str) -> str:
        """Clean and standardize description text."""
        if not text or text == 'No detectado':
            return 'No detectado'
        
    
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        cleaned = re.sub(r'[^\w\s\.\,\-\(\)\[\]]', ' ', cleaned)
        
        
        words = cleaned.split()
        filtered_words = [word for word in words if len(word) > 1 or word.isdigit()]
        
        result = ' '.join(filtered_words).strip()
        return result if result else 'No detectado'
    
    def _clean_quantity_text(self, text: str) -> str:
        """Clean and standardize quantity text."""
        if not text or text == 'No detectado':
            return 'No detectado'
        
   
        numeric_match = re.search(r'(\d+(?:\.\d+)?)', text)
        if numeric_match:
            return numeric_match.group(1)
        
        return 'No detectado'
    
    def _clean_price_text(self, text: str) -> str:
        """Clean and standardize price text."""
        if not text or text == 'No detectado':
            return 'No detectado'
        
     
        price_match = re.search(r'[\$]?\s*([\d,]+\.?\d{0,2})', text)
        if price_match:
            value = price_match.group(1)
            return self._format_monetary_value(value)
        
        return 'No detectado'
    
    def _format_monetary_value(self, value: str) -> str:
        """Format monetary value consistently."""
        try:
         
            cleaned_value = re.sub(r'[^\d\.]', '', value)
            
          
            numeric_value = float(cleaned_value)
            
         
            formatted = f"${numeric_value:.2f}"
            
            return formatted
            
        except (ValueError, TypeError):
            return value
    
    def _classify_row_fields(self, row: Dict) -> Dict[str, str]:
        """Classify the type of content in each field of a row."""
        field_types = {}
        
        for field_name, content in row.items():
            if field_name in ['description', 'quantity', 'unit_price', 'total_price']:
                field_type = self._classify_field_content(content, field_name)
                field_types[field_name] = field_type
        
        return field_types
    
    def _classify_field_content(self, content: str, expected_field: str) -> str:
        """Classify the type of content in a field."""
        if not content or content == 'No detectado':
            return 'empty'
        
      
        if re.search(r'[\$€]|(\d+[,.]?\d*)', content):
            return 'monetary'
        
      
        if re.match(r'^\d+(\.\d+)?$', content.strip()):
            return 'numeric'
        
      
        if len(content.split()) > 2:
            return 'text_description'
        
    
        if re.search(r'\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}', content):
            return 'date'
        
     
        return 'text'
    
    def _calculate_row_confidence(self, row: Dict) -> float:
        """Calculate confidence score for a row based on field quality."""
        confidence_factors = []
        
        original_confidence = row.get('confidence', 0.0)
        confidence_factors.append(original_confidence)
        
     
        fields = ['description', 'quantity', 'unit_price', 'total_price']
        non_empty_fields = sum(1 for field in fields 
                              if row.get(field, 'No detectado') != 'No detectado')
        completeness_score = non_empty_fields / len(fields)
        confidence_factors.append(completeness_score)
        
    
        field_types = row.get('field_types', {})
        type_consistency = 0.0
        
        if field_types.get('quantity') in ['numeric', 'monetary']:
            type_consistency += 0.25
        if field_types.get('unit_price') == 'monetary':
            type_consistency += 0.25
        if field_types.get('total_price') == 'monetary':
            type_consistency += 0.25
        if field_types.get('description') in ['text_description', 'text']:
            type_consistency += 0.25
        
        confidence_factors.append(type_consistency)
        
      
        weights = [0.4, 0.3, 0.3]  
        final_confidence = sum(f * w for f, w in zip(confidence_factors, weights))
        
        return min(max(final_confidence, 0.0), 1.0)
    
    def _clean_extracted_data(self, data: Dict[str, str]) -> Dict[str, str]:
        """Clean and validate extracted key-value data."""
        cleaned_data = {}
        
        for key, value in data.items():
            if not value:
                continue
            
            if key == 'ruc':
             
                cleaned_ruc = re.sub(r'[^\d]', '', value)
                if len(cleaned_ruc) >= 10:
                    cleaned_data[key] = cleaned_ruc
            
            elif key == 'date':
              
                cleaned_date = self._standardize_date(value)
                if cleaned_date:
                    cleaned_data[key] = cleaned_date
            
            elif key in ['subtotal', 'iva', 'total']:
              
                formatted_value = self._format_monetary_value(value)
                if formatted_value:
                    cleaned_data[key] = formatted_value
            
            else:
            
                cleaned_value = re.sub(r'\s+', ' ', value.strip())
                if cleaned_value:
                    cleaned_data[key] = cleaned_value
        
        return cleaned_data
    
    def _standardize_date(self, date_str: str) -> Optional[str]:
        """Standardize date format."""
        try:
           
            patterns = [
                r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2,4})',
                r'(\d{1,2})\s+de\s+\w+\s+de\s+(\d{4})'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, date_str)
                if match:
                    if len(match.groups()) == 3:
                        day, month, year = match.groups()
                     
                        if len(year) == 2:
                            year = '20' + year if int(year) < 50 else '19' + year
                        return f"{day.zfill(2)}/{month.zfill(2)}/{year}"
            
            return date_str  
            
        except Exception as e:
            logger.warning(f"Date standardization failed: {e}")
            return date_str
    
    def _analyze_confidence_distribution(self, confidence_scores: List[float]) -> Dict[str, Any]:
        """Analyze the distribution of confidence scores."""
        if not confidence_scores:
            return {'mean': 0.0, 'std': 0.0, 'min': 0.0, 'max': 0.0}
        
        scores_array = np.array(confidence_scores)
        
        return {
            'mean': float(np.mean(scores_array)),
            'std': float(np.std(scores_array)),
            'min': float(np.min(scores_array)),
            'max': float(np.max(scores_array)),
            'median': float(np.median(scores_array)),
            'quartiles': {
                'q25': float(np.percentile(scores_array, 25)),
                'q75': float(np.percentile(scores_array, 75))
            }
        }