#!/usr/bin/env python3
"""
Test Simple OCR - Diagnóstico directo
"""

import cv2
import numpy as np
import pytesseract
import easyocr
from pdf2image import convert_from_path
import sys
import os

def test_simple_ocr():
    print("🔍 DIAGNÓSTICO SIMPLE OCR")
    print("=" * 50)
    
    # Test 1: Tesseract
    try:
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract version: {version}")
    except Exception as e:
        print(f"❌ Tesseract error: {e}")
        return
    
    # Test 2: EasyOCR
    try:
        reader = easyocr.Reader(['es', 'en'], gpu=False)
        print("✅ EasyOCR inicializado")
    except Exception as e:
        print(f"❌ EasyOCR error: {e}")
        return
    
    # Test 3: Imagen simple
    # Crear imagen de prueba con texto
    img = np.ones((100, 400, 3), dtype=np.uint8) * 255
    cv2.putText(img, 'FACTURA 001-001-12345', (10, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    
    print("\n📝 PRUEBA DE TEXTO SIMPLE:")
    
    # Tesseract
    try:
        text = pytesseract.image_to_string(img, config='--psm 8 -l spa+eng')
        print(f"✅ Tesseract: '{text.strip()}'")
    except Exception as e:
        print(f"❌ Tesseract OCR error: {e}")
    
    # EasyOCR
    try:
        results = reader.readtext(img)
        for (bbox, text, conf) in results:
            print(f"✅ EasyOCR: '{text}' (conf: {conf:.2f})")
    except Exception as e:
        print(f"❌ EasyOCR error: {e}")
    
    print("\n🎯 DIAGNÓSTICO COMPLETADO")

if __name__ == "__main__":
    test_simple_ocr()