# <div align="center"><img src="images/logozato.png" alt="FrontPOSw Logo" width="200"/><br/></div>

<div align="center">
  
  [![Contributors](https://img.shields.io/github/contributors/ZatoBox/main.svg?style=for-the-badge)](https://github.com/ZatoBox/main/graphs/contributors)
  [![Forks](https://img.shields.io/github/forks/ZatoBox/main.svg?style=for-the-badge)](https://github.com/ZatoBox/main/network/members)
  [![Stargazers](https://img.shields.io/github/stars/ZatoBox/main.svg?style=for-the-badge)](https://github.com/ZatoBox/main/stargazers)
  [![Issues](https://img.shields.io/github/issues/ZatoBox/main.svg?style=for-the-badge)](https://github.com/ZatoBox/main/issues)
  [![License](https://img.shields.io/github/license/ZatoBox/main.svg?style=for-the-badge)](https://github.com/ZatoBox/main/blob/master/LICENSE.txt)
  [![Discord](https://img.shields.io/discord/1223295651599507486?label=Discord&logo=discord&style=for-the-badge&color=5865F2)](https://discord.gg/2zUVsv9aMF)
  <br/>
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB"/>
  <img src="https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white"/>
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white"/>
  <img src="https://img.shields.io/badge/Tailwind-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white"/>
  <img src="https://img.shields.io/badge/Express.js-000000?style=for-the-badge&logo=express&logoColor=white"/>
  <img src="https://img.shields.io/badge/Node-v16%2B-brightgreen?style=for-the-badge&logo=node.js"/>
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

**FrontPOSw** is a web solution for inventory and sales management, designed for businesses that need efficient control over products, stock, sales, and users. It features secure authentication, an admin panel, OCR document processing, and a modern, responsive interface.

---

## ✨ Main Features

- JWT Authentication (login, registration, profiles)
- Product management (CRUD, images, variants)
- Inventory control (stock movements, low stock alerts)
- Sales system (processing, history, statistics)
- OCR document processing (simulated)
- User panel and profile configuration
- Documented RESTful API
- PostgreSQL database with Sequelize ORM
- Rate limiting protection
- File upload (product images)
- Modern interface with React and Tailwind CSS

---

## 🛠️ Tech Stack

**Frontend:**
- React
- Vite
- Tailwind CSS
- Context API

**Backend:**
- Node.js
- Express
- Sequelize ORM
- PostgreSQL
- Multer (file upload)
- JWT (authentication)
- Express-validator (validation)
- CORS

---

## 🖼️ Demo / Screenshots

<div align="center">
  <img src="images/screenshot.png" alt="FrontPOSw Screenshot" width="600"/>
</div>

---

## 📋 Prerequisites

- Node.js (v16 or higher)
- PostgreSQL (v12 or higher)
- npm or yarn

---

## ⚡ Installation & Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/ZatoBox/main.git
cd main
```

### 2. Backend Setup

```bash
cd backend
npm install
cp env.example .env
```
Edit `.env` with your PostgreSQL and JWT settings.

Create the database:
```sql
CREATE DATABASE frontposw;
```

Seed the database with sample data:
```bash
npm run seed
```

Start the backend:
```bash
npm run dev
```
Backend will be available at: [http://localhost:3000](http://localhost:3000)

### 3. Frontend Setup

```bash
cd ..
npm install
npm run dev
```
Frontend will be available at: [http://localhost:5173](http://localhost:5173)

---

## 🗂️ Project Structure

```text
main/
│
├── backend/
│   ├── src/
│   │   ├── config/
│   │   ├── middleware/
│   │   ├── models/
│   │   ├── routes/
│   │   └── utils/
│   ├── server.js
│   └── ...
│
├── src/
│   ├── components/
│   ├── contexts/
│   ├── services/
│   ├── App.tsx
│   └── ...
│
├── public/
├── images/
└── ...
```

---

## 🔗 Backend-Frontend Connections

### Ports & Base URLs
| Service   | URL Base                | Port   |
|-----------|-------------------------|--------|
| Backend   | http://localhost:4444   | 4444   |
| Frontend  | http://localhost:5173   | 5173   |

### Authentication Flow
1. User registers → `POST /api/auth/register`
2. User logs in → `POST /api/auth/login` → receives TOKEN
3. With the TOKEN, user can access:
   - Products (full CRUD)
   - Inventory (view & update)
   - Sales (create & view history)
   - Profile (view & update)

**Token usage example in frontend:**
```js
const token = localStorage.getItem('token');
fetch('http://localhost:4444/api/products', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

### Key Endpoints
- **Authentication:** `/api/auth/register`, `/api/auth/login`, `/api/auth/me`, `/api/auth/logout`
- **Products:** `/api/products` (GET, POST, PUT, DELETE)
- **Inventory:** `/api/inventory` (GET, PUT)
- **Sales:** `/api/sales` (GET, POST)
- **Profile:** `/api/profile` (GET, PUT)

### Example Users
- **Admin:** `admin@frontposw.com` / `admin123`
- **User:** `user@frontposw.com` / `user123`

### Run & Check Services
**Start backend:**
```bash
cd backend
node test-server.js
```
**Start frontend:**
```bash
npm run dev
```
**Check backend health:**
- [http://localhost:4444/health](http://localhost:4444/health)
**Check users:**
- [http://localhost:4444/api/users](http://localhost:4444/api/users)
**Check products:**
- [http://localhost:4444/api/products](http://localhost:4444/api/products)
**Check sales:**
- [http://localhost:4444/api/sales](http://localhost:4444/api/sales)

### Troubleshooting
- **Backend logs:** Console where `node test-server.js` runs
- **Frontend logs:** Browser DevTools (F12)
- **Check ports:**
```bash
netstat -ano | findstr "4444"
netstat -ano | findstr "5173"
```

### Security Summary
- **Public endpoints:**
  - `POST /api/auth/register` (register)
  - `POST /api/auth/login` (login)
  - `GET /health` (server health)
- **Private endpoints (require token):**
  - All product, inventory, sales, and profile endpoints
- **Token flow:**
  1. Register/Login → get token
  2. Token saved in localStorage
  3. All private requests include `Authorization: Bearer {token}`
  4. Backend validates token
  5. If invalid → 401 Unauthorized

---

## 🧭 Usage Guide

### Access

- **Admin:**  
  User: `admin@frontposw.com`  
  Password: `admin123`

- **Standard User:**  
  User: `user@frontposw.com`  
  Password: `user123`

### Features

- Log in or register.
- Manage products: create, edit, delete, and upload images.
- Control inventory: view stock, movements, and alerts.
- Make sales and view history.
- Access and update your profile.
- Use the OCR module to process documents (simulated).

---

## 📚 API Documentation

### Authentication
- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Log in
- `POST /api/auth/logout` - Log out
- `GET /api/auth/me` - Get current user

### Products
- `GET /api/products` - List products
- `GET /api/products/:id` - Get product
- `POST /api/products` - Create product
- `PUT /api/products/:id` - Update product
- `DELETE /api/products/:id` - Delete product
- `POST /api/products/:id/images` - Upload images

### Inventory
- `GET /api/inventory` - List inventory
- `GET /api/inventory/low-stock` - Low stock products
- `PUT /api/inventory/:id/stock` - Update stock
- `GET /api/inventory/movements` - Inventory movements
- `POST /api/inventory/bulk-update` - Bulk update

### Sales
- `GET /api/sales` - List sales
- `GET /api/sales/:id` - Get sale
- `POST /api/sales` - Create sale
- `PATCH /api/sales/:id/status` - Update status
- `GET /api/sales/stats/summary` - Statistics

### Profile
- `GET /api/profile` - Get profile
- `PUT /api/profile` - Update profile
- `PUT /api/profile/password` - Change password
- `GET /api/profile/sessions` - Active sessions

### OCR
- `POST /api/ocr/process-document` - Process document
- `GET /api/ocr/history` - Processing history
- `GET /api/ocr/status/:jobId` - Processing status

---

## 🧪 Testing

```bash
# Backend
cd backend
npm test
```

---

## 🚀 Deployment

### Production

1. Set environment variables for production.
2. Install dependencies: `npm install --production`
3. Run migrations: `npm run migrate`
4. Start the server: `npm start`

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

---

## 🤝 Contributing

Contributions are welcome!  
1. Fork the project  
2. Create a branch (`git checkout -b feature/new-feature`)  
3. Commit your changes (`git commit -m 'Add new feature'`)  
4. Push to the branch (`git push origin feature/new-feature`)  
5. Open a Pull Request

---

## 📄 License

MIT License. See [`LICENSE.txt`](https://github.com/ZatoBox/main/blob/master/LICENSE.txt) for more information.

---

## 📬 Contact & Support

For technical support or questions, contact the development team or open an [issue](https://github.com/ZatoBox/main/issues) in the repository.

Join our community on [Discord](https://discord.gg/2zUVsv9aMF)!

---

## 🙏 Acknowledgments

- [React](https://reactjs.org/)
- [Node.js](https://nodejs.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Express](https://expressjs.com/)
- [Sequelize](https://sequelize.org/)
- [Vite](https://vitejs.dev/)
- And all open source libraries and resources used. 
