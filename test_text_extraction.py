import requests
import json
from pathlib import Path

def test_text_extraction():
    """Test text extraction specifically"""
    print("Testing text extraction from invoices...")
    
    # Find invoice folder
    invoice_folder = Path("C:/Users/aryes/OneDrive/Documentos/Luis/Luis 1")
    
    if not invoice_folder.exists():
        print(f"Invoice folder not found: {invoice_folder}")
        return
    
    # Get multiple PDF files to test
    pdf_files = list(invoice_folder.glob("*.pdf"))[:3]  # Test first 3
    if not pdf_files:
        print("No PDF files found")
        return
    
    print(f"Found {len(pdf_files)} PDF files to test")
    
    for i, test_file in enumerate(pdf_files, 1):
        print(f"\n{'='*60}")
        print(f"Testing {i}/{len(pdf_files)}: {test_file.name}")
        print(f"{'='*60}")
        
        # Test the backend
        url = "http://localhost:8001/api/v1/invoice/process"
        
        try:
            with open(test_file, 'rb') as f:
                files = {'file': (test_file.name, f, 'application/pdf')}
                data = {
                    'enhance_ocr': 'true',
                    'rotation_correction': 'true',
                    'confidence_threshold': '0.05'  # Very low threshold
                }
                
                print("Sending request...")
                response = requests.post(url, files=files, data=data, timeout=300)
                
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Check if we got the new logging
                    success = result.get('success', False)
                    message = result.get('message', 'No message')
                    processing_time = result.get('processing_time', 0)
                    
                    print(f"Success: {success}")
                    print(f"Message: {message}")
                    print(f"Processing time: {processing_time}s")
                    
                    # Check metadata
                    metadata = result.get('metadata', {})
                    extracted_count = 0
                    for field, value in metadata.items():
                        if value and value != 'None' and value.strip():
                            print(f"✅ {field}: '{value}'")
                            extracted_count += 1
                        else:
                            print(f"❌ {field}: Empty/None")
                    
                    print(f"📊 Total extracted: {extracted_count}/7 fields")
                    
                    # Check products
                    line_items = result.get('line_items', [])
                    if line_items:
                        print(f"📦 Products found: {len(line_items)}")
                        for j, item in enumerate(line_items[:2]):  # Show first 2
                            print(f"  Product {j+1}: {item.get('description', 'N/A')}")
                    else:
                        print("📦 No products found")
                    
                    # Check statistics
                    stats = result.get('statistics', {})
                    if stats:
                        print(f"📈 YOLO detections: {stats.get('yolo_detections', 0)}")
                        print(f"📈 Pattern detections: {stats.get('pattern_detections', 0)}")
                        print(f"📈 OCR confidence: {stats.get('ocr_confidence', 0):.2f}")
                
                else:
                    print(f"❌ Error {response.status_code}: {response.text}")
                    
        except Exception as e:
            print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_text_extraction()