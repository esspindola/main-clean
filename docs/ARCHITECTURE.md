# ZatoBox - Backend-Frontend Architecture and Connections

## 🏗️ General System Architecture

### ZatoBox v2.0
- **Type**: Full-Stack Application
- **Backend**: Node.js + Express
- **Frontend**: React + TypeScript + Vite
- **Database**: JSON Files (users.json, products.json)
- **Authentication**: JWT Tokens
- **Ports**: Backend (4444), Frontend (5173)

---

## 🔧 Backend Architecture

### 📁 Backend File Structure
- **test-server.js** (Main File)
  - Express Server
  - CORS Configuration
  - Authentication Middleware
  - API Endpoints
  - File Handling

### 🔐 Backend Authentication System
- **JWT Token Management**
  - Token generation
  - Token validation
  - Authentication middleware
- **User Management**
  - User registration
  - Login/Logout
  - User profiles
  - Roles (admin/user)

### 📊 Data Persistence
- **users.json**
  - Registered user data
  - Profile information
  - Roles and permissions
- **In-Memory Products**
  - Temporary storage
  - Frontend synchronization
- **Image Files**
  - uploads/products/
  - Unique generated names
  - Type validation

### 🌐 Network Configuration
- **CORS Configuration**
  - Allowed origins
  - HTTP methods
  - Authorized headers
- **Port**: 4444
- **Protocol**: HTTP

---

## 🎨 Frontend Architecture

### 📁 Frontend File Structure
- **src/**
  - **components/** (React Components)
  - **contexts/** (State Contexts)
  - **services/** (API Services)
  - **config/** (Configuration)
  - **App.tsx** (Main Component)

### 🔄 Frontend Global State
- **AuthContext**
  - Authentication state
  - Token management
  - User data
  - Login/Logout functions
- **PluginContext**
  - Plugin state
  - Configurations

### 🛣️ Frontend Routing
- **React Router**
  - Protected routes
  - Dynamic navigation
  - Sidebar integration

---

## 🔗 Backend-Frontend Connections

### 🌐 HTTP Communication
- **Base URL**: http://localhost:4444
- **Protocol**: REST API
- **Content-Type**: application/json
- **Authentication**: Bearer Token

### 📡 Data Flow
```
Frontend → HTTP Request → Backend
Backend → JSON Response → Frontend
```

### 🔐 Authentication Flow
```
1. Frontend: Login/Register Request
2. Backend: Validate & Generate Token
3. Backend: Return Token + User Data
4. Frontend: Store Token (localStorage)
5. Frontend: Include Token in Headers
6. Backend: Validate Token on Protected Routes
```

---

## 📋 API Endpoints

### 🔓 Public Endpoints
- **POST /api/auth/register**
  - User registration
  - Data validation
  - Token generation
- **POST /api/auth/login**
  - User authentication
  - Credential validation
  - Token return
- **GET /health**
  - Server health check
  - System status

### 🔒 Protected Endpoints
- **GET /api/auth/me**
  - Get current user
  - Token validation
- **POST /api/auth/logout**
  - Logout
  - Token invalidation

### 📦 Product Endpoints
- **GET /api/products**
  - List products
  - Filters and pagination
- **POST /api/products**
  - Create product
  - Image upload
- **PUT /api/products/:id**
  - Update product
  - Modify images
- **DELETE /api/products/:id**
  - Delete product
  - Confirmation modal

### 📊 Inventory Endpoints
- **GET /api/inventory**
  - Get inventory
  - Current stock
- **PUT /api/inventory/:id**
  - Update stock
  - Inventory movements

### 💰 Sales Endpoints
- **POST /api/sales**
  - Create sale
  - Stock validation
  - Automatic update
- **GET /api/sales**
  - Sales history
  - Statistics

### 👤 Profile Endpoints
- **GET /api/profile**
  - Get profile
  - User data
- **PUT /api/profile**
  - Update profile
  - Modify information

---

## 🖼️ Image System

### 📤 Image Upload
- **Multer Configuration**
  - Disk storage
  - Unique names
  - Type validation
  - Size limit (5MB)
- **Allowed Types**
  - JPEG, JPG, PNG, GIF, WebP
- **File Structure**
  - uploads/products/
  - Names: product-timestamp-random.ext

### 🌐 Serve Images
- **Static File Serving**
  - Express.static middleware
  - URL: /uploads/products/filename
- **Frontend Integration**
  - URL construction
  - Image fallback
  - Upload preview

---

## 🔄 Main Data Flows

### 📦 Product Management
```
1. Frontend: Form Data + Images
2. Backend: Validate & Store
3. Backend: Save Images
4. Backend: Return Product Data
5. Frontend: Update UI
6. Frontend: Show Success/Error
```

### 💰 Sales Process
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

### 🗑️ Product Deletion
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

## 🛡️ Security and Validation

### 🔐 Authentication
- **JWT Tokens**
  - Secure generation
  - Validation on each request
  - Automatic expiration
- **Auth Middleware**
  - Token verification
  - User data extraction
  - Error handling

### ✅ Data Validation
- **Frontend Validation**
  - Form validation
  - File type checking
  - Required fields
- **Backend Validation**
  - Input sanitization
  - Type checking
  - Business logic validation

### 🛡️ CORS Security
- **Allowed Origins**
  - localhost:5173-5183
  - 127.0.0.1:5173-5183
- **HTTP Methods**
  - GET, POST, PUT, DELETE, PATCH
- **Headers**
  - Content-Type, Authorization

---

## 📱 Frontend Components

### 🏠 Main Pages
- **HomePage**
  - Main dashboard
  - Sales summary
  - Quick access
- **InventoryPage**
  - Product list
  - CRUD operations
  - Filters and search
- **NewProductPage**
  - Creation form
  - Image upload
  - Real-time validation
- **EditProductPage**
  - Product editing
  - Image modification
  - Data updates

### 🔐 Authentication Pages
- **LoginPage**
  - Login form
  - Credential validation
  - Error handling
- **RegisterPage**
  - User registration
  - Data validation
  - Password confirmation

### 💰 Sales Pages
- **PaymentScreen**
  - Payment processing
  - Change calculator
  - Payment methods
- **SalesDrawer**
  - Sales history
  - Date filters
  - Transaction details

### 👤 User Pages
- **ProfilePage**
  - User information
  - Profile editing
  - Settings
- **SideMenu**
  - Main navigation
  - User menu
  - Logout

---

## 🔧 Services and Utilities

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

## 📊 Application State

### 🔄 Main States
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

### 💾 Local Persistence
- **localStorage**
  - JWT token
  - User preferences
  - Cart data
- **Session Storage**
  - Temporary data
  - Form state

---

## 🚀 Deployment and Configuration

### 🔧 Environment Variables
- **Backend**
  - PORT=4444
  - JWT_SECRET
  - CORS_ORIGINS
- **Frontend**
  - VITE_API_URL
  - VITE_APP_NAME

### 📦 Deployment Scripts
- **Development**
  - Backend: `node test-server.js`
  - Frontend: `npm run dev`
- **Production**
  - Backend: `npm start`
  - Frontend: `npm run build`

### 🌐 Network Configuration
- **Development**
  - Backend: localhost:4444
  - Frontend: localhost:5173
- **Production**
  - Backend: domain.com:4444
  - Frontend: domain.com

---

## 🔍 Monitoring and Debugging

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

## 📈 Metrics and Performance

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

## 🔮 Roadmap and Improvements

### 🚀 Upcoming Features
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

### 🔧 Technical Improvements
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

## 📚 Related Documentation

### 📖 Documentation Files
- **README.md** - Main documentation
- **CONEXIONES_BACKEND_FRONTEND.md** - Technical guide in Spanish
- **CONEXIONES_BACKEND_FRONTEND_ENGLISH.md** - Technical guide in English
- **CONNECTION_GUIDE.md** - Quick connection guide
- **MAQUETADO.md** - Architecture guide in Spanish

### 🔗 Useful Links
- **GitHub Repository**: https://github.com/ZatoBox/main
- **Discord Community**: https://discord.gg/2zUVsv9aMF
- **Issue Tracker**: https://github.com/ZatoBox/main/issues

---

## 🎯 Key Features v2.0

### 🗑️ Enhanced Delete System
- **Modal confirmation** instead of browser confirm
- **Loading states** during deletion
- **Visual feedback** with colors and messages
- **Error prevention** with disabled buttons

### 💰 Complete Sales System
- **Stock validation** before creating sales
- **Automatic inventory updates**
- **Change calculator** with quick amount buttons
- **Sales history** tracking

### 🖼️ Image Upload System
- **Drag & drop** interface
- **Multiple format support** (JPG, PNG, GIF, WebP)
- **File validation** (type and size)
- **Image preview** before upload

### 🔧 Improved Error Handling
- **Detailed logging** for debugging
- **User-friendly error messages**
- **Robust validation** in backend and frontend

---

## 🔄 Data Synchronization

### 📊 Real-time Updates
- **Automatic inventory sync** after sales
- **Stock validation** in real-time
- **Complete response** with updated products
- **Error handling** with automatic rollback

### 🔄 State Management
- **Context API** for global state
- **Local storage** for persistence
- **Session management** for temporary data
- **Error boundaries** for fault tolerance

---

## 🛠️ Development Workflow

### 🔧 Development Environment
- **Hot reload** for frontend development
- **Live server** for backend testing
- **CORS configuration** for cross-origin requests
- **Error logging** for debugging

### 📦 Build Process
- **Vite** for fast frontend builds
- **Node.js** for backend execution
- **TypeScript** for type safety
- **ESLint** for code quality

### 🧪 Testing Strategy
- **Manual testing** for user flows
- **API testing** with curl/Postman
- **Browser testing** for UI components
- **Error testing** for edge cases

---

## 📊 System Metrics

### 📈 Current Statistics
- **React Components**: 15+
- **API Endpoints**: 20+
- **Main Features**: 8
- **Configuration Files**: 5
- **Documentation**: 4 languages (ES, EN, Technical, Architecture)

### 🎯 Achieved Goals
- ✅ **Modern Interface**: Responsive design with Tailwind CSS
- ✅ **Secure Authentication**: JWT with robust validation
- ✅ **Product Management**: Complete CRUD with images
- ✅ **Sales System**: Complete flow with validations
- ✅ **Smart Inventory**: Automatic updates
- ✅ **Error Handling**: Clear user feedback
- ✅ **Complete Documentation**: Detailed technical guides

---

**ZatoBox v2.0** - Complete Architecture of Inventory and Sales Management System 