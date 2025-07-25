
"""
Script para probar la conectividad y CORS del backend OCR
"""

import requests
import json

def test_backend_connection():
    """Prueba la conexión al backend"""
    print("🔍 Probando conexión al backend OCR...")
    
    # URLs a probar
    base_urls = [
        "http://localhost:8001",  # Docker
        "http://localhost:5000",  # Directo prueba
    ]
    
    endpoints = [
        "/health",
        "/api/v1/test-connection",
        "/api/v1/invoice/debug"
    ]
    
    for base_url in base_urls:
        print(f"\n📡 Probando {base_url}...")
        
        for endpoint in endpoints:
            try:
                url = f"{base_url}{endpoint}"
                print(f"  📍 GET {endpoint}...")
                
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"    ✅ Status: {response.status_code}")
                    if 'cors_enabled' in data:
                        print(f"    🌐 CORS: {'✅' if data['cors_enabled'] else '❌'}")
                    if 'model_loaded' in data:
                        print(f"    🤖 Model: {'✅' if data['model_loaded'] else '❌'}")
                else:
                    print(f"    ❌ Status: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                print(f"    ❌ Conexión rechazada")
            except requests.exceptions.Timeout:
                print(f"    ⏰ Timeout")
            except Exception as e:
                print(f"    ❌ Error: {e}")

def test_cors_from_browser():
    """Simula una solicitud CORS desde el navegador"""
    print("\n🌐 Probando CORS desde frontend...")
    
    headers = {
        'Origin': 'http://localhost:5173',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'Content-Type'
    }
    
    urls = [
        "http://localhost:8001/api/v1/invoice/process",
        "http://localhost:5000/api/v1/invoice/process"
    ]
    
    for url in urls:
        try:
            print(f"📍 OPTIONS {url}...")
            response = requests.options(url, headers=headers, timeout=5)
            print(f"  Status: {response.status_code}")
            
            # Verificar headers CORS
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            
            for header, value in cors_headers.items():
                if value:
                    print(f"  ✅ {header}: {value}")
                else:
                    print(f"  ❌ {header}: No configurado")
                    
        except Exception as e:
            print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de conectividad y CORS...")
    print("=" * 60)
    
    test_backend_connection()
    test_cors_from_browser()
    
    print("\n" + "=" * 60)
    print("📋 Para solucionar problemas:")
    print("1. Asegúrate de que Docker esté ejecutándose: docker compose up -d")
    print("2. O ejecuta directamente: python app.py")
    print("3. Verifica que los puertos 5000/8001 estén disponibles")
    print("4. Reinicia el frontend: npm run dev")