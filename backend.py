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

# Directorio base
BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

MODEL_PATH = BASE_DIR / 'yolov5/runs/train/exp4/weights/best.pt'

# Configurar pytesseract
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
TESSDATA_DIR = '/usr/share/tesseract-ocr/5/tessdata/'
os.environ['TESSDATA_PREFIX'] = TESSDATA_DIR

# Cargar modelo YOLOv5 (como en tus commits anteriores)
try:
    model = torch.hub.load(
        str(BASE_DIR / 'yolov5'), 
        'custom', 
        path=str(MODEL_PATH), 
        source='local', 
        force_reload=True
    )
except Exception as e:
    print(f"Error cargando el modelo YOLOv5: {e}")
    exit(1)

def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'tiff', 'bmp', 'pdf'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def preprocess_image(image):
    """
    Preprocesar la imagen (en BGR) para mejorar OCR (opcional).
    Si quieres usarlo en ROI, llama preprocess_image(roi) antes de Tesseract.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thres = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    return thres

def detect_sections(image):
    """
    Detectar regiones usando YOLOv5. 
    Llama directamente a model(image), y parsea con results.pandas().xyxy[0].
    """
    results = model(image)
    detections = results.pandas().xyxy[0]
    print(f"Detecciones YOLOv5:\n{detections}")
    return detections

def mark_detections(image, detections):
    """
    Marcar detecciones en la imagen con cuadros delimitadores (BGR).
    """
    for _, row in detections.iterrows():
        x_min = int(row['xmin'])
        y_min = int(row['ymin'])
        x_max = int(row['xmax'])
        y_max = int(row['ymax'])
        cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
        cv2.putText(
            image, 
            str(row['name']), 
            (x_min, y_min - 10), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.5, 
            (255, 0, 0), 
            1
        )
    return image

def image_to_base64(image):
    """Convertir una imagen BGR en Base64."""
    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer).decode('utf-8')

def process_detected_regions(image, detections):
    """
    Procesar regiones detectadas (logo, descripción, total, etc.).
    Clampea bounding boxes para evitar 'tile cannot extend outside image'.
    """
    extracted_data = []
    img_h, img_w = image.shape[:2]  # alto y ancho de la imagen BGR

    for _, row in detections.iterrows():
        cls_name = row['name']  # Clase detectada (p.ej. "numero_factura", "logo", etc.)
        x_min = int(row['xmin'])
        y_min = int(row['ymin'])
        x_max = int(row['xmax'])
        y_max = int(row['ymax'])

        # Clamping: evitar coords negativas o mayores que la imagen
        x_min = max(0, min(x_min, img_w))
        x_max = max(0, min(x_max, img_w))
        y_min = max(0, min(y_min, img_h))
        y_max = max(0, min(y_max, img_h))

        if x_max <= x_min or y_max <= y_min:
            # ROI inválido
            text = "Texto no encontrado."
            print(f"ROI fuera de límites para {cls_name}, bounding box inválido.")
        else:
            # Extraer ROI
            roi = image[y_min:y_max, x_min:x_max]

            # Si deseas preprocesar para mejorar OCR, descomenta:
            # roi = preprocess_image(roi)

            # Aplicar OCR a la región
            try:
                text = pytesseract.image_to_string(roi, config='--psm 6', lang='spa').strip()
                # Ejemplo: buscar "numero_factura"
                if cls_name == "numero_factura":
                    factura_match = re.search(r'\d{3}-\d{3}-\d{6}', text)
                    if factura_match:
                        text = factura_match.group(0)
                    else:
                        text = "No encontrado"

                if not text:
                    text = "Texto no encontrado."
                print(f"Texto extraído para {cls_name}: {text}")
            except Exception as e:
                text = f"Error al procesar texto: {e}"
                print(f"Error para {cls_name}: {text}")

        conf_val = row['confidence'] if 'confidence' in row else None

        extracted_data.append({
            "class": cls_name,
            "bbox": f"{x_min},{y_min},{x_max},{y_max}",
            "text": text,
            "confidence": conf_val
        })

    # Filtrar duplicados si quieres (por "class"):
    processed_classes = set()
    filtered_data = []
    for item in extracted_data:
        if item["class"] not in processed_classes:
            filtered_data.append(item)
            processed_classes.add(item["class"])

    return filtered_data

@app.route('/process-document', methods=['POST'])
def process_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'El nombre del archivo está vacío'}), 400

    if file and allowed_file(file.filename):
        try:
            # Dependiendo del tipo (PDF o imagen)
            if file.filename.lower().endswith('.pdf'):
                # Convertir PDF a PIL pages
                pages = convert_from_bytes(file.read())
                results = []
                base64_image = None

                for page in pages:
                    # page es PIL en RGB, conviértelo a BGR
                    image_bgr = np.array(page)
                    image_bgr = cv2.cvtColor(image_bgr, cv2.COLOR_RGB2BGR)

                    # YOLOv5 
                    detections = detect_sections(image_bgr)  # model(image) => .pandas().xyxy[0]
                    data = process_detected_regions(image_bgr, detections)
                    results.extend(data)

                    # Marcar detecciones y a base64
                    marked_image = mark_detections(image_bgr, detections)
                    base64_image = image_to_base64(marked_image)

                return jsonify({'data': results, 'image': base64_image}), 200

            else:
                # Procesar imagen normal
                pil_img = Image.open(file.stream).convert('RGB')
                image_bgr = np.array(pil_img)
                image_bgr = cv2.cvtColor(image_bgr, cv2.COLOR_RGB2BGR)

                detections = detect_sections(image_bgr)
                data = process_detected_regions(image_bgr, detections)
                marked_image = mark_detections(image_bgr, detections)
                base64_image = image_to_base64(marked_image)

                return jsonify({'data': data, 'image': base64_image}), 200

        except Exception as e:
            traceback.print_exc()
            return jsonify({'error': f'Error procesando el archivo: {e}'}), 500
    else:
        return jsonify({'error': 'Tipo de archivo no soportado'}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
