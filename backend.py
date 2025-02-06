from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from PIL import Image
import cv2
import pytesseract
import torch
import traceback
from pdf2image import convert_from_bytes
import os
import re
import base64
import io
from pathlib import Path
import pandas as pd  
from dotenv import load_dotenv
import sys
import yaml

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR / 'yolov5'))  

try:
    from utils.general import non_max_suppression
except ImportError:
    non_max_suppression = None  
app = Flask(__name__)

NGROK_URL = os.getenv("NEXT_PUBLIC_API_URL", "")
ENV = os.getenv("FLASK_ENV", "production")

allowed_origins = [
    "http://127.0.0.1:3000",  # Localhost para desarrollo
    "https://web-navy-nine.vercel.app",  # App en Vercel
    "https://*.ngrok-free.app"  # Dominios de ngrok
]

if NGROK_URL:
    allowed_origins.append(NGROK_URL)  # URL dinámica de ngrok

if ENV == "development":
    CORS(app, resources={r"/*": {"origins": ["https://*.ngrok-free.app", "https://web-navy-nine.vercel.app/ocr"]}}, supports_credentials=True)

    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    print("CORS configurado para desarrollo (orígenes: *)")
else:
   
 @app.after_request
 def add_cors_headers(response):
    """
    Agregar encabezados CORS adicionales para asegurar compatibilidad.
    """
    origin = request.headers.get("Origin")
    if origin and origin in allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


# MODEL_PATH = BASE_DIR / 'yolov5/runs/train/exp_retrain/weights/best.pt' #este era el primer entrenamiento que se hizo :)
MODEL_PATH = Path('/home/yesenia/Escritorio/react/Alcolab/Web/backend/backup-backend-ocr.git/yolov5/runs/train/exp_retrain/weights/best.pt')
DATA_PATH = BASE_DIR / '/datasets/data.yaml'

if not MODEL_PATH.exists():
    print(f"ERROR: El modelo no existe en la ruta: {MODEL_PATH}")
    exit(1)

    if not MODEL_PATH.exists():
        print(f"ERROR: El modelo no existe en la ruta: {MODEL_PATH}")
    exit(1)

    if not DATA_PATH.exists():
        print(f"ERROR: No se encontro el archivo de configuracion: {DATA_PATH}")
        exit(1)


    if DATA_PATH.exists():
     with open(DATA_PATH, 'r') as file:
        classes = yaml.safe_load(file).get('names', {})
    print(f"Clases cargadas desde YAML: {classes}")
else:
    print(f"ERROR: No se encontró el archivo de clases en {DATA_PATH}")
    classes = {int(k): f'class_{k}' for k in range(100)}  # Fallback genérico    

    
# Configurar pytesseract
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
TESSDATA_DIR = '/usr/share/tesseract-ocr/5/tessdata/'
os.environ['TESSDATA_PREFIX'] = TESSDATA_DIR

print(f"Tesseract versión: {pytesseract.get_tesseract_version()}")
print(f"TESSDATA_PREFIX: {os.environ.get('TESSDATA_PREFIX')}")


DATA_PATH = BASE_DIR / '/datasets/data.yaml'

if not DATA_PATH.exists():
    print("Usando fallback de clases en código.")
    classes = {0: 'logo', 1: 'R.U.C', 2: 'numero_factura', 3: 'fecha_hora',
               4: 'razon_social', 5: 'cantidad', 6: 'descripcion', 7: 'precio_unitario',
               8: 'precio_total', 9: 'subtotal', 10: 'iva',11: 'Descripcion', 12: 'Cantidad', 13: 'unidades', 14: 'unidad', 15: 'Cajas_cantidad', 16: 'Articulo', 17: 'Nombre_del_producto'}
    print(f"Clases por defecto: {classes}")
    print(f"Clases cargadas desde YAML: {classes}")
    print(f"Ruta esperada de data.yaml: {DATA_PATH}")

else:
    print(f"ERROR: No se encontró el archivo de clases en {DATA_PATH}")
    classes = {int(k): f'class_{k}' for k in range(100)}  # Fallback genérico

try:
    model = torch.hub.load(
        str(BASE_DIR / 'yolov5'),
        'custom',
        path=str(MODEL_PATH),
        source='local',
        force_reload=True
    )
    print(f"Clases del modelo (por defecto): {model.names}")
except Exception as e:
    print(f"Error cargando el modelo YOLOv5: {e}")
    exit(1)


def allowed_file(filename):
    return ('.' in filename and 
            filename.rsplit('.', 1)[1].lower() in 
            {'png','jpg','jpeg','tiff','bmp','pdf'})

def detect_sections(image):
    """Realiza la detección de secciones en la factura usando YOLOv5"""
    try:
        results = model(image)
        df = results.pandas().xyxy[0]
        if hasattr(model, 'names'):
            class_map = model.names
        else:
            class_map = classes
        df['name'] = df['class'].apply(lambda c: class_map.get(int(c), f'Clase_desconocida_{int(c)}'))
        print("Detecciones YOLOv5:", df)
        return df
    except Exception as e:
        print(f"Error en YOLOv5: {e}")
        return pd.DataFrame(columns=['xmin', 'ymin', 'xmax', 'ymax', 'confidence', 'class', 'name'])

def detect_sections_plan_b(image_bgr):
    """
    PLAN B: Se llama cuando 'model(image)' falla en producción.
    1) Convertir BGR a Tensor
    2) Llamar al modelo => salida bruta
    3) Non-Max-Suppression => Nx6
    4) Convertir a DataFrame => columns=[xmin,ymin,xmax,ymax,confidence,class]
       + name
    """
    if non_max_suppression is None:
        print("No se pudo importar non_max_suppression. Actualiza tu 'yolov5'.")
        # Retorna un DF vacío
        return pd.DataFrame(columns=['xmin','ymin','xmax','ymax','confidence','class','name'])

    if len(image_bgr.shape) == 3 and image_bgr.shape[2] == 3:
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    else:
        image_rgb = image_bgr
    image_rgb = cv2.resize(image_rgb, (640,640), interpolation=cv2.INTER_LINEAR)

    image_tensor = torch.from_numpy(image_rgb).float().permute(2,0,1).unsqueeze(0)/255.0

    with torch.no_grad():
        raw_preds = model(image_tensor) 

    nms = non_max_suppression(raw_preds, conf_thres=0.25, iou_thres=0.45)
    if not nms or nms[0] is None or len(nms[0])==0:
        print("Detecciones YOLOv5 (Plan B): vacio")
        df = pd.DataFrame(columns=['xmin','ymin','xmax','ymax','confidence','class','name'])
        return df

    pred = nms[0].cpu().numpy()  
    df = pd.DataFrame(
        pred, 
        columns=['xmin','ymin','xmax','ymax','confidence','class']
    )
    df['name'] = df['class'].apply(lambda c: classes.get(int(c), f'class_{int(c)}'))
    print("Detecciones YOLOv5 (Plan B) => DF:\n", df)
    return df


def extract_text_from_roi(image, detections):
    extracted_data = []
    
    for _, row in detections.iterrows():
        cls_name = row['name']
        x_min, y_min, x_max, y_max = map(int, [row['xmin'], row['ymin'], row['xmax'], row['ymax']])
        roi = image[y_min:y_max, x_min:x_max]
        text = pytesseract.image_to_string(roi, config='--psm 6', lang='spa').strip()
        text = normalize_text(text)

        # Corregir clasificación de descripción
        if cls_name == "logo" and len(text.split()) > 3:
            cls_name = "descripcion"

        # Detectar correctamente cantidad
        if re.search(r'\b(Cant\.?|Cantidad)\b', text, re.IGNORECASE):
            cls_name = "cantidad"

        # Diferenciar precios de cantidad
        if re.match(r'^\d+(\.\d+)?$', text): 
            if "precio" not in cls_name.lower():
                cls_name = "cantidad"

        extracted_data.append({
            "class": cls_name,
            "text": text,
            "confidence": row['confidence'],
            "bbox": [x_min, y_min, x_max, y_max]
        })
    
    return extracted_data



def mark_detections(image, detections):
    """Dibuja las cajas de detección en la imagen y las devuelve para el frontend"""
    if image is None or image.size == 0:
        return None

    for _, row in detections.iterrows():
        x_min, y_min, x_max, y_max = map(int, [row['xmin'], row['ymin'], row['xmax'], row['ymax']])
        class_name = row['name']
        confidence = row['confidence']

        cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
        cv2.putText(image, f"{class_name} ({confidence:.2f})", (x_min, y_min - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

    return image



def image_to_base64(image):

    """Convierte la imagen a formato Base64 solo si es válida."""
    if image is None or image.size == 0:
        print("⚠ Advertencia: La imagen está vacía, se devuelve un valor por defecto.")
        return None  
    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer).decode('utf-8')




def preprocess_image(image):
    """Preprocesa la imagen para mejorar la detección del OCR"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convertir a escala de grises
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)  # Reducir ruido con desenfoque
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)  
    return thresh


def normalize_text(text):
    text = re.sub(r'[^\w\d\s.,-]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def process_detected_regions(image, detections):
    """Procesa las regiones detectadas, extrayendo texto y clasificando correctamente las cantidades"""
    extracted_data = []
    detected_values = {
        "cantidad": [],
        "descripcion": []
    }

    for _, row in detections.iterrows():
        cls_id = int(row['class'])
        cls_name = classes.get(cls_id, f'class_{cls_id}')
        
        x_min, y_min, x_max, y_max = map(int, [row['xmin'], row['ymin'], row['xmax'], row['ymax']])
        roi = image[y_min:y_max, x_min:x_max]
        preprocessed_roi = preprocess_image(roi)

        try:
            text = pytesseract.image_to_string(preprocessed_roi, config='--psm 6', lang='spa').strip()
            text = normalize_text(text)

            if re.search(r'\b(Cant\.?|Cantidad)\b', text, re.IGNORECASE):
                cls_name = "cantidad"

            # Diferenciar cantidades de precios
            if re.match(r'^\d+(\.\d+)?$', text):  
                if "precio" in cls_name.lower():  
                    continue  # Saltar este valor si es un precio
                cls_name = "cantidad"
                detected_values["cantidad"].append(text)

            # Asegurar que el precio tenga formato correcto con $
            if re.match(r'^\$\d+(\.\d+)?$', text):  
                cls_name = "precio_unitario"

            extracted_data.append({
                "class": cls_name,
                "text": text,
                "confidence": row['confidence'],  # Agregar confianza
                "bbox": [x_min, y_min, x_max, y_max]
            })

        except Exception as e:
            extracted_data.append({"class": cls_name, "text": "Error OCR", "confidence": 0.0})

    return extracted_data

@app.route('/process-document', methods=['POST'])
def process_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo'}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'El nombre del archivo está vacío'}), 400
    
    image_bgr = None
    
    if file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
        try:
            image_bgr = cv2.cvtColor(np.array(Image.open(file.stream).convert('RGB')), cv2.COLOR_RGB2BGR)
        except Exception as e:
            return jsonify({'error': f'Error procesando la imagen: {e}'}), 500
    
    elif file.filename.lower().endswith('.pdf'):
        try:
            images = convert_from_bytes(file.read())
            if not images:
                return jsonify({'error': 'No se pudo convertir el PDF en imágenes'}), 400
            image_bgr = cv2.cvtColor(np.array(images[0]), cv2.COLOR_RGB2BGR)
        except Exception as e:
            return jsonify({'error': f'Error procesando el PDF: {e}'}), 500
    else:
        return jsonify({'error': 'Tipo de archivo no soportado'}), 400

    detections = detect_sections(image_bgr)
    data = extract_text_from_roi(image_bgr, detections)

    marked_image = mark_detections(image_bgr, detections)
    image_base64 = image_to_base64(marked_image)

    return jsonify({'data': data, 'image': image_base64}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
