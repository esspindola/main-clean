# 🏗️ Arquitectura del Sistema ZatoBox v2.0

## 📋 Resumen Ejecutivo

ZatoBox v2.0 es una aplicación full-stack moderna construida con tecnologías web estándar, siguiendo principios de arquitectura limpia y escalabilidad.

## 🎯 Principios de Arquitectura

- **Separación de Responsabilidades**: Frontend y Backend completamente separados
- **Escalabilidad**: Diseño modular que permite crecimiento horizontal
- **Mantenibilidad**: Código limpio y bien documentado
- **Testabilidad**: Arquitectura que facilita testing en todos los niveles
- **Flexibilidad**: Sistema de plugins para extensibilidad

## 🏛️ Arquitectura General

```
┌─────────────────┐    HTTP/HTTPS    ┌─────────────────┐
│   Frontend      │ ◄──────────────► │    Backend      │
│   (React)       │                  │   (Node.js)     │
└─────────────────┘                  └─────────────────┘
         │                                     │
         │                                     │
         ▼                                     ▼
┌─────────────────┐                  ┌─────────────────┐
│   Browser       │                  │   SQLite DB     │
│   Storage       │                  │   File System   │
└─────────────────┘                  └─────────────────┘
```

## 🎨 Capa de Presentación (Frontend)

### Tecnologías
- **React 18**: Biblioteca de UI moderna
- **TypeScript**: Tipado estático para mayor seguridad
- **Vite**: Build tool ultra rápido
- **Tailwind CSS**: Framework CSS utility-first
- **React Router v6**: Navegación declarativa

### Estructura de Componentes

```
src/
├── components/           # Componentes de UI
│   ├── HomePage.tsx     # Página principal
│   ├── InventoryPage.tsx # Gestión de inventario
│   ├── NewProductPage.tsx # Crear productos
│   ├── SettingsPage.tsx # Configuración del sistema
│   ├── SideMenu.tsx     # Menú lateral
│   └── ...
├── contexts/            # Contextos de React
│   ├── AuthContext.tsx  # Gestión de autenticación
│   └── PluginContext.tsx # Gestión de plugins
├── config/              # Configuración
│   └── api.ts          # Configuración de API
├── services/            # Servicios de API
│   └── api.ts          # Cliente HTTP
└── test/               # Tests del frontend
```

### Patrones de Diseño
- **Context API**: Para estado global
- **Custom Hooks**: Para lógica reutilizable
- **Component Composition**: Para composición de componentes
- **Render Props**: Para compartir lógica entre componentes

## ⚙️ Capa de Lógica de Negocio (Backend)

### Tecnologías
- **Node.js**: Runtime de JavaScript
- **Express.js**: Framework web minimalista
- **SQLite**: Base de datos ligera
- **JWT**: Autenticación stateless
- **Multer**: Manejo de uploads

### Estructura del Backend

```
backend/
├── src/
│   ├── models/          # Modelos de datos
│   │   ├── User.js     # Modelo de usuario
│   │   ├── Product.js  # Modelo de producto
│   │   ├── Sale.js     # Modelo de venta
│   │   └── ...
│   ├── routes/          # Rutas API
│   │   ├── auth.js     # Rutas de autenticación
│   │   ├── products.js # Rutas de productos
│   │   ├── sales.js    # Rutas de ventas
│   │   └── ...
│   ├── middleware/      # Middleware
│   │   ├── auth.js     # Middleware de autenticación
│   │   └── ...
│   ├── config/          # Configuración
│   │   ├── database.js # Configuración de BD
│   │   └── ...
│   └── utils/           # Utilidades
├── test-server.js       # Servidor de desarrollo
└── users.json           # Datos de usuarios
```

### Patrones de Diseño
- **MVC**: Model-View-Controller
- **Middleware Pattern**: Para procesamiento de requests
- **Repository Pattern**: Para acceso a datos
- **Service Layer**: Para lógica de negocio

## 🗄️ Capa de Datos

### Base de Datos
- **SQLite**: Base de datos ligera y eficiente
- **JSON Files**: Para datos simples (usuarios, configuración)
- **File System**: Para almacenamiento de imágenes

### Modelos de Datos

#### Usuario
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

#### Producto
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

#### Venta
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

## 🔌 Sistema de Plugins

### Arquitectura de Plugins
```
Plugin System
├── Plugin Registry     # Registro de plugins disponibles
├── Plugin Loader      # Cargador dinámico de plugins
├── Plugin Context     # Contexto compartido entre plugins
└── Plugin Store       # Tienda de plugins
```

### Plugins Disponibles
- **Smart Inventory**: IA para gestión de inventario
- **OCR Module**: Procesamiento de documentos
- **POS Integration**: Integración con sistemas POS

### API de Plugins
```javascript
// Interfaz de plugin
interface Plugin {
  id: string;
  name: string;
  description: string;
  version: string;
  isActive: boolean;
  initialize(): Promise<void>;
  destroy(): Promise<void>;
}
```

## 🔐 Seguridad

### Autenticación
- **JWT Tokens**: Autenticación stateless
- **Password Hashing**: bcrypt para contraseñas
- **Session Management**: Gestión de sesiones
- **Role-based Access**: Control de acceso por roles

### Autorización
- **Middleware de Autenticación**: Verificación de tokens
- **Role-based Routes**: Rutas protegidas por rol
- **Input Validation**: Validación de entrada
- **CORS Configuration**: Configuración de CORS

## 📡 Comunicación Frontend-Backend

### Protocolo
- **HTTP/HTTPS**: Protocolo de comunicación
- **RESTful API**: Diseño de API REST
- **JSON**: Formato de datos
- **CORS**: Cross-origin resource sharing

### Endpoints Principales
```
Authentication:
├── POST /api/auth/login
├── POST /api/auth/register
├── POST /api/auth/logout
└── GET /api/auth/me

Products:
├── GET /api/products
├── POST /api/products
├── PUT /api/products/:id
└── DELETE /api/products/:id

Sales:
├── GET /api/sales
├── POST /api/sales
└── GET /api/sales/:id

System:
├── GET /health
└── GET /api/health
```

## 🧪 Testing

### Frontend Testing
- **Vitest**: Framework de testing
- **React Testing Library**: Testing de componentes
- **Jest DOM**: Matchers para DOM
- **Coverage**: 95%+ cobertura

### Backend Testing
- **Jest**: Framework de testing
- **Supertest**: Testing de APIs
- **Mocking**: Simulación de dependencias
- **Integration Tests**: Tests de integración

## 🚀 Deployment

### Desarrollo
- **Vite Dev Server**: Puerto 5173
- **Express Dev Server**: Puerto 4444
- **Hot Reload**: Recarga automática
- **Source Maps**: Para debugging

### Producción
- **Build Optimization**: Optimización de build
- **Static Assets**: Servido de assets estáticos
- **Environment Variables**: Variables de entorno
- **Logging**: Sistema de logging

## 📊 Monitoreo y Logging

### Logging
- **Console Logging**: Logs en consola
- **Request Logging**: Logs de requests
- **Error Logging**: Logs de errores
- **Performance Logging**: Logs de rendimiento

### Health Checks
- **Health Endpoint**: `/health`
- **API Health**: `/api/health`
- **Database Health**: Verificación de BD
- **Dependencies Health**: Verificación de dependencias

## 🔄 Flujo de Datos

### Creación de Producto
```
1. Frontend: Formulario de producto
2. Frontend: Validación de datos
3. Frontend: Envío a API
4. Backend: Validación de entrada
5. Backend: Procesamiento de imágenes
6. Backend: Guardado en BD
7. Backend: Respuesta exitosa
8. Frontend: Actualización de UI
```

### Autenticación
```
1. Frontend: Formulario de login
2. Frontend: Envío de credenciales
3. Backend: Validación de credenciales
4. Backend: Generación de JWT
5. Backend: Respuesta con token
6. Frontend: Almacenamiento de token
7. Frontend: Redirección a dashboard
```

## 🎯 Escalabilidad

### Horizontal Scaling
- **Load Balancer**: Distribución de carga
- **Multiple Instances**: Múltiples instancias
- **Database Clustering**: Clustering de BD
- **CDN**: Content Delivery Network

### Vertical Scaling
- **Resource Optimization**: Optimización de recursos
- **Caching**: Sistema de caché
- **Database Optimization**: Optimización de BD
- **Code Optimization**: Optimización de código

## 🔮 Futuras Mejoras

### Arquitectura
- **Microservices**: Migración a microservicios
- **Event-Driven**: Arquitectura basada en eventos
- **GraphQL**: Implementación de GraphQL
- **Real-time**: Comunicación en tiempo real

### Tecnologías
- **Docker**: Containerización
- **Kubernetes**: Orquestación de contenedores
- **Redis**: Caché en memoria
- **PostgreSQL**: Base de datos más robusta

---

**ZatoBox v2.0** - Arquitectura moderna y escalable 🏗️

*Diseñada para crecer con tu negocio.* 