# 📡 Referencias Técnicas - ZatoBox v2.0

Referencias técnicas completas del sistema ZatoBox v2.0, incluyendo documentación de API, endpoints y ejemplos de uso.

## 📋 Índice de Referencias

### 📡 API Reference
- **[📡 API Reference Completa](./api-reference.md)** - Documentación completa de la API
  - Endpoints de autenticación
  - Gestión de productos
  - Sistema de ventas
  - Inventario y movimientos
  - OCR y plugins
  - Health checks

## 🎯 Información de la API

### 🔗 Base URL
```
Development: http://localhost:4444
Production: https://api.zatobox.com
```

### 🔐 Autenticación
La API utiliza **JWT (JSON Web Tokens)** para autenticación:

```
Authorization: Bearer <your-jwt-token>
```

### 📊 Formato de Respuesta
Todas las respuestas siguen este formato:

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful",
  "timestamp": "2025-07-24T00:00:00.000Z"
}
```

## 📡 Endpoints Principales

### 🔐 Autenticación
- `POST /api/auth/login` - Iniciar sesión
- `POST /api/auth/register` - Registrar usuario
- `POST /api/auth/logout` - Cerrar sesión
- `GET /api/auth/me` - Información del usuario actual

### 📦 Productos
- `GET /api/products` - Listar productos
- `POST /api/products` - Crear producto
- `PUT /api/products/:id` - Actualizar producto
- `DELETE /api/products/:id` - Eliminar producto
- `GET /api/products/:id` - Obtener producto específico

### 💰 Ventas
- `GET /api/sales` - Listar ventas
- `POST /api/sales` - Crear venta
- `GET /api/sales/:id` - Obtener venta específica

### 📊 Inventario
- `GET /api/inventory` - Estado del inventario
- `POST /api/inventory/movements` - Registrar movimiento
- `GET /api/inventory/movements` - Historial de movimientos

### 🔍 OCR
- `POST /api/ocr/upload` - Subir documento para OCR
- `GET /api/ocr/history` - Historial de OCR
- `GET /api/ocr/status/:jobId` - Estado del procesamiento

### 🔌 Plugins
- `GET /api/plugins` - Lista de plugins disponibles
- `POST /api/plugins/:id/toggle` - Activar/desactivar plugin

### 🏥 Health Checks
- `GET /health` - Health check básico del sistema
- `GET /api/health` - Health check detallado de la API

## 🚨 Códigos de Estado HTTP

- `200` - OK: Operación exitosa
- `201` - Created: Recurso creado
- `400` - Bad Request: Datos inválidos
- `401` - Unauthorized: No autenticado
- `403` - Forbidden: No autorizado
- `404` - Not Found: Recurso no encontrado
- `500` - Internal Server Error: Error del servidor

## 📝 Ejemplos de Uso

### JavaScript/Node.js
```javascript
const axios = require('axios');

const api = axios.create({
  baseURL: 'http://localhost:4444',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});

// Login
const login = async (email, password) => {
  const response = await api.post('/api/auth/login', {
    email,
    password
  });
  return response.data;
};

// Get products
const getProducts = async () => {
  const response = await api.get('/api/products');
  return response.data;
};
```

### cURL
```bash
# Login
curl -X POST http://localhost:4444/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@frontposw.com","password":"admin12345678"}'

# Get products (with token)
curl -X GET http://localhost:4444/api/products \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Create product
curl -X POST http://localhost:4444/api/products \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "name=New Product" \
  -F "price=99.99" \
  -F "stock=10" \
  -F "images=@product-image.jpg"
```

## 🔑 Credenciales de Prueba

### Administrador
- **Email**: `admin@frontposw.com`
- **Password**: `admin12345678`

### Usuario Regular
- **Email**: `user@frontposw.com`
- **Password**: `user12345678`

## 🧪 Testing de la API

### Health Check
```bash
curl http://localhost:4444/health
```

### API Health Check
```bash
curl http://localhost:4444/api/health
```

### Test CORS
Abrir `test-cors.html` en el navegador para verificar comunicación CORS.

## 📊 Modelos de Datos

### Usuario
```javascript
{
  id: string,
  email: string,
  password: string (hashed),
  fullName: string,
  role: 'admin' | 'user',
  createdAt: Date,
  updatedAt: Date
}
```

### Producto
```javascript
{
  id: number,
  name: string,
  description: string,
  sku: string,
  category: string,
  price: number,
  stock: number,
  status: 'active' | 'inactive',
  images: string[],
  createdAt: Date,
  updatedAt: Date
}
```

### Venta
```javascript
{
  id: number,
  userId: string,
  products: Array<{
    productId: number,
    quantity: number,
    price: number
  }>,
  total: number,
  paymentMethod: string,
  status: 'pending' | 'completed' | 'cancelled',
  createdAt: Date
}
```

## 🔧 Configuración

### Variables de Entorno
```bash
# Backend
PORT=4444
JWT_SECRET=your-jwt-secret
NODE_ENV=development

# Frontend
VITE_API_URL=http://localhost:4444
VITE_APP_NAME=ZatoBox
```

### CORS Configuration
```javascript
app.use(cors({
  origin: true, // Permitir todos los orígenes en desarrollo
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With']
}));
```

## 🚨 Errores Comunes

### 400 - Bad Request
```json
{
  "success": false,
  "error": "VALIDATION_ERROR",
  "message": "Invalid input data",
  "details": {
    "email": "Invalid email format",
    "password": "Password must be at least 8 characters"
  }
}
```

### 401 - Unauthorized
```json
{
  "success": false,
  "error": "AUTHENTICATION_ERROR",
  "message": "Invalid or expired token"
}
```

### 404 - Not Found
```json
{
  "success": false,
  "error": "NOT_FOUND",
  "message": "Resource not found"
}
```

---

**ZatoBox v2.0 API** - Referencias técnicas completas 📡

*Documentación de API mantenida y actualizada regularmente.* 