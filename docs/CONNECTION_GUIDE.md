# ZatoBox - Connection Guide v2.0

## 📋 Quick Start Guide

This guide will help you set up and run the ZatoBox application locally.

---

## 🚀 Prerequisites

- **Node.js** (v16 or higher)
- **npm** or **yarn** package manager
- **Modern web browser** (Chrome, Firefox, Safari, Edge)

---

## ⚡ Installation Steps

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/ZatoBox/main.git
cd main

# Install frontend dependencies
npm install

# Install backend dependencies
cd backend
npm install
cd ..
```

### 2. Start the Backend

```bash
cd backend
node test-server.js
```

**Backend will be available at**: http://localhost:4444

### 3. Start the Frontend

```bash
npm run dev
```

**Frontend will be available at**: http://localhost:5173

---

## 🔍 Verification

### Check Services Status

```bash
# Check if backend is running
curl http://localhost:4444/health

# Check if frontend is running
curl http://localhost:5173

# Check ports in use
netstat -ano | findstr "4444"
netstat -ano | findstr "5173"
```

### Expected Responses

**Backend Health Check:**
```json
{
  "status": "ok",
  "message": "ZatoBox Backend is running",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Frontend:**
- Should return the React application HTML

---

## 🔐 Default Users

### Admin User
- **Email**: `admin@zatobox.com`
- **Password**: `admin12345678`
- **Role**: Administrator

### Standard User
- **Email**: `user@zatobox.com`
- **Password**: `user12345678`
- **Role**: User

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
netstat -ano | findstr "4444"
netstat -ano | findstr "5173"

# Kill the process if needed
taskkill /PID <process_id> /F
```

#### 2. Backend Not Starting
```bash
# Check if all dependencies are installed
cd backend
npm install

# Check for errors in console
node test-server.js
```

#### 3. Frontend Not Loading
```bash
# Clear cache and reinstall
rm -rf node_modules
npm install
npm run dev
```

#### 4. CORS Errors
- Backend is configured to allow all localhost ports
- Check that backend is running on port 4444
- Verify frontend is accessing the correct backend URL

#### 5. Authentication Issues
- Clear browser localStorage
- Check that token is being saved correctly
- Verify backend is responding to auth endpoints

---

## 📊 API Endpoints Reference

### Public Endpoints (No Auth Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Server health check |
| POST | `/api/auth/register` | User registration |
| POST | `/api/auth/login` | User login |

### Protected Endpoints (Auth Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/auth/me` | Get current user |
| POST | `/api/auth/logout` | User logout |
| GET | `/api/products` | List products |
| POST | `/api/products` | Create product |
| PUT | `/api/products/:id` | Update product |
| DELETE | `/api/products/:id` | Delete product |
| GET | `/api/inventory` | Get inventory |
| PUT | `/api/inventory/:id` | Update stock |
| POST | `/api/sales` | Create sale |
| GET | `/api/sales` | Get sales history |
| GET | `/api/profile` | Get user profile |
| PUT | `/api/profile` | Update profile |

---

## 🔧 Development Commands

### Backend Development
```bash
cd backend
node test-server.js
```

### Frontend Development
```bash
npm run dev
```

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

---

## 📁 Project Structure

```
ZatoBox-main/
├── backend/
│   ├── test-server.js          # Main server file
│   ├── users.json              # User data storage
│   ├── uploads/                # File uploads directory
│   │   └── products/           # Product images
│   └── package.json            # Backend dependencies
├── src/
│   ├── components/             # React components
│   │   ├── HomePage.tsx        # Main dashboard
│   │   ├── InventoryPage.tsx   # Product management
│   │   ├── LoginPage.tsx       # Authentication
│   │   ├── NewProductPage.tsx  # Product creation
│   │   ├── EditProductPage.tsx # Product editing
│   │   ├── PaymentScreen.tsx   # Sales processing
│   │   └── ...                 # Other components
│   ├── contexts/               # React contexts
│   │   └── AuthContext.tsx     # Authentication context
│   ├── services/               # API services
│   │   └── api.ts              # API client
│   └── App.tsx                 # Main app component
├── public/                     # Static assets
├── package.json                # Frontend dependencies
└── README.md                   # Main documentation
```

---

## 🆕 New Features v2.0

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

## 🔒 Security Features

### Authentication
- **JWT tokens** for session management
- **Token validation** on all protected endpoints
- **Automatic logout** on token expiration
- **Secure token storage** in localStorage

### File Upload Security
- **File type validation** (images only)
- **File size limits** (5MB maximum)
- **Unique filename generation**
- **Authentication required** for uploads

### API Security
- **CORS configuration** for development
- **Input validation** on all endpoints
- **Error handling** without exposing internals
- **Rate limiting** protection

---

## 📈 Performance Features

### Frontend Optimizations
- **React 18** with concurrent features
- **Vite** for fast development and building
- **Code splitting** for better loading times
- **Optimized images** with lazy loading

### Backend Optimizations
- **JSON file storage** for simplicity
- **Static file serving** for images
- **Efficient data structures**
- **Minimal dependencies**

---

## 🧪 Testing

### Manual Testing Checklist

#### Authentication
- [ ] User registration works
- [ ] User login works
- [ ] Token persistence on page reload
- [ ] Logout clears session

#### Product Management
- [ ] Create product with images
- [ ] Edit product details
- [ ] Delete product with confirmation
- [ ] View product list

#### Sales System
- [ ] Add products to cart
- [ ] Process payment
- [ ] Calculate change correctly
- [ ] Update inventory automatically

#### Inventory Management
- [ ] View current stock
- [ ] Update stock quantities
- [ ] Low stock alerts
- [ ] Stock movement tracking

### API Testing

```bash
# Test backend health
curl http://localhost:4444/health

# Test user registration
curl -X POST http://localhost:4444/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123","fullName":"Test User"}'

# Test product creation (with token)
curl -X POST http://localhost:4444/api/products \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: multipart/form-data" \
  -F "name=Test Product" \
  -F "price=29.99" \
  -F "stock=100"
```

---

## 🚀 Deployment

### Development Environment
```bash
# Backend
cd backend
node test-server.js

# Frontend
npm run dev
```

### Production Environment
```bash
# Build frontend
npm run build

# Serve static files
npm install -g serve
serve -s dist -l 5173

# Backend (with PM2 or similar)
cd backend
npm install -g pm2
pm2 start test-server.js
```

### Environment Variables
```bash
# Backend (.env)
PORT=4444
JWT_SECRET=your-secret-key
CORS_ORIGIN=http://localhost:5173

# Frontend (.env)
VITE_API_URL=http://localhost:4444
```

---

## 📞 Support

### Getting Help
1. **Check the documentation**: README.md and connection guides
2. **Review error logs**: Browser console and backend terminal
3. **Test endpoints**: Use curl or Postman
4. **Create an issue**: GitHub issues page

### Common Solutions
- **Clear browser cache** and localStorage
- **Restart both services** (backend and frontend)
- **Check port availability** and firewall settings
- **Verify Node.js version** (v16+ required)

---

## 📝 Changelog

### v2.0 (Current)
- ✅ Enhanced delete system with modal confirmation
- ✅ Complete sales system with inventory sync
- ✅ Image upload with drag & drop
- ✅ Improved error handling and logging
- ✅ Modern UI/UX with Tailwind CSS

### v1.0
- ✅ Basic authentication system
- ✅ Product CRUD operations
- ✅ Simple inventory management
- ✅ Basic sales processing

---

**ZatoBox v2.0** - Modern Inventory & Sales Management System

For detailed technical information, see:
- [CONEXIONES_BACKEND_FRONTEND.md](CONEXIONES_BACKEND_FRONTEND.md) (Spanish)
- [CONEXIONES_BACKEND_FRONTEND_ENGLISH.md](CONEXIONES_BACKEND_FRONTEND_ENGLISH.md) (English) 