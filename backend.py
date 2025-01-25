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
import pandas as pd  # Ojo: Asegúrate de tenerlo en requirements.txt
from dotenv import load_dotenv
import sys
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR / 'yolov5'))  # Ajusta si tu yolov5 está en esa carpeta
try:
    from utils.general import non_max_suppression
except ImportError:
    non_max_suppression = None  # Si no existe, daremos error

app = Flask(__name__)
ENV = os.getenv("FLASK_ENV", "production")

if ENV == "development":
    CORS(app, resources={r"/*": {"origins": "*"}})
    print("CORS configurado para desarrollo (orígenes: *)")
else:
    # Permitir solo el dominio de producción
    CORS(app, resources={r"/*": {"origins": "https://web-navy-nine.vercel.app"}})
    print("CORS configurado para producción (orígenes: https://web-navy-nine.vercel.app/ocr)")

MODEL_PATH = BASE_DIR / 'yolov5/runs/train/exp4/weights/best.pt'
if not MODEL_PATH.exists():
    print(f"ERROR: El modelo no existe en la ruta: {MODEL_PATH}")
    exit(1)


# Configurar pytesseract
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
TESSDATA_DIR = '/usr/share/tesseract-ocr/5/tessdata/'
os.environ['TESSDATA_PREFIX'] = TESSDATA_DIR

print(f"Tesseract versión: {pytesseract.get_tesseract_version()}")
print(f"TESSDATA_PREFIX: {os.environ.get('TESSDATA_PREFIX')}")


# Cargar modelo YOLOv5 (versión local con 'custom' + force_reload)
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
    return ('.' in filename and 
            filename.rsplit('.', 1)[1].lower() in 
            {'png','jpg','jpeg','tiff','bmp','pdf'})

def detect_sections(image):
    """
    Unifica ambos métodos:
    1) Intenta 'model(image)' + 'results.pandas().xyxy[0]' (modo local).
    2) Si falla en producción, pasamos a 'Plan B':
       - Convertir 'image' a tensor
       - Llamar al modelo
       - Hacer NMS manual
       - Armar DataFrame con [xmin,ymin,xmax,ymax,confidence,class,name]
    """
    try:
        # ----- PLAN A: Lógica vieja -----
        results = model(image)  # si local lo soporta
        df = results.pandas().xyxy[0]
        print("Detecciones YOLOv5 (Plan A):\n", df)
        return df

    except TypeError as ex:
        # Aparece en producción: conv2d(...) invalid arguments
        print("**Fallo con 'model(image)'; intentando Plan B**:", ex)
        return detect_sections_plan_b(image)

    except RuntimeError as ex:
        # A veces da un RuntimeError similar
        print("**Fallo con 'model(image)'; intentando Plan B**:", ex)
        return detect_sections_plan_b(image)

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
        # Si no tenemos la función importada, no podemos proseguir
        print("No se pudo importar non_max_suppression. Actualiza tu 'yolov5'.")
        # Retorna un DF vacío
        return pd.DataFrame(columns=['xmin','ymin','xmax','ymax','confidence','class','name'])

    if len(image_bgr.shape) == 3 and image_bgr.shape[2] == 3:
        # BGR -> RGB
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    else:
        # imagen de 1 canal o 2 => no debería pasar
        image_rgb = image_bgr

    # Redimensionar a 640x640 (opcional)
    image_rgb = cv2.resize(image_rgb, (640,640), interpolation=cv2.INTER_LINEAR)

    # [1,3,640,640], float, normalizado
    image_tensor = torch.from_numpy(image_rgb).float().permute(2,0,1).unsqueeze(0)/255.0

    # forward
    with torch.no_grad():
        raw_preds = model(image_tensor)  # shape [1, #Anchors, #Datos]

    # NMS
    # conf_thres=0.25, iou_thres=0.45 se suelen usar por defecto
    nms = non_max_suppression(raw_preds, conf_thres=0.25, iou_thres=0.45)
    # nms es lista de (batch_size) tensores Nx6
    if not nms or nms[0] is None or len(nms[0])==0:
        # Sin detecciones
        df = pd.DataFrame(columns=['xmin','ymin','xmax','ymax','confidence','class','name'])
        print("Detecciones YOLOv5 (Plan B): vacio")
        return df

    # Tomar la primera
    pred = nms[0].cpu().numpy()  # Nx6
    df = pd.DataFrame(
        pred, 
        columns=['xmin','ymin','xmax','ymax','confidence','class']
    )
    # Generar 'name' asumiendo que no tenemos un mapeo exacto
    df['name'] = df['class'].apply(lambda c: f"class_{int(c)}")

    print("Detecciones YOLOv5 (Plan B) => DF:\n", df)
    return df

def mark_detections(image, detections):
    """Igual que siempre"""
    for _, row in detections.iterrows():
        x_min, y_min = int(row['xmin']), int(row['ymin'])
        x_max, y_max = int(row['xmax']), int(row['ymax'])
        cv2.rectangle(image, (x_min, y_min),(x_max, y_max),(0,255,0),2)
        cv2.putText(image,str(row['name']),(x_min,y_min-10),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,0,0),1)
    return image

def image_to_base64(image):
    _, buffer = cv2.imencode('.jpg', image)
    return base64.b64encode(buffer).decode('utf-8')

def process_detected_regions(image, detections):
    """
    Igual a tu lógica antigua, con bounding boxes y OCR.
    + Clamping para tile outside.
    """
    extracted_data = []
    h, w = image.shape[:2]

    for _, row in detections.iterrows():
        cls_name = row['name']
        x_min, y_min = int(row['xmin']), int(row['ymin'])
        x_max, y_max = int(row['xmax']), int(row['ymax'])

        # Clamping
        x_min = max(0, min(x_min, w))
        x_max = max(0, min(x_max, w))
        y_min = max(0, min(y_min, h))
        y_max = max(0, min(y_max, h))

        if x_max<=x_min or y_max<=y_min:
            text="Texto no encontrado."
            print(f"ROI fuera de límites para {cls_name}.")
        else:
            roi = image[y_min:y_max, x_min:x_max]
            try:
                text = pytesseract.image_to_string(roi, config='--psm 6', lang='spa').strip()
                if cls_name=="numero_factura":
                    factura_match = re.search(r'\d{3}-\d{3}-\d{6}', text)
                    if factura_match:
                        text = factura_match.group(0)
                    else:
                        text="No encontrado"
                if not text: text="Texto no encontrado."
                print(f"Texto extraído para {cls_name}: {text}")
            except Exception as e:
                text = f"Error al procesar texto: {e}"
                print(f"Error para {cls_name}: {text}")

        conf = row['confidence'] if 'confidence' in row else None
        extracted_data.append({
            "class": cls_name,
            "bbox": f"{x_min},{y_min},{x_max},{y_max}",
            "text": text,
            "confidence": conf
        })

    # Quitar duplicados
    processed_classes=set()
    filtered_data=[]
    for item in extracted_data:
        if item["class"] not in processed_classes:
            filtered_data.append(item)
            processed_classes.add(item["class"])
    return filtered_data

@app.route('/process-document', methods=['POST'])
def process_document():
    if 'file' not in request.files:
        return jsonify({'error':'No se envió ningún archivo'}),400

    file=request.files['file']
    if file.filename=='':
        return jsonify({'error':'El nombre del archivo está vacío'}),400

    if file and allowed_file(file.filename):
        try:
            # Si es PDF
            if file.filename.lower().endswith('.pdf'):
                pages=convert_from_bytes(file.read())
                results=[]
                base64_image=None
                for page in pages:
                    image_bgr=np.array(page)
                    cv2.imwrite("pdf_page_debug.jpg", image_bgr)  # Guardar página como imagen
                    image_bgr=cv2.cvtColor(image_bgr, cv2.COLOR_RGB2BGR)
                    cv2.imwrite("bgr_image_debug.jpg", image_bgr)  # Guardar imagen convertida

                    detections=detect_sections(image_bgr)
                    data=process_detected_regions(image_bgr,detections)
                    results.extend(data)

                    marked_image=mark_detections(image_bgr,detections)
                    base64_image=image_to_base64(marked_image)
                return jsonify({'data':results,'image':base64_image}),200

            # Imagen normal
            else:
                pil_img=Image.open(file.stream).convert('RGB')
                image_bgr=np.array(pil_img)
                image_bgr=cv2.cvtColor(image_bgr, cv2.COLOR_RGB2BGR)

                detections=detect_sections(image_bgr)
                data=process_detected_regions(image_bgr,detections)
                marked_image=mark_detections(image_bgr,detections)
                base64_image=image_to_base64(marked_image)

                return jsonify({'data':data,'image':base64_image}),200

        except Exception as e:
            traceback.print_exc()
            return jsonify({'error':f'Error procesando el archivo: {e}'}),500
    else:
        return jsonify({'error':'Tipo de archivo no soportado'}),400

if __name__=='__main__':
    port=int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port, debug=True)
