"""
Enhanced OCR Service
Combines the best of the original backend.py with the current architecture
"""

import cv2
import numpy as np
import pandas as pd

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ EasyOCR not available: {e}")
    EASYOCR_AVAILABLE = False
    easyocr = None
import pytesseract
import logging
from typing import List, Dict, Tuple, Optional
from collections import Counter
import re

logger = logging.getLogger(__name__)


class EnhancedOCRService:
    """
    Enhanced OCR service that combines YOLO detections with advanced OCR
    using the same logic that worked well in the original backend.py
    """
    
    def __init__(self):
        self.easyocr_reader = None
        if EASYOCR_AVAILABLE:
            try:
                self.easyocr_reader = easyocr.Reader(['es', 'en'], gpu=False)
                logger.info("EasyOCR initialized with Spanish and English")
            except Exception as e:
                logger.error(f"Failed to initialize EasyOCR: {e}")
                self.easyocr_reader = None
        else:
            logger.warning("EasyOCR not available, using Tesseract only")
        
    def find_table_roi(self, img_bgr: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Find table region of interest using morphological operations
        Returns (x,y,w,h) or None if no table found
        """
        try:
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                     cv2.THRESH_BINARY_INV, 15, -2)

           
            hor = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
            ver = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
            mask = cv2.dilate(cv2.erode(bw, hor), hor) | cv2.dilate(cv2.erode(bw, ver), ver)

            cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not cnts:
                return None
                
            
            x, y, w, h = cv2.boundingRect(max(cnts, key=cv2.contourArea))
            
           
            if w * h < 0.1 * img_bgr.shape[0] * img_bgr.shape[1]:
                return None
                
            return (x, y, w, h)
        except Exception as e:
            logger.warning(f"Table ROI detection failed: {e}")
            return None

    def easyocr_text_regions(self, image: np.ndarray) -> List[Dict]:
        """Extract text regions using EasyOCR"""
        if not self.easyocr_reader:
            logger.warning("EasyOCR not available, skipping")
            return []
            
        try:
            results = self.easyocr_reader.readtext(image)
            boxes = []
            
            for bbox, text, confidence in results:
                if confidence > 0.2:  
                    text = text.strip()
                
                    if len(text) < 1:
                        continue
                        
                    xs = [p[0] for p in bbox]
                    ys = [p[1] for p in bbox]
                    boxes.append({
                        "text": text,
                        "confidence": confidence,
                        "xmin": int(min(xs)),
                        "ymin": int(min(ys)),
                        "xmax": int(max(xs)),
                        "ymax": int(max(ys)),
                        "class": "easyocr"
                    })
            
            logger.info(f"EasyOCR detected {len(boxes)} text regions")
            return boxes
        except Exception as e:
            logger.error(f"EasyOCR failed: {e}")
            return []

    def tesseract_text_regions(self, image: np.ndarray) -> List[Dict]:
        """Extract text regions using Tesseract with multiple configurations"""
        try:
            boxes = []
          
            configs = [
                '--psm 6 -l spa+eng',  
                '--psm 8 -l spa+eng',  
                '--psm 7 -l spa+eng', 
                '--psm 13 -l spa+eng'  
            ]
            
            for config in configs:
                try:
                    data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)
                    
                    for i in range(len(data['text'])):
                        text = data['text'][i].strip()
                        conf = int(data['conf'][i])
                        
                        if text and conf > 20:  
                            # Clean text
                            text = re.sub(r'[^\w\s\$\.,\-]', '', text).strip()
                            if len(text) >= 1:  
                                boxes.append({
                                    "text": text,
                                    "confidence": conf / 100.0, 
                                    "xmin": data['left'][i],
                                    "ymin": data['top'][i],
                                    "xmax": data['left'][i] + data['width'][i],
                                    "ymax": data['top'][i] + data['height'][i],
                                    "class": "tesseract"
                                })
                    break  
                except Exception as config_error:
                    continue
            
            logger.info(f"Tesseract detected {len(boxes)} text regions")
            return boxes
        except Exception as e:
            logger.error(f"Tesseract failed: {e}")
            return []

    def split_and_classify_text(self, bb: Dict) -> List[Dict]:
        """Split multi-token text into individual tokens"""
        text = bb["text"]
        tokens = text.split()
        
        sub_bboxes = []
        for tok in tokens:
            new_bb = bb.copy()
            new_bb["text"] = tok
            sub_bboxes.append(new_bb)
        
        return sub_bboxes

    def assign_column(self, bb: Dict, x_desc_max: int, x_cant_max: int) -> str:
        """Enhanced column assignment using both content and position"""
        text = bb["text"].strip().lower()
        x_cent = (bb["xmin"] + bb["xmax"]) / 2

        
        if any(indicator in text for indicator in ["$", "usd", "precio", "total"]):
            return "precio"
            
    
        if re.match(r'^\d+[.,]\d{2}$', text) or (re.match(r'^\d+$', text) and len(text) >= 4):
            return "precio"
        
        
        if re.match(r'^\d+$', text) and len(text) <= 3 and int(text) < 1000:
            return "cantidad"
            
        if any(unit in text for unit in ["unid", "pza", "kg", "lt", "und", "pcs"]):
            return "cantidad"
        
        
        if x_cent < x_desc_max:
            return "descripcion"
        elif x_cent < x_cant_max:
            return "cantidad"
        else:
            return "precio"

    def group_bboxes_by_rows_and_cols(self, bboxes: List[Dict], 
                                    row_tol: Optional[int] = None,
                                    x_desc_max: int = 1400,
                                    x_cant_max: int = 1900) -> List[Dict]:
        """Group text boxes into table rows and classify columns"""
        
        SKIP_CLASSES = {"logo", "r.u.c", "ruc", "fecha_hora", "numero_factura", "razon_social"}
        
        good = [bb for bb in bboxes 
                if isinstance(bb, dict) and bb.get("class", "").lower() not in SKIP_CLASSES]
        
        if not good:
            return []

        if row_tol is None:
            img_h = max(bb["ymax"] for bb in good)
            row_tol = int(img_h * 0.008) or 15

        for bb in good:
            bb["y_center"] = (bb["ymin"] + bb["ymax"]) / 2
        good.sort(key=lambda b: b["y_center"])

        rows = []
        current_row = [good[0]]
        current_center = good[0]["y_center"]
        
        for bb in good[1:]:
            if abs(bb["y_center"] - current_center) < row_tol:
                current_row.append(bb)
                current_center = sum(b["y_center"] for b in current_row) / len(current_row)
            else:
                rows.append(current_row)
                current_row = [bb]
                current_center = bb["y_center"]
        rows.append(current_row)

        extracted_rows = []
        for row in rows:
            desc_parts = []
            cant_parts = []
            price_parts = []
            row_conf = 1.0
            
            for bb in row:
                column = self.assign_column(bb, x_desc_max, x_cant_max)
                row_conf = min(row_conf, bb.get("confidence", 1.0))
                token = bb["text"]
                
                if column == "descripcion":
                    desc_parts.append(token)
                elif column == "cantidad":
                    cant_parts.append(token)
                elif column == "precio":
                    price_parts.append(token)


            classes = [bb.get("class", "") for bb in row]
            top_class = Counter(classes).most_common(1)
            top_class = top_class[0][0] if top_class else ""

            extracted_rows.append({
                "descripcion": " ".join(desc_parts) or "No detectado",
                "cantidad": " ".join(cant_parts) or "No detectado", 
                "precio": " ".join(price_parts) or "No detectado",
                "confidence": round(row_conf, 3),
                "class": top_class
            })

        return extracted_rows

    def extract_text_from_yolo_regions(self, image: np.ndarray, yolo_detections: List[Dict]) -> List[Dict]:
        """Extract text from YOLO detected regions using both OCR engines"""
        enriched_detections = []
        
        for detection in yolo_detections:
            
            x1, y1 = int(detection.get('xmin', 0)), int(detection.get('ymin', 0))
            x2, y2 = int(detection.get('xmax', 0)), int(detection.get('ymax', 0))
            
            if x2 > x1 and y2 > y1:
                region = image[y1:y2, x1:x2]
                
                
                region_texts = []
                
                # EasyOCR first
                easy_boxes = self.easyocr_text_regions(region)
                for box in easy_boxes:
                    if box['confidence'] > 0.4:
                        region_texts.append((box['text'], box['confidence']))
                
                # Tesseract as backup
                if not region_texts:
                    tess_boxes = self.tesseract_text_regions(region)
                    for box in tess_boxes:
                        if box['confidence'] > 0.3:
                            region_texts.append((box['text'], box['confidence']))
                
                # Choose best text
                if region_texts:
                    best_text, best_conf = max(region_texts, key=lambda x: x[1])
                    detection['extracted_text'] = best_text
                    detection['ocr_confidence'] = best_conf
                else:
                    detection['extracted_text'] = ''
                    detection['ocr_confidence'] = 0.0
            
            enriched_detections.append(detection)
        
        return enriched_detections
    
    def get_all_bboxes(self, image_np: np.ndarray, yolo_detections: Optional[List[Dict]] = None) -> Tuple[List[Dict], bool]:
        """Combine YOLO detections with OCR results - enhanced version"""
        
       
        roi_coords = self.find_table_roi(image_np)
        has_roi = roi_coords is not None
        
      
        if roi_coords:
            x, y, w, h = roi_coords
            ocr_target = image_np[y:y + h, x:x + w]
            logger.info(f"Using table ROI: {roi_coords}")
        else:
            ocr_target = image_np
            logger.info("Using full image for OCR")

      
        yolo_boxes = []
        if yolo_detections:
            enriched_yolo = self.extract_text_from_yolo_regions(image_np, yolo_detections)
            for detection in enriched_yolo:
                yolo_boxes.append({
                    "class": detection.get("class_name", "unknown"),
                    "text": detection.get("extracted_text", ""),
                    "confidence": detection.get("confidence", 0.0),
                    "ocr_confidence": detection.get("ocr_confidence", 0.0),
                    "xmin": int(detection.get("xmin", 0)),
                    "ymin": int(detection.get("ymin", 0)),
                    "xmax": int(detection.get("xmax", 0)),
                    "ymax": int(detection.get("ymax", 0)),
                })

      
        image_rgb = cv2.cvtColor(ocr_target, cv2.COLOR_BGR2RGB)
        ocr_boxes = self.easyocr_text_regions(image_rgb)
        
      
        tesseract_boxes = self.tesseract_text_regions(ocr_target)
        ocr_boxes.extend(tesseract_boxes)

       
        if roi_coords:
            x, y = roi_coords[:2]
            for box in ocr_boxes:
                box["xmin"] += x
                box["xmax"] += x
                box["ymin"] += y
                box["ymax"] += y

        expanded = []
        for box in ocr_boxes:
            expanded.extend(self.split_and_classify_text(box))

        logger.info(f"Combined {len(yolo_boxes)} YOLO boxes with {len(expanded)} OCR boxes")
        return yolo_boxes + expanded, has_roi

    def extract_invoice_data(self, image: np.ndarray, yolo_detections: Optional[List[Dict]] = None) -> List[Dict]:
        """
        Main method to extract invoice line items from image
        Combines YOLO detections with advanced OCR processing
        """
        try:
           
            all_boxes, has_roi = self.get_all_bboxes(image, yolo_detections)
            
            
            W = image.shape[1]
            if has_roi:
                x_desc = int(0.40 * W)  
                x_cant = int(0.60 * W)  
            else:
                x_desc = int(0.45 * W)   
                x_cant = int(0.65 * W) 

            rows = self.group_bboxes_by_rows_and_cols(
                all_boxes,
                row_tol=None,  
                x_desc_max=x_desc,
                x_cant_max=x_cant
            )

            logger.info(f"Extracted {len(rows)} invoice line items")
            return rows
            
        except Exception as e:
            logger.error(f"Invoice data extraction failed: {e}")
            return []