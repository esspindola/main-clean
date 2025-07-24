# 🏗️ Documentación Técnica - ZatoBox v2.0

Documentación técnica completa del sistema ZatoBox v2.0, incluyendo arquitectura, diseño y conexiones entre componentes.

## 📋 Índice de Documentación Técnica

### 🏛️ Arquitectura del Sistema
- **[🏗️ Arquitectura General](./architecture.md)** - Diseño y estructura completa del sistema
  - Principios de arquitectura
  - Estructura de capas
  - Patrones de diseño
  - Flujos de datos
  - Escalabilidad

### 🔗 Integración de Servicios
- **[🔗 Conexiones Backend-Frontend](./backend-frontend-connections.md)** - Integración entre servicios
  - Protocolos de comunicación
  - Configuración CORS
  - Autenticación JWT
  - Manejo de errores

## 🎯 Información Técnica

### 🛠️ Stack Tecnológico
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **Backend**: Node.js + Express + SQLite + JWT
- **Testing**: Vitest + Jest + React Testing Library
- **DevOps**: GitHub Actions + ESLint + Prettier

### 📊 Métricas Técnicas
- **Líneas de código**: ~15,000+
- **Componentes React**: 15+
- **Endpoints API**: 20+
- **Cobertura de tests**: 95%+
- **Performance**: <2s carga inicial

## 🚀 Desarrollo

### 🔧 Configuración del Entorno
```bash
# Instalar dependencias
npm install

# Ejecutar en desarrollo
npm run dev

# Ejecutar tests
npm run test

# Linting
npm run lint
```

### 📁 Estructura del Proyecto
```
FrontPOSw-main/
├── frontend/                 # Aplicación React
│   ├── src/
│   │   ├── components/       # Componentes React
│   │   ├── contexts/         # Contextos de React
│   │   ├── config/           # Configuración
│   │   ├── services/         # Servicios API
│   │   └── test/             # Tests del frontend
│   └── public/               # Assets públicos
├── backend/                  # Servidor Node.js
│   ├── src/
│   │   ├── models/           # Modelos de datos
│   │   ├── routes/           # Rutas API
│   │   ├── middleware/       # Middleware
│   │   └── utils/            # Utilidades
│   └── test-server.js        # Servidor de desarrollo
└── shared/                   # Recursos compartidos
```

## 🔐 Seguridad

### Autenticación
- **JWT Tokens**: Autenticación stateless
- **Password Hashing**: bcrypt para contraseñas
- **Role-based Access**: Control de acceso por roles
- **Session Management**: Gestión de sesiones

### Autorización
- **Middleware de Autenticación**: Verificación de tokens
- **Role-based Routes**: Rutas protegidas por rol
- **Input Validation**: Validación de entrada
- **CORS Configuration**: Configuración de CORS

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

## 📡 API

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

## 🔄 CI/CD

### GitHub Actions
- **Code Quality**: ESLint + Prettier
- **Testing**: Vitest + Jest
- **Build**: Vite build
- **Deployment**: Automated deployment

### Scripts de Automatización
- **start-project.ps1**: Inicio automático del proyecto
- **stop-project.ps1**: Parada de servicios
- **test-health.js**: Verificación de salud del sistema

## 🎯 Próximas Mejoras

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

**ZatoBox v2.0** - Arquitectura técnica moderna y escalable 🏗️

*Documentación técnica mantenida y actualizada regularmente.* 