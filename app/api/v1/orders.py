"""
Orders Management API
Handle invoice archiving and order management
"""

from flask import request
from flask_restx import Namespace, Resource, fields
import json
import os
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

orders_ns = Namespace('orders', description='Order and invoice management')


order_model = orders_ns.model('Order', {
    'id': fields.String(required=True, description='Order ID'),
    'fecha': fields.String(required=True, description='Order date'),
    'proveedor': fields.String(required=True, description='Provider name'),
    'total': fields.Float(required=True, description='Total amount'),
    'estado': fields.String(required=True, description='Order status'),
    'acciones': fields.List(fields.String, description='Available actions'),
    'lineas': fields.List(fields.Raw, description='Order line items')
})

archive_request_model = orders_ns.model('ArchiveRequest', {
    'fecha': fields.String(required=True, description='Invoice date'),
    'proveedor': fields.String(required=True, description='Provider name'),
    'total': fields.Float(required=True, description='Total amount'),
    'estado': fields.String(description='Order status', default='Pendiente'),
    'lineas': fields.List(fields.Raw, required=True, description='Invoice line items')
})


@orders_ns.route('')
class OrdersList(Resource):
    """Orders list management."""
    
    @orders_ns.marshal_list_with(order_model)
    def get(self):
        """
        Get all orders
        
        Returns a list of all archived orders with their details.
        """
        try:
            file_path = "orders.json"
            
            if not os.path.exists(file_path):
                return [], 200
            
            with open(file_path, "r", encoding="utf-8") as f:
                orders = json.load(f)
            
            logger.info(f"Retrieved {len(orders)} orders")
            return orders, 200
            
        except Exception as e:
            logger.error(f"Failed to retrieve orders: {e}")
            return {
                'error': 'Failed to retrieve orders',
                'details': str(e)
            }, 500


@orders_ns.route('/<string:order_id>')
class OrderDetail(Resource):
    """Individual order management."""
    
    @orders_ns.marshal_with(order_model)
    def get(self, order_id):
        """
        Get specific order
        
        Retrieve details for a specific order by ID.
        """
        try:
            file_path = "orders.json"
            
            if not os.path.exists(file_path):
                return {'error': 'No orders found'}, 404
            
            with open(file_path, "r", encoding="utf-8") as f:
                orders = json.load(f)
            
            order = next((o for o in orders if o["id"] == order_id), None)
            
            if not order:
                return {'error': 'Order not found'}, 404
            
            logger.info(f"Retrieved order: {order_id}")
            return order, 200
            
        except Exception as e:
            logger.error(f"Failed to retrieve order {order_id}: {e}")
            return {
                'error': 'Failed to retrieve order',
                'details': str(e)
            }, 500


@orders_ns.route('/archive')
class ArchiveInvoice(Resource):
    """Archive processed invoices as orders."""
    
    @orders_ns.expect(archive_request_model)
    @orders_ns.marshal_with(order_model, code=201)
    def post(self):
        """
        Archive processed invoice
        
        Convert a processed invoice into an archived order for inventory management.
        """
        try:
            data = request.get_json()
            
            if not data:
                return {'error': 'No data provided'}, 400
            
            required_fields = ['fecha', 'proveedor', 'total', 'lineas']
            for field in required_fields:
                if field not in data:
                    return {'error': f'Missing required field: {field}'}, 400
            
            file_path = "orders.json"
            
           
            if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump([], f)
            
           
            with open(file_path, "r+", encoding="utf-8") as f:
                try:
                    orders = json.load(f)
                except json.JSONDecodeError:
                    orders = []
            
                new_order = {
                    "id": str(uuid.uuid4()),
                    "fecha": data.get("fecha", datetime.now().strftime("%d/%m/%Y")),
                    "proveedor": data.get("proveedor", "Proveedor Desconocido"),
                    "total": float(data.get("total", 0.0)),
                    "estado": data.get("estado", "Pendiente"),
                    "acciones": ["Ver Factura", "Ver Recepción", "Editar", "Eliminar"],
                    "lineas": data.get("lineas", []),
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                
                orders.append(new_order)
                
              
                f.seek(0)
                json.dump(orders, f, indent=2, ensure_ascii=False)
                f.truncate()
            
            logger.info(f"Invoice archived as order: {new_order['id']}")
            return new_order, 201
            
        except Exception as e:
            logger.error(f"Failed to archive invoice: {e}")
            return {
                'error': 'Failed to archive invoice',
                'details': str(e)
            }, 500


@orders_ns.route('/stats')
class OrdersStats(Resource):
    """Order statistics and analytics."""
    
    def get(self):
        """
        Get order statistics
        
        Returns summary statistics for all orders.
        """
        try:
            file_path = "orders.json"
            
            if not os.path.exists(file_path):
                return {
                    'total_orders': 0,
                    'total_value': 0.0,
                    'by_status': {},
                    'by_provider': {}
                }, 200
            
            with open(file_path, "r", encoding="utf-8") as f:
                orders = json.load(f)
            
           
            total_orders = len(orders)
            total_value = sum(order.get('total') or 0 for order in orders)
            
           
            by_status = {}
            for order in orders:
                status = order.get('estado', 'Unknown')
                by_status[status] = by_status.get(status, 0) + 1
            
         
            by_provider = {}
            for order in orders:
                provider = order.get('proveedor', 'Unknown')
                by_provider[provider] = by_provider.get(provider, 0) + 1
            
            stats = {
                'total_orders': total_orders,
                'total_value': round(total_value, 2),
                'average_order_value': round(total_value / total_orders, 2) if total_orders > 0 else 0,
                'by_status': by_status,
                'by_provider': dict(list(by_provider.items())[:10]) 
            }
            
            return stats, 200
            
        except Exception as e:
            logger.error(f"Failed to calculate order stats: {e}")
            return {
                'error': 'Failed to calculate statistics',
                'details': str(e)
            }, 500