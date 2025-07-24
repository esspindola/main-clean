# 🚀 ZatoBox v2.0 - Sistema de Punto de Venta Inteligente

Un sistema completo de punto de venta con inventario inteligente, OCR, y gestión avanzada de productos.

## ✨ Características Principales

- 🛍️ **Gestión de Productos**: CRUD completo con imágenes
- 📊 **Inventario Inteligente**: Control de stock y movimientos
- 🔍 **OCR Avanzado**: Escaneo de documentos y facturas
- 💳 **Sistema de Pagos**: Múltiples métodos de pago
- 📈 **Reportes de Ventas**: Análisis detallado
- 🔐 **Autenticación Segura**: JWT con roles de usuario
- 📱 **Interfaz Moderna**: React + TypeScript + Tailwind CSS
- ⚡ **Backend Robusto**: Node.js + Express + SQLite

## 🛠️ Tecnologías Utilizadas

### Frontend
- **React 18** - Biblioteca de UI
- **TypeScript** - Tipado estático
- **Vite** - Build tool rápido
- **Tailwind CSS** - Framework CSS
- **React Router** - Navegación
- **Lucide React** - Iconos
- **Vitest** - Testing

### Backend
- **Node.js** - Runtime de JavaScript
- **Express.js** - Framework web
- **SQLite** - Base de datos
- **JWT** - Autenticación
- **Multer** - Upload de archivos
- **CORS** - Cross-origin requests
- **Jest** - Testing

## 🚀 Instalación y Configuración

### Prerrequisitos
- **Node.js** v18 o superior
- **npm** v8 o superior

### Instalación Rápida

1. **Clonar el repositorio**
```bash
git clone https://github.com/tu-usuario/zatobox.git
cd zatobox
```

2. **Instalar dependencias**
```bash
npm install
```

3. **Ejecutar el proyecto**

#### Opción A: Script Automático (Recomendado)
```powershell
# Windows PowerShell
.\start-project.ps1
```

#### Opción B: Comandos Manuales
```bash
# Terminal 1 - Backend
npm run dev:backend

# Terminal 2 - Frontend
npm run dev:frontend
```

#### Opción C: Ambos Servicios
```bash
npm run dev
```

## 📱 Acceso a la Aplicación

- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:4444
- **Health Check**: http://localhost:4444/health

## 🔑 Credenciales de Prueba

### Administrador
- **Email**: `admin@frontposw.com`
- **Password**: `admin12345678`

### Usuario Regular
- **Email**: `user@frontposw.com`
- **Password**: `user12345678`

## 🧪 Testing

### Frontend Tests
```bash
cd frontend
npm run test
```

### Backend Tests
```bash
cd backend
npm run test
```

### Tests Completos
```bash
npm run test
```

## 📁 Estructura del Proyecto

```
FrontPOSw-main/
├── frontend/                 # Aplicación React
│   ├── src/
│   │   ├── components/       # Componentes React
│   │   ├── contexts/         # Contextos de React
│   │   ├── config/           # Configuración
│   │   ├── services/         # Servicios API
│   │   └── test/             # Tests del frontend
│   ├── package.json
│   └── vite.config.ts
├── backend/                  # Servidor Node.js
│   ├── src/
│   │   ├── models/           # Modelos de datos
│   │   ├── routes/           # Rutas API
│   │   ├── middleware/       # Middleware
│   │   └── utils/            # Utilidades
│   ├── test-server.js        # Servidor de desarrollo
│   └── package.json
├── docs/                     # Documentación
├── scripts/                  # Scripts de automatización
├── start-project.ps1         # Script de inicio
├── stop-project.ps1          # Script de parada
└── package.json              # Configuración raíz
```

## 🔧 Scripts Disponibles

### Scripts Principales
```bash
npm run dev              # Inicia frontend y backend
npm run dev:frontend     # Solo frontend
npm run dev:backend      # Solo backend
npm run build            # Build de producción
npm run test             # Tests completos
npm run lint             # Verificación de código
```

### Scripts de Desarrollo
```bash
npm run install:all      # Instala todas las dependencias
npm run clean            # Limpia node_modules
npm run reset            # Reset completo del proyecto
```

## 🐛 Solución de Problemas

### Puerto 4444 en uso
```powershell
# Detener procesos que usan el puerto
.\stop-project.ps1

# O manualmente
Get-Process -Name "node" | Stop-Process -Force
```

### Errores de CORS
- Verificar que el backend esté ejecutándose en puerto 4444
- Verificar configuración CORS en `backend/test-server.js`
- Usar el archivo `test-cors.html` para verificar comunicación

### Dependencias no encontradas
```bash
# Reinstalar dependencias
npm run clean
npm run install:all
```

## 📊 API Endpoints

### Autenticación
- `POST /api/auth/login` - Iniciar sesión
- `POST /api/auth/register` - Registrar usuario
- `POST /api/auth/logout` - Cerrar sesión
- `GET /api/auth/profile` - Perfil de usuario

### Productos
- `GET /api/products` - Listar productos
- `POST /api/products` - Crear producto
- `PUT /api/products/:id` - Actualizar producto
- `DELETE /api/products/:id` - Eliminar producto

### Ventas
- `GET /api/sales` - Listar ventas
- `POST /api/sales` - Crear venta
- `GET /api/sales/:id` - Obtener venta

### Inventario
- `GET /api/inventory` - Estado del inventario
- `POST /api/inventory/movements` - Registrar movimiento

### OCR
- `POST /api/ocr/upload` - Subir documento para OCR
- `GET /api/ocr/history` - Historial de OCR
- `GET /api/ocr/status/:jobId` - Estado del procesamiento

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE.txt` para más detalles.

## 🆘 Soporte

- **Documentación**: Revisa la carpeta `docs/`
- **Issues**: Reporta bugs en GitHub Issues
- **Discusiones**: Únete a las discusiones en GitHub

## 🎯 Roadmap

- [ ] Integración con pasarelas de pago
- [ ] App móvil nativa
- [ ] Reportes avanzados
- [ ] Integración con contabilidad
- [ ] Múltiples sucursales
- [ ] API pública

---

**ZatoBox v2.0** - Transformando el comercio digital 🚀 
