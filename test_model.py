import torch


model_path = 'yolov5/runs/train/exp4/weights/best.pt'


try:
    model = torch.hub.load('yolov5', 'custom', path=model_path, source='local')
    print("Modelo cargado exitosamente.")
except Exception as e:
    print(f"Error al cargar el modelo: {e}")
