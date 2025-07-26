# FrontPOSw Backend

Backend completo para el sistema de inventario y ventas FrontPOSw.

## 🚀 Características

- **Autenticación JWT** - Sistema completo de login/registro
- **Gestión de Productos** - CRUD completo con imágenes y variantes
- **Control de Inventario** - Movimientos de stock y alertas
- **Sistema de Ventas** - Procesamiento de transacciones
- **Perfil de Usuario** - Configuraciones y preferencias
- **OCR** - Procesamiento de documentos (simulado)
- **API RESTful** - Endpoints bien documentados
- **Base de Datos PostgreSQL** - Con Sequelize ORM
- **Validación de Datos** - Con express-validator
- **Subida de Archivos** - Con multer
- **Rate Limiting** - Protección contra spam
- **CORS** - Configurado para frontend

## 📋 Prerrequisitos

- Node.js (v16 o superior)
- PostgreSQL (v12 o superior)
- npm o yarn

## 🛠️ Instalación

1. **Clonar el repositorio**
   ```bash
   cd backend
   ```

2. **Instalar dependencias**
   ```bash
   npm install
   ```

3. **Configurar variables de entorno**
   ```bash
   cp env.example .env
   ```
   
   Editar `.env` con tus configuraciones:
   ```env
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=frontposw
   DB_USER=postgres
   DB_PASSWORD=tu-password
   JWT_SECRET=tu-super-secreto-jwt-key
   ```

4. **Crear base de datos**
   ```sql
   CREATE DATABASE frontposw;
   ```

5. **Ejecutar el servidor**
   ```bash
   # Desarrollo
   npm run dev
   
   # Producción
   npm start
   ```

## 📊 Estructura de la Base de Datos

### Tablas Principales

- **users** - Usuarios del sistema
- **products** - Productos del inventario
- **sales** - Transacciones de venta
- **inventory_movements** - Movimientos de stock

### Relaciones

- Un usuario puede tener muchos productos
- Un usuario puede tener muchas ventas
- Un producto puede tener muchos movimientos de inventario

## 🔌 Endpoints de la API

### Autenticación
- `POST /api/auth/register` - Registrar usuario
- `POST /api/auth/login` - Iniciar sesión
- `POST /api/auth/logout` - Cerrar sesión
- `GET /api/auth/me` - Obtener usuario actual

### Productos
- `GET /api/products` - Listar productos
- `GET /api/products/:id` - Obtener producto
- `POST /api/products` - Crear producto
- `PUT /api/products/:id` - Actualizar producto
- `DELETE /api/products/:id` - Eliminar producto
- `POST /api/products/:id/images` - Subir imágenes

### Inventario
- `GET /api/inventory` - Listar inventario
- `GET /api/inventory/low-stock` - Productos con stock bajo
- `PUT /api/inventory/:id/stock` - Actualizar stock
- `GET /api/inventory/movements` - Movimientos de inventario
- `POST /api/inventory/bulk-update` - Actualización masiva

### Ventas
- `GET /api/sales` - Listar ventas
- `GET /api/sales/:id` - Obtener venta
- `POST /api/sales` - Crear venta
- `PATCH /api/sales/:id/status` - Actualizar estado
- `GET /api/sales/stats/summary` - Estadísticas

### Perfil
- `GET /api/profile` - Obtener perfil
- `PUT /api/profile` - Actualizar perfil
- `PUT /api/profile/password` - Cambiar contraseña
- `GET /api/profile/sessions` - Sesiones activas

### OCR
- `POST /api/ocr/process-document` - Procesar documento
- `GET /api/ocr/history` - Historial de procesamiento
- `GET /api/ocr/status/:jobId` - Estado del procesamiento

## 🔒 Autenticación

Todas las rutas protegidas requieren el header:
```
Authorization: Bearer <token>
```

## 📁 Estructura del Proyecto

```
backend/
├── src/
│   ├── config/
│   │   └── database.js
│   ├── controllers/
│   ├── models/
│   │   ├── User.js
│   │   ├── Product.js
│   │   ├── Sale.js
│   │   └── InventoryMovement.js
│   ├── routes/
│   │   ├── auth.js
│   │   ├── products.js
│   │   ├── inventory.js
│   │   ├── sales.js
│   │   ├── profile.js
│   │   └── ocr.js
│   ├── middleware/
│   │   └── auth.js
│   ├── services/
│   └── utils/
├── uploads/
├── package.json
├── server.js
└── README.md
```

## 🧪 Testing

```bash
npm test
```

## 📝 Scripts Disponibles

- `npm start` - Iniciar servidor en producción
- `npm run dev` - Iniciar servidor en desarrollo con nodemon
- `npm test` - Ejecutar tests

## 🔧 Configuración de Desarrollo

### Variables de Entorno

```env
# Base de datos
DB_HOST=localhost
DB_PORT=5432
DB_NAME=frontposw
DB_USER=postgres
DB_PASSWORD=postgres123

# JWT
JWT_SECRET=your-super-secret-jwt-key

# Servidor
PORT=3000
NODE_ENV=development

# Frontend
FRONTEND_URL=http://localhost:5173
```

### Base de Datos

El sistema usa PostgreSQL con Sequelize ORM. Las tablas se crean automáticamente al iniciar el servidor.

## 🚀 Despliegue

### Producción

1. Configurar variables de entorno para producción
2. Instalar dependencias: `npm install --production`
3. Ejecutar migraciones: `npm run migrate`
4. Iniciar servidor: `npm start`

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --production
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

## 📞 Soporte

Para soporte técnico o preguntas, contacta al equipo de desarrollo.

## 📄 Licencia

MIT License 