<<<<<<< HEAD
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from PIL import Image
from pdf2image import convert_from_bytes
import pandas as pd
import cv2
import pytesseract
import torch
import traceback
import base64
import time
from pathlib import Path
import io

# Importar analizador inteligente
try:
    from intelligent_invoice_analyzer import intelligent_analyzer
    print("✅ Analizador inteligente importado correctamente")
except Exception as e:
    print(f"❌ Error importando analizador inteligente: {e}")
    intelligent_analyzer = None

# Ejemplo básico para verificar si OpenCV funciona
print(f"OpenCV Version: {cv2.__version__}")

app = Flask(__name__)

# CORS configuration mejorada
CORS(app, 
     resources={
         r"/*": {
             "origins": [
                 "http://localhost:5173",  # Vite dev server
                 "http://localhost:3000",  # React dev server
                 "http://localhost:4444",  # Backend API
                 "http://localhost:8001",  # Docker OCR backend
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

# Global variables
model = None
model_classes = []

def load_yolo_model():
    """Carga el modelo YOLO con manejo de errores mejorado"""
    global model, model_classes
    try:
        model_path = Path('models/best.pt')
        if model_path.exists():
            model = torch.hub.load('ultralytics/yolov5', 'custom', path=str(model_path), force_reload=True)
            model_classes = list(model.names.values())
            print(f"✅ Modelo YOLO cargado exitosamente desde: {model_path}")
            print(f"📊 Clases detectables ({len(model_classes)}): {model_classes}")
            return True
        else:
            print(f"⚠️ Modelo no encontrado en {model_path}. Usando YOLOv5s por defecto.")
            model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
            model_classes = list(model.names.values())
            return True
    except Exception as e:
        print(f"❌ Error cargando modelo: {e}")
        try:
            model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
            model_classes = list(model.names.values())
            return True
        except Exception as e2:
            print(f"❌ Error cargando modelo por defecto: {e2}")
            return False

# Cargar modelo al iniciar
model_loaded = load_yolo_model()



def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'tiff', 'bmp', 'pdf'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    return thresh

def detect_sections(image):
    """Detecta secciones usando YOLO - Compatible con versiones nuevas"""
    if not model:
        print("⚠️ Modelo YOLO no cargado")
        return pd.DataFrame()
    
    try:
        results = model(image)
        print(f"🔍 YOLO detectó {len(results)} resultado(s)")
        
      
        if hasattr(results, 'pandas'):
            try:
              
                detections = results.pandas().xyxy[0]
                print(f"📊 Detecciones (método pandas): {len(detections)}")
                return detections
            except Exception as pandas_error:
                print(f"⚠️ Error con método pandas: {pandas_error}")
        
     
        if hasattr(results, '__iter__'):
           
            result = results[0] if results else None
            if result is not None:
                if hasattr(result, 'boxes') and result.boxes is not None:
                  
                    boxes = result.boxes
                    if boxes.xyxy is not None and len(boxes.xyxy) > 0:
                   
                        detections_data = []
                        for i in range(len(boxes.xyxy)):
                            detection = {
                                'xmin': float(boxes.xyxy[i][0]),
                                'ymin': float(boxes.xyxy[i][1]),
                                'xmax': float(boxes.xyxy[i][2]),
                                'ymax': float(boxes.xyxy[i][3]),
                                'confidence': float(boxes.conf[i]) if boxes.conf is not None else 0.5,
                                'class': int(boxes.cls[i]) if boxes.cls is not None else 0,
                                'name': model.names[int(boxes.cls[i])] if boxes.cls is not None and model.names else f'class_{i}'
                            }
                            detections_data.append(detection)
                        
                        detections_df = pd.DataFrame(detections_data)
                        print(f"📊 Detecciones (método boxes): {len(detections_df)}")
                        return detections_df
                
        print("⚠️ No se pudieron extraer detecciones, usando datos dummy")
      
        return pd.DataFrame(columns=['xmin', 'ymin', 'xmax', 'ymax', 'confidence', 'class', 'name'])
        
    except Exception as e:
        print(f"❌ Error en detección YOLO: {e}")
        traceback.print_exc()
        return pd.DataFrame(columns=['xmin', 'ymin', 'xmax', 'ymax', 'confidence', 'class', 'name'])

def clean_row(row_text):
    """Limpia y procesa una fila de texto OCR"""
    import re
    if not row_text:
        return ""
  
    cleaned = re.sub(r'[^\w\s.,:-]', '', str(row_text))
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def extract_tables_and_text(image, detections):
    table_data = []
    for _, row in detections.iterrows():
        if row['name'] == 'Product_Table':
           
            x_min, y_min, x_max, y_max = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
            table_image = image[y_min:y_max, x_min:x_max]

         
            ocr_result = pytesseract.image_to_string(table_image, config='--psm 6', lang='spa')
            rows = ocr_result.split('\n')
            cleaned_rows = [clean_row(row) for row in rows if row.strip() != '']
            table_data.extend(cleaned_rows)
    return table_data

def extract_key_value_pairs(image, detections):
    key_value_pairs = {}
    for _, row in detections.iterrows():
        if row['name'] == 'Invoice_Header' or row['name'] == 'Total_Amount':
            x_min, y_min, x_max, y_max = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
            section_image = image[y_min:y_max, x_min:x_max]

         
            ocr_result = pytesseract.image_to_data(section_image, output_type=pytesseract.Output.DATAFRAME, lang='spa')
            ocr_result = ocr_result[ocr_result.conf > 50]
            
            current_key = None
            current_value = ""
            for _, word_row in ocr_result.iterrows():
                word = word_row['text']
                if word.endswith(":"):
                    if current_key:
                        key_value_pairs[current_key] = current_value.strip()
                    current_key = word[:-1]
                    current_value = ""
                elif current_key:
                    current_value += word + " "
            if current_key:
                key_value_pairs[current_key] = current_value.strip()
    return key_value_pairs

def process_image(file):
    try:
        start_time = time.time()
        
      
        image = Image.open(file.stream).convert('RGB')
        image = np.array(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

     
        if image is None or image.size == 0:
            return {'error': 'Error al procesar la imagen: imagen vacía o inválida.'}

        # Detectar secciones con YOLOv5
        detections = detect_sections(image)

        # Extraer tablas y pares clave-valor
        table_data = extract_tables_and_text(image, detections)
        key_value_pairs = extract_key_value_pairs(image, detections)

        # Separar encabezados y cuerpo de la tabla
        headers = table_data[0] if len(table_data) > 0 else []
        table_body = table_data[1:] if len(table_data) > 1 else []

   
        processing_time = time.time() - start_time
        
   
        line_items = []
        for item in table_body:
            if isinstance(item, str) and item.strip():
                parts = item.split()
                line_items.append({
                    'description': ' '.join(parts[:-2]) if len(parts) > 3 else item,
                    'quantity': parts[-2] if len(parts) > 2 else '1',
                    'unit_price': parts[-1] if len(parts) > 1 else '0.00',
                    'total_price': parts[-1] if len(parts) > 1 else '0.00',
                    'confidence': 0.85
                })

        return {
            'success': True,
            'message': 'Imagen procesada exitosamente',
            'headers': headers, 
            'tableData': table_body, 
            'keyValuePairs': key_value_pairs,
            'metadata': key_value_pairs,
            'line_items': line_items,
            'detections': [],
            'processed_image': None,
            'processing_time': round(processing_time, 2),
            'statistics': {
                'yolo_detections': len(detections),
                'table_regions': len([d for d in detections.iterrows() if 'table' in str(d[1].get('name', '')).lower()]),
                'ocr_confidence': 0.85,
                'model_status': {
                    'yolo_loaded': model is not None,
                    'classes_count': len(model_classes),
                    'is_loaded': model_loaded
                }
            }
        }

    except Exception as e:
        print(f"Error al procesar la imagen: {e}")
        traceback.print_exc()
        return {'error': f'Error al procesar la imagen: {e}'}

def process_pdf(file):
    try:
        start_time = time.time()
        
    
        images = convert_from_bytes(file.read())
        all_table_data = []
        all_key_value_pairs = {}
        total_detections = 0

        for image in images:
            image_array = np.array(image)
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)

            detections = detect_sections(image_array)
            total_detections += len(detections)
            
            table_data = extract_tables_and_text(image_array, detections)
            key_value_pairs = extract_key_value_pairs(image_array, detections)

            if table_data:
                all_table_data.extend(table_data)
            if key_value_pairs:
                all_key_value_pairs.update(key_value_pairs)

        headers = all_table_data[0] if len(all_table_data) > 0 else []
        table_data = all_table_data[1:] if len(all_table_data) > 1 else []

    
        processing_time = time.time() - start_time
        
    
        line_items = []
        for item in table_data:
            if isinstance(item, str) and item.strip():
                parts = item.split()
                line_items.append({
                    'description': ' '.join(parts[:-2]) if len(parts) > 3 else item,
                    'quantity': parts[-2] if len(parts) > 2 else '1',
                    'unit_price': parts[-1] if len(parts) > 1 else '0.00',
                    'total_price': parts[-1] if len(parts) > 1 else '0.00',
                    'confidence': 0.85
                })

        return {
            'success': True,
            'message': f'PDF procesado exitosamente ({len(images)} páginas)',
            'headers': headers, 
            'tableData': table_data, 
            'keyValuePairs': all_key_value_pairs,
            'metadata': all_key_value_pairs,
            'line_items': line_items,
            'detections': [],
            'processed_image': None,
            'processing_time': round(processing_time, 2),
            'statistics': {
                'yolo_detections': total_detections,
                'table_regions': len([item for item in table_data if item]),
                'ocr_confidence': 0.85,
                'model_status': {
                    'yolo_loaded': model is not None,
                    'classes_count': len(model_classes),
                    'is_loaded': model_loaded
                }
            },
            'pages_processed': len(images)
        }

    except Exception as e:
        print(f"Error al procesar el PDF: {e}")
        traceback.print_exc()
        return {'error': f'Error al procesar el PDF: {e}'}

def extract_text_with_multiple_ocr(region_image):
    """Extrae texto usando múltiples engines OCR para mayor precisión"""
    texts = []
    
 
    try:
      
        text1 = pytesseract.image_to_string(region_image, config='--psm 6', lang='spa')
        if text1.strip():
            texts.append(clean_row(text1))
        
    
        text2 = pytesseract.image_to_string(region_image, config='--psm 8 -c tessedit_char_whitelist=0123456789.-/', lang='spa')
        if text2.strip():
            texts.append(clean_row(text2))
            
     
        text3 = pytesseract.image_to_string(region_image, config='--psm 7', lang='spa')
        if text3.strip():
            texts.append(clean_row(text3))
            
    except Exception as e:
        print(f"Error con Tesseract: {e}")
    
  
    try:
        import easyocr
        reader = easyocr.Reader(['es', 'en'])
        easy_results = reader.readtext(region_image)
        for (bbox, text, conf) in easy_results:
            if conf > 0.5 and text.strip():
                texts.append(clean_row(text))
    except Exception as e:
        print(f"Error con EasyOCR: {e}")
    
    # Elegir el mejor resultado (el más largo y con más información)
    if texts:
        best_text = max(texts, key=lambda x: len(x) if x else 0)
        return best_text
    
    return ""

def apply_intelligent_patterns_to_text(full_text):
    """Aplica patrones inteligentes para extraer campos específicos - Versión integrada"""
    import re
    
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
    
    detected_fields = {}
    
    print(f"📝 Aplicando patrones inteligentes a texto de {len(full_text)} caracteres")
    
    for field_type, pattern_list in patterns.items():
        best_match = None
        best_confidence = 0
        
        for pattern in pattern_list:
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
                print(f"Error aplicando patrón {pattern}: {e}")
                continue
        
        if best_match:
            detected_fields[field_type] = best_match
            print(f"🎯 {field_type}: '{best_match}' (confianza: {best_confidence:.2f})")
    
    return detected_fields

def extract_products_from_text(full_text):
    """Extrae productos del texto completo"""
    import re
    products = []
    
    lines = full_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if len(line) < 5:  
            continue
        
    
        pattern1 = r'(\d+(?:[.,]\d+)?)\s+(.+?)\s+(\d+[.,]\d{2})'
      
        pattern2 = r'(.+?)\s+(\d+)\s+(\d+[.,]\d{2})\s+(\d+[.,]\d{2})'
        
        match1 = re.search(pattern1, line)
        match2 = re.search(pattern2, line)
        
        if match1:
            products.append({
                'description': match1.group(2).strip(),
                'quantity': match1.group(1),
                'unit_price': match1.group(3),
                'total_price': match1.group(3),
                'confidence': 0.8
            })
        elif match2:
            products.append({
                'description': match2.group(1).strip(),
                'quantity': match2.group(2),
                'unit_price': match2.group(3),
                'total_price': match2.group(4),
                'confidence': 0.85
            })
        elif any(word in line.lower() for word in ['producto', 'item', 'art', 'serv']) and len(line) > 10:
            products.append({
                'description': line,
                'quantity': '1',
                'unit_price': '0.00',
                'total_price': '0.00',
                'confidence': 0.5
            })
    
    print(f"📦 Productos extraídos: {len(products)}")
    return products

def extract_invoice_data_structured(image, detections, confidence_threshold=0.25):
    """Extrae datos específicos de factura organizados por las 18 clases"""
    
    print(f"🔍 Procesando {len(detections)} detecciones con threshold {confidence_threshold}")
    
 
    expected_classes = [
        'logo', 'razon_social', 'R.U.C', 'numero_factura', 'fecha_hora',
        'descripcion', 'cantidad', 'precio_unitario', 'precio_total',
        'subtotal', 'iva', 'total_amount', 'product_table', 'header',
        'footer', 'barcode', 'qr_code', 'signature'
    ]
    
    extracted_data = {
        'metadata': {},
        'line_items': [],
        'detections': [],
        'class_regions': {}
    }
    
    if detections.empty:
        print("⚠️ No hay detecciones YOLO, procesando imagen completa con OCR")
    
        try:
            full_text = extract_text_with_multiple_ocr(image)
            print(f"📄 Texto extraído de imagen completa: {full_text[:200]}...")
            
         
            import re
            
       
            ruc_match = re.search(r'R\.?U\.?C\.?\s*:?\s*(\d{11,13})', full_text, re.IGNORECASE)
            if ruc_match:
                extracted_data['metadata']['ruc'] = ruc_match.group(1)
                print(f"🔍 RUC encontrado: {ruc_match.group(1)}")
            
     
            date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', full_text)
            if date_match:
                extracted_data['metadata']['date'] = date_match.group(1)
                print(f"📅 Fecha encontrada: {date_match.group(1)}")
            
     
            total_match = re.search(r'total\s*:?\s*\$?\s*(\d+[.,]\d{2})', full_text, re.IGNORECASE)
            if total_match:
                extracted_data['metadata']['total'] = total_match.group(1)
                print(f"💰 Total encontrado: {total_match.group(1)}")
                
        except Exception as e:
            print(f"Error procesando imagen completa: {e}")
        
        return extracted_data
    
    for _, detection in detections.iterrows():
        try:
            if detection['confidence'] < confidence_threshold:
                continue
                
            class_name = detection['name']
            x_min, y_min, x_max, y_max = int(detection['xmin']), int(detection['ymin']), int(detection['xmax']), int(detection['ymax'])
            
            print(f"🎯 Procesando región {class_name} con confianza {detection['confidence']:.2f}")
            
       
            h, w = image.shape[:2]
            x_min = max(0, min(x_min, w-1))
            y_min = max(0, min(y_min, h-1))
            x_max = max(x_min+1, min(x_max, w))
            y_max = max(y_min+1, min(y_max, h))
            
    
            region_image = image[y_min:y_max, x_min:x_max]
            
            if region_image.size == 0:
                print(f"⚠️ Región vacía para {class_name}")
                continue
            
       
            ocr_text = extract_text_with_multiple_ocr(region_image)
            
            if ocr_text:
                print(f"📝 {class_name}: '{ocr_text}'")
                
         
                detection_data = {
                    'field_type': class_name,
                    'text': ocr_text,
                    'confidence': float(detection['confidence']),
                    'bbox': {
                        'xmin': x_min,
                        'ymin': y_min,
                        'xmax': x_max,
                        'ymax': y_max
                    },
                    'ocr_confidence': 0.8
                }
                extracted_data['detections'].append(detection_data)
                
           
                if class_name not in extracted_data['class_regions']:
                    extracted_data['class_regions'][class_name] = []
                extracted_data['class_regions'][class_name].append({
                    'text': ocr_text,
                    'bbox': detection_data['bbox'],
                    'confidence': float(detection['confidence'])
                })
                
          
                if class_name in ['razon_social', 'company_name']:
                    extracted_data['metadata']['company_name'] = ocr_text
                elif class_name in ['R.U.C', 'ruc']:
                    extracted_data['metadata']['ruc'] = ocr_text
                elif class_name in ['numero_factura', 'invoice_number']:
                    extracted_data['metadata']['invoice_number'] = ocr_text
                elif class_name in ['fecha_hora', 'date']:
                    extracted_data['metadata']['date'] = ocr_text
                elif class_name == 'subtotal':
                    extracted_data['metadata']['subtotal'] = ocr_text
                elif class_name == 'iva':
                    extracted_data['metadata']['iva'] = ocr_text
                elif class_name in ['total_amount', 'total']:
                    extracted_data['metadata']['total'] = ocr_text
                elif class_name in ['product_table', 'descripcion', 'description']:
                
                    lines = ocr_text.split('\n')
                    for line in lines:
                        if line.strip() and len(line.strip()) > 3:
                         
                            parts = line.split()
                            if len(parts) >= 1:
                                extracted_data['line_items'].append({
                                    'description': ' '.join(parts[:-2]) if len(parts) > 3 else line.strip(),
                                    'quantity': parts[-2] if len(parts) > 2 else '1',
                                    'unit_price': parts[-1] if len(parts) > 1 else '0.00',
                                    'total_price': parts[-1] if len(parts) > 1 else '0.00',
                                    'confidence': float(detection['confidence'])
                                })
            else:
                print(f"⚠️ No se pudo extraer texto de {class_name}")
                
        except Exception as e:
            print(f"❌ Error procesando región {detection.get('name', 'unknown')}: {e}")
            continue
    
    print(f"✅ Datos extraídos: {len(extracted_data['metadata'])} metadatos, {len(extracted_data['line_items'])} items")
    return extracted_data

def create_detection_image(image, detections):
    """Crea imagen con detecciones marcadas"""
    try:
        result_image = image.copy()
        
        for _, detection in detections.iterrows():
            x_min, y_min, x_max, y_max = int(detection['xmin']), int(detection['ymin']), int(detection['xmax']), int(detection['ymax'])
            confidence = detection['confidence']
            class_name = detection['name']
            
      
            color = (0, 255, 0) 
            if 'table' in class_name.lower():
                color = (255, 0, 0)  
            elif any(key in class_name.lower() for key in ['total', 'subtotal', 'iva']):
                color = (0, 255, 255)  
            
            # Dibujar rectángulo
            cv2.rectangle(result_image, (x_min, y_min), (x_max, y_max), color, 2)
            
            # Etiqueta
            label = f'{class_name}: {confidence:.2f}'
            cv2.putText(result_image, label, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # Convertir a base64
        _, buffer = cv2.imencode('.jpg', result_image)
        encoded_image = base64.b64encode(buffer).decode('utf-8')
        return encoded_image
        
    except Exception as e:
        print(f"Error creando imagen de detección: {e}")
        return None

def process_image_structured(file, options=None):
    """Procesa un archivo de imagen con sistema híbrido YOLO + Patrones"""
    if options is None:
        options = {}
        
    try:
        start_time = time.time()
        
        print("🚀 [SISTEMA HÍBRIDO] Iniciando procesamiento con YOLO + Patrones...")
        print(f"📁 Archivo recibido: {file.filename}")
        print(f"⚙️ Opciones: {options}")
        
 
        filename = file.filename.lower()
        if filename.endswith('.pdf'):
            print("📄 Detectado PDF, convirtiendo a imagen...")
            try:
          
                file.stream.seek(0) 
                images = convert_from_bytes(file.stream.read())
                if not images:
                    print("❌ Error: No se pudieron extraer páginas del PDF")
                    return {'success': False, 'message': 'Error al convertir PDF: no se pudieron extraer páginas.'}
                
                print(f"✅ PDF convertido: {len(images)} páginas encontradas")
           
                pil_image = images[0]
                image = np.array(pil_image)
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                print(f"📷 Imagen del PDF cargada: {image.shape}")
            except Exception as pdf_error:
                print(f"❌ Error convirtiendo PDF: {pdf_error}")
                return {'success': False, 'message': f'Error al convertir PDF: {pdf_error}'}
        else:
            print("🖼️ Detectada imagen, procesando directamente...")
            try:
                file.stream.seek(0)
                image = Image.open(file.stream).convert('RGB')
                image = np.array(image)
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                print(f"📷 Imagen cargada: {image.shape}")
            except Exception as img_error:
                print(f"❌ Error cargando imagen: {img_error}")
                return {'success': False, 'message': f'Error al cargar imagen: {img_error}'}
        
        if image is None or image.size == 0:
            print("❌ Error: imagen vacía o inválida")
            return {'success': False, 'message': 'Error al procesar la imagen: imagen vacía o inválida.'}
        
        print(f"📷 Imagen cargada: {image.shape}")
        
     
        yolo_detections = pd.DataFrame()
        try:
            yolo_detections = detect_sections(image)
            print(f"🎯 YOLO detectó {len(yolo_detections)} regiones")
        except Exception as e:
            print(f"⚠️ YOLO falló, continuando con análisis por patrones: {e}")
        
        # SISTEMA HÍBRIDO INTELIGENTE - YOLO + PATRONES
        print("🧠 Inicializando sistema híbrido...")
        
        # Importar sistema robusto multi-motor
        try:
            from robust_multi_engine_ocr import RobustMultiEngineOCR
            robust_system = RobustMultiEngineOCR(yolo_model=model, model_classes=model_classes)
            print("✅ Sistema robusto multi-motor inicializado correctamente")
        except Exception as e:
            print(f"❌ Error importando sistema robusto: {e}")
            return {'success': False, 'message': f'Error inicializando sistema robusto: {e}'}
        
       
        print("🔄 Ejecutando procesamiento robusto multi-motor...")
        robust_result = robust_system.process_invoice_robust(image)
        
    
        if not robust_result.get('success', False):
            print(f"❌ Error en sistema robusto: {robust_result.get('message', 'Error desconocido')}")
            return robust_result
        
      
        print("✅ Sistema robusto multi-motor completado exitosamente")
        
      
        if not yolo_detections.empty:
            try:
                processed_image = create_detection_image(image, yolo_detections)
                robust_result['processed_image'] = processed_image
            except Exception as e:
                print(f"⚠️ Error creando imagen procesada: {e}")
                robust_result['processed_image'] = None
        
      
        detections = []
        metadata = robust_result.get('metadata', {})
        for field, value in metadata.items():
            if value and value.strip():
                detections.append({
                    'field_type': field,
                    'text': value,
                    'confidence': 0.8,
                    'bbox': {'xmin': 0, 'ymin': 0, 'xmax': 100, 'ymax': 100},
                    'ocr_confidence': 0.8
                })
        
        robust_result['detections'] = detections
        robust_result['class_regions'] = {}  
        
        return robust_result
        
    except Exception as e:
        print(f"❌ Error procesando imagen: {e}")
        traceback.print_exc()
        return {'success': False, 'message': f'Error al procesar imagen: {str(e)}'}



@app.route('/api/v1/invoice/process', methods=['POST'])
def process_invoice():
    """Endpoint principal para procesamiento de facturas"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No se envió ningún archivo'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'El nombre del archivo está vacío'}), 400
    
    if not file or not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'Tipo de archivo no soportado'}), 400
    
  
    options = {
        'enhance_ocr': request.form.get('enhance_ocr', 'true').lower() == 'true',
        'rotation_correction': request.form.get('rotation_correction', 'true').lower() == 'true',
        'confidence_threshold': float(request.form.get('confidence_threshold', 0.25))
    }
    
  
    print(f"🔄 Procesando archivo: {file.filename}")
    result = process_image_structured(file, options)
    
    if result.get('success', False):
        return jsonify(result), 200
    else:
        return jsonify(result), 500

@app.route('/api/v1/invoice/validate', methods=['POST'])
def validate_file():
    """Valida un archivo antes del procesamiento"""
    if 'file' not in request.files:
        return jsonify({'valid': False, 'error': 'No se envió ningún archivo'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'valid': False, 'error': 'El nombre del archivo está vacío'}), 400
    

    if not allowed_file(file.filename):
        return jsonify({
            'valid': False, 
            'error': 'Tipo de archivo no soportado. Use: PNG, JPG, JPEG, TIFF, BMP, PDF'
        }), 400
    

    file.seek(0, 2)  
    size = file.tell()
    file.seek(0)  
    
    if size > 50 * 1024 * 1024:  # 50MB
        return jsonify({
            'valid': False,
            'error': 'Archivo demasiado grande. Máximo 50MB permitido'
        }), 400
    
    return jsonify({
        'valid': True,
        'message': 'Archivo válido para procesamiento',
        'file_info': {
            'filename': file.filename,
            'size': size,
            'content_type': file.content_type or 'unknown'
        }
    }), 200

@app.route('/api/v1/invoice/debug', methods=['GET'])
def debug_info():
    """Información de debug del sistema"""
    debug_data = {
        'model_status': {
            'yolo_loaded': model is not None,
            'classes_count': len(model_classes) if model_classes else 0,
            'available_classes': model_classes[:10] if model_classes else [],  # Primeras 10 clases
            'model_path_exists': Path('models/best.pt').exists()
        },
        'ocr_engines': {
            'tesseract': {
                'status': 'available',
                'version': 'Unknown'
            }
        },
        'simple_test': {
            'system_ready': model_loaded,
            'classes_loaded': len(model_classes) > 0
        }
    }
    
    return jsonify(debug_data), 200

@app.route('/api/v1/invoice/supported-formats', methods=['GET'])
def supported_formats():
    """Formatos soportados y capacidades"""
    return jsonify({
        'supported_formats': ['PDF', 'PNG', 'JPG', 'JPEG', 'TIFF', 'BMP'],
        'max_file_size_mb': 50,
        'ocr_languages': ['spa', 'eng'],
        'capabilities': {
            'pdf_processing': True,
            'image_processing': True,
            'table_detection': True,
            'rotation_correction': True,
            'multi_ocr_engines': False,
            'yolo_field_detection': True
        },
        'optimal_conditions': {
            'dpi': '300+',
            'format': 'PDF or high-quality PNG/JPG',
            'quality': 'High contrast, clear text',
            'orientation': 'Upright, minimal skew'
        },
        'detected_classes': model_classes if model_classes else []
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'classes_available': len(model_classes),
        'cors_enabled': True,
        'timestamp': time.time()
    }), 200

@app.route('/api/v1/test-connection', methods=['GET', 'OPTIONS'])
def test_connection():
    """Test endpoint para verificar conectividad y CORS"""
    if request.method == 'OPTIONS':
        return '', 200
    
    return jsonify({
        'success': True,
        'message': 'Conexión exitosa desde frontend',
        'cors_working': True,
        'backend_ready': True,
        'model_status': {
            'loaded': model is not None,
            'classes': len(model_classes)
        }
    }), 200

@app.route('/process-document', methods=['POST'])
def process_document():
    """Endpoint legacy para compatibilidad - Ahora devuelve estructura compatible"""
    if 'file' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'El nombre del archivo está vacío'}), 400

    if file and allowed_file(file.filename):
        filename = file.filename.lower()
        if filename.endswith('.pdf'):
            data = process_pdf(file)
        else:
            data = process_image(file)

        if 'error' in data:
            return jsonify({'success': False, 'message': data['error']}), 500

     
        if 'success' in data and data['success']:
            return jsonify(data), 200
        else:
           
            legacy_data = {
                'success': True,
                'message': 'Documento procesado exitosamente',
                'metadata': data.get('keyValuePairs', {}),
                'line_items': data.get('line_items', []),
                'detections': data.get('detections', []),
                'processed_image': data.get('processed_image'),
                'processing_time': data.get('processing_time', 0),
                'statistics': data.get('statistics', {
                    'yolo_detections': 0,
                    'table_regions': len(data.get('tableData', [])),
                    'ocr_confidence': 0.85,
                    'model_status': {
                        'yolo_loaded': model is not None,
                        'classes_count': len(model_classes),
                        'is_loaded': model_loaded
                    }
                })
            }
            return jsonify({'data': legacy_data}), 200
    else:
        return jsonify({'error': 'Tipo de archivo no soportado'}), 400

if __name__ == '__main__':
     app.run(host='0.0.0.0', port=5000)
=======
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from PIL import Image
from pdf2image import convert_from_bytes
import pandas as pd
import cv2
import pytesseract
import torch
import traceback
import base64
import time
from pathlib import Path
import io

# Importar analizador inteligente
try:
    from intelligent_invoice_analyzer import intelligent_analyzer
    print("✅ Analizador inteligente importado correctamente")
except Exception as e:
    print(f"❌ Error importando analizador inteligente: {e}")
    intelligent_analyzer = None

# Ejemplo básico para verificar si OpenCV funciona
print(f"OpenCV Version: {cv2.__version__}")

app = Flask(__name__)

# CORS configuration mejorada
CORS(app, 
     resources={
         r"/*": {
             "origins": [
                 "http://localhost:5173",  # Vite dev server
                 "http://localhost:3000",  # React dev server
                 "http://localhost:4444",  # Backend API
                 "http://localhost:8001",  # Docker OCR backend
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

# Global variables
model = None
model_classes = []

def load_yolo_model():
    """Carga el modelo YOLO con manejo de errores mejorado"""
    global model, model_classes
    try:
        model_path = Path('models/best.pt')
        if model_path.exists():
            model = torch.hub.load('ultralytics/yolov5', 'custom', path=str(model_path), force_reload=True)
            model_classes = list(model.names.values())
            print(f"✅ Modelo YOLO cargado exitosamente desde: {model_path}")
            print(f"📊 Clases detectables ({len(model_classes)}): {model_classes}")
            return True
        else:
            print(f"⚠️ Modelo no encontrado en {model_path}. Usando YOLOv5s por defecto.")
            model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
            model_classes = list(model.names.values())
            return True
    except Exception as e:
        print(f"❌ Error cargando modelo: {e}")
        try:
            model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
            model_classes = list(model.names.values())
            return True
        except Exception as e2:
            print(f"❌ Error cargando modelo por defecto: {e2}")
            return False

# Cargar modelo al iniciar
model_loaded = load_yolo_model()



def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'tiff', 'bmp', 'pdf'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    return thresh

def detect_sections(image):
    """Detecta secciones usando YOLO - Compatible con versiones nuevas"""
    if not model:
        print("⚠️ Modelo YOLO no cargado")
        return pd.DataFrame()
    
    try:
        results = model(image)
        print(f"🔍 YOLO detectó {len(results)} resultado(s)")
        
      
        if hasattr(results, 'pandas'):
            try:
              
                detections = results.pandas().xyxy[0]
                print(f"📊 Detecciones (método pandas): {len(detections)}")
                return detections
            except Exception as pandas_error:
                print(f"⚠️ Error con método pandas: {pandas_error}")
        
     
        if hasattr(results, '__iter__'):
           
            result = results[0] if results else None
            if result is not None:
                if hasattr(result, 'boxes') and result.boxes is not None:
                  
                    boxes = result.boxes
                    if boxes.xyxy is not None and len(boxes.xyxy) > 0:
                   
                        detections_data = []
                        for i in range(len(boxes.xyxy)):
                            detection = {
                                'xmin': float(boxes.xyxy[i][0]),
                                'ymin': float(boxes.xyxy[i][1]),
                                'xmax': float(boxes.xyxy[i][2]),
                                'ymax': float(boxes.xyxy[i][3]),
                                'confidence': float(boxes.conf[i]) if boxes.conf is not None else 0.5,
                                'class': int(boxes.cls[i]) if boxes.cls is not None else 0,
                                'name': model.names[int(boxes.cls[i])] if boxes.cls is not None and model.names else f'class_{i}'
                            }
                            detections_data.append(detection)
                        
                        detections_df = pd.DataFrame(detections_data)
                        print(f"📊 Detecciones (método boxes): {len(detections_df)}")
                        return detections_df
                
        print("⚠️ No se pudieron extraer detecciones, usando datos dummy")
      
        return pd.DataFrame(columns=['xmin', 'ymin', 'xmax', 'ymax', 'confidence', 'class', 'name'])
        
    except Exception as e:
        print(f"❌ Error en detección YOLO: {e}")
        traceback.print_exc()
        return pd.DataFrame(columns=['xmin', 'ymin', 'xmax', 'ymax', 'confidence', 'class', 'name'])

def clean_row(row_text):
    """Limpia y procesa una fila de texto OCR"""
    import re
    if not row_text:
        return ""
  
    cleaned = re.sub(r'[^\w\s.,:-]', '', str(row_text))
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def extract_tables_and_text(image, detections):
    table_data = []
    for _, row in detections.iterrows():
        if row['name'] == 'Product_Table':
           
            x_min, y_min, x_max, y_max = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
            table_image = image[y_min:y_max, x_min:x_max]

         
            ocr_result = pytesseract.image_to_string(table_image, config='--psm 6', lang='spa')
            rows = ocr_result.split('\n')
            cleaned_rows = [clean_row(row) for row in rows if row.strip() != '']
            table_data.extend(cleaned_rows)
    return table_data

def extract_key_value_pairs(image, detections):
    key_value_pairs = {}
    for _, row in detections.iterrows():
        if row['name'] == 'Invoice_Header' or row['name'] == 'Total_Amount':
            x_min, y_min, x_max, y_max = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
            section_image = image[y_min:y_max, x_min:x_max]

         
            ocr_result = pytesseract.image_to_data(section_image, output_type=pytesseract.Output.DATAFRAME, lang='spa')
            ocr_result = ocr_result[ocr_result.conf > 50]
            
            current_key = None
            current_value = ""
            for _, word_row in ocr_result.iterrows():
                word = word_row['text']
                if word.endswith(":"):
                    if current_key:
                        key_value_pairs[current_key] = current_value.strip()
                    current_key = word[:-1]
                    current_value = ""
                elif current_key:
                    current_value += word + " "
            if current_key:
                key_value_pairs[current_key] = current_value.strip()
    return key_value_pairs

def process_image(file):
    try:
        start_time = time.time()
        
      
        image = Image.open(file.stream).convert('RGB')
        image = np.array(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

     
        if image is None or image.size == 0:
            return {'error': 'Error al procesar la imagen: imagen vacía o inválida.'}

        # Detectar secciones con YOLOv5
        detections = detect_sections(image)

        # Extraer tablas y pares clave-valor
        table_data = extract_tables_and_text(image, detections)
        key_value_pairs = extract_key_value_pairs(image, detections)

        # Separar encabezados y cuerpo de la tabla
        headers = table_data[0] if len(table_data) > 0 else []
        table_body = table_data[1:] if len(table_data) > 1 else []

   
        processing_time = time.time() - start_time
        
   
        line_items = []
        for item in table_body:
            if isinstance(item, str) and item.strip():
                parts = item.split()
                line_items.append({
                    'description': ' '.join(parts[:-2]) if len(parts) > 3 else item,
                    'quantity': parts[-2] if len(parts) > 2 else '1',
                    'unit_price': parts[-1] if len(parts) > 1 else '0.00',
                    'total_price': parts[-1] if len(parts) > 1 else '0.00',
                    'confidence': 0.85
                })

        return {
            'success': True,
            'message': 'Imagen procesada exitosamente',
            'headers': headers, 
            'tableData': table_body, 
            'keyValuePairs': key_value_pairs,
            'metadata': key_value_pairs,
            'line_items': line_items,
            'detections': [],
            'processed_image': None,
            'processing_time': round(processing_time, 2),
            'statistics': {
                'yolo_detections': len(detections),
                'table_regions': len([d for d in detections.iterrows() if 'table' in str(d[1].get('name', '')).lower()]),
                'ocr_confidence': 0.85,
                'model_status': {
                    'yolo_loaded': model is not None,
                    'classes_count': len(model_classes),
                    'is_loaded': model_loaded
                }
            }
        }

    except Exception as e:
        print(f"Error al procesar la imagen: {e}")
        traceback.print_exc()
        return {'error': f'Error al procesar la imagen: {e}'}

def process_pdf(file):
    try:
        start_time = time.time()
        
    
        images = convert_from_bytes(file.read())
        all_table_data = []
        all_key_value_pairs = {}
        total_detections = 0

        for image in images:
            image_array = np.array(image)
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)

            detections = detect_sections(image_array)
            total_detections += len(detections)
            
            table_data = extract_tables_and_text(image_array, detections)
            key_value_pairs = extract_key_value_pairs(image_array, detections)

            if table_data:
                all_table_data.extend(table_data)
            if key_value_pairs:
                all_key_value_pairs.update(key_value_pairs)

        headers = all_table_data[0] if len(all_table_data) > 0 else []
        table_data = all_table_data[1:] if len(all_table_data) > 1 else []

    
        processing_time = time.time() - start_time
        
    
        line_items = []
        for item in table_data:
            if isinstance(item, str) and item.strip():
                parts = item.split()
                line_items.append({
                    'description': ' '.join(parts[:-2]) if len(parts) > 3 else item,
                    'quantity': parts[-2] if len(parts) > 2 else '1',
                    'unit_price': parts[-1] if len(parts) > 1 else '0.00',
                    'total_price': parts[-1] if len(parts) > 1 else '0.00',
                    'confidence': 0.85
                })

        return {
            'success': True,
            'message': f'PDF procesado exitosamente ({len(images)} páginas)',
            'headers': headers, 
            'tableData': table_data, 
            'keyValuePairs': all_key_value_pairs,
            'metadata': all_key_value_pairs,
            'line_items': line_items,
            'detections': [],
            'processed_image': None,
            'processing_time': round(processing_time, 2),
            'statistics': {
                'yolo_detections': total_detections,
                'table_regions': len([item for item in table_data if item]),
                'ocr_confidence': 0.85,
                'model_status': {
                    'yolo_loaded': model is not None,
                    'classes_count': len(model_classes),
                    'is_loaded': model_loaded
                }
            },
            'pages_processed': len(images)
        }

    except Exception as e:
        print(f"Error al procesar el PDF: {e}")
        traceback.print_exc()
        return {'error': f'Error al procesar el PDF: {e}'}

def extract_text_with_multiple_ocr(region_image):
    """Extrae texto usando múltiples engines OCR para mayor precisión"""
    texts = []
    
 
    try:
      
        text1 = pytesseract.image_to_string(region_image, config='--psm 6', lang='spa')
        if text1.strip():
            texts.append(clean_row(text1))
        
    
        text2 = pytesseract.image_to_string(region_image, config='--psm 8 -c tessedit_char_whitelist=0123456789.-/', lang='spa')
        if text2.strip():
            texts.append(clean_row(text2))
            
     
        text3 = pytesseract.image_to_string(region_image, config='--psm 7', lang='spa')
        if text3.strip():
            texts.append(clean_row(text3))
            
    except Exception as e:
        print(f"Error con Tesseract: {e}")
    
  
    try:
        import easyocr
        reader = easyocr.Reader(['es', 'en'])
        easy_results = reader.readtext(region_image)
        for (bbox, text, conf) in easy_results:
            if conf > 0.5 and text.strip():
                texts.append(clean_row(text))
    except Exception as e:
        print(f"Error con EasyOCR: {e}")
    
    # Elegir el mejor resultado (el más largo y con más información)
    if texts:
        best_text = max(texts, key=lambda x: len(x) if x else 0)
        return best_text
    
    return ""

def apply_intelligent_patterns_to_text(full_text):
    """Aplica patrones inteligentes para extraer campos específicos - Versión integrada"""
    import re
    
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
    
    detected_fields = {}
    
    print(f"📝 Aplicando patrones inteligentes a texto de {len(full_text)} caracteres")
    
    for field_type, pattern_list in patterns.items():
        best_match = None
        best_confidence = 0
        
        for pattern in pattern_list:
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
                print(f"Error aplicando patrón {pattern}: {e}")
                continue
        
        if best_match:
            detected_fields[field_type] = best_match
            print(f"🎯 {field_type}: '{best_match}' (confianza: {best_confidence:.2f})")
    
    return detected_fields

def extract_products_from_text(full_text):
    """Extrae productos del texto completo"""
    import re
    products = []
    
    lines = full_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if len(line) < 5:  
            continue
        
    
        pattern1 = r'(\d+(?:[.,]\d+)?)\s+(.+?)\s+(\d+[.,]\d{2})'
      
        pattern2 = r'(.+?)\s+(\d+)\s+(\d+[.,]\d{2})\s+(\d+[.,]\d{2})'
        
        match1 = re.search(pattern1, line)
        match2 = re.search(pattern2, line)
        
        if match1:
            products.append({
                'description': match1.group(2).strip(),
                'quantity': match1.group(1),
                'unit_price': match1.group(3),
                'total_price': match1.group(3),
                'confidence': 0.8
            })
        elif match2:
            products.append({
                'description': match2.group(1).strip(),
                'quantity': match2.group(2),
                'unit_price': match2.group(3),
                'total_price': match2.group(4),
                'confidence': 0.85
            })
        elif any(word in line.lower() for word in ['producto', 'item', 'art', 'serv']) and len(line) > 10:
            products.append({
                'description': line,
                'quantity': '1',
                'unit_price': '0.00',
                'total_price': '0.00',
                'confidence': 0.5
            })
    
    print(f"📦 Productos extraídos: {len(products)}")
    return products

def extract_invoice_data_structured(image, detections, confidence_threshold=0.25):
    """Extrae datos específicos de factura organizados por las 18 clases"""
    
    print(f"🔍 Procesando {len(detections)} detecciones con threshold {confidence_threshold}")
    
 
    expected_classes = [
        'logo', 'razon_social', 'R.U.C', 'numero_factura', 'fecha_hora',
        'descripcion', 'cantidad', 'precio_unitario', 'precio_total',
        'subtotal', 'iva', 'total_amount', 'product_table', 'header',
        'footer', 'barcode', 'qr_code', 'signature'
    ]
    
    extracted_data = {
        'metadata': {},
        'line_items': [],
        'detections': [],
        'class_regions': {}
    }
    
    if detections.empty:
        print("⚠️ No hay detecciones YOLO, procesando imagen completa con OCR")
    
        try:
            full_text = extract_text_with_multiple_ocr(image)
            print(f"📄 Texto extraído de imagen completa: {full_text[:200]}...")
            
         
            import re
            
       
            ruc_match = re.search(r'R\.?U\.?C\.?\s*:?\s*(\d{11,13})', full_text, re.IGNORECASE)
            if ruc_match:
                extracted_data['metadata']['ruc'] = ruc_match.group(1)
                print(f"🔍 RUC encontrado: {ruc_match.group(1)}")
            
     
            date_match = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', full_text)
            if date_match:
                extracted_data['metadata']['date'] = date_match.group(1)
                print(f"📅 Fecha encontrada: {date_match.group(1)}")
            
     
            total_match = re.search(r'total\s*:?\s*\$?\s*(\d+[.,]\d{2})', full_text, re.IGNORECASE)
            if total_match:
                extracted_data['metadata']['total'] = total_match.group(1)
                print(f"💰 Total encontrado: {total_match.group(1)}")
                
        except Exception as e:
            print(f"Error procesando imagen completa: {e}")
        
        return extracted_data
    
    for _, detection in detections.iterrows():
        try:
            if detection['confidence'] < confidence_threshold:
                continue
                
            class_name = detection['name']
            x_min, y_min, x_max, y_max = int(detection['xmin']), int(detection['ymin']), int(detection['xmax']), int(detection['ymax'])
            
            print(f"🎯 Procesando región {class_name} con confianza {detection['confidence']:.2f}")
            
       
            h, w = image.shape[:2]
            x_min = max(0, min(x_min, w-1))
            y_min = max(0, min(y_min, h-1))
            x_max = max(x_min+1, min(x_max, w))
            y_max = max(y_min+1, min(y_max, h))
            
    
            region_image = image[y_min:y_max, x_min:x_max]
            
            if region_image.size == 0:
                print(f"⚠️ Región vacía para {class_name}")
                continue
            
       
            ocr_text = extract_text_with_multiple_ocr(region_image)
            
            if ocr_text:
                print(f"📝 {class_name}: '{ocr_text}'")
                
         
                detection_data = {
                    'field_type': class_name,
                    'text': ocr_text,
                    'confidence': float(detection['confidence']),
                    'bbox': {
                        'xmin': x_min,
                        'ymin': y_min,
                        'xmax': x_max,
                        'ymax': y_max
                    },
                    'ocr_confidence': 0.8
                }
                extracted_data['detections'].append(detection_data)
                
           
                if class_name not in extracted_data['class_regions']:
                    extracted_data['class_regions'][class_name] = []
                extracted_data['class_regions'][class_name].append({
                    'text': ocr_text,
                    'bbox': detection_data['bbox'],
                    'confidence': float(detection['confidence'])
                })
                
          
                if class_name in ['razon_social', 'company_name']:
                    extracted_data['metadata']['company_name'] = ocr_text
                elif class_name in ['R.U.C', 'ruc']:
                    extracted_data['metadata']['ruc'] = ocr_text
                elif class_name in ['numero_factura', 'invoice_number']:
                    extracted_data['metadata']['invoice_number'] = ocr_text
                elif class_name in ['fecha_hora', 'date']:
                    extracted_data['metadata']['date'] = ocr_text
                elif class_name == 'subtotal':
                    extracted_data['metadata']['subtotal'] = ocr_text
                elif class_name == 'iva':
                    extracted_data['metadata']['iva'] = ocr_text
                elif class_name in ['total_amount', 'total']:
                    extracted_data['metadata']['total'] = ocr_text
                elif class_name in ['product_table', 'descripcion', 'description']:
                
                    lines = ocr_text.split('\n')
                    for line in lines:
                        if line.strip() and len(line.strip()) > 3:
                         
                            parts = line.split()
                            if len(parts) >= 1:
                                extracted_data['line_items'].append({
                                    'description': ' '.join(parts[:-2]) if len(parts) > 3 else line.strip(),
                                    'quantity': parts[-2] if len(parts) > 2 else '1',
                                    'unit_price': parts[-1] if len(parts) > 1 else '0.00',
                                    'total_price': parts[-1] if len(parts) > 1 else '0.00',
                                    'confidence': float(detection['confidence'])
                                })
            else:
                print(f"⚠️ No se pudo extraer texto de {class_name}")
                
        except Exception as e:
            print(f"❌ Error procesando región {detection.get('name', 'unknown')}: {e}")
            continue
    
    print(f"✅ Datos extraídos: {len(extracted_data['metadata'])} metadatos, {len(extracted_data['line_items'])} items")
    return extracted_data

def create_detection_image(image, detections):
    """Crea imagen con detecciones marcadas"""
    try:
        result_image = image.copy()
        
        for _, detection in detections.iterrows():
            x_min, y_min, x_max, y_max = int(detection['xmin']), int(detection['ymin']), int(detection['xmax']), int(detection['ymax'])
            confidence = detection['confidence']
            class_name = detection['name']
            
      
            color = (0, 255, 0) 
            if 'table' in class_name.lower():
                color = (255, 0, 0)  
            elif any(key in class_name.lower() for key in ['total', 'subtotal', 'iva']):
                color = (0, 255, 255)  
            
            # Dibujar rectángulo
            cv2.rectangle(result_image, (x_min, y_min), (x_max, y_max), color, 2)
            
            # Etiqueta
            label = f'{class_name}: {confidence:.2f}'
            cv2.putText(result_image, label, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # Convertir a base64
        _, buffer = cv2.imencode('.jpg', result_image)
        encoded_image = base64.b64encode(buffer).decode('utf-8')
        return encoded_image
        
    except Exception as e:
        print(f"Error creando imagen de detección: {e}")
        return None

def process_image_structured(file, options=None):
    """Procesa un archivo de imagen con sistema híbrido YOLO + Patrones"""
    if options is None:
        options = {}
        
    try:
        start_time = time.time()
        
        print("🚀 [SISTEMA HÍBRIDO] Iniciando procesamiento con YOLO + Patrones...")
        print(f"📁 Archivo recibido: {file.filename}")
        print(f"⚙️ Opciones: {options}")
        
 
        filename = file.filename.lower()
        if filename.endswith('.pdf'):
            print("📄 Detectado PDF, convirtiendo a imagen...")
            try:
          
                file.stream.seek(0) 
                images = convert_from_bytes(file.stream.read())
                if not images:
                    print("❌ Error: No se pudieron extraer páginas del PDF")
                    return {'success': False, 'message': 'Error al convertir PDF: no se pudieron extraer páginas.'}
                
                print(f"✅ PDF convertido: {len(images)} páginas encontradas")
           
                pil_image = images[0]
                image = np.array(pil_image)
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                print(f"📷 Imagen del PDF cargada: {image.shape}")
            except Exception as pdf_error:
                print(f"❌ Error convirtiendo PDF: {pdf_error}")
                return {'success': False, 'message': f'Error al convertir PDF: {pdf_error}'}
        else:
            print("🖼️ Detectada imagen, procesando directamente...")
            try:
                file.stream.seek(0)
                image = Image.open(file.stream).convert('RGB')
                image = np.array(image)
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                print(f"📷 Imagen cargada: {image.shape}")
            except Exception as img_error:
                print(f"❌ Error cargando imagen: {img_error}")
                return {'success': False, 'message': f'Error al cargar imagen: {img_error}'}
        
        if image is None or image.size == 0:
            print("❌ Error: imagen vacía o inválida")
            return {'success': False, 'message': 'Error al procesar la imagen: imagen vacía o inválida.'}
        
        print(f"📷 Imagen cargada: {image.shape}")
        
     
        yolo_detections = pd.DataFrame()
        try:
            yolo_detections = detect_sections(image)
            print(f"🎯 YOLO detectó {len(yolo_detections)} regiones")
        except Exception as e:
            print(f"⚠️ YOLO falló, continuando con análisis por patrones: {e}")
        
        # SISTEMA HÍBRIDO INTELIGENTE - YOLO + PATRONES
        print("🧠 Inicializando sistema híbrido...")
        
        # Importar sistema robusto multi-motor
        try:
            from robust_multi_engine_ocr import RobustMultiEngineOCR
            robust_system = RobustMultiEngineOCR(yolo_model=model, model_classes=model_classes)
            print("✅ Sistema robusto multi-motor inicializado correctamente")
        except Exception as e:
            print(f"❌ Error importando sistema robusto: {e}")
            return {'success': False, 'message': f'Error inicializando sistema robusto: {e}'}
        
       
        print("🔄 Ejecutando procesamiento robusto multi-motor...")
        robust_result = robust_system.process_invoice_robust(image)
        
    
        if not robust_result.get('success', False):
            print(f"❌ Error en sistema robusto: {robust_result.get('message', 'Error desconocido')}")
            return robust_result
        
      
        print("✅ Sistema robusto multi-motor completado exitosamente")
        
      
        if not yolo_detections.empty:
            try:
                processed_image = create_detection_image(image, yolo_detections)
                robust_result['processed_image'] = processed_image
            except Exception as e:
                print(f"⚠️ Error creando imagen procesada: {e}")
                robust_result['processed_image'] = None
        
      
        detections = []
        metadata = robust_result.get('metadata', {})
        for field, value in metadata.items():
            if value and value.strip():
                detections.append({
                    'field_type': field,
                    'text': value,
                    'confidence': 0.8,
                    'bbox': {'xmin': 0, 'ymin': 0, 'xmax': 100, 'ymax': 100},
                    'ocr_confidence': 0.8
                })
        
        robust_result['detections'] = detections
        robust_result['class_regions'] = {}  
        
        return robust_result
        
    except Exception as e:
        print(f"❌ Error procesando imagen: {e}")
        traceback.print_exc()
        return {'success': False, 'message': f'Error al procesar imagen: {str(e)}'}



@app.route('/api/v1/invoice/process', methods=['POST'])
def process_invoice():
    """Endpoint principal para procesamiento de facturas"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No se envió ningún archivo'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'El nombre del archivo está vacío'}), 400
    
    if not file or not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'Tipo de archivo no soportado'}), 400
    
  
    options = {
        'enhance_ocr': request.form.get('enhance_ocr', 'true').lower() == 'true',
        'rotation_correction': request.form.get('rotation_correction', 'true').lower() == 'true',
        'confidence_threshold': float(request.form.get('confidence_threshold', 0.25))
    }
    
  
    print(f"🔄 Procesando archivo: {file.filename}")
    result = process_image_structured(file, options)
    
    if result.get('success', False):
        return jsonify(result), 200
    else:
        return jsonify(result), 500

@app.route('/api/v1/invoice/validate', methods=['POST'])
def validate_file():
    """Valida un archivo antes del procesamiento"""
    if 'file' not in request.files:
        return jsonify({'valid': False, 'error': 'No se envió ningún archivo'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'valid': False, 'error': 'El nombre del archivo está vacío'}), 400
    

    if not allowed_file(file.filename):
        return jsonify({
            'valid': False, 
            'error': 'Tipo de archivo no soportado. Use: PNG, JPG, JPEG, TIFF, BMP, PDF'
        }), 400
    

    file.seek(0, 2)  
    size = file.tell()
    file.seek(0)  
    
    if size > 50 * 1024 * 1024:  # 50MB
        return jsonify({
            'valid': False,
            'error': 'Archivo demasiado grande. Máximo 50MB permitido'
        }), 400
    
    return jsonify({
        'valid': True,
        'message': 'Archivo válido para procesamiento',
        'file_info': {
            'filename': file.filename,
            'size': size,
            'content_type': file.content_type or 'unknown'
        }
    }), 200

@app.route('/api/v1/invoice/debug', methods=['GET'])
def debug_info():
    """Información de debug del sistema"""
    debug_data = {
        'model_status': {
            'yolo_loaded': model is not None,
            'classes_count': len(model_classes) if model_classes else 0,
            'available_classes': model_classes[:10] if model_classes else [],  # Primeras 10 clases
            'model_path_exists': Path('models/best.pt').exists()
        },
        'ocr_engines': {
            'tesseract': {
                'status': 'available',
                'version': 'Unknown'
            }
        },
        'simple_test': {
            'system_ready': model_loaded,
            'classes_loaded': len(model_classes) > 0
        }
    }
    
    return jsonify(debug_data), 200

@app.route('/api/v1/invoice/supported-formats', methods=['GET'])
def supported_formats():
    """Formatos soportados y capacidades"""
    return jsonify({
        'supported_formats': ['PDF', 'PNG', 'JPG', 'JPEG', 'TIFF', 'BMP'],
        'max_file_size_mb': 50,
        'ocr_languages': ['spa', 'eng'],
        'capabilities': {
            'pdf_processing': True,
            'image_processing': True,
            'table_detection': True,
            'rotation_correction': True,
            'multi_ocr_engines': False,
            'yolo_field_detection': True
        },
        'optimal_conditions': {
            'dpi': '300+',
            'format': 'PDF or high-quality PNG/JPG',
            'quality': 'High contrast, clear text',
            'orientation': 'Upright, minimal skew'
        },
        'detected_classes': model_classes if model_classes else []
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'classes_available': len(model_classes),
        'cors_enabled': True,
        'timestamp': time.time()
    }), 200

@app.route('/api/v1/test-connection', methods=['GET', 'OPTIONS'])
def test_connection():
    """Test endpoint para verificar conectividad y CORS"""
    if request.method == 'OPTIONS':
        return '', 200
    
    return jsonify({
        'success': True,
        'message': 'Conexión exitosa desde frontend',
        'cors_working': True,
        'backend_ready': True,
        'model_status': {
            'loaded': model is not None,
            'classes': len(model_classes)
        }
    }), 200

@app.route('/process-document', methods=['POST'])
def process_document():
    """Endpoint legacy para compatibilidad - Ahora devuelve estructura compatible"""
    if 'file' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'El nombre del archivo está vacío'}), 400

    if file and allowed_file(file.filename):
        filename = file.filename.lower()
        if filename.endswith('.pdf'):
            data = process_pdf(file)
        else:
            data = process_image(file)

        if 'error' in data:
            return jsonify({'success': False, 'message': data['error']}), 500

     
        if 'success' in data and data['success']:
            return jsonify(data), 200
        else:
           
            legacy_data = {
                'success': True,
                'message': 'Documento procesado exitosamente',
                'metadata': data.get('keyValuePairs', {}),
                'line_items': data.get('line_items', []),
                'detections': data.get('detections', []),
                'processed_image': data.get('processed_image'),
                'processing_time': data.get('processing_time', 0),
                'statistics': data.get('statistics', {
                    'yolo_detections': 0,
                    'table_regions': len(data.get('tableData', [])),
                    'ocr_confidence': 0.85,
                    'model_status': {
                        'yolo_loaded': model is not None,
                        'classes_count': len(model_classes),
                        'is_loaded': model_loaded
                    }
                })
            }
            return jsonify({'data': legacy_data}), 200
    else:
        return jsonify({'error': 'Tipo de archivo no soportado'}), 400

if __name__ == '__main__':
     app.run(host='0.0.0.0', port=5000)
>>>>>>> origin/luis-develop
