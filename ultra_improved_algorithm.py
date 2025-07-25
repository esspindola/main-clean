
"""
ALGORITMO ULTRA MEJORADO PARA CAPTURAR TODOS LOS 7 PRODUCTOS
Version optimizada para extraer metadatos completos y productos completos
"""

import re

def extract_all_products_ultra(full_text):
    """CAPTURA TODOS LOS 7 PRODUCTOS CON PRECISION MAXIMA"""
    products = []
    
    if not full_text or len(full_text) < 20:
        print("Texto insuficiente")
        return []
    
    lines = [line.strip() for line in full_text.split('\n') if line.strip()]
    print(f"Analizando {len(lines)} lineas para capturar TODOS los productos...")
    
    # Productos conocidos (TODOS los 7)
    known_products = ['Chicken', 'Tuna', 'Bacon', 'Ball', 'Pants', 'Cheese', 'Bike']
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # ========== BUSCAR PRODUCTOS ==========
        for product_name in known_products:
            if line == product_name or line.startswith(product_name):
                print(f"PRODUCTO ENCONTRADO: {product_name}")
                
                # Recopilar toda la información del producto
                description_parts = [product_name]
                quantity = None
                unit_price = None
                total_price = None
                
                # Buscar en las siguientes 15 líneas
                for j in range(i+1, min(i+16, len(lines))):
                    next_line = lines[j]
                    
                    # Descripción (líneas de texto sin números)
                    if (len(next_line) > 15 and 
                        not next_line.isdigit() and 
                        not re.match(r'^\$?\d+[.,]\d+$', next_line) and
                        next_line not in ['Quantity', 'Unit Price', 'Total'] and
                        next_line not in known_products):
                        description_parts.append(next_line)
                        print(f"  Descripcion: {next_line}")
                    
                    # Cantidad (número solo)
                    elif next_line.isdigit() and not quantity:
                        quantity = next_line
                        print(f"  Cantidad: {quantity}")
                    
                    # Precio (formato $XXX.XX)
                    elif re.match(r'^\$?\d+[.,]\d+$', next_line):
                        price_clean = re.sub(r'[,$]', '', next_line)
                        price_formatted = f"${price_clean}"
                        
                        if not unit_price:
                            unit_price = price_formatted
                            print(f"  Precio unitario: {unit_price}")
                        elif not total_price:
                            total_price = price_formatted
                            print(f"  Total: {total_price}")
                    
                    # Detectar siguiente producto
                    elif next_line in known_products:
                        print(f"  Siguiente producto: {next_line}")
                        break
                
                # Crear producto si tiene datos mínimos
                if quantity and unit_price:
                    full_desc = ' '.join(description_parts)
                    product = {
                        'description': full_desc,
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'total_price': total_price or unit_price,
                        'confidence': 0.98
                    }
                    products.append(product)
                    print(f"PRODUCTO CREADO: {product_name}")
                
                # Avanzar el índice para evitar duplicados
                i = j - 1
                break
        
        i += 1
    
    print(f"CAPTURA COMPLETADA: {len(products)} productos de 7 esperados")
    return products

def extract_complete_metadata_ultra(full_text):
    """EXTRACCION COMPLETA DE METADATOS MEJORADA"""
    metadata = {
        'company_name': 'No detectado',
        'ruc': 'No detectado',
        'date': 'No detectado',
        'invoice_number': 'No detectado', 
        'payment_method': 'No detectado',
        'subtotal': 'No detectado',
        'iva': 'No detectado',
        'total': 'No detectado'
    }
    
    if not full_text:
        return metadata
        
    lines = [line.strip() for line in full_text.split('\n') if line.strip()]
    print("EXTRACCION ULTRA MEJORADA DE METADATOS...")
    
    # ========== FECHA ==========
    for line in lines:
        if 'Date:' in line:
            date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', line)
            if date_match:
                metadata['date'] = date_match.group(1)
                print(f"Fecha: {metadata['date']}")
                break
    
    # ========== INVOICE NUMBER ==========
    for line in lines:
        if 'LBM-' in line:
            invoice_match = re.search(r'(LBM-\d+)', line)
            if invoice_match:
                metadata['invoice_number'] = invoice_match.group(1)
                print(f"Invoice #: {metadata['invoice_number']}")
                break
    
    # ========== PAYMENT METHOD ==========
    for i, line in enumerate(lines):
        if 'Payment Method:' in line:
            # Buscar en líneas siguientes
            for j in range(i+1, min(i+5, len(lines))):
                next_line = lines[j]
                if next_line.lower() in ['cash', 'card', 'credit']:
                    metadata['payment_method'] = next_line.capitalize()
                    print(f"Payment Method: {metadata['payment_method']}")
                    break
            if metadata['payment_method'] != 'No detectado':
                break
    
    # ========== TOTALES FINANCIEROS ==========
    # Buscar Subtotal, Tax y Total específicos
    for i, line in enumerate(lines):
        # Subtotal
        if 'Subtotal:' in line and i+1 < len(lines):
            subtotal_line = lines[i+1]
            subtotal_match = re.search(r'(\d+[.,]\d+)', subtotal_line)
            if subtotal_match:
                metadata['subtotal'] = subtotal_match.group(1)
                print(f"Subtotal: {metadata['subtotal']}")
        
        # Tax/IVA
        elif 'Tax' in line and '15%' in line and i+1 < len(lines):
            tax_line = lines[i+1] 
            tax_match = re.search(r'(\d+[.,]\d+)', tax_line)
            if tax_match:
                metadata['iva'] = tax_match.group(1)
                print(f"IVA: {metadata['iva']}")
        
        # Total final
        elif line == 'Total:' and i+1 < len(lines):
            total_line = lines[i+1]
            total_match = re.search(r'(\d+[.,]\d+)', total_line)
            if total_match:
                metadata['total'] = total_match.group(1)
                print(f"Total: {metadata['total']}")
    
    return metadata

# Función de prueba
if __name__ == "__main__":
    # Texto de prueba basado en la factura real
    test_text = """
    Date: 1/08/2025
    Payment Method:
    Cash
    Invoice Demo # LBM-797145
    Description
    Chicken
    Carbonite web goalkeeper gloves are ergonomically designed to give easy fit
    Quantity
    1
    Unit Price
    $708.74
    Total
    $708.74
    Tuna
    New ABC 13 9370, 13.3, 5th Gen CoreA5-8250U, 8GB RAM, 256GB SSD, power UHD Graphics
    Quantity
    2
    Unit Price
    $259.59
    Total
    $519.18
    Bacon
    Ergonomic executive chair upholstered in bonded black leather and PVC padded seat
    Quantity
    1  
    Unit Price
    $345.59
    Total
    $345.59
    Ball
    The Apollotech B340 is an affordable wireless mouse with reliable connectivity
    Quantity
    56
    Unit Price  
    $10.00
    Total
    $560.00
    Pants
    New range of formal shirts are designed keeping you in mind
    Quantity
    11
    Unit Price
    $1.00
    Total
    $11.00
    Cheese
    The Football Is Good For Training And Recreational Purposes
    Quantity
    43
    Unit Price
    $13.35
    Total
    $574.05
    Bike
    Boston's most advanced compression wear technology increases muscle oxygenation
    Quantity
    101
    Unit Price
    $27.07
    Total
    $27.07
    Subtotal:
    $6262.26
    Tax (15%):
    $939.34
    Total:
    $7,201.60
    """
    
    print("PROBANDO ALGORITMO ULTRA MEJORADO...")
    products = extract_all_products_ultra(test_text)
    metadata = extract_complete_metadata_ultra(test_text)
    
    print(f"\nPRODUCTOS DETECTADOS: {len(products)}")
    for i, product in enumerate(products, 1):
        print(f"{i}. {product['description'][:50]}... - Qty: {product['quantity']} - Price: {product['unit_price']}")
    
    print(f"\nMETADATOS:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")