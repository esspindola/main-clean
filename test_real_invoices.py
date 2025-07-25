
"""
Script para probar el análisis inteligente con facturas reales
Prueba múltiples facturas y genera reporte de efectividad
"""

import sys
import os
import cv2
import numpy as np
from pathlib import Path
import json
from datetime import datetime
import requests
import time

# Configurar paths
INVOICE_FOLDER = Path("C:/Users/aryes/OneDrive/Documentos/Luis/Luis 1")
OCR_API_URL = "http://localhost:8001/api/v1/invoice/process"
RESULTS_FOLDER = Path("test_results")

def setup_test_environment():
    """Prepara el entorno de pruebas"""
    RESULTS_FOLDER.mkdir(exist_ok=True)
    print(f"🔧 Configurando pruebas...")
    print(f"📁 Carpeta de facturas: {INVOICE_FOLDER}")
    print(f"📊 Resultados en: {RESULTS_FOLDER}")

def test_api_connection():
    """Prueba la conexión con la API"""
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            print("✅ API conectada correctamente")
            return True
        else:
            print(f"❌ API respondió con código {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando con API: {e}")
        return False

def process_invoice_file(file_path: Path):
    """Procesa un archivo de factura individual"""
    print(f"\n🔍 Procesando: {file_path.name}")
    
    try:
        # Preparar archivo para envío
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/pdf')}
            
            # Opciones de procesamiento
            data = {
                'enhance_ocr': 'true',
                'rotation_correction': 'true',
                'confidence_threshold': '0.2'  # Umbral más bajo para capturar más datos
            }
            
            start_time = time.time()
            response = requests.post(OCR_API_URL, files=files, data=data, timeout=120)
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                return analyze_result(file_path.name, result, processing_time)
            else:
                print(f"❌ Error {response.status_code}: {response.text}")
                return {
                    'filename': file_path.name,
                    'success': False,
                    'error': f"HTTP {response.status_code}",
                    'processing_time': processing_time
                }
                
    except Exception as e:
        print(f"❌ Error procesando {file_path.name}: {e}")
        return {
            'filename': file_path.name,
            'success': False,
            'error': str(e),
            'processing_time': 0
        }

def analyze_result(filename: str, result: dict, processing_time: float):
    """Analiza los resultados de procesamiento"""
    analysis = {
        'filename': filename,
        'success': result.get('success', False),
        'processing_time': processing_time,
        'format_detected': result.get('format_detected', 'unknown'),
        'confidence_score': result.get('confidence_score', 0),
        'fields_extracted': {},
        'products_count': 0,
        'yolo_detections': 0,
        'pattern_detections': 0
    }
    
    # Analizar metadatos extraídos
    metadata = result.get('metadata', {})
    for field in ['company_name', 'ruc', 'invoice_number', 'date', 'subtotal', 'iva', 'total']:
        value = metadata.get(field, '')
        analysis['fields_extracted'][field] = {
            'value': value,
            'extracted': bool(value and value != 'No detectado')
        }
    
    # Contar productos
    line_items = result.get('line_items', [])
    analysis['products_count'] = len(line_items)
    
    # Estadísticas de detección
    stats = result.get('statistics', {})
    analysis['yolo_detections'] = stats.get('yolo_detections', 0)
    analysis['pattern_detections'] = stats.get('pattern_detections', 0)
    
    # Mostrar resumen
    extracted_fields = sum(1 for field_data in analysis['fields_extracted'].values() if field_data['extracted'])
    print(f"   📊 Campos extraídos: {extracted_fields}/7")
    print(f"   📦 Productos: {analysis['products_count']}")
    print(f"   🎯 Confianza: {analysis['confidence_score']:.2f}")
    print(f"   📋 Formato: {analysis['format_detected']}")
    print(f"   ⏱️ Tiempo: {processing_time:.2f}s")
    
    # Mostrar campos extraídos
    for field, data in analysis['fields_extracted'].items():
        if data['extracted']:
            print(f"      ✅ {field}: {data['value']}")
    
    return analysis

def generate_report(results: list):
    """Genera reporte completo de las pruebas"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_invoices': len(results),
        'successful_processing': sum(1 for r in results if r['success']),
        'average_processing_time': sum(r['processing_time'] for r in results) / len(results) if results else 0,
        'field_extraction_stats': {},
        'format_distribution': {},
        'results': results
    }
    
    # Estadísticas de extracción por campo
    fields = ['company_name', 'ruc', 'invoice_number', 'date', 'subtotal', 'iva', 'total']
    for field in fields:
        extracted_count = sum(1 for r in results if r.get('fields_extracted', {}).get(field, {}).get('extracted', False))
        report['field_extraction_stats'][field] = {
            'extracted': extracted_count,
            'percentage': (extracted_count / len(results) * 100) if results else 0
        }
    
    # Distribución de formatos
    for result in results:
        format_type = result.get('format_detected', 'unknown')
        report['format_distribution'][format_type] = report['format_distribution'].get(format_type, 0) + 1
    
    # Guardar reporte
    report_file = RESULTS_FOLDER / f"invoice_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📋 REPORTE GENERADO: {report_file}")
    return report

def print_summary(report: dict):
    """Imprime resumen ejecutivo"""
    print("\n" + "="*80)
    print("📊 RESUMEN EJECUTIVO - ANÁLISIS DE FACTURAS")
    print("="*80)
    
    print(f"📈 Facturas procesadas: {report['total_invoices']}")
    print(f"✅ Procesamiento exitoso: {report['successful_processing']}/{report['total_invoices']} ({report['successful_processing']/report['total_invoices']*100:.1f}%)")
    print(f"⏱️ Tiempo promedio: {report['average_processing_time']:.2f}s por factura")
    
    print(f"\n🎯 EFECTIVIDAD POR CAMPO:")
    for field, stats in report['field_extraction_stats'].items():
        print(f"   {field:15}: {stats['extracted']:2d}/{report['total_invoices']} ({stats['percentage']:5.1f}%)")
    
    print(f"\n📋 FORMATOS DETECTADOS:")
    for format_type, count in report['format_distribution'].items():
        percentage = count / report['total_invoices'] * 100
        print(f"   {format_type:25}: {count:2d} ({percentage:5.1f}%)")
    
    # Top performers
    successful_results = [r for r in report['results'] if r['success']]
    if successful_results:
        best_confidence = max(successful_results, key=lambda x: x['confidence_score'])
        most_fields = max(successful_results, key=lambda x: sum(1 for f in x['fields_extracted'].values() if f['extracted']))
        
        print(f"\n🏆 MEJORES RESULTADOS:")
        print(f"   Mayor confianza: {best_confidence['filename']} ({best_confidence['confidence_score']:.2f})")
        print(f"   Más campos: {most_fields['filename']} ({sum(1 for f in most_fields['fields_extracted'].values() if f['extracted'])}/7 campos)")

def run_comprehensive_test():
    """Ejecuta pruebas completas con todas las facturas"""
    print("🚀 INICIANDO ANÁLISIS COMPLETO DE FACTURAS REALES")
    print("="*80)
    
    # Verificar configuración
    setup_test_environment()
    
    if not INVOICE_FOLDER.exists():
        print(f"❌ Carpeta de facturas no encontrada: {INVOICE_FOLDER}")
        return False
    
    # Verificar conexión API
    if not test_api_connection():
        print("❌ No se puede conectar con la API OCR")
        return False
    
    # Obtener lista de facturas
    invoice_files = list(INVOICE_FOLDER.glob("*.pdf")) + list(INVOICE_FOLDER.glob("*.PDF"))
    print(f"📁 Facturas encontradas: {len(invoice_files)}")
    
    if not invoice_files:
        print("❌ No se encontraron archivos PDF en la carpeta")
        return False
    
    # Procesar facturas
    results = []
    for i, invoice_file in enumerate(invoice_files[:10], 1):  # Limitar a 10 para prueba inicial
        print(f"\n[{i}/{min(10, len(invoice_files))}] {invoice_file.name}")
        result = process_invoice_file(invoice_file)
        results.append(result)
        
        # Pequeña pausa para no saturar el servidor
        time.sleep(1)
    
    # Generar reporte
    report = generate_report(results)
    print_summary(report)
    
    print(f"\n✅ Análisis completado. Resultados guardados en {RESULTS_FOLDER}")
    return True

if __name__ == "__main__":
    print("🧠 SISTEMA INTELIGENTE DE ANÁLISIS DE FACTURAS")
    print("Developed by Advanced AI System - PhD Level Analysis")
    print("-" * 80)
    
    try:
        success = run_comprehensive_test()
        if success:
            print("\n🎉 ¡PRUEBAS COMPLETADAS EXITOSAMENTE!")
        else:
            print("\n❌ Las pruebas no se completaron correctamente")
    except KeyboardInterrupt:
        print("\n⏹️ Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        
    input("\nPresiona Enter para salir...")