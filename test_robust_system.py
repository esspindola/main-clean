
"""
Prueba del Sistema Robusto Multi-Motor
"""

import requests
import json
from pathlib import Path
import time

def test_robust_multi_engine():
    """Probar sistema robusto con múltiples motores"""
    print("🚀 PROBANDO SISTEMA ROBUSTO MULTI-MOTOR")
    print("🎯 YOLO + PaddleOCR + Tesseract + Patrones Ecuatorianos")
    print("="*70)
    
    # Buscar facturas
    invoice_folder = Path("C:/Users/aryes/OneDrive/Documentos/Luis/Luis 1")
    
    if not invoice_folder.exists():
        print(f"❌ Carpeta no encontrada: {invoice_folder}")
        return
    
    pdf_files = list(invoice_folder.glob("*.pdf"))[:5]  # Probar primeras 5
    
    if not pdf_files:
        print("❌ No se encontraron archivos PDF")
        return
    
    print(f"📁 Facturas encontradas: {len(pdf_files)}")
    
    results_summary = {
        'total_processed': 0,
        'successful': 0,
        'total_fields_extracted': 0,
        'motor_performance': {
            'yolo_working': 0,
            'paddle_working': 0,
            'tesseract_working': 0,
            'patterns_working': 0
        }
    }
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n{'='*50}")
        print(f"🧪 FACTURA {i}/{len(pdf_files)}: {pdf_file.name}")
        print(f"{'='*50}")
        
        try:
            url = "http://localhost:8001/api/v1/invoice/process"
            
            with open(pdf_file, 'rb') as f:
                files = {'file': (pdf_file.name, f, 'application/pdf')}
                data = {
                    'enhance_ocr': 'true',
                    'rotation_correction': 'true', 
                    'confidence_threshold': '0.05'  # Umbral muy bajo
                }
                
                print("📡 Enviando a sistema robusto...")
                start_time = time.time()
                
                response = requests.post(url, files=files, data=data, timeout=600)  # 10 min timeout
                
                request_time = time.time() - start_time
                results_summary['total_processed'] += 1
                
                print(f"⏱️ Request time: {request_time:.2f}s")
                print(f"📊 HTTP Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    
                    success = result.get('success', False)
                    message = result.get('message', '')
                    processing_time = result.get('processing_time', 0)
                    
                    print(f"✅ Success: {success}")  
                    print(f"📝 Message: {message}")
                    print(f"⏱️ Processing time: {processing_time}s")
                    
                    if success:
                        results_summary['successful'] += 1
                        
                        # Analizar metadata extraída
                        metadata = result.get('metadata', {})
                        extracted_count = 0
                        
                        print(f"\n📋 CAMPOS EXTRAÍDOS:")
                        field_order = ['company_name', 'ruc', 'invoice_number', 'date', 'subtotal', 'iva', 'total']
                        
                        for field in field_order:
                            value = metadata.get(field, '')
                            if value and str(value).strip() and str(value) != 'None':
                                print(f"  ✅ {field:15}: '{value}'")
                                extracted_count += 1
                            else:
                                print(f"  ❌ {field:15}: No detectado")
                        
                        results_summary['total_fields_extracted'] += extracted_count
                        print(f"\n📊 Efectividad: {extracted_count}/7 campos ({extracted_count/7*100:.1f}%)")
                        
                        # Analizar rendimiento de motores
                        multi_engine_info = result.get('multi_engine_info', {})
                        
                        print(f"\n🔧 RENDIMIENTO DE MOTORES:")
                        motors = [
                            ('🎯 YOLO', 'yolo_working', multi_engine_info.get('yolo_working', False)),
                            ('🏮 PaddleOCR', 'paddle_working', multi_engine_info.get('paddle_working', False)),
                            ('🔍 Tesseract', 'tesseract_working', multi_engine_info.get('tesseract_working', False)),
                            ('🇪🇨 Patrones', 'patterns_working', multi_engine_info.get('patterns_working', False))
                        ]
                        
                        for name, key, working in motors:
                            status = "✅ FUNCIONANDO" if working else "❌ FALLÓ"
                            print(f"  {name:15}: {status}")
                            if working:
                                results_summary['motor_performance'][key] += 1
                        
                        # Mostrar estadísticas detalladas
                        stats = result.get('statistics', {})
                        print(f"\n📈 ESTADÍSTICAS DETALLADAS:")
                        print(f"  YOLO detections: {stats.get('yolo_detections', 0)}")
                        print(f"  Pattern detections: {stats.get('pattern_detections', 0)}")
                        print(f"  PaddleOCR structured: {stats.get('paddle_structured', 0)}")
                        print(f"  OCR confidence: {stats.get('ocr_confidence', 0):.2f}")
                        
                        # Texto extraído
                        text_length = multi_engine_info.get('total_text_length', 0)
                        print(f"  Total text length: {text_length} chars")
                        
                        # Productos
                        products = result.get('line_items', [])
                        if products:
                            print(f"\n📦 PRODUCTOS ENCONTRADOS: {len(products)}")
                            for j, product in enumerate(products[:3], 1):
                                desc = product.get('description', 'N/A')[:40]
                                qty = product.get('quantity', 'N/A')
                                price = product.get('total_price', 'N/A')
                                print(f"  {j}. {desc}... (Qty: {qty}, Total: {price})")
                        else:
                            print(f"\n📦 No se encontraron productos")
                        
                        # Calificación del resultado
                        if extracted_count >= 5:
                            print(f"\n🏆 EXCELENTE: {extracted_count}/7 campos extraídos")
                        elif extracted_count >= 3:
                            print(f"\n👍 BUENO: {extracted_count}/7 campos extraídos")
                        elif extracted_count >= 1:
                            print(f"\n⚠️ REGULAR: {extracted_count}/7 campos extraídos")
                        else:
                            print(f"\n❌ POBRE: No se extrajeron campos")
                    
                    else:
                        print(f"❌ Procesamiento falló: {message}")
                        
                else:
                    print(f"❌ HTTP Error {response.status_code}")
                    error_text = response.text[:300] if hasattr(response, 'text') else 'No error text'
                    print(f"Error: {error_text}")
                    
        except Exception as e:
            print(f"❌ Error procesando {pdf_file.name}: {e}")
    
    # RESUMEN FINAL DETALLADO
    print(f"\n{'='*70}")
    print("📊 RESUMEN FINAL DEL SISTEMA ROBUSTO")
    print(f"{'='*70}")
    
    total = results_summary['total_processed']
    successful = results_summary['successful']
    
    print(f"📈 ESTADÍSTICAS GENERALES:")
    print(f"  Facturas procesadas: {successful}/{total}")
    print(f"  Tasa de éxito: {successful/total*100:.1f}%" if total > 0 else "  Tasa de éxito: 0%")
    
    if successful > 0:
        avg_fields = results_summary['total_fields_extracted'] / successful
        print(f"  Promedio campos extraídos: {avg_fields:.1f}/7")
        print(f"  Efectividad promedio: {avg_fields/7*100:.1f}%")
    
    print(f"\n🔧 RENDIMIENTO DE MOTORES:")
    motors_perf = results_summary['motor_performance']
    for motor_name, motor_key in [
        ('YOLO', 'yolo_working'),
        ('PaddleOCR', 'paddle_working'), 
        ('Tesseract', 'tesseract_working'),
        ('Patrones', 'patterns_working')
    ]:
        working_count = motors_perf[motor_key]
        percentage = working_count/total*100 if total > 0 else 0
        print(f"  {motor_name:12}: {working_count}/{total} facturas ({percentage:.1f}%)")
    
    print(f"\n💡 INTERPRETACIÓN:")
    if successful/total >= 0.8 if total > 0 else False:
        print("  🏆 SISTEMA FUNCIONANDO EXCELENTEMENTE")
        print("  ✅ La mayoría de motores están operativos")
    elif successful/total >= 0.5 if total > 0 else False:
        print("  👍 SISTEMA FUNCIONANDO BIEN")
        print("  ⚠️ Algunos motores pueden necesitar ajustes")
    else:
        print("  ⚠️ SISTEMA NECESITA MEJORAS")
        print("  🔧 Revisa la configuración de los motores")
    
    print(f"\n🎯 PRÓXIMOS PASOS RECOMENDADOS:")
    if motors_perf['yolo_working'] == 0:
        print("  1. 🎯 Arreglar modelo YOLO - verificar weights y clases")
    if motors_perf['paddle_working'] < total:
        print("  2. 🏮 Optimizar configuración PaddleOCR")  
    if motors_perf['patterns_working'] < total:
        print("  3. 🇪🇨 Refinar patrones ecuatorianos")
    
    print(f"\n✨ El sistema robusto combina 4 motores para máxima efectividad!")

if __name__ == "__main__":
    test_robust_multi_engine()