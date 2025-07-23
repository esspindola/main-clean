# <div align="center"><img src="images/logozato.png" alt="ZatoBox Logo" height="200"/><br/></div>

<div align="center">
  
  [![Contributors](https://img.shields.io/github/contributors/ZatoBox/main.svg?style=for-the-badge)](https://github.com/ZatoBox/main/graphs/contributors)
  [![Forks](https://img.shields.io/github/forks/ZatoBox/main.svg?style=for-the-badge)](https://github.com/ZatoBox/main/network/members)
  [![Stargazers](https://img.shields.io/github/stars/ZatoBox/main.svg?style=for-the-badge)](https://github.com/ZatoBox/main/stargazers)
  [![Issues](https://img.shields.io/github/issues/ZatoBox/main.svg?style=for-the-badge)](https://github.com/ZatoBox/main/issues)
  [![License](https://img.shields.io/github/license/ZatoBox/main.svg?style=for-the-badge)](https://github.com/ZatoBox/main/blob/master/LICENSE.txt)
  [![Discord](https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/2zUVsv9aMF)
  <br/>
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB"/>
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white"/>
  <img src="https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white"/>
  <img src="https://img.shields.io/badge/Express.js-000000?style=for-the-badge&logo=express&logoColor=white"/>
  <img src="https://img.shields.io/badge/Tailwind-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white"/>
  <img src="https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white"/>
</div>

---

<a id="table-of-contents"></a>
## 📑 Table of Contents
- [Table of Contents](#-table-of-contents)
- [Overview](#-overview)
- [Main Features](#-main-features)
- [Tech Stack](#-tech-stack)
- [Demo / Screenshots](#-demo--screenshots)
- [Prerequisites](#-prerequisites)
- [Installation & Getting Started](#-installation--getting-started)
- [Project Structure](#-project-structure)
- [Backend-Frontend Connections](#-backend-frontend-connections)
- [Usage Guide](#-usage-guide)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact & Support](#-contact--support)
- [Acknowledgments](#-acknowledgments)

---

## 📖 Overview

**FrontPOSw** is a modern, full-stack web application for inventory and sales management, designed for businesses that need efficient control over products, stock, sales, and users. It features secure authentication, real-time inventory management, sales processing, OCR document processing, and a responsive interface built with React and TypeScript.

### 🆕 Latest Updates (v2.0)
- ✅ **Enhanced Delete Functionality**: Modal-based confirmation system
- ✅ **Improved Error Handling**: Better API error management and user feedback
- ✅ **Real-time Inventory Updates**: Automatic stock synchronization
- ✅ **Advanced Image Management**: Drag & drop upload with preview
- ✅ **Modern UI/UX**: Responsive design with Tailwind CSS
- ✅ **Comprehensive Logging**: Detailed debugging and monitoring

---

## ✨ Main Features

### 🔐 Authentication & Security
- JWT-based authentication (login, registration, profile management)
- Role-based access control (admin/user)
- Secure token management with localStorage
- Protected routes and API endpoints

### 📦 Product Management
- Complete CRUD operations for products
- Image upload with drag & drop interface
- Product categorization and search
- Stock tracking and management
- Bulk operations support

### 📊 Inventory Control
- Real-time stock monitoring
- Low stock alerts and notifications
- Inventory movement tracking
- Stock adjustment capabilities
- Visual stock status indicators

### 💰 Sales System
- Complete sales processing workflow
- Payment method selection
- Change calculation with quick amount buttons
- Sales history and reporting
- Automatic inventory updates

### 🖼️ Media Management
- Multi-image upload support
- Image preview and validation
- Automatic URL generation
- File type and size validation
- Secure file storage

### 📱 User Interface
- Modern, responsive design
- Dark/light theme support
- Mobile-first approach
- Intuitive navigation
- Real-time feedback and notifications

---

## 🛠️ Tech Stack

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety and development experience
- **Vite** - Fast build tool and development server
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Context API** - State management
- **Lucide React** - Icon library

### Backend
- **Node.js** - Runtime environment
- **Express.js** - Web framework
- **Multer** - File upload handling
- **CORS** - Cross-origin resource sharing
- **JSON Storage** - File-based data persistence
- **JWT** - Authentication tokens

### Development Tools
- **ESLint** - Code linting
- **PostCSS** - CSS processing
- **Autoprefixer** - CSS vendor prefixing

---

## 🖼️ Demo / Screenshots / Video

<div align="center">
  <a href="https://www.youtube.com/watch?v=6Ig0CUW7A8M&t=33s" target="_blank">
    <img src="images/demo.jpg" alt="ZatoBox Screenshot" width="600"/>
  </a>
</div>

---

## 📋 Prerequisites

- **Node.js** (v16 or higher)
- **npm** or **yarn** package manager
- **Modern web browser** (Chrome, Firefox, Safari, Edge)

---

## ⚡ Installation & Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/ZatoBox/main.git
cd main
```

### 2. Install Dependencies

```bash
# Install frontend dependencies
npm install

# Install backend dependencies
cd backend
npm install
cd ..
```

### 3. Start the Backend

```bash
cd backend
<<<<<<< Updated upstream
npm install
cp env.example .env
```
Edit `.env` with your PostgreSQL and JWT settings.

Create the database:
```sql
CREATE DATABASE ZatoBox;
=======
node test-server.js
>>>>>>> Stashed changes
```

The backend will be available at: [http://localhost:4444](http://localhost:4444)

### 4. Start the Frontend

```bash
npm run dev
```

The frontend will be available at: [http://localhost:5173](http://localhost:5173)

### 5. Verify Installation

Check that both services are running:
```bash
# Check backend
curl http://localhost:4444/health

# Check frontend
curl http://localhost:5173
```

---

## 🗂️ Project Structure

```text
FrontPOSw-main/
├── backend/
│   ├── test-server.js          # Main server file
│   ├── users.json              # User data storage
│   ├── uploads/                # File uploads directory
│   │   └── products/           # Product images
│   ├── package.json            # Backend dependencies
│   └── README.md               # Backend documentation
│
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
│   ├── config/                 # Configuration
│   │   └── api.ts              # API configuration
│   └── App.tsx                 # Main app component
│
├── public/                     # Static assets
├── images/                     # Project images
├── package.json                # Frontend dependencies
├── README.md                   # This file
└── docs/                       # Complete documentation
    ├── README.md               # Documentation index
    ├── CONEXIONES_BACKEND_FRONTEND.md      # Spanish technical guide
    ├── CONEXIONES_BACKEND_FRONTEND_ENGLISH.md # English technical guide
    ├── MAQUETADO.md            # Spanish architecture guide
    ├── ARCHITECTURE.md         # English architecture guide
    └── CONNECTION_GUIDE.md     # Quick connection guide
```

---

## 🔗 Backend-Frontend Connections

### Ports & Base URLs
| Service   | URL Base                | Port   | Status |
|-----------|-------------------------|--------|--------|
| Backend   | http://localhost:4444   | 4444   | ✅ Active |
| Frontend  | http://localhost:5173   | 5173   | ✅ Active |

### Authentication Flow
1. **User Registration** → `POST /api/auth/register`
2. **User Login** → `POST /api/auth/login` → receives TOKEN
3. **With TOKEN**, user can access:
   - Products (full CRUD + images)
   - Inventory (view & update)
   - Sales (create & view history)
   - Profile (view & update)

### Default Users
- **Admin:** `admin@frontposw.com` / `admin12345678`
- **User:** `user@frontposw.com` / `user12345678`

### Key Endpoints

#### Public Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /health` - Server health check

#### Protected Endpoints (require token)
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - User logout
- `GET /api/products` - List products
- `POST /api/products` - Create product (with images)
- `PUT /api/products/:id` - Update product
- `DELETE /api/products/:id` - Delete product
- `POST /api/products/:id/images` - Upload images
- `GET /api/inventory` - Get inventory
- `PUT /api/inventory/:id` - Update stock
- `POST /api/sales` - Create sale
- `GET /api/sales` - Get sales history
- `GET /api/profile` - Get user profile
- `PUT /api/profile` - Update profile

### Token Usage Example
```javascript
const token = localStorage.getItem('token');
fetch('http://localhost:4444/api/products', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

### Service Verification
```bash
# Check backend status
netstat -ano | findstr "4444"

# Check frontend status  
netstat -ano | findstr "5173"

# Test backend health
curl http://localhost:4444/health

# Test API endpoints
curl http://localhost:4444/api/users
```

---

## 🧭 Usage Guide

### Quick Start

1. **Access the application**: [http://localhost:5173](http://localhost:5173)
2. **Login with default credentials**:
   - Admin: `admin@frontposw.com` / `admin12345678`
   - User: `user@frontposw.com` / `user12345678`
3. **Explore features**:
   - Dashboard overview
   - Product management
   - Inventory control
   - Sales processing
   - User profile

### Product Management

1. **Create Products**:
   - Navigate to "New Product"
   - Fill in product details
   - Upload images (drag & drop)
   - Set stock and pricing
   - Save product

2. **Edit Products**:
   - Find product in inventory
   - Click edit button
   - Modify details
   - Update images if needed
   - Save changes

3. **Delete Products**:
   - Find product in inventory
   - Click delete button (trash icon)
   - Confirm deletion in modal
   - Product removed from system

### Sales Processing

1. **Create Sale**:
   - Select products from inventory
   - Set quantities
   - Proceed to payment
   - Choose payment method
   - Calculate change
   - Complete transaction

2. **View Sales History**:
   - Access sales drawer
   - View transaction details
   - Filter by date/status
   - Export data if needed

### Inventory Management

1. **Monitor Stock**:
   - View current stock levels
   - Check low stock alerts
   - Track inventory movements
   - Update stock quantities

2. **Stock Adjustments**:
   - Select product
   - Modify stock level
   - Add movement notes
   - Save changes

---

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "fullName": "John Doe",
  "phone": "+1234567890"
}
```

#### Login User
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer {token}
```

### Product Endpoints

#### List Products
```http
GET /api/products
Authorization: Bearer {token}
```

#### Create Product
```http
POST /api/products
Authorization: Bearer {token}
Content-Type: multipart/form-data

{
  "name": "Product Name",
  "description": "Product description",
  "price": 29.99,
  "stock": 100,
  "category": "Electronics",
  "images": [file1, file2, ...]
}
```

#### Update Product
```http
PUT /api/products/:id
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

#### Delete Product
```http
DELETE /api/products/:id
Authorization: Bearer {token}
```

### Sales Endpoints

#### Create Sale
```http
POST /api/sales
Authorization: Bearer {token}
Content-Type: application/json

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
```

#### Get Sales History
```http
GET /api/sales
Authorization: Bearer {token}
```

### Inventory Endpoints

#### Get Inventory
```http
GET /api/inventory
Authorization: Bearer {token}
```

#### Update Stock
```http
PUT /api/inventory/:id
Authorization: Bearer {token}
Content-Type: application/json

{
  "quantity": 95
}
```

---

## 🧪 Testing

### Manual Testing
```bash
# Test backend health
curl http://localhost:4444/health

# Test user registration
curl -X POST http://localhost:4444/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123","fullName":"Test User"}'

# Test product deletion (with token)
curl -X DELETE http://localhost:4444/api/products/1 \
  -H "Authorization: Bearer {your-token}"
```

### Browser Testing
1. Open [http://localhost:5173](http://localhost:5173)
2. Open browser DevTools (F12)
3. Check Console for logs
4. Test all user flows
5. Verify error handling

---

## 🚀 Deployment

### Development
```bash
# Backend
cd backend
node test-server.js

# Frontend
npm run dev
```

### Production Setup
1. **Environment Configuration**:
   ```bash
   # Backend
   cd backend
   cp env.example .env
   # Edit .env with production values
   ```

2. **Build Frontend**:
   ```bash
   npm run build
   ```

3. **Start Production Server**:
   ```bash
   # Backend
   cd backend
   npm start
   
   # Frontend (serve built files)
   npm install -g serve
   serve -s dist -l 5173
   ```

### Docker Deployment
```dockerfile
# Backend Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --production
COPY . .
EXPOSE 4444
CMD ["node", "test-server.js"]
```

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes** and test thoroughly
4. **Commit your changes**:
   ```bash
   git commit -m 'Add amazing feature'
   ```
5. **Push to the branch**:
   ```bash
   git push origin feature/amazing-feature
   ```
6. **Open a Pull Request**

### Development Guidelines
- Follow TypeScript best practices
- Use meaningful commit messages
- Test your changes thoroughly
- Update documentation as needed
- Follow the existing code style

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

---

## 📬 Contact & Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/ZatoBox/main/issues)
- **Discord Community**: [Join our Discord server](https://discord.gg/2zUVsv9aMF)
- **Documentation**: Check the [docs/](docs/) folder for complete technical documentation

---

## 🙏 Acknowledgments

- [React](https://reactjs.org/) - UI framework
- [TypeScript](https://www.typescriptlang.org/) - Type safety
- [Node.js](https://nodejs.org/) - Runtime environment
- [Express](https://expressjs.com/) - Web framework
- [Tailwind CSS](https://tailwindcss.com/) - CSS framework
- [Vite](https://vitejs.dev/) - Build tool
- [Lucide](https://lucide.dev/) - Icon library
- And all the open source contributors and libraries that made this project possible.

---

## 📈 Project Status

- ✅ **Core Features**: Complete
- ✅ **Authentication**: Complete
- ✅ **Product Management**: Complete
- ✅ **Inventory Control**: Complete
- ✅ **Sales System**: Complete
- ✅ **Image Upload**: Complete
- ✅ **Error Handling**: Complete
- ✅ **Documentation**: Complete
- 🔄 **Testing**: In Progress
- 🔄 **Performance Optimization**: In Progress

---

**FrontPOSw** - Modern Inventory & Sales Management System 
