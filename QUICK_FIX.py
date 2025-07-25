#!/usr/bin/env python3
"""
QUICK FIX - SIN REBUILD COMPLETO
Actualizar solo el archivo que causa bucle infinito
"""

import subprocess
import time

print("QUICK FIX - ACTUALIZANDO SOLO ARCHIVO PROBLEMATICO")
print("=" * 60)

# 1. Copiar archivo corregido al contenedor en ejecución
try:
    print("Copiando archivo corregido al contenedor...")
    subprocess.run([
        'docker', 'cp', 
        'robust_multi_engine_ocr.py', 
        'backend-ocr-ocr-backend-1:/app/robust_multi_engine_ocr.py'
    ], check=True)
    print("Archivo copiado exitosamente")
except Exception as e:
    print(f"Error copiando archivo: {e}")
    print("Intentando con nombre de contenedor alternativo...")
    try:
        subprocess.run([
            'docker', 'cp', 
            'robust_multi_engine_ocr.py', 
            'ocr-backend:/app/robust_multi_engine_ocr.py'
        ], check=True)
        print("Archivo copiado exitosamente (alternativo)")
    except Exception as e2:
        print(f"Error con nombre alternativo: {e2}")

# 2. Reiniciar solo el servicio backend
try:
    print("Reiniciando servicio backend...")
    subprocess.run(['docker', 'compose', 'restart', 'backend-ocr'], check=True)
    print("Backend reiniciado")
except Exception as e:
    print(f"Error reiniciando: {e}")

print("\nQUICK FIX COMPLETADO")
print("Espera 10 segundos y prueba en Swagger")
print("http://localhost:8001/docs")