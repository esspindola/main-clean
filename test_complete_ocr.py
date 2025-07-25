
"""
Test script for the complete OCR functionality
Tests both YOLO model loading and OCR processing
"""

import os
import sys
import logging
from pathlib import Path

# Add the app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app
from app.core.config import DevelopmentConfig

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_model_loading():
    """Test if models load correctly"""
    print("🔧 Creating Flask app...")
    app = create_app(DevelopmentConfig)
    
    with app.app_context():
        print("📊 Testing model loading...")
        
        # Check if model manager exists
        if not hasattr(app, 'model_manager'):
            print("❌ Model manager not found")
            return False
        
        model_info = app.model_manager.get_model_info()
        print(f"📈 Model Info:")
        print(f"   - YOLO Loaded: {model_info['yolo_loaded']}")
        print(f"   - Classes Count: {model_info['classes_count']}")
        print(f"   - Is Loaded: {model_info['is_loaded']}")
        print(f"   - Confidence Threshold: {model_info['confidence_threshold']}")
        
        if model_info['yolo_loaded'] and model_info['classes_count'] > 0:
            print("✅ Models loaded successfully!")
            print(f"📋 Available classes: {model_info['classes'][:5]}...")  # Show first 5
            return True
        else:
            print("❌ Models failed to load properly")
            return False

def test_ocr_engines():
    """Test OCR engines functionality"""
    print("\n🔍 Testing OCR engines...")
    
    try:
        import cv2
        import numpy as np
        import pytesseract
        
        # Create a test image with Spanish text
        test_img = np.ones((200, 600, 3), dtype=np.uint8) * 255
        cv2.putText(test_img, 'FACTURA No: 001-001-123456', (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        cv2.putText(test_img, 'SUBTOTAL: $125.50', (50, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        cv2.putText(test_img, 'TOTAL: $140.56', (50, 150), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        
        # Test Tesseract
        text = pytesseract.image_to_string(test_img, config='--psm 6 -l spa+eng')
        print(f"📝 Tesseract extracted: '{text.strip()}'")
        
        # Test EasyOCR
        try:
            import easyocr
            reader = easyocr.Reader(['es', 'en'], gpu=False)
            results = reader.readtext(test_img)
            print(f"🎯 EasyOCR found {len(results)} text regions")
            for bbox, text, conf in results:
                if conf > 0.5:
                    print(f"   - '{text}' (confidence: {conf:.2f})")
        except Exception as e:
            print(f"⚠️  EasyOCR test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ OCR engines test failed: {e}")
        return False

def test_enhanced_ocr_service():
    """Test the enhanced OCR service"""
    print("\n🚀 Testing Enhanced OCR Service...")
    
    try:
        from app.services.enhanced_ocr import EnhancedOCRService
        import cv2
        import numpy as np
        
        # Create test invoice-like image
        test_img = np.ones((400, 600, 3), dtype=np.uint8) * 255
        
        # Add some invoice-like content
        cv2.putText(test_img, 'Producto A', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        cv2.putText(test_img, '2', (300, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        cv2.putText(test_img, '$25.50', (450, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        cv2.putText(test_img, 'Producto B', (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        cv2.putText(test_img, '1', (300, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        cv2.putText(test_img, '$15.75', (450, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        enhanced_ocr = EnhancedOCRService()
        
        # Test table ROI detection
        roi = enhanced_ocr.find_table_roi(test_img)
        print(f"📍 Table ROI detected: {roi is not None}")
        if roi:
            print(f"   - ROI coordinates: {roi}")
        
        # Test invoice data extraction
        line_items = enhanced_ocr.extract_invoice_data(test_img)
        print(f"📋 Extracted {len(line_items)} line items:")
        
        for i, item in enumerate(line_items):
            print(f"   - Item {i+1}: {item.get('descripcion', 'N/A')} | "
                  f"Qty: {item.get('cantidad', 'N/A')} | "
                  f"Price: {item.get('precio', 'N/A')} | "
                  f"Conf: {item.get('confidence', 0):.2f}")
        
        return len(line_items) > 0
        
    except Exception as e:
        print(f"❌ Enhanced OCR test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Starting Complete OCR System Test")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Model Loading
    if test_model_loading():
        tests_passed += 1
    
    # Test 2: OCR Engines
    if test_ocr_engines():
        tests_passed += 1
    
    # Test 3: Enhanced OCR Service
    if test_enhanced_ocr_service():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Your OCR system is ready to process invoices!")
        print("\n💡 Next steps:")
        print("   1. Start the Flask app: python run.py")
        print("   2. Test with Swagger UI at: http://localhost:5000/docs/")
        print("   3. Upload a test invoice via /api/v1/invoice/process")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())