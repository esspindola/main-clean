import torch
from flask import Flask, request, jsonify
import os
import cv2
from flask_cors import CORS
import pytesseract

# Inicializar la aplicación Flask y habilitar CORS para comunicar con front
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Ruta completa al modelo entrenado
model_path = 'yolov5/runs/train/exp15/weights/best.pt'

# Carga del modelo YOLOv5 desde el repositorio local
model = torch.hub.load('yolov5', 'custom', path=model_path, source='local')

@app.route('/process-document', methods=['POST'])
def process_document():
    try:
        file = request.files.get('file')
        if not file:
            return jsonify({'error': 'No se proporcionó ningún archivo.'}), 400

        temp_path = os.path.join('temp', file.filename)
        file.save(temp_path)

        image = cv2.imread(temp_path)
        results = model(image)
        detections = results.xyxy[0].tolist()
        names = model.names

        extracted_rows = []  # Lista de filas dinámicas

        for det in detections:
            xmin, ymin, xmax, ymax, conf, cls_index = det
            cls_name = names[int(cls_index)].strip().lower()
            x1, y1, x2, y2 = int(xmin), int(ymin), int(xmax), int(ymax)

            #texto usando pytesseract
            roi = image[y1:y2, x1:x2]
            text = pytesseract.image_to_string(roi, lang='eng').strip()

            # aqui fila dinámica para el frontend
            extracted_rows.append({
                "bbox": f"{x1},{y1},{x2},{y2}",
                "class": cls_name,
                "text": text,
                "confidence": conf
            })

        os.remove(temp_path)
        return jsonify({"data": extracted_rows}), 200

    except Exception as e:
        print('Error:', e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs('temp', exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
