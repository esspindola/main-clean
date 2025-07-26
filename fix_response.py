#!/usr/bin/env python3
"""
EMERGENCY FIX: Script para arreglar el response del API de invoices
Este script se puede ejecutar independientemente para probar la lógica
"""

def fix_metadata_response(metadata_dict):
    """
    Función para limpiar metadata que viene con formato complejo
    """
    clean_metadata = {}
    
    for field, value in metadata_dict.items():
        print(f"🔧 Processing {field}: {type(value)} -> {value}")
        
        if isinstance(value, dict) and 'value' in value:
            # Es un diccionario con 'value'
            clean_value = value['value']
            clean_metadata[field] = clean_value if clean_value else 'No detectado'
            print(f"  ✅ DICT CLEANED {field}: '{clean_value}'")
            
        elif isinstance(value, str) and "{'value':" in value:
            # Es un string que parece diccionario
            try:
                import ast
                parsed = ast.literal_eval(value)
                clean_value = parsed.get('value', 'No detectado')
                clean_metadata[field] = clean_value
                print(f"  ✅ STRING PARSED {field}: '{clean_value}'")
            except Exception as e:
                print(f"  ❌ PARSE FAILED {field}: {e}")
                clean_metadata[field] = 'No detectado'
                
        else:
            # Valor directo
            final_value = value if value else 'No detectado'
            clean_metadata[field] = final_value
            print(f"  ✅ DIRECT {field}: '{final_value}'")
    
    return clean_metadata

# Ejemplo de test
if __name__ == "__main__":
    test_metadata = {
        'ruc': "{'value': '1390012949001', 'confidence': 0.8, 'bbox': {'xmin': 0, 'ymin': 0, 'xmax': 100, 'ymax': 100}}",
        'company_name': "{'value': 'IS.A.ElGnicodocumentovalidoparareconocerelpagoeselreciboemitidoporlaFabrilS.A.', 'confidence': 0.8, 'bbox': {'xmin': 0, 'ymin': 0, 'xmax': 100, 'ymax': 100}}",
        'date': "{'value': '24/06/2024', 'confidence': 0.8, 'bbox': {'xmin': 0, 'ymin': 0, 'xmax': 100, 'ymax': 100}}",
        'total': "{'value': '83.69', 'confidence': 0.8, 'bbox': {'xmin': 0, 'ymin': 0, 'xmax': 100, 'ymax': 100}}"
    }
    
    print("🧪 TESTING METADATA CLEANUP:")
    print("="*50)
    
    result = fix_metadata_response(test_metadata)
    
    print("\n✨ FINAL RESULT:")
    print("="*50)
    for field, value in result.items():
        print(f"  {field}: '{value}'")