# 🚀 Guía de Conexión Frontend-Backend

Esta guía te ayudará a conectar el frontend React con el backend Node.js para que toda la aplicación funcione al 100%.

## 📋 Prerrequisitos

- Node.js (v16 o superior)
- PostgreSQL (v12 o superior)
- npm o yarn

## 🛠️ Configuración del Backend

### 1. Instalar dependencias del backend
```bash
cd backend
npm install
```

### 2. Configurar base de datos PostgreSQL
```bash
# Crear base de datos
createdb frontposw

# O usando psql
psql -U postgres
CREATE DATABASE frontposw;
\q
```

### 3. Configurar variables de entorno
```bash
cd backend
cp env.example .env
```

Editar `.env`:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=frontposw
DB_USER=postgres
DB_PASSWORD=tu-password-postgres
JWT_SECRET=tu-super-secreto-jwt-key-muy-largo
PORT=3000
NODE_ENV=development
FRONTEND_URL=http://localhost:5173
```

### 4. Iniciar el backend
```bash
cd backend
npm run dev
```

El backend estará disponible en: http://localhost:3000

### 5. Poblar la base de datos con datos de ejemplo
```bash
cd backend
npm run seed
```

**Credenciales de ejemplo:**
- Admin: `admin@frontposw.com` / `admin123`
- User: `user@frontposw.com` / `user123`

## 🎨 Configuración del Frontend

### 1. Instalar dependencias del frontend
```bash
# En la raíz del proyecto
npm install
```

### 2. Configurar el contexto de autenticación
El archivo `src/contexts/AuthContext.tsx` ya está creado y configurado.

### 3. Configurar el servicio de API
El archivo `src/services/api.js` ya está creado y apunta a `http://localhost:3000/api`.

### 4. Iniciar el frontend
```bash
npm run dev
```

El frontend estará disponible en: http://localhost:5173

## 🔗 Conexión de Componentes

### LoginPage.tsx
```typescript
import { useAuth } from '../contexts/AuthContext';

const LoginPage: React.FC = () => {
  const { login } = useAuth();
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(formData.email, formData.password);
      navigate('/');
    } catch (error) {
      console.error('Login failed:', error);
    }
  };
};
```

### RegisterPage.tsx
```typescript
import { useAuth } from '../contexts/AuthContext';

const RegisterPage: React.FC = () => {
  const { register } = useAuth();
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await register(formData);
      navigate('/');
    } catch (error) {
      console.error('Registration failed:', error);
    }
  };
};
```

### HomePage.tsx
```typescript
import { productsAPI } from '../services/api';
import { useEffect, useState } from 'react';

const HomePage: React.FC = () => {
  const [products, setProducts] = useState([]);
  
  useEffect(() => {
    const loadProducts = async () => {
      try {
        const response = await productsAPI.getAll();
        setProducts(response.products);
      } catch (error) {
        console.error('Failed to load products:', error);
      }
    };
    
    loadProducts();
  }, []);
};
```

### InventoryPage.tsx
```typescript
import { inventoryAPI } from '../services/api';

const InventoryPage: React.FC = () => {
  const [inventory, setInventory] = useState([]);
  
  useEffect(() => {
    const loadInventory = async () => {
      try {
        const response = await inventoryAPI.getAll();
        setInventory(response.products);
      } catch (error) {
        console.error('Failed to load inventory:', error);
      }
    };
    
    loadInventory();
  }, []);
};
```

### NewProductPage.tsx
```typescript
import { productsAPI } from '../services/api';

const NewProductPage: React.FC = () => {
  const handleSave = async () => {
    try {
      await productsAPI.create(formData);
      navigate('/inventory');
    } catch (error) {
      console.error('Failed to create product:', error);
    }
  };
};
```

### EditProductPage.tsx
```typescript
import { productsAPI } from '../services/api';

const EditProductPage: React.FC = () => {
  const { id } = useParams();
  
  useEffect(() => {
    const loadProduct = async () => {
      try {
        const response = await productsAPI.getById(id);
        setFormData(response.product);
      } catch (error) {
        console.error('Failed to load product:', error);
      }
    };
    
    if (id) {
      loadProduct();
    }
  }, [id]);
  
  const handleSave = async () => {
    try {
      await productsAPI.update(id, formData);
      navigate('/inventory');
    } catch (error) {
      console.error('Failed to update product:', error);
    }
  };
};
```

### OCRResultPage.tsx
```typescript
import { ocrAPI } from '../services/api';

const OCRResultPage: React.FC = () => {
  const handleUpload = async () => {
    if (!file) return;
    
    setLoading(true);
    try {
      const response = await ocrAPI.processDocument(file);
      setResult(response.data);
    } catch (error) {
      setError('Error de conexión con el backend OCR');
    } finally {
      setLoading(false);
    }
  };
};
```

## 🔒 Protección de Rutas

### App.tsx con AuthProvider
```typescript
import { AuthProvider } from './contexts/AuthContext';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        {/* ... resto del código ... */}
      </BrowserRouter>
    </AuthProvider>
  );
}
```

### Componente ProtectedRoute
```typescript
import { useAuth } from '../contexts/AuthContext';
import { Navigate } from 'react-router-dom';

const ProtectedRoute: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return <div>Cargando...</div>;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};
```

## 🧪 Testing de la Conexión

### 1. Verificar que el backend esté funcionando
```bash
curl http://localhost:3000/health
```

Respuesta esperada:
```json
{
  "status": "OK",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "uptime": 123.456
}
```

### 2. Probar autenticación
```bash
# Registrar usuario
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "fullName": "Test User"
  }'

# Login
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 3. Probar productos (con token)
```bash
# Obtener productos
curl -X GET http://localhost:3000/api/products \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

## 🚨 Solución de Problemas

### Error: "Cannot connect to database"
- Verificar que PostgreSQL esté corriendo
- Verificar credenciales en `.env`
- Verificar que la base de datos `frontposw` exista

### Error: "CORS error"
- Verificar que `FRONTEND_URL` en `.env` sea correcto
- Verificar que el frontend esté corriendo en el puerto correcto

### Error: "JWT token invalid"
- Verificar que `JWT_SECRET` esté configurado
- Limpiar localStorage del navegador
- Hacer logout y login nuevamente

### Error: "Port already in use"
- Cambiar el puerto en `.env` (PORT=3001)
- Actualizar `API_BASE_URL` en `src/services/api.js`

## 📊 Endpoints Disponibles

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

### Inventario
- `GET /api/inventory` - Listar inventario
- `GET /api/inventory/low-stock` - Productos con stock bajo
- `PUT /api/inventory/:id/stock` - Actualizar stock
- `GET /api/inventory/movements` - Movimientos de inventario

### Ventas
- `GET /api/sales` - Listar ventas
- `POST /api/sales` - Crear venta
- `GET /api/sales/stats/summary` - Estadísticas

### Perfil
- `GET /api/profile` - Obtener perfil
- `PUT /api/profile` - Actualizar perfil
- `PUT /api/profile/password` - Cambiar contraseña

### OCR
- `POST /api/ocr/process-document` - Procesar documento

## 🎉 ¡Listo!

Una vez completados estos pasos, tu aplicación FrontPOSw estará completamente funcional con:

- ✅ Autenticación JWT
- ✅ Gestión de productos
- ✅ Control de inventario
- ✅ Sistema de ventas
- ✅ Perfil de usuario
- ✅ OCR (simulado)
- ✅ Base de datos PostgreSQL
- ✅ API RESTful completa

¡Disfruta tu aplicación de inventario y ventas! 🚀 