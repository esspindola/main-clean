
"""
Test script para verificar endpoints del OCR backend
"""

import requests
import json
from pathlib import Path

# Configuración
BASE_URL = "http://localhost:5000"
API_BASE_URL = f"{BASE_URL}/api/v1"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_debug():
    """Test debug endpoint"""
    print("\n🔍 Testing debug endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/invoice/debug")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Model loaded: {data['model_status']['yolo_loaded']}")
        print(f"Classes count: {data['model_status']['classes_count']}")
        print(f"Available classes: {data['model_status']['available_classes']}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_supported_formats():
    """Test supported formats endpoint"""
    print("\n🔍 Testing supported formats endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/invoice/supported-formats")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Supported formats: {data['supported_formats']}")
        print(f"Max file size: {data['max_file_size_mb']}MB")
        print(f"Detected classes: {len(data['detected_classes'])} classes")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_file_validation():
    """Test file validation with dummy file"""
    print("\n🔍 Testing file validation...")
    try:
        # Crear archivo dummy
        dummy_content = b"dummy image content"
        files = {'file': ('test.jpg', dummy_content, 'image/jpeg')}
        
        response = requests.post(f"{API_BASE_URL}/invoice/validate", files=files)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Valid: {data.get('valid', False)}")
        print(f"Message: {data.get('message', data.get('error', 'No message'))}")
        return True  # Cualquier respuesta es válida para validación que sale aqui
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_all_tests():
    """Ejecutar todas las pruebas"""
    print("🚀 Iniciando pruebas del OCR Backend...")
    print("=" * 50)
    
    tests = [
        ("Health Check", test_health),
        ("Debug Info", test_debug),
        ("Supported Formats", test_supported_formats),
        ("File Validation", test_file_validation),
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
        print(f"{'✅' if result else '❌'} {test_name}: {'PASS' if result else 'FAIL'}")
    
    print("\n" + "=" * 50)
    print("📊 Resumen de pruebas:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"Pasadas: {passed}/{total}")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron!")
    else:
        print("⚠️ Algunas pruebas fallaron. Verifica que el servidor esté ejecutándose.")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests()