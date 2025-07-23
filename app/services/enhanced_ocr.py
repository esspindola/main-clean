"""
Enhanced OCR Service
Combines the best of the original backend.py with the current architecture
"""

import cv2
import numpy as np
import pandas as pd
import easyocr
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
        self.easyocr_reader = easyocr.Reader(['es'], gpu=False)
        
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
        try:
            results = self.easyocr_reader.readtext(image)
            boxes = []
            
            for bbox, text, confidence in results:
                if confidence > 0.3:  
                    xs = [p[0] for p in bbox]
                    ys = [p[1] for p in bbox]
                    boxes.append({
                        "text": text.strip(),
                        "confidence": confidence,
                        "xmin": int(min(xs)),
                        "ymin": int(min(ys)),
                        "xmax": int(max(xs)),
                        "ymax": int(max(ys)),
                        "class": "ocr"
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
                        
                        if text and conf > 30:  
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
        """Assign column type based on text content and position"""
        text = bb["text"].strip().lower()
        x_cent = (bb["xmin"] + bb["xmax"]) / 2


        if any(indicator in text for indicator in ["$", "usd", "precio"]) or re.match(r'^\d+[.,]\d{2}$', text):
            return "precio"
        
        if re.match(r'^\d+$', text) and len(text) <= 3:
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

    def get_all_bboxes(self, image_np: np.ndarray, yolo_detections: Optional[List[Dict]] = None) -> Tuple[List[Dict], bool]:
        """Combine YOLO detections with OCR results"""
        
        roi_coords = self.find_table_roi(image_np)
        has_roi = roi_coords is not None
        
        if roi_coords:
            x, y, w, h = roi_coords
            ocr_target = image_np[y:y + h, x:x + w]
        else:
            ocr_target = image_np

        # YOLO boxes
        yolo_boxes = []
        if yolo_detections:
            for detection in yolo_detections:
                yolo_boxes.append({
                    "class": detection.get("class_name", "unknown"),
                    "text": "",
                    "confidence": detection.get("confidence", 0.0),
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