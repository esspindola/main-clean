const bcrypt = require('bcryptjs');

// Datos de ejemplo para poblar la base de datos
const users = [
  {
    email: 'admin@frontposw.com',
    password: 'admin12345678',
    fullName: 'Administrador',
    phone: '+1234567890',
    role: 'admin',
    emailVerified: true,
    address: '123 Main St, City, Country'
  },
  {
    email: 'user@frontposw.com',
    password: 'user12345678',
    fullName: 'Usuario Regular',
    phone: '+0987654321',
    role: 'user',
    emailVerified: true,
    address: '456 Oak Ave, Town, Country'
  }
];

const products = [
  {
    name: 'Cabinet with Doors',
    description: 'Mueble de oficina con puertas corredizas',
    sku: 'CAB-001',
    category: 'Muebles',
    price: 180.00,
    stock: 25,
    lowStockAlert: 5,
    status: 'active',
    productType: 'Producto físico',
    location: 'almacen-principal',
    unit: 'Por artículo',
    weight: 25.50,
    userId: 1, // Se asignará al primer usuario creado
    images: ['https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400&h=300&fit=crop']
  },
  {
    name: 'Escritorio Ejecutivo',
    description: 'Escritorio de madera para ejecutivos',
    sku: 'ESC-001',
    category: 'Muebles',
    price: 250.00,
    stock: 8,
    lowStockAlert: 3,
    status: 'active',
    productType: 'Producto físico',
    location: 'almacen-principal',
    unit: 'Por artículo',
    weight: 35.00,
    userId: 1,
    images: ['https://images.unsplash.com/photo-1497366216548-37526070297c?w=400&h=300&fit=crop']
  },
  {
    name: 'Silla Ergonómica',
    description: 'Silla de oficina ergonómica',
    sku: 'SIL-001',
    category: 'Muebles',
    price: 120.00,
    stock: 15,
    lowStockAlert: 5,
    status: 'active',
    productType: 'Producto físico',
    location: 'almacen-principal',
    unit: 'Por artículo',
    weight: 12.00,
    userId: 1,
    images: ['https://images.unsplash.com/photo-1592078615290-033ee584e267?w=400&h=300&fit=crop']
  },
  {
    name: 'Monitor 24 pulgadas',
    description: 'Monitor LED de 24 pulgadas',
    sku: 'MON-001',
    category: 'Electrónicos',
    price: 180.00,
    stock: 6,
    lowStockAlert: 2,
    status: 'active',
    productType: 'Producto físico',
    location: 'almacen-electronica',
    unit: 'Por artículo',
    weight: 8.50,
    userId: 1,
    images: ['https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=400&h=300&fit=crop']
  },
  {
    name: 'Teclado Mecánico',
    description: 'Teclado mecánico gaming',
    sku: 'TEC-001',
    category: 'Electrónicos',
    price: 85.00,
    stock: 20,
    lowStockAlert: 5,
    status: 'active',
    productType: 'Producto físico',
    location: 'almacen-electronica',
    unit: 'Por artículo',
    weight: 1.20,
    userId: 1,
    images: ['https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=400&h=300&fit=crop']
  },
  {
    name: 'Lámpara LED',
    description: 'Lámpara LED de escritorio',
    sku: 'LAM-001',
    category: 'Iluminación',
    price: 35.00,
    stock: 0,
    lowStockAlert: 5,
    status: 'inactive',
    productType: 'Producto físico',
    location: 'almacen-principal',
    unit: 'Por artículo',
    weight: 2.50,
    userId: 1,
    images: ['https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=400&h=300&fit=crop']
  }
];

const sales = [
  {
    userId: 1,
    items: [
      {
        id: 1,
        name: 'Cabinet with Doors',
        price: 180.00,
        quantity: 2,
        total: 360.00
      },
      {
        id: 3,
        name: 'Silla Ergonómica',
        price: 120.00,
        quantity: 1,
        total: 120.00
      }
    ],
    paymentMethod: 'Tarjeta de Crédito/Débito',
    status: 'completed',
    customerInfo: {
      name: 'Cliente Ejemplo',
      email: 'cliente@ejemplo.com'
    },
    notes: 'Venta de ejemplo'
  },
  {
    userId: 1,
    items: [
      {
        id: 4,
        name: 'Monitor 24 pulgadas',
        price: 180.00,
        quantity: 1,
        total: 180.00
      }
    ],
    paymentMethod: 'Cash on Delivery',
    status: 'completed',
    customerInfo: {
      name: 'Otro Cliente',
      email: 'otro@cliente.com'
    }
  }
];

const inventoryMovements = [
  {
    productId: 1,
    userId: 1,
    type: 'in',
    quantity: 30,
    previousStock: 0,
    newStock: 30,
    reason: 'Compra inicial',
    notes: 'Stock inicial del producto'
  },
  {
    productId: 1,
    userId: 1,
    type: 'out',
    quantity: 2,
    previousStock: 30,
    newStock: 28,
    reason: 'Venta',
    reference: 'Sale #1'
  },
  {
    productId: 1,
    userId: 1,
    type: 'out',
    quantity: 3,
    previousStock: 28,
    newStock: 25,
    reason: 'Ajuste de inventario',
    notes: 'Corrección de stock'
  }
];

module.exports = {
  users,
  products,
  sales,
  inventoryMovements
}; 