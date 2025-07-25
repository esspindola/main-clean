import sys
import os
from pathlib import Path


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_extraction_patterns():
    """Test pattern extraction on simple text"""
    import re
    
    test_text = """
    FACTURA No: 001-001-000000123
    RUC: 1234567890001
    EMPRESA DEMO S.A.
    FECHA: 15/01/2024
    SUBTOTAL: 100.00
    IVA 12%: 12.00
    TOTAL: 112.00
    """
    
    print("Testing pattern extraction...")
    print(f"Input text: {test_text}")
    
    # Test RUC pattern
    ruc_patterns = [
        r'R\.?U\.?C\.?\s*:?\s*(\d{11,13})',
        r'RUC[\s:]*(\d{11,13})',
    ]
    
    for pattern in ruc_patterns:
        matches = re.finditer(pattern, test_text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            text = match.group(1) if match.groups() else match.group(0)
            print(f"RUC found: '{text}'")
    
    # Test invoice number pattern
    invoice_patterns = [
        r'FACTURA[\s#:Nº]*(\d{3,15})',
        r'(\d{3}-\d{3}-\d{6,9})',
    ]
    
    for pattern in invoice_patterns:
        matches = re.finditer(pattern, test_text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            text = match.group(1) if match.groups() else match.group(0)
            print(f"Invoice number found: '{text}'")
    
    # Test total pattern
    total_patterns = [
        r'TOTAL[\s:$]*(\d+[.,]\d{2})',
    ]
    
    for pattern in total_patterns:
        matches = re.finditer(pattern, test_text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            text = match.group(1) if match.groups() else match.group(0)
            print(f"Total found: '{text}'")

if __name__ == "__main__":
    print("Testing intelligent extraction patterns...")
    test_extraction_patterns()