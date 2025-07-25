
"""
Script para probar el sistema híbrido YOLO + Patrones
"""

import requests
import json
from pathlib import Path
import time

def test_hybrid_system():
    """Probar el sistema híbrido con facturas reales"""
    print("🚀 PROBANDO SISTEMA HÍBRIDO YOLO + PATRONES")
    print("="*60)
    
    # Buscar facturas
    invoice_folder = Path("C:/Users/aryes/OneDrive/Documentos/Luis/Luis 1")
    
    if not invoice_folder.exists():
        print(f"❌ Carpeta no encontrada: {invoice_folder}")
        return
    
    pdf_files = list(invoice_folder.glob("*.pdf"))[:3]  # Probar primeras 3
    
    if not pdf_files:
        print("❌ No se encontraron archivos PDF")
        return
    
    print(f"📁 Encontradas {len(pdf_files)} facturas para probar")
    
    success_count = 0
    total_fields_extracted = 0
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n{'='*50}")
        print(f"🧪 PRUEBA {i}/{len(pdf_files)}: {pdf_file.name}")
        print(f"{'='*50}")
        
        try:
            # Probar con backend
            url = "http://localhost:8001/api/v1/invoice/process"
            
            with open(pdf_file, 'rb') as f:
                files = {'file': (pdf_file.name, f, 'application/pdf')}
                data = {
                    'enhance_ocr': 'true',
                    'rotation_correction': 'true',
                    'confidence_threshold': '0.2'
                }
                
                print("📡 Enviando a sistema híbrido...")
                start_time = time.time()
                
                response = requests.post(url, files=files, data=data, timeout=300)
                
                request_time = time.time() - start_time
                print(f"⏱️ Tiempo de request: {request_time:.2f}s")
                print(f"📊 Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    
                    success = result.get('success', False)
                    message = result.get('message', 'Sin mensaje')
                    processing_time = result.get('processing_time', 0)
                    
                    print(f"✅ Success: {success}")
                    print(f"📝 Message: {message}")
                    print(f"⏱️ Processing time: {processing_time}s")
                    
                    if success:
                        success_count += 1
                        
                        # Analizar metadata extraída
                        metadata = result.get('metadata', {})
                        extracted_count = 0
                        
                        print(f"\n📋 CAMPOS EXTRAÍDOS:")
                        for field, value in metadata.items():
                            if value and value.strip() and value != 'None':
                                print(f"  ✅ {field}: '{value}'")
                                extracted_count += 1
                            else:
                                print(f"  ❌ {field}: No detectado")
                        
                        total_fields_extracted += extracted_count
                        print(f"📊 Total extraído: {extracted_count}/7 campos")
                        
                        # Analizar productos
                        products = result.get('line_items', [])
                        if products:
                            print(f"📦 Productos encontrados: {len(products)}")
                            for j, product in enumerate(products[:2], 1):
                                desc = product.get('description', 'N/A')[:50]
                                print(f"  {j}. {desc}...")
                        else:
                            print("📦 No se encontraron productos")
                        
                        # Analizar estadísticas híbridas
                        stats = result.get('statistics', {})
                        hybrid_info = result.get('hybrid_info', {})
                        
                        print(f"\n🔬 ESTADÍSTICAS HÍBRIDAS:")
                        print(f"  🎯 YOLO detections: {stats.get('yolo_detections', 0)}")
                        print(f"  🔍 Pattern detections: {stats.get('pattern_detections', 0)}")
                        print(f"  🧠 YOLO fields: {hybrid_info.get('yolo_fields', 0)}")
                        print(f"  🔍 Pattern fields: {hybrid_info.get('pattern_fields', 0)}")
                        print(f"  🎯 OCR confidence: {stats.get('ocr_confidence', 0):.2f}")
                        print(f"  📝 Text length: {hybrid_info.get('text_length', 0)}")
                        
                        # Verificar si el modelo YOLO está funcionando
                        model_status = stats.get('model_status', {})
                        print(f"\n🤖 ESTADO DEL MODELO:")
                        print(f"  YOLO loaded: {model_status.get('yolo_loaded', False)}")
                        print(f"  Classes count: {model_status.get('classes_count', 0)}")
                        print(f"  Is loaded: {model_status.get('is_loaded', False)}")
                        
                    else:
                        print(f"❌ Error: {message}")
                        
                else:
                    print(f"❌ HTTP Error {response.status_code}: {response.text[:200]}")
                    
        except Exception as e:
            print(f"❌ Error procesando {pdf_file.name}: {e}")
    
    # Resumen final
    print(f"\n{'='*60}")
    print("📊 RESUMEN DEL SISTEMA HÍBRIDO")
    print(f"{'='*60}")
    print(f"✅ Facturas procesadas exitosamente: {success_count}/{len(pdf_files)}")
    
    if success_count > 0:
        avg_fields = total_fields_extracted / success_count
        print(f"📊 Promedio de campos extraídos: {avg_fields:.1f}/7")
        
        effectiveness = (success_count / len(pdf_files)) * 100
        print(f"🎯 Efectividad del sistema: {effectiveness:.1f}%")
        
        if avg_fields >= 4:
            print("🏆 ¡EXCELENTE! El sistema híbrido está funcionando muy bien")
        elif avg_fields >= 2:
            print("👍 BIEN: El sistema está extrayendo datos, se puede mejorar")
        else:
            print("⚠️ MEJORABLE: El sistema necesita ajustes")
    
    print(f"\n💡 El sistema híbrido combina:")
    print(f"   🎯 Tu modelo YOLO entrenado (exp_4/exp_retrain)")
    print(f"   🔍 Patrones inteligentes como respaldo")
    print(f"   🧠 Fusión automática de resultados")

if __name__ == "__main__":
    test_hybrid_system()