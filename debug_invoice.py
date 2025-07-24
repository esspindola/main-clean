#!/usr/bin/env python3

import requests
import os
from pathlib import Path

def test_invoice_processing():
    print("Testing invoice processing with debug...")
    
    # Find an invoice file
    invoice_folder = Path("C:/Users/aryes/OneDrive/Documentos/Luis/Luis 1")
    
    if not invoice_folder.exists():
        print(f"Invoice folder not found: {invoice_folder}")
        return
    
    # Get first PDF file
    pdf_files = list(invoice_folder.glob("*.pdf"))
    if not pdf_files:
        print("No PDF files found")
        return
    
    test_file = pdf_files[0]
    print(f"Testing with: {test_file.name}")
    
    # Process the file
    url = "http://localhost:8001/api/v1/invoice/process"
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'application/pdf')}
            data = {
                'enhance_ocr': 'true',
                'rotation_correction': 'true',
                'confidence_threshold': '0.1'
            }
            
            print("Sending request...")
            response = requests.post(url, files=files, data=data, timeout=120)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                print("\n=== RESULTS ===")
                print(f"Success: {result.get('success', False)}")
                print(f"Message: {result.get('message', 'N/A')}")
                
                metadata = result.get('metadata', {})
                print(f"\n=== METADATA ===")
                for field, value in metadata.items():
                    print(f"{field}: '{value}'")
                
                print(f"\n=== STATISTICS ===")
                stats = result.get('statistics', {})
                for key, value in stats.items():
                    print(f"{key}: {value}")
                
                line_items = result.get('line_items', [])
                print(f"\n=== LINE ITEMS ({len(line_items)}) ===")
                for i, item in enumerate(line_items[:3]):  # Show first 3
                    print(f"Item {i+1}:")
                    for k, v in item.items():
                        print(f"  {k}: {v}")
                
            else:
                print(f"Error: {response.text}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_invoice_processing()