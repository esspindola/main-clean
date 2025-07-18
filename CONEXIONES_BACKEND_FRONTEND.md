# CONEXIONES BACKEND-FRONTEND - FrontPOSw

## 📋 RESUMEN DE CONEXIONES

### Backend (Puerto 4444)
- **URL Base**: http://localhost:4444
- **Archivo**: `backend/test-server.js`
- **Persistencia**: Archivo JSON (`backend/users.json`)

### Frontend (Puerto 5173)
- **URL Base**: http://localhost:5173
- **Framework**: React + TypeScript + Vite
- **Contexto de Auth**: `src/contexts/AuthContext.tsx`

---

## 🔐 ENDPOINTS DE AUTENTICACIÓN

### 🔑 FLUJO DE AUTENTICACIÓN
```
1. Usuario se registra → POST /api/auth/register
2. Usuario hace login → POST /api/auth/login → Recibe TOKEN
3. Con el TOKEN puede acceder a:
   - Productos (CRUD completo)
   - Inventario (ver y actualizar)
   - Ventas (crear y ver historial) ✨ NUEVO
   - Perfil (ver y actualizar)
```

### 1. REGISTRO DE USUARIO
```
POST /api/auth/register
Content-Type: application/json

Body:
{
  "email": "usuario@ejemplo.com",
  "password": "password123",
  "fullName": "Nombre Completo",
  "phone": "+1234567890"
}

Response:
{
  "success": true,
  "message": "User registered successfully",
  "user": {
    "id": 3,
    "email": "usuario@ejemplo.com",
    "fullName": "Nombre Completo",
    "role": "user"
  },
  "token": "test-token-3-1234567890"
}
```

**Frontend**: `src/components/RegisterPage.tsx`
- Función: `handleSubmit`
- Contexto: `AuthContext.register`

### 2. LOGIN DE USUARIO
```
POST /api/auth/login
Content-Type: application/json

Body:
{
  "email": "usuario@ejemplo.com",
  "password": "password123"
}

Response:
{
  "success": true,
  "message": "Login successful",
  "token": "test-token-3-1234567890",
  "user": {
    "id": 3,
    "email": "usuario@ejemplo.com",
    "fullName": "Nombre Completo",
    "role": "user"
  }
}
```

**Frontend**: `src/components/LoginPage.tsx`
- Función: `handleSubmit`
- Contexto: `AuthContext.login`

### 3. VERIFICAR AUTENTICACIÓN
```
GET /api/auth/me
Authorization: Bearer test-token-3-1234567890

Response:
{
  "success": true,
  "user": {
    "id": 3,
    "email": "usuario@ejemplo.com",
    "fullName": "Nombre Completo",
    "role": "user"
  }
}
```

**Frontend**: `src/contexts/AuthContext.tsx`
- Función: `checkAuth`
- Uso: Verificar token al cargar la app

### 4. LOGOUT
```
POST /api/auth/logout
Authorization: Bearer test-token-3-1234567890

Response:
{
  "success": true,
  "message": "Logout successful"
}
```

**Frontend**: `src/components/SideMenu.tsx`
- Función: `handleLogout`
- Contexto: `AuthContext.logout`

### 🔐 USO DEL TOKEN EN FRONTEND
```javascript
// Ejemplo de cómo se envía el token en las peticiones
const token = localStorage.getItem('token');

fetch('http://localhost:4444/api/products', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

**Contexto de Auth** (`src/contexts/AuthContext.tsx`):
- Guarda el token en localStorage al hacer login
- Incluye el token automáticamente en todas las peticiones
- Verifica el token al cargar la aplicación

---

## 👥 GESTIÓN DE USUARIOS

### LISTAR USUARIOS (Solo desarrollo)
```
GET /api/users

Response:
{
  "success": true,
  "totalUsers": 3,
  "users": [
    {
      "id": 1,
      "email": "admin@frontposw.com",
      "fullName": "Administrador",
      "role": "admin",
      "phone": "+1234567890",
      "address": "123 Main St, City, Country"
    }
  ]
}
```

**Frontend**: No implementado aún
- Propósito: Panel de administración

---

## 📦 ENDPOINTS DE PRODUCTOS (REQUIERE AUTENTICACIÓN)

### 1. LISTAR PRODUCTOS
```
GET /api/products
Authorization: Bearer test-token-3-1234567890

Response:
{
  "success": true,
  "products": [
    {
      "id": 1,
      "name": "Producto Ejemplo",
      "description": "Descripción del producto",
      "price": 29.99,
      "stock": 100,
      "category": "Electrónicos",
      "image": "producto1.jpg"
    }
  ]
}
```

**Frontend**: `src/components/InventoryPage.tsx`
- Función: `fetchProducts`
- Hook: `useEffect`

### 2. CREAR PRODUCTO
```
POST /api/products
Authorization: Bearer test-token-3-1234567890
Content-Type: application/json

Body:
{
  "name": "Nuevo Producto",
  "description": "Descripción",
  "price": 29.99,
  "stock": 100,
  "category": "Electrónicos"
}

Response:
{
  "success": true,
  "message": "Product created successfully",
  "product": {
    "id": 2,
    "name": "Nuevo Producto",
    "description": "Descripción",
    "price": 29.99,
    "stock": 100,
    "category": "Electrónicos"
  }
}
```

**Frontend**: `src/components/NewProductPage.tsx`
- Función: `handleSubmit`

### 3. ACTUALIZAR PRODUCTO
```
PUT /api/products/:id
Authorization: Bearer test-token-3-1234567890
Content-Type: application/json

Body:
{
  "name": "Producto Actualizado",
  "description": "Nueva descripción",
  "price": 39.99,
  "stock": 50,
  "category": "Electrónicos"
}

Response:
{
  "success": true,
  "message": "Product updated successfully",
  "product": {
    "id": 1,
    "name": "Producto Actualizado",
    "description": "Nueva descripción",
    "price": 39.99,
    "stock": 50,
    "category": "Electrónicos"
  }
}
```

**Frontend**: `src/components/EditProductPage.tsx`
- Función: `handleSubmit`

### 4. ELIMINAR PRODUCTO
```
DELETE /api/products/:id
Authorization: Bearer test-token-3-1234567890

Response:
{
  "success": true,
  "message": "Product deleted successfully"
}
```

**Frontend**: `src/components/InventoryPage.tsx`
- Función: `handleDelete`

---

## 📊 ENDPOINTS DE INVENTARIO (REQUIERE AUTENTICACIÓN)

### 1. OBTENER INVENTARIO
```
GET /api/inventory
Authorization: Bearer test-token-3-1234567890

Response:
{
  "success": true,
  "inventory": [
    {
      "id": 1,
      "productId": 1,
      "productName": "Producto Ejemplo",
      "quantity": 100,
      "minStock": 10,
      "lastUpdated": "2024-01-15T10:30:00Z"
    }
  ]
}
```

**Frontend**: `src/components/SmartInventoryPage.tsx`
- Función: `fetchInventory`

### 2. ACTUALIZAR STOCK
```
PUT /api/inventory/:id
Authorization: Bearer test-token-3-1234567890
Content-Type: application/json

Body:
{
  "quantity": 95
}

Response:
{
  "success": true,
  "message": "Stock updated successfully",
  "inventory": {
    "id": 1,
    "productId": 1,
    "quantity": 95,
    "lastUpdated": "2024-01-15T10:35:00Z"
  }
}
```

**Frontend**: `src/components/SmartInventoryPage.tsx`
- Función: `updateStock`

---

## 💰 ENDPOINTS DE VENTAS (REQUIERE AUTENTICACIÓN) ✨ NUEVO

### 🔄 FLUJO COMPLETO DE VENTAS
```
1. Usuario selecciona productos → Se agregan al carrito
2. Usuario procede al pago → Se abre PaymentScreen
3. Usuario completa el pago → Se ejecuta handlePaymentSuccess
4. Backend recibe la venta → Valida stock y actualiza inventario
5. Frontend actualiza UI → Muestra productos con stock actualizado
6. Usuario ve confirmación → PaymentSuccessScreen con detalles
```

### 1. CREAR VENTA ✨ NUEVO
```
POST /api/sales
Authorization: Bearer test-token-3-1234567890
Content-Type: application/json

Body:
{
  "items": [
    {
      "productId": 1,
      "quantity": 2,
      "price": 29.99
    }
  ],
  "total": 59.98,
  "paymentMethod": "cash"
}

Response:
{
  "success": true,
  "message": "Sale created successfully",
  "sale": {
    "id": 1752853147640,
    "items": [
      {
        "productId": 1,
        "productName": "Cabinet with Doors",
        "quantity": 2,
        "price": 29.99
      }
    ],
    "total": 59.98,
    "paymentMethod": "cash",
    "status": "completed",
    "createdAt": "2025-07-18T15:39:07.640Z",
    "userId": 1
  },
  "updatedProducts": [
    {
      "id": 1,
      "name": "Cabinet with Doors",
      "stock": 23,
      "price": 180
    }
  ]
}
```

**Frontend**: `src/components/HomePage.tsx`
- Función: `handlePaymentSuccess`
- Integración: `salesAPI.create()`

**Características del Endpoint:**
- ✅ **Validación de stock**: Verifica que haya suficiente inventario
- ✅ **Actualización automática**: El stock se reduce inmediatamente
- ✅ **Manejo de errores**: Retorna errores específicos si algo falla
- ✅ **Respuesta completa**: Incluye detalles de la venta y productos actualizados

### 2. OBTENER HISTORIAL DE VENTAS
```
GET /api/sales
Authorization: Bearer test-token-3-1234567890

Response:
{
  "success": true,
  "sales": [
    {
      "id": 1,
      "total": 59.98,
      "paymentMethod": "cash",
      "createdAt": "2024-01-15T10:40:00Z",
      "items": [
        {
          "productId": 1,
          "productName": "Producto Ejemplo",
          "quantity": 2,
          "price": 29.99
        }
      ]
    }
  ]
}
```

**Frontend**: `src/components/SalesDrawer.tsx`
- Función: `fetchSales`

---

## 👤 ENDPOINTS DE PERFIL (REQUIERE AUTENTICACIÓN)

### 1. OBTENER PERFIL
```
GET /api/profile
Authorization: Bearer test-token-3-1234567890

Response:
{
  "success": true,
  "profile": {
    "id": 3,
    "email": "usuario@ejemplo.com",
    "fullName": "Nombre Completo",
    "role": "user",
    "phone": "+1234567890",
    "address": "123 Main St"
  }
}
```

**Frontend**: `src/components/ProfilePage.tsx`
- Función: `fetchProfile`

### 2. ACTUALIZAR PERFIL
```
PUT /api/profile
Authorization: Bearer test-token-3-1234567890
Content-Type: application/json

Body:
{
  "fullName": "Nuevo Nombre",
  "phone": "+1234567891",
  "address": "456 Oak St"
}

Response:
{
  "success": true,
  "message": "Profile updated successfully",
  "profile": {
    "id": 3,
    "email": "usuario@ejemplo.com",
    "fullName": "Nuevo Nombre",
    "role": "user",
    "phone": "+1234567891",
    "address": "456 Oak St"
  }
}
```

**Frontend**: `src/components/ProfilePage.tsx`
- Función: `handleSubmit`

---

## 🔧 CONFIGURACIÓN DE CORS

**Backend** (`backend/test-server.js`):
```javascript
app.use(cors({
  origin: [
    'http://localhost:5173',
    'http://localhost:5174',
    'http://localhost:5175',
    'http://localhost:5176',
    'http://localhost:5177'
  ],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));
```

---

## 🚀 FUNCIONES ESPECÍFICAS PARA ARREGLAR

### 1. **Autenticación Persistente**
- **Problema**: Token se pierde al recargar página
- **Archivo**: `src/contexts/AuthContext.tsx`
- **Función**: `checkAuth` - Verificar token en localStorage

### 2. **Manejo de Errores**
- **Problema**: No hay manejo de errores en las peticiones
- **Archivos**: Todos los componentes que hacen fetch
- **Solución**: Implementar try-catch y mostrar mensajes de error

### 3. **Validación de Formularios**
- **Problema**: No hay validación en el frontend
- **Archivos**: `LoginPage.tsx`, `RegisterPage.tsx`, `NewProductPage.tsx`
- **Solución**: Agregar validación con librería como Formik o react-hook-form

### 4. **Loading States**
- **Problema**: No hay indicadores de carga
- **Archivos**: Todos los componentes que hacen peticiones
- **Solución**: Agregar estados de loading

### 5. **Refresh Token**
- **Problema**: No hay renovación automática de tokens
- **Archivo**: `src/contexts/AuthContext.tsx`
- **Solución**: Implementar refresh token

### 6. **Optimistic Updates**
- **Problema**: UI no se actualiza inmediatamente
- **Archivos**: `InventoryPage.tsx`, `SmartInventoryPage.tsx`
- **Solución**: Actualizar estado local antes de confirmar con backend

### 7. **Paginación**
- **Problema**: No hay paginación en listas grandes
- **Archivos**: `InventoryPage.tsx`, `SmartInventoryPage.tsx`
- **Solución**: Implementar paginación con limit/offset

### 8. **Búsqueda y Filtros**
- **Problema**: No hay búsqueda en productos
- **Archivo**: `src/components/InventoryPage.tsx`
- **Solución**: Agregar input de búsqueda y filtros

---

## 📁 ESTRUCTURA DE ARCHIVOS

```
FrontPOSw-main/
├── backend/
│   ├── test-server.js          # Servidor de prueba ✨ ACTUALIZADO
│   ├── users.json              # Usuarios persistidos
│   └── server.js               # Servidor principal (no usado)
├── src/
│   ├── components/
│   │   ├── LoginPage.tsx       # Login
│   │   ├── RegisterPage.tsx    # Registro
│   │   ├── InventoryPage.tsx   # Lista de productos
│   │   ├── NewProductPage.tsx  # Crear producto
│   │   ├── EditProductPage.tsx # Editar producto
│   │   ├── SmartInventoryPage.tsx # Inventario inteligente
│   │   ├── PaymentScreen.tsx   # Pantalla de pago ✨ MEJORADO
│   │   ├── SalesDrawer.tsx     # Historial de ventas
│   │   ├── ProfilePage.tsx     # Perfil de usuario
│   │   └── SideMenu.tsx        # Menú lateral
│   ├── contexts/
│   │   └── AuthContext.tsx     # Contexto de autenticación
│   └── App.tsx                 # Componente principal
└── CONEXIONES_BACKEND_FRONTEND.md # Este archivo ✨ ACTUALIZADO
```

---

## 🛠️ COMANDOS PARA DESPLEGAR

### Backend:
```bash
cd backend
node test-server.js
```

### Frontend:
```bash
npm run dev
```

### Verificar servicios:
```bash
# Backend
netstat -ano | findstr "4444"

# Frontend  
netstat -ano | findstr "5173"
```

---

## 🔍 DEBUGGING

### Verificar conexión backend:
- http://localhost:4444/health

### Verificar usuarios registrados:
- http://localhost:4444/api/users

### Verificar productos:
- http://localhost:4444/api/products

### Verificar ventas: ✨ NUEVO
- http://localhost:4444/api/sales

### Logs del backend:
- Revisar consola donde corre `node test-server.js`

### Logs del frontend:
- Revisar DevTools del navegador (F12)

---

## 🔒 RESUMEN DE SEGURIDAD

### Endpoints PÚBLICOS (sin autenticación):
- `POST /api/auth/register` - Registro de usuarios
- `POST /api/auth/login` - Login de usuarios
- `GET /health` - Health check del servidor

### Endpoints PRIVADOS (requieren token):
- `GET /api/auth/me` - Verificar autenticación
- `POST /api/auth/logout` - Cerrar sesión
- `GET /api/products` - Listar productos
- `POST /api/products` - Crear producto
- `PUT /api/products/:id` - Actualizar producto
- `DELETE /api/products/:id` - Eliminar producto
- `GET /api/inventory` - Obtener inventario
- `PUT /api/inventory/:id` - Actualizar stock
- `POST /api/sales` - Crear venta ✨ NUEVO
- `GET /api/sales` - Historial de ventas
- `GET /api/profile` - Obtener perfil
- `PUT /api/profile` - Actualizar perfil

### 🔑 Flujo de Seguridad:
1. **Registro/Login** → Obtiene token
2. **Token se guarda** en localStorage del frontend
3. **Todas las peticiones privadas** incluyen `Authorization: Bearer {token}`
4. **Backend valida** el token en cada petición
5. **Si token inválido** → Retorna 401 Unauthorized

---

## 🆕 NUEVAS FUNCIONALIDADES AGREGADAS

### 💰 **Sistema de Ventas Completo**
- ✅ **Endpoint POST /api/sales**: Crear ventas con validación de stock
- ✅ **Actualización automática de inventario**: Stock se reduce al crear venta
- ✅ **Integración frontend-backend**: Flujo completo de pago
- ✅ **Manejo de errores**: Validaciones y mensajes de error específicos

### 💳 **Calculadora de Cambio Mejorada**
- ✅ **Cálculo automático**: Cambio calculado en tiempo real
- ✅ **Validación de monto**: Verifica que el pago sea suficiente
- ✅ **Botones de monto rápido**: $10, $20, $50, $100, $200, $500
- ✅ **Feedback visual**: Colores y mensajes informativos
- ✅ **Formato de moneda**: Formato español con separadores de miles

### 🔄 **Sincronización de Inventario**
- ✅ **Actualización inmediata**: UI se actualiza al completar venta
- ✅ **Validación de stock**: Previene ventas con stock insuficiente
- ✅ **Respuesta completa**: Incluye productos actualizados
- ✅ **Manejo de errores**: Rollback en caso de fallo

### 📊 **Mejoras en la UI/UX**
- ✅ **Estados de carga**: Indicadores durante operaciones
- ✅ **Mensajes de confirmación**: Feedback claro al usuario
- ✅ **Validaciones en tiempo real**: Verificación de datos
- ✅ **Interfaz responsiva**: Adaptable a diferentes pantallas

---

## 🧪 PRUEBAS REALIZADAS

### ✅ **Prueba de Venta Exitosa**
```
Venta creada con ID: 1752853147640
Stock actualizado: Cabinet with Doors pasó de 25 a 23 unidades
Respuesta incluye productos actualizados
No hay errores en el proceso
```

### ✅ **Prueba de Validación de Stock**
```
Error cuando stock insuficiente
Mensaje específico: "Insufficient stock for product"
Prevención de ventas inválidas
```

### ✅ **Prueba de Calculadora de Cambio**
```
Cálculo correcto del cambio
Validación de monto mínimo
Botones de monto rápido funcionando
Formato de moneda correcto
```

---

## 🚀 ESTADO ACTUAL DEL PROYECTO

### ✅ **Funcionalidades Completadas**
- [x] Autenticación completa (login/registro/logout)
- [x] CRUD de productos
- [x] Gestión de inventario
- [x] Sistema de ventas completo ✨ NUEVO
- [x] Calculadora de cambio ✨ NUEVO
- [x] Sincronización automática de inventario ✨ NUEVO
- [x] Interfaz de usuario moderna
- [x] Manejo de errores robusto

### 🔄 **Funcionalidades en Desarrollo**
- [ ] Historial de ventas detallado
- [ ] Reportes y estadísticas
- [ ] Notificaciones de stock bajo
- [ ] Exportación de datos
- [ ] Panel de administración

### 📋 **Próximas Mejoras**
- [ ] Paginación en listas grandes
- [ ] Búsqueda avanzada con filtros
- [ ] Refresh token automático
- [ ] Validación de formularios mejorada
- [ ] Optimistic updates en toda la app 