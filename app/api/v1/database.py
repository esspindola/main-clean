"""
API endpoints para consultar la base de datos de facturas
"""

from flask import request
from flask_restx import Namespace, Resource, fields
import logging

from app.database.invoice_db import get_invoice_db

logger = logging.getLogger(__name__)

# Namespace para la base de datos
db_ns = Namespace('database', description='Consultas de facturas guardadas')

# Modelos para documentación
invoice_summary_model = db_ns.model('InvoiceSummary', {
    'id': fields.Integer(required=True, description='ID de la factura'),
    'filename': fields.String(required=True, description='Nombre del archivo'),
    'upload_time': fields.String(required=True, description='Fecha de subida'),
    'processing_time': fields.Float(description='Tiempo de procesamiento'),
    'success': fields.Integer(description='Éxito (1) o fallo (0)'),
    'ruc': fields.String(description='RUC extraído'),
    'company_name': fields.String(description='Nombre de empresa'),
    'invoice_number': fields.String(description='Número de factura'),
    'date': fields.String(description='Fecha de factura'),
    'total': fields.String(description='Total de factura'),
    'fields_found': fields.Integer(description='Campos extraídos'),
    'extraction_method': fields.String(description='Método de extracción')
})

stats_model = db_ns.model('DatabaseStats', {
    'total_invoices': fields.Integer(description='Total de facturas'),
    'successful_invoices': fields.Integer(description='Facturas exitosas'),
    'success_rate': fields.Float(description='Tasa de éxito (%)'),
    'avg_fields_extracted': fields.Float(description='Promedio de campos extraídos'),
    'avg_processing_time': fields.Float(description='Tiempo promedio de procesamiento')
})


@db_ns.route('/invoices')
class InvoiceList(Resource):
    """Lista de facturas procesadas"""
    
    @db_ns.marshal_list_with(invoice_summary_model)
    def get(self):
        """
        Obtener lista de facturas procesadas
        
        Retorna las últimas facturas procesadas con información básica.
        """
        try:
            limit = request.args.get('limit', 20, type=int)
            limit = min(limit, 100)  # Máximo 100
            
            db = get_invoice_db()
            invoices = db.get_invoices(limit=limit)
            
            logger.info(f"Retrieved {len(invoices)} invoices from database")
            
            return invoices, 200
            
        except Exception as e:
            logger.error(f"Failed to get invoices: {e}")
            return {'error': 'Failed to retrieve invoices'}, 500


@db_ns.route('/invoices/<int:invoice_id>')
class InvoiceDetails(Resource):
    """Detalles de una factura específica"""
    
    def get(self, invoice_id):
        """
        Obtener detalles completos de una factura
        
        Incluye todos los datos extraídos, items individuales y metadatos completos.
        """
        try:
            db = get_invoice_db()
            invoice = db.get_invoice_details(invoice_id)
            
            if not invoice:
                return {'error': 'Invoice not found'}, 404
            
            logger.info(f"Retrieved details for invoice {invoice_id}")
            
            return invoice, 200
            
        except Exception as e:
            logger.error(f"Failed to get invoice details: {e}")
            return {'error': 'Failed to retrieve invoice details'}, 500


@db_ns.route('/stats')
class DatabaseStats(Resource):
    """Estadísticas de la base de datos"""
    
    @db_ns.marshal_with(stats_model)
    def get(self):
        """
        Obtener estadísticas del sistema
        
        Retorna métricas sobre las facturas procesadas.
        """
        try:
            db = get_invoice_db()
            stats = db.get_stats()
            
            logger.info("Retrieved database statistics")
            
            return stats, 200
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {'error': 'Failed to retrieve statistics'}, 500


@db_ns.route('/recent')
class RecentInvoices(Resource):
    """Facturas recientes con datos completos"""
    
    def get(self):
        """
        Obtener facturas recientes con datos de extracción
        
        Optimizado para mostrar en el frontend.
        """
        try:
            db = get_invoice_db()
            invoices = db.get_invoices(limit=10)
            
            # Formatear para el frontend
            formatted_invoices = []
            for invoice in invoices:
                formatted_invoices.append({
                    'id': invoice['id'],
                    'filename': invoice['filename'],
                    'upload_time': invoice['upload_time'],
                    'processing_time': invoice['processing_time'],
                    'success': bool(invoice['success']),
                    'extraction_summary': {
                        'ruc': invoice['ruc'] or 'No detectado',
                        'company_name': invoice['company_name'] or 'No detectado',
                        'invoice_number': invoice['invoice_number'] or 'No detectado',
                        'date': invoice['date'] or 'No detectado',
                        'total': invoice['total'] or 'No detectado',
                        'fields_extracted': f"{invoice['fields_found']}/7"
                    },
                    'status': 'Exitoso' if invoice['success'] else 'Fallido'
                })
            
            return {
                'invoices': formatted_invoices,
                'total_count': len(formatted_invoices)
            }, 200
            
        except Exception as e:
            logger.error(f"Failed to get recent invoices: {e}")
            return {'error': 'Failed to retrieve recent invoices'}, 500