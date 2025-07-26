
"""
SISTEMA OCR ULTRA LIGERO - SOLO PATRONES INTELIGENTES
Sin PyTorch, sin YOLO, sin EasyOCR - Solo Tesseract + Patrones NLP
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from PIL import Image
from pdf2image import convert_from_bytes
import pandas as pd
import cv2
import pytesseract
import traceback
import base64
import time
import re
from pathlib import Path
import io

app = Flask(__name__)

# CORS configuration
CORS(app, 
     resources={
         r"/*": {
             "origins": [
                 "http://localhost:5173",
                 "http://localhost:3000", 
                 "http://localhost:4444",
                 "http://localhost:8001",
                 "http://127.0.0.1:5173",
                 "http://127.0.0.1:3000",
                 "http://127.0.0.1:4444", 
                 "http://127.0.0.1:8001"
             ],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
             "supports_credentials": True
         }
     })

print("✅ SISTEMA OCR ULTRA LIGERO - PATTERN-ONLY MODE")
print("🚀 Skipping YOLO/PyTorch for maximum speed and efficiency")

def allowed_file(filename):
    """Verificar tipos de archivo permitidos"""
    allowed_extensions = {'png', 'jpg', 'jpeg', 'tiff', 'bmp', 'pdf'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def clean_text(text):
    """Limpia texto OCR"""
    if not text:
        return ""
   
    cleaned = re.sub(r'[^\w\s.,:-]', '', str(text))
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def extract_invoice_patterns(full_text):
    """Sistema inteligente de extracción basado en patrones NLP"""
    print(f"🧠 Analizando texto con patrones inteligentes: {len(full_text)} caracteres")
    
  
    patterns = {
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
            r'(?:INVOICE|INV)[\s#:]*(\d{3,15})',
            r'N[ºo°]\.?\s*(\d{3,15})',
            r'(\d{3}-\d{3}-\d{6,9})',
        ],
        'empresa': [
            r'(?:RAZON SOCIAL|RAZÓN SOCIAL)[\s:]*([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ\s&\.]{8,60})',
            r'(?:EMPRESA|COMPANY)[\s:]*([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ\s&\.]{8,60})',
        ],
        'subtotal': [
            r'SUBTOTAL[\s:$]*(\d+[.,]\d{2})',
            r'SUB[\s\-]*TOTAL[\s:$]*(\d+[.,]\d{2})',
            r'BASE[\s]*IMPONIBLE[\s:$]*(\d+[.,]\d{2})',
        ],
        'iva': [
            r'I\.?V\.?A\.?[\s:$%]*(\d+[.,]\d{2})',
            r'IMPUESTO[\s:$]*(\d+[.,]\d{2})',
            r'(?:12%|15%)[\s:$]*(\d+[.,]\d{2})',
        ],
        'total': [
            r'TOTAL[\s:$]*(\d+[.,]\d{2})',
            r'TOTAL\s*A\s*PAGAR[\s:$]*(\d+[.,]\d{2})',
            r'IMPORTE[\s]*TOTAL[\s:$]*(\d+[.,]\d{2})',
            r'GRAN[\s]*TOTAL[\s:$]*(\d+[.,]\d{2})',
        ]
    }
    
    extracted_data = {}
    
    for field_type, pattern_list in patterns.items():
        best_match = None
        best_confidence = 0
        
        for pattern in pattern_list:
            try:
                matches = re.finditer(pattern, full_text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    text = match.group(1) if match.groups() else match.group(0)
                    
                    # Calcular confianza 
                    confidence = 0.8  # Base confidence
                    
                    # Bonus por contexto
                    context = full_text[max(0, match.start()-30):min(len(full_text), match.end()+30)]
                    if any(keyword in context.lower() for keyword in [field_type, 'factura', 'invoice']):
                        confidence += 0.15
                    
                    if confidence > best_confidence:
                        best_match = text.strip()
                        best_confidence = confidence
                        
            except Exception as e:
                continue
        
        if best_match:
            extracted_data[field_type] = best_match
            print(f"🎯 {field_type}: '{best_match}' (confianza: {best_confidence:.2f})")
    
    return extracted_data

def extract_line_items_smart(full_text):
    """Extracción inteligente de productos/items"""
    products = []
    lines = full_text.split('\n')
    
    print(f"📦 Analizando {len(lines)} líneas para productos...")
    
    for i, line in enumerate(lines):
        line = line.strip()
        if len(line) < 8: 
            continue
        
      
        pattern1 = r'(\d+(?:[.,]\d+)?)\s+(.{5,40}?)\s+(\d+[.,]\d{2})'
        match1 = re.search(pattern1, line)
        
     
        pattern2 = r'(.{5,40}?)\s+(\d+)\s+(\d+[.,]\d{2})\s+(\d+[.,]\d{2})'
        match2 = re.search(pattern2, line)
        
        if match1:
            desc = clean_text(match1.group(2))
            if len(desc) > 3:  
                products.append({
                    'description': desc,
                    'quantity': match1.group(1),
                    'unit_price': f"${match1.group(3)}",
                    'total_price': f"${match1.group(3)}",
                    'confidence': 0.85
                })
                
        elif match2:
            desc = clean_text(match2.group(1))
            if len(desc) > 3:
                products.append({
                    'description': desc,
                    'quantity': match2.group(2),
                    'unit_price': f"${match2.group(3)}",
                    'total_price': f"${match2.group(4)}",
                    'confidence': 0.9
                })
        
    
        elif any(word in line.lower() for word in ['producto', 'articulo', 'item', 'servicio']) and len(line) > 10:
            # Buscar números en la línea
            numbers = re.findall(r'\d+[.,]\d{2}', line)
            if numbers:
                price = numbers[-1]  
                desc = re.sub(r'\d+[.,]\d{2}', '', line).strip()
                desc = clean_text(desc)
                
                if len(desc) > 3:
                    products.append({
                        'description': desc,
                        'quantity': '1',
                        'unit_price': f"${price}",
                        'total_price': f"${price}",
                        'confidence': 0.7
                    })
    
    print(f"✅ Extraídos {len(products)} productos")
    return products

def process_document_intelligent(file, options=None):
    """Procesamiento inteligente sin YOLO - Solo patrones + OCR"""
    if options is None:
        options = {}

    try:
        start_time = time.time()
        print("🚀 [SISTEMA INTELIGENTE] Iniciando procesamiento pattern-only...")

    
        filename = file.filename.lower()
        file_bytes = file.read()

        if filename.endswith('.pdf'):
            print("📄 Procesando PDF...") 
            images = convert_from_bytes(file_bytes)
            if not images:
                return {'success': False, 'message': 'Error al convertir PDF'}
            pil_image = images[0]
            image = np.array(pil_image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            print(f" Imagen PDF cargada: {image.shape}")
        else:
            print("🖼️ Procesando imagen...")
            pil_image = Image.open(io.BytesIO(file_bytes)).convert('RGB')
            image = np.array(pil_image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            print(f"📷 Imagen cargada: {image.shape}")

       
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        print("🔍 Ejecutando OCR con Tesseract...")
        ocr_text1 = pytesseract.image_to_string(gray, config='--psm 6', lang='spa')
        ocr_text2 = pytesseract.image_to_string(gray, config='--psm 8', lang='spa')
        full_text = f"{ocr_text1}\n{ocr_text2}"
        full_text = clean_text(full_text)

        print(f"📝 Texto extraído: {len(full_text)} caracteres")

      
        print("🧠 Aplicando sistema inteligente de patrones...")
        metadata = extract_invoice_patterns(full_text)

     
        line_items = extract_line_items_smart(full_text)

    
        processing_time = time.time() - start_time

        result = {
            'success': True,
            'message': 'Documento procesado exitosamente con sistema inteligente',
            'metadata': {
                'company_name': metadata.get('empresa', 'No detectado'),
                'ruc': metadata.get('ruc', 'No detectado'),
                'invoice_number': metadata.get('numero_factura', 'No detectado'),
                'date': metadata.get('fecha', 'No detectado'),
                'subtotal': metadata.get('subtotal', 'No detectado'),
                'iva': metadata.get('iva', 'No detectado'),
                'total': metadata.get('total', 'No detectado')
            },
            'line_items': line_items,
            'detections': [], 
            'processed_image': None,  
            'processing_time': round(processing_time, 2),
            'statistics': {
                'yolo_detections': 0,  # No YOLO
                'table_regions': len(line_items),
                'ocr_confidence': 0.85,
                'model_status': {
                    'yolo_loaded': False,  
                    'classes_count': 0,
                    'is_loaded': True,  
                    'intelligent_mode': True
                }
            },
            'intelligent_analysis': {
                'pattern_matches': len(metadata),
                'extracted_fields': list(metadata.keys()),
                'text_length': len(full_text),
                'processing_mode': 'PATTERN_ONLY'
            }
        }

        print(f"✅ Procesamiento completado en {processing_time:.2f}s")
        print(f"📊 Metadatos: {len(metadata)}, Items: {len(line_items)}")
        return result

    except Exception as e:
        print(f"❌ Error en procesamiento: {e}")
        traceback.print_exc()
        return {
            'success': False,
            'message': f'Error al procesar documento: {str(e)}'
        }



@app.route('/api/v1/invoice/process', methods=['POST'])
def process_invoice():
    """Endpoint principal - Sistema inteligente"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No se envió archivo'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Nombre de archivo vacío'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'Tipo de archivo no soportado'}), 400
    

    options = {
        'enhance_ocr': request.form.get('enhance_ocr', 'true').lower() == 'true',
        'rotation_correction': request.form.get('rotation_correction', 'true').lower() == 'true',
        'confidence_threshold': float(request.form.get('confidence_threshold', 0.25))
    }
    
    result = process_document_intelligent(file, options)
    
    if result.get('success'):
        return jsonify(result), 200
    else:
        return jsonify(result), 500

@app.route('/api/v1/invoice/validate', methods=['POST'])
def validate_file():
    """Validar archivo"""
    if 'file' not in request.files:
        return jsonify({'valid': False, 'error': 'No se envió archivo'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'valid': False, 'error': 'Nombre vacío'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            'valid': False,
            'error': 'Tipo no soportado. Use: PNG, JPG, JPEG, TIFF, BMP, PDF'
        }), 400
    
 
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    
    if size > 50 * 1024 * 1024:  # 50MB
        return jsonify({
            'valid': False,
            'error': 'Archivo muy grande. Máximo 50MB'
        }), 400
    
    return jsonify({
        'valid': True,
        'message': 'Archivo válido',
        'file_info': {
            'filename': file.filename,
            'size': size,
            'content_type': file.content_type or 'unknown'
        }
    }), 200

@app.route('/api/v1/invoice/debug', methods=['GET'])
def debug_info():
    """Debug info"""
    return jsonify({
        'model_status': {
            'yolo_loaded': False,  # Intencionalmente deshabilitado
            'classes_count': 0,
            'available_classes': [],
            'intelligent_mode': True,
            'pattern_system': True
        },
        'ocr_engines': {
            'tesseract': {
                'status': 'available',
                'version': 'Unknown'
            }
        },
        'system_mode': 'PATTERN_ONLY_INTELLIGENT',
        'performance': {
            'lightweight': True,
            'memory_optimized': True,
            'no_pytorch': True
        }
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'system_mode': 'INTELLIGENT_PATTERN_ONLY',
        'model_loaded': False,  # No YOLO
        'intelligent_system': True,
        'timestamp': time.time()
    }), 200


@app.route('/process-document', methods=['POST'])
def process_document_legacy():
    """Endpoint legacy - redirige al inteligente"""
    return process_invoice()

if __name__ == '__main__':
    print("🚀 INICIANDO SISTEMA OCR ULTRA LIGERO")
    print("📋 Modo: PATTERN-ONLY (Sin YOLO/PyTorch)")
    print("🎯 Puerto: 5000")
    print("✅ Sistema inteligente de patrones: ACTIVO")
    app.run(host='0.0.0.0', port=5000, debug=False)