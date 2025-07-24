#!/usr/bin/env python3

import requests
import json
from pathlib import Path

def test_with_logging():
    """Test backend with detailed logging"""
    print("Testing backend with detailed logging...")
    
    # Find a test invoice
    invoice_folder = Path("C:/Users/aryes/OneDrive/Documentos/Luis/Luis 1")
    
    if not invoice_folder.exists():
        print(f"Invoice folder not found: {invoice_folder}")
        return
    
    # Get a PDF file
    pdf_files = list(invoice_folder.glob("*.pdf"))
    if not pdf_files:
        print("No PDF files found")
        return
    
    test_file = pdf_files[0]  # Use first PDF
    print(f"Testing with: {test_file.name}")
    
    # Test the backend
    url = "http://localhost:8001/api/v1/invoice/process"
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'application/pdf')}
            data = {
                'enhance_ocr': 'true',
                'rotation_correction': 'true',
                'confidence_threshold': '0.1'
            }
            
            print("Sending request to backend...")
            response = requests.post(url, files=files, data=data, timeout=180)
            
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                
                print("\n=== FULL RESPONSE ===")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
                # Analyze specific fields
                print("\n=== ANALYSIS ===")
                metadata = result.get('metadata', {})
                for field, value in metadata.items():
                    print(f"{field}: '{value}' (type: {type(value)})")
                
                processing_time = result.get('processing_time', 0)
                print(f"Processing time: {processing_time}s")
                
                statistics = result.get('statistics', {})
                print(f"Statistics: {statistics}")
                
            else:
                print(f"Error response: {response.text}")
                
    except Exception as e:
        print(f"Request failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_with_logging()