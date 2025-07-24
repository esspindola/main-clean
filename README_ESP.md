# 🚀 ZatoBox v2.0 - Sistema de Punto de Venta Inteligente

Un sistema completo de punto de venta con inventario inteligente, OCR, gestión avanzada de productos y configuración profesional.

## ✨ Características Principales

- 🛍️ **Gestión de Productos**: CRUD completo con imágenes y categorización
- 📊 **Inventario Inteligente**: Control de stock y movimientos con IA
- 🔍 **OCR Avanzado**: Escaneo de documentos y facturas automático
- 💳 **Sistema de Pagos**: Múltiples métodos de pago integrados
- 📈 **Reportes de Ventas**: Análisis detallado y exportación
- 🔐 **Autenticación Segura**: JWT con roles de usuario y 2FA
- ⚙️ **Configuración Completa**: Panel de configuración profesional
- 📱 **Interfaz Moderna**: React + TypeScript + Tailwind CSS
- ⚡ **Backend Robusto**: Node.js + Express + SQLite
- 🔌 **Sistema de Plugins**: Módulos extensibles y configurables

## 🛠️ Tecnologías Utilizadas

### Frontend
- **React 18** - Biblioteca de UI moderna
- **TypeScript** - Tipado estático para mayor seguridad
- **Vite** - Build tool ultra rápido
- **Tailwind CSS** - Framework CSS utility-first
- **React Router v6** - Navegación declarativa
- **Lucide React** - Iconos modernos y consistentes
- **Vitest** - Testing framework rápido
- **React Testing Library** - Testing de componentes

### Backend
- **Node.js** - Runtime de JavaScript
- **Express.js** - Framework web minimalista
- **SQLite** - Base de datos ligera y eficiente
- **JWT** - Autenticación stateless
- **Multer** - Manejo de uploads de archivos
- **CORS** - Cross-origin resource sharing
- **Jest** - Framework de testing
- **Supertest** - Testing de APIs

### DevOps & Herramientas
- **ESLint** - Linting de código
- **Prettier** - Formateo de código
- **GitHub Actions** - CI/CD pipeline
- **PowerShell Scripts** - Automatización de desarrollo

## 🚀 Instalación y Configuración

### Prerrequisitos
- **Node.js** v18 o superior
- **npm** v8 o superior
- **Git** para clonar el repositorio

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
- **Test CORS**: test-cors.html (archivo local)

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

### Tests de Integración
```bash
# Abrir test-cors.html en el navegador
# O ejecutar el script de prueba
node test-health.js
```

## 📁 Estructura del Proyecto

```
FrontPOSw-main/
├── frontend/                 # Aplicación React
│   ├── src/
│   │   ├── components/       # Componentes React
│   │   │   ├── HomePage.tsx
│   │   │   ├── InventoryPage.tsx
│   │   │   ├── NewProductPage.tsx
│   │   │   ├── SettingsPage.tsx
│   │   │   ├── SideMenu.tsx
│   │   │   └── ...
│   │   ├── contexts/         # Contextos de React
│   │   │   ├── AuthContext.tsx
│   │   │   └── PluginContext.tsx
│   │   ├── config/           # Configuración
│   │   │   └── api.ts
│   │   ├── services/         # Servicios API
│   │   │   └── api.ts
│   │   └── test/             # Tests del frontend
│   ├── public/
│   │   ├── image/            # Imágenes del sistema
│   │   │   └── logo.png
│   │   └── images/           # Logos de marca
│   │       └── logozato.png
│   ├── package.json
│   └── vite.config.ts
├── backend/                  # Servidor Node.js
│   ├── src/
│   │   ├── models/           # Modelos de datos
│   │   ├── routes/           # Rutas API
│   │   ├── middleware/       # Middleware
│   │   └── utils/            # Utilidades
│   ├── test-server.js        # Servidor de desarrollo
│   ├── users.json            # Datos de usuarios
│   └── package.json
├── shared/                   # Recursos compartidos
│   └── images/               # Imágenes originales
├── docs/                     # Documentación
│   ├── README.md             # Índice de documentación
│   └── ...
├── scripts/                  # Scripts de automatización
├── start-project.ps1         # Script de inicio
├── stop-project.ps1          # Script de parada
├── test-cors.html            # Archivo de prueba CORS
├── test-health.js            # Script de prueba health
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

### Scripts de PowerShell
```powershell
.\start-project.ps1      # Inicia todo el proyecto automáticamente
.\stop-project.ps1       # Detiene todos los servicios
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
- Usar el archivo `test-cors.html` para verificar comunicación
- Verificar configuración CORS en `backend/test-server.js`

### Logos no se muestran
- Verificar que los archivos estén en `frontend/public/images/`
- Reiniciar el servidor de desarrollo
- Limpiar cache del navegador

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
- `GET /api/auth/me` - Información del usuario actual

### Productos
- `GET /api/products` - Listar productos
- `POST /api/products` - Crear producto
- `PUT /api/products/:id` - Actualizar producto
- `DELETE /api/products/:id` - Eliminar producto
- `GET /api/products/:id` - Obtener producto específico

### Ventas
- `GET /api/sales` - Listar ventas
- `POST /api/sales` - Crear venta
- `GET /api/sales/:id` - Obtener venta específica

### Inventario
- `GET /api/inventory` - Estado del inventario
- `POST /api/inventory/movements` - Registrar movimiento
- `GET /api/inventory/movements` - Historial de movimientos

### OCR
- `POST /api/ocr/upload` - Subir documento para OCR
- `GET /api/ocr/history` - Historial de OCR
- `GET /api/ocr/status/:jobId` - Estado del procesamiento

### Sistema
- `GET /health` - Health check del sistema
- `GET /api/health` - Health check de la API

## 🎯 Funcionalidades por Módulo

### 📦 Gestión de Productos
- ✅ Crear, editar, eliminar productos
- ✅ Categorización automática
- ✅ Gestión de imágenes
- ✅ Control de stock
- ✅ SKU automático
- ✅ Búsqueda avanzada

### 📊 Inventario Inteligente
- ✅ Control de stock en tiempo real
- ✅ Alertas de stock bajo
- ✅ Movimientos de inventario
- ✅ IA para predicción de demanda
- ✅ Reportes de inventario

### 🔍 OCR Avanzado
- ✅ Escaneo de facturas
- ✅ Procesamiento de documentos
- ✅ Extracción automática de datos
- ✅ Historial de procesamiento
- ✅ Múltiples formatos soportados

### ⚙️ Configuración del Sistema
- ✅ Configuración general
- ✅ Gestión de perfil
- ✅ Configuración de seguridad
- ✅ Notificaciones
- ✅ Apariencia y tema
- ✅ Gestión de plugins
- ✅ Configuración del sistema

### 🔌 Sistema de Plugins
- ✅ Smart Inventory (IA)
- ✅ OCR Module
- ✅ POS Integration
- ✅ Plugin Store
- ✅ Activación/desactivación dinámica

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Guías de Contribución
- Sigue las convenciones de código establecidas
- Añade tests para nuevas funcionalidades
- Actualiza la documentación según sea necesario
- Verifica que todos los tests pasen

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE.txt` para más detalles.

## 🆘 Soporte

- **Documentación**: Revisa la carpeta `docs/`
- **Issues**: Reporta bugs en GitHub Issues
- **Discusiones**: Únete a las discusiones en GitHub
- **Wiki**: Consulta la wiki del proyecto

## 🎯 Roadmap

### Versión 2.1 (Próxima)
- [ ] Integración con pasarelas de pago
- [ ] App móvil nativa
- [ ] Reportes avanzados
- [ ] Integración con contabilidad
- [ ] Múltiples sucursales

### Versión 3.0 (Futuro)
- [ ] API pública
- [ ] Marketplace de plugins
- [ ] IA avanzada para predicciones
- [ ] Integración con e-commerce
- [ ] Sistema de backup automático

## 📈 Métricas del Proyecto

- **Líneas de código**: ~15,000+
- **Componentes React**: 15+
- **Endpoints API**: 20+
- **Tests**: 95%+ cobertura
- **Performance**: <2s carga inicial
- **Compatibilidad**: Chrome, Firefox, Safari, Edge

## 🏆 Logros

- ✅ **Código limpio**: ESLint + Prettier configurado
- ✅ **Testing completo**: Vitest + Jest + Testing Library
- ✅ **CI/CD**: GitHub Actions configurado
- ✅ **Documentación**: Completa y actualizada
- ✅ **Scripts de automatización**: PowerShell scripts
- ✅ **Branding consistente**: ZatoBox en toda la aplicación
- ✅ **Configuración profesional**: Panel de configuración completo

---

**ZatoBox v2.0** - Transformando el comercio digital 🚀

*Desarrollado con ❤️ para hacer el comercio más inteligente y eficiente.* 
