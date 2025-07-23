# ZatoBox - Arquitectura y Conexiones Backend-Frontend

## 🏗️ Arquitectura General del Sistema

### ZatoBox v2.0
- **Tipo**: Aplicación Full-Stack
- **Backend**: Node.js + Express
- **Frontend**: React + TypeScript + Vite
- **Base de Datos**: JSON Files (users.json, products.json)
- **Autenticación**: JWT Tokens
- **Puertos**: Backend (4444), Frontend (5173)

---

## 🔧 Backend Architecture

### 📁 Estructura de Archivos Backend
- **test-server.js** (Archivo Principal)
  - Servidor Express
  - Configuración CORS
  - Middleware de Autenticación
  - Endpoints API
  - Manejo de Archivos

### 🔐 Sistema de Autenticación Backend
- **JWT Token Management**
  - Generación de tokens
  - Validación de tokens
  - Middleware de autenticación
- **User Management**
  - Registro de usuarios
  - Login/Logout
  - Perfiles de usuario
  - Roles (admin/user)

### 📊 Persistencia de Datos
- **users.json**
  - Datos de usuarios registrados
  - Información de perfiles
  - Roles y permisos
- **Productos en Memoria**
  - Almacenamiento temporal
  - Sincronización con frontend
- **Archivos de Imágenes**
  - uploads/products/
  - Nombres únicos generados
  - Validación de tipos

### 🌐 Configuración de Red
- **CORS Configuration**
  - Orígenes permitidos
  - Métodos HTTP
  - Headers autorizados
- **Puerto**: 4444
- **Protocolo**: HTTP

---

## 🎨 Frontend Architecture

### 📁 Estructura de Archivos Frontend
- **src/**
  - **components/** (Componentes React)
  - **contexts/** (Contextos de Estado)
  - **services/** (Servicios API)
  - **config/** (Configuración)
  - **App.tsx** (Componente Principal)

### 🔄 Estado Global Frontend
- **AuthContext**
  - Estado de autenticación
  - Token management
  - User data
  - Login/Logout functions
- **PluginContext**
  - Estado de plugins
  - Configuraciones

### 🛣️ Routing Frontend
- **React Router**
  - Rutas protegidas
  - Navegación dinámica
  - Sidebar integration

---

## 🔗 Conexiones Backend-Frontend

### 🌐 Comunicación HTTP
- **Base URL**: http://localhost:4444
- **Protocolo**: REST API
- **Content-Type**: application/json
- **Autenticación**: Bearer Token

### 📡 Flujo de Datos
```
Frontend → HTTP Request → Backend
Backend → JSON Response → Frontend
```

### 🔐 Flujo de Autenticación
```
1. Frontend: Login/Register Request
2. Backend: Validate & Generate Token
3. Backend: Return Token + User Data
4. Frontend: Store Token (localStorage)
5. Frontend: Include Token in Headers
6. Backend: Validate Token on Protected Routes
```

---

## 📋 Endpoints API

### 🔓 Endpoints Públicos
- **POST /api/auth/register**
  - Registro de usuarios
  - Validación de datos
  - Generación de token
- **POST /api/auth/login**
  - Autenticación de usuarios
  - Validación de credenciales
  - Retorno de token
- **GET /health**
  - Health check del servidor
  - Estado del sistema

### 🔒 Endpoints Protegidos
- **GET /api/auth/me**
  - Obtener usuario actual
  - Validación de token
- **POST /api/auth/logout**
  - Cerrar sesión
  - Invalidar token

### 📦 Endpoints de Productos
- **GET /api/products**
  - Listar productos
  - Filtros y paginación
- **POST /api/products**
  - Crear producto
  - Subida de imágenes
- **PUT /api/products/:id**
  - Actualizar producto
  - Modificar imágenes
- **DELETE /api/products/:id**
  - Eliminar producto
  - Confirmación modal

### 📊 Endpoints de Inventario
- **GET /api/inventory**
  - Obtener inventario
  - Stock actual
- **PUT /api/inventory/:id**
  - Actualizar stock
  - Movimientos de inventario

### 💰 Endpoints de Ventas
- **POST /api/sales**
  - Crear venta
  - Validación de stock
  - Actualización automática
- **GET /api/sales**
  - Historial de ventas
  - Estadísticas

### 👤 Endpoints de Perfil
- **GET /api/profile**
  - Obtener perfil
  - Datos del usuario
- **PUT /api/profile**
  - Actualizar perfil
  - Modificar información

---

## 🖼️ Sistema de Imágenes

### 📤 Subida de Imágenes
- **Multer Configuration**
  - Almacenamiento en disco
  - Nombres únicos
  - Validación de tipos
  - Límite de tamaño (5MB)
- **Tipos Permitidos**
  - JPEG, JPG, PNG, GIF, WebP
- **Estructura de Archivos**
  - uploads/products/
  - Nombres: product-timestamp-random.ext

### 🌐 Servir Imágenes
- **Static File Serving**
  - Express.static middleware
  - URL: /uploads/products/filename
- **Frontend Integration**
  - Construcción de URLs
  - Fallback para imágenes
  - Preview antes de subir

---

## 🔄 Flujos de Datos Principales

### 📦 Gestión de Productos
```
1. Frontend: Form Data + Images
2. Backend: Validate & Store
3. Backend: Save Images
4. Backend: Return Product Data
5. Frontend: Update UI
6. Frontend: Show Success/Error
```

### 💰 Proceso de Venta
```
1. Frontend: Select Products
2. Frontend: Calculate Total
3. Frontend: Payment Screen
4. Frontend: Send Sale Data
5. Backend: Validate Stock
6. Backend: Update Inventory
7. Backend: Create Sale Record
8. Frontend: Show Success
9. Frontend: Update Product List
```

### 🗑️ Eliminación de Productos
```
1. Frontend: Delete Button Click
2. Frontend: Show Confirmation Modal
3. Frontend: User Confirms
4. Frontend: Send Delete Request
5. Backend: Validate & Delete
6. Backend: Return Success
7. Frontend: Remove from UI
8. Frontend: Show Success Message
```

---

## 🛡️ Seguridad y Validación

### 🔐 Autenticación
- **JWT Tokens**
  - Generación segura
  - Validación en cada request
  - Expiración automática
- **Middleware de Auth**
  - Verificación de token
  - Extracción de user data
  - Manejo de errores

### ✅ Validación de Datos
- **Frontend Validation**
  - Form validation
  - File type checking
  - Required fields
- **Backend Validation**
  - Input sanitization
  - Type checking
  - Business logic validation

### 🛡️ CORS Security
- **Orígenes Permitidos**
  - localhost:5173-5183
  - 127.0.0.1:5173-5183
- **Métodos HTTP**
  - GET, POST, PUT, DELETE, PATCH
- **Headers**
  - Content-Type, Authorization

---

## 📱 Componentes Frontend

### 🏠 Páginas Principales
- **HomePage**
  - Dashboard principal
  - Resumen de ventas
  - Accesos rápidos
- **InventoryPage**
  - Lista de productos
  - CRUD operations
  - Filtros y búsqueda
- **NewProductPage**
  - Formulario de creación
  - Subida de imágenes
  - Validación en tiempo real
- **EditProductPage**
  - Edición de productos
  - Modificación de imágenes
  - Actualización de datos

### 🔐 Páginas de Autenticación
- **LoginPage**
  - Formulario de login
  - Validación de credenciales
  - Manejo de errores
- **RegisterPage**
  - Registro de usuarios
  - Validación de datos
  - Confirmación de contraseña

### 💰 Páginas de Ventas
- **PaymentScreen**
  - Procesamiento de pagos
  - Calculadora de cambio
  - Métodos de pago
- **SalesDrawer**
  - Historial de ventas
  - Filtros por fecha
  - Detalles de transacciones

### 👤 Páginas de Usuario
- **ProfilePage**
  - Información del usuario
  - Edición de perfil
  - Configuraciones
- **SideMenu**
  - Navegación principal
  - Menú de usuario
  - Logout

---

## 🔧 Servicios y Utilidades

### 📡 API Services
- **authAPI**
  - Login/Register
  - Token management
  - User operations
- **productsAPI**
  - CRUD operations
  - Image upload
  - Search and filters
- **salesAPI**
  - Create sales
  - Get history
  - Statistics
- **inventoryAPI**
  - Stock management
  - Updates
  - Movements

### 🎨 UI Components
- **ProductCard**
  - Display product info
  - Image handling
  - Action buttons
- **ProtectedRoute**
  - Route protection
  - Auth checking
  - Redirect logic

---

## 📊 Estado de la Aplicación

### 🔄 Estados Principales
- **Authentication State**
  - isAuthenticated
  - user data
  - token
  - loading
- **Product State**
  - products list
  - selected product
  - filters
  - loading
- **Sales State**
  - cart items
  - total amount
  - payment method
  - processing

### 💾 Persistencia Local
- **localStorage**
  - JWT token
  - User preferences
  - Cart data
- **Session Storage**
  - Temporary data
  - Form state

---

## 🚀 Despliegue y Configuración

### 🔧 Variables de Entorno
- **Backend**
  - PORT=4444
  - JWT_SECRET
  - CORS_ORIGINS
- **Frontend**
  - VITE_API_URL
  - VITE_APP_NAME

### 📦 Scripts de Despliegue
- **Development**
  - Backend: `node test-server.js`
  - Frontend: `npm run dev`
- **Production**
  - Backend: `npm start`
  - Frontend: `npm run build`

### 🌐 Configuración de Red
- **Development**
  - Backend: localhost:4444
  - Frontend: localhost:5173
- **Production**
  - Backend: domain.com:4444
  - Frontend: domain.com

---

## 🔍 Monitoreo y Debugging

### 📝 Logging
- **Backend Logs**
  - Console output
  - Error tracking
  - Request logging
- **Frontend Logs**
  - Browser console
  - Error boundaries
  - Performance monitoring

### 🐛 Error Handling
- **Backend Errors**
  - Try-catch blocks
  - Error middleware
  - Status codes
- **Frontend Errors**
  - Error boundaries
  - User feedback
  - Fallback UI

---

## 📈 Métricas y Rendimiento

### ⚡ Performance
- **Backend**
  - Response times
  - Memory usage
  - CPU utilization
- **Frontend**
  - Load times
  - Bundle size
  - Runtime performance

### 📊 Analytics
- **User Activity**
  - Page views
  - Feature usage
  - Error rates
- **Business Metrics**
  - Sales volume
  - Product performance
  - User engagement

---

## 🔮 Roadmap y Mejoras

### 🚀 Próximas Funcionalidades
- **Real-time Updates**
  - WebSocket integration
  - Live inventory sync
  - Notifications
- **Advanced Analytics**
  - Sales reports
  - Inventory analytics
  - User insights
- **Mobile App**
  - React Native
  - Offline support
  - Push notifications

### 🔧 Mejoras Técnicas
- **Database Migration**
  - PostgreSQL integration
  - Data migration
  - Backup systems
- **API Enhancement**
  - GraphQL support
  - Rate limiting
  - Caching
- **Security Upgrades**
  - 2FA support
  - Role-based access
  - Audit logging

---

## 📚 Documentación Relacionada

### 📖 Archivos de Documentación
- **README.md** - Documentación principal
- **CONEXIONES_BACKEND_FRONTEND.md** - Guía técnica en español
- **CONEXIONES_BACKEND_FRONTEND_ENGLISH.md** - Guía técnica en inglés
- **CONNECTION_GUIDE.md** - Guía de conexión rápida

### 🔗 Enlaces Útiles
- **GitHub Repository**: https://github.com/ZatoBox/main
- **Discord Community**: https://discord.gg/2zUVsv9aMF
- **Issue Tracker**: https://github.com/ZatoBox/main/issues

---

**ZatoBox v2.0** - Arquitectura Completa del Sistema de Gestión de Inventario y Ventas 