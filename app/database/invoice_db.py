"""
Base de datos simple SQLite para facturas procesadas
Sistema ligero y eficaz para el proyecto OCR
"""

import sqlite3
import json
import hashlib
import os
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class InvoiceDB:
    """Base de datos simple para facturas"""
    
    def __init__(self):
        self.db_path = "data/invoices.db"
        self._ensure_directory()
        self._create_tables()
    
    def _ensure_directory(self):
        """Crear directorio data si no existe"""
        os.makedirs("data", exist_ok=True)
    
    def _create_tables(self):
        """Crear tablas básicas"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS invoices (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename TEXT NOT NULL,
                        file_hash TEXT UNIQUE,
                        upload_time TEXT,
                        processing_time REAL,
                        success INTEGER,
                        
                        -- Datos extraídos
                        ruc TEXT,
                        company_name TEXT,
                        invoice_number TEXT,
                        date TEXT,
                        subtotal TEXT,
                        iva TEXT,
                        total TEXT,
                        
                        -- Estadísticas
                        fields_found INTEGER DEFAULT 0,
                        extraction_method TEXT,
                        
                        -- JSON completo
                        full_data TEXT
                    )
                ''')
                
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS invoice_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        invoice_id INTEGER,
                        description TEXT,
                        quantity TEXT,
                        unit_price TEXT,
                        total_price TEXT,
                        FOREIGN KEY (invoice_id) REFERENCES invoices (id)
                    )
                ''')
                
                logger.info("✅ Database tables created")
                
        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
    
    def save_invoice(self, filename: str, result_data: Dict) -> int:
        """Guardar factura procesada"""
        try:
            # Generar hash del archivo
            file_hash = hashlib.md5(filename.encode()).hexdigest()
            
            # Extraer y limpiar datos
            metadata = result_data.get('metadata', {})
            line_items = result_data.get('line_items', [])
            
            # Limpiar metadata de diccionarios complejos
            clean_metadata = {}
            for field, value in metadata.items():
                if isinstance(value, dict) and 'value' in value:
                    clean_metadata[field] = value['value']
                else:
                    clean_metadata[field] = value
            
            # Contar campos extraídos
            fields_found = sum(1 for v in clean_metadata.values() 
                             if v and str(v) not in ['No detectado', 'None', ''])
            
            with sqlite3.connect(self.db_path) as conn:
                # Guardar factura principal
                cursor = conn.execute('''
                    INSERT OR REPLACE INTO invoices 
                    (filename, file_hash, upload_time, processing_time, success,
                     ruc, company_name, invoice_number, date, subtotal, iva, total,
                     fields_found, extraction_method, full_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    filename,
                    file_hash,
                    datetime.now().isoformat(),
                    result_data.get('processing_time', 0),
                    1 if result_data.get('success', False) else 0,
                    clean_metadata.get('ruc'),
                    clean_metadata.get('company_name'),
                    clean_metadata.get('invoice_number'),
                    clean_metadata.get('date'),
                    clean_metadata.get('subtotal'),
                    clean_metadata.get('iva'),
                    clean_metadata.get('total'),
                    fields_found,
                    'SISTEMA_ROBUSTO',
                    json.dumps(result_data, ensure_ascii=False)
                ))
                
                invoice_id = cursor.lastrowid
                
                # Limpiar items anteriores
                conn.execute('DELETE FROM invoice_items WHERE invoice_id = ?', (invoice_id,))
                
                # Guardar items
                for item in line_items or []:
                    conn.execute('''
                        INSERT INTO invoice_items (invoice_id, description, quantity, unit_price, total_price)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        invoice_id,
                        item.get('description'),
                        item.get('quantity'),
                        item.get('unit_price'),
                        item.get('total_price')
                    ))
                
                logger.info(f"✅ Factura guardada: ID={invoice_id}, campos={fields_found}")
                return invoice_id
                
        except Exception as e:
            logger.error(f"❌ Error guardando factura: {e}")
            return 0
    
    def get_invoices(self, limit: int = 20) -> List[Dict]:
        """Obtener lista de facturas"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT id, filename, upload_time, processing_time, success,
                           ruc, company_name, invoice_number, date, total,
                           fields_found, extraction_method
                    FROM invoices 
                    ORDER BY upload_time DESC 
                    LIMIT ?
                ''', (limit,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo facturas: {e}")
            return []
    
    def get_invoice_details(self, invoice_id: int) -> Optional[Dict]:
        """Obtener detalles completos de una factura"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Datos principales
                cursor = conn.execute('SELECT * FROM invoices WHERE id = ?', (invoice_id,))
                invoice = cursor.fetchone()
                
                if not invoice:
                    return None
                
                invoice_data = dict(invoice)
                
                # Items
                cursor = conn.execute('''
                    SELECT description, quantity, unit_price, total_price
                    FROM invoice_items WHERE invoice_id = ?
                ''', (invoice_id,))
                
                invoice_data['items'] = [dict(row) for row in cursor.fetchall()]
                
                # Parsear JSON completo
                try:
                    invoice_data['full_data'] = json.loads(invoice_data['full_data'] or '{}')
                except:
                    invoice_data['full_data'] = {}
                
                return invoice_data
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo detalles: {e}")
            return None
    
    def get_stats(self) -> Dict:
        """Obtener estadísticas básicas"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT COUNT(*), AVG(fields_found), AVG(processing_time) FROM invoices')
                total, avg_fields, avg_time = cursor.fetchone()
                
                cursor = conn.execute('SELECT COUNT(*) FROM invoices WHERE success = 1')
                successful = cursor.fetchone()[0]
                
                return {
                    'total_invoices': total or 0,
                    'successful_invoices': successful or 0,
                    'success_rate': round((successful / total * 100) if total > 0 else 0, 1),
                    'avg_fields_extracted': round(avg_fields or 0, 1),
                    'avg_processing_time': round(avg_time or 0, 2)
                }
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {}


# Instancia global
_db_instance = None

def get_invoice_db():
    """Obtener instancia de la base de datos"""
    global _db_instance
    if _db_instance is None:
        _db_instance = InvoiceDB()
    return _db_instance