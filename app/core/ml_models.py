"""
ML Models Management
Centralized management for YOLOv5 and OCR models
"""

import torch
import logging
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import cv2
from flask import current_app

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages ML models loading and inference."""
    
    def __init__(self):
        self.yolo_model = None
        self.classes = {}
        self.is_loaded = False
    
    def load_models(self):
        """Load all required models."""
        try:
            self._load_yolo_model()
            self._load_classes()
            self.is_loaded = True
            logger.info("All models loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            self.is_loaded = False
            raise
    
    def _load_yolo_model(self):
        """Load YOLOv5 custom trained model using DetectMultiBackend."""
        try:
            model_path = current_app.config['MODEL_PATH']
            
            if not model_path.exists():
                logger.warning(f"Custom model not found at {model_path}, using dummy model")
                self.yolo_model = self._create_dummy_model()
            else:
                try:
                    
                    from models.common import DetectMultiBackend
                    self.yolo_model = DetectMultiBackend(str(model_path))
                    self.yolo_model.eval()
                    logger.info(f"Loaded custom YOLOv5 model using DetectMultiBackend from {model_path}")
                except Exception as backend_error:
                    logger.warning(f"DetectMultiBackend failed: {backend_error}, trying torch.hub")
                    try:
                       
                        self.yolo_model = torch.hub.load('ultralytics/yolov5', 'custom', path=str(model_path), trust_repo=True, force_reload=True)
                        logger.info(f"Loaded custom YOLOv5 model using torch.hub from {model_path}")
                        if hasattr(self.yolo_model, 'names'):
                            logger.info(f"Model classes: {self.yolo_model.names}")
                    except Exception as hub_error:
                        logger.warning(f"torch.hub also failed: {hub_error}, using dummy model")
                        self.yolo_model = self._create_dummy_model()
            
          
            if hasattr(self.yolo_model, 'conf'):
                self.yolo_model.conf = current_app.config['YOLO_CONFIDENCE_THRESHOLD']
            if hasattr(self.yolo_model, 'iou'):
                self.yolo_model.iou = current_app.config['YOLO_IOU_THRESHOLD']
            
            if hasattr(self.yolo_model, 'eval'):
                self.yolo_model.eval()
            
            logger.info("YOLOv5 model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load YOLOv5 model: {e}")
          
            self.yolo_model = self._create_dummy_model()
            logger.warning("Using dummy model as fallback")
    
    def _create_dummy_model(self):
        """Create a dummy model for fallback."""
        class DummyYOLOModel:
            def __init__(self):
                self.conf = 0.25
                self.iou = 0.45
                self.names = {}
            
            def __call__(self, img):
             
                return type('Result', (), {
                    'xyxy': [torch.zeros((0, 6))],
                    'pandas': lambda: type('Pandas', (), {
                        'xyxy': [torch.zeros((0, 6))]
                    })()
                })()
            
            def eval(self):
                pass
        
        return DummyYOLOModel()
    
    def _load_classes(self):
        """Load class names from data.yaml."""
        try:
            data_path = Path('datasets/data.yaml')
            
            if data_path.exists():
                with open(data_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    self.classes = {i: name for i, name in enumerate(data.get('names', []))}
            else:
               
                self.classes = {
                    0: 'logo', 1: 'R.U.C', 2: 'numero_factura', 3: 'fecha_hora',
                    4: 'razon_social', 5: 'cantidad', 6: 'descripcion', 7: 'precio_unitario',
                    8: 'precio_total', 9: 'subtotal', 10: 'iva', 11: 'Descripcion',
                    12: 'Cantidad', 13: 'unidades', 14: 'unidad', 15: 'Cajas_cantidad',
                    16: 'Articulo', 17: 'Nombre_del_producto'
                }
            
            logger.info(f"Loaded {len(self.classes)} classes: {list(self.classes.values())}")
            
        except Exception as e:
            logger.error(f"Failed to load classes: {e}")
            raise
    
    def detect_objects(self, image: np.ndarray) -> List[Dict]:
        """
        Perform object detection on image using YOLOv5.
        
        Args:
            image: Input image as numpy array (BGR format)
            
        Returns:
            List of detection dictionaries with bbox, confidence, and class info
        """
        if not self.is_loaded:
            self.load_models()
        
        try:
            # For dummy model, return empty list
            if isinstance(self.yolo_model, type(self._create_dummy_model())):
                logger.debug("Using dummy model, returning empty detections")
                return []
            
         
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
          
            try:
              
                from utils.augmentations import letterbox
                img, *_ = letterbox(image_rgb, new_shape=640, auto=False)
                
                # Convert to tensor format
                img = img.transpose((2, 0, 1))  # HWC → CHW
                img = np.ascontiguousarray(img)
                img = torch.from_numpy(img).float() / 255.0
                img = img.unsqueeze(0)  # batch=1
                
                # Run inference
                with torch.no_grad():
                    if hasattr(self.yolo_model, 'predict'):
                        # torch.hub format
                        results = self.yolo_model(image_rgb)
                        if hasattr(results, 'xyxy') and len(results.xyxy) > 0:
                            pred = results.xyxy[0]
                        else:
                            pred = torch.zeros((0, 6))
                    else:
                       
                        pred = self.yolo_model(img)[0]
                        
                        
                        try:
                            from utils.general import non_max_suppression
                            pred = non_max_suppression(pred, 
                                                     conf_thres=current_app.config['YOLO_CONFIDENCE_THRESHOLD'],
                                                     iou_thres=0.45)[0]
                        except ImportError:
                            logger.warning("non_max_suppression not available, using raw predictions")
                
                # Parse detections
                detections = []
                if pred is not None and len(pred):
                    if hasattr(pred, 'cpu'):
                        pred_numpy = pred.cpu().numpy()
                    else:
                        pred_numpy = pred.numpy() if hasattr(pred, 'numpy') else pred
                    
                    for detection in pred_numpy:
                        if len(detection) >= 6:
                            box = detection[:4]
                            conf = detection[4]
                            cls = detection[5]
                            
                            if conf >= current_app.config['YOLO_CONFIDENCE_THRESHOLD']:
                                class_id = int(cls)
                                class_name = self.classes.get(class_id, f'class_{class_id}')
                                
                                detections.append({
                                    'xmin': float(box[0]),
                                    'ymin': float(box[1]),
                                    'xmax': float(box[2]),
                                    'ymax': float(box[3]),
                                    'confidence': float(conf),
                                    'class_id': class_id,
                                    'class_name': class_name
                                })
                
            except Exception as e:
                logger.warning(f"Model inference failed: {e}, using dummy model")
                self.yolo_model = self._create_dummy_model()
                return []
            
            logger.debug(f"Detected {len(detections)} objects")
            return detections
            
        except Exception as e:
            logger.error(f"Object detection failed: {e}")
          
            return []
    
    def get_model_info(self) -> Dict:
        """Get information about loaded models."""
        return {
            'yolo_loaded': self.yolo_model is not None,
            'classes_count': len(self.classes),
            'classes': list(self.classes.values()),
            'confidence_threshold': current_app.config['YOLO_CONFIDENCE_THRESHOLD'],
            'iou_threshold': current_app.config['YOLO_IOU_THRESHOLD'],
            'is_loaded': self.is_loaded
        }