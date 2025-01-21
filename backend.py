import torch
from flask import Flask, request, jsonify
import os
import cv2
from flask_cors import CORS
import pytesseract
from pdf2image import convert_from_bytes
import numpy as np
from PIL import Image

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Ruta del modelo YOLOv5
model_path = 'yolov5/runs/train/exp15/weights/best.pt'
model = torch.hub.load('yolov5', 'custom', path=model_path, source='local')

def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'tiff', 'bmp', 'pdf'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def detect_objects(image):
    results = model(image)
    detections = results.xyxy[0].tolist()
    names = model.names
    extracted_data = []

    for det in detections:
        xmin, ymin, xmax, ymax, conf, cls_index = det
        cls_name = names[int(cls_index)].strip().lower()
        x1, y1, x2, y2 = int(xmin), int(ymin), int(xmax), int(ymax)
        roi = image[y1:y2, x1:x2]
        text = pytesseract.image_to_string(roi, lang='eng').strip()
        extracted_data.append({
            "bbox": f"{x1},{y1},{x2},{y2}",
            "class": cls_name,
            "text": text,
            "confidence": conf
        })

    return extracted_data

def process_image(file):
    image = Image.open(file.stream).convert('RGB')
    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return detect_objects(image)

def process_pdf(file):
    images = convert_from_bytes(file.read())
    all_data = []

    for image in images:
        image_array = np.array(image)
        image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        data = detect_objects(image_array)
        all_data.extend(data)

    return all_data

@app.route('/process-document', methods=['POST'])
def process_document():
    if 'file' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'El nombre del archivo está vacío'}), 400

    if file and allowed_file(file.filename):
        filename = file.filename.lower()
        try:
            if filename.endswith('.pdf'):
                data = process_pdf(file)
            else:
                data = process_image(file)

            return jsonify({'data': data}), 200
        except Exception as e:
            return jsonify({'error': f'Error procesando el archivo: {e}'}), 500
    else:
        return jsonify({'error': 'Tipo de archivo no soportado'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
