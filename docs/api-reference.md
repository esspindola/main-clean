# 📡 API Reference - ZatoBox v2.0

## 📋 General Information

### Base URL
```
Development: http://localhost:4444
Production: https://api.zatobox.com
```

### Authentication
The API uses **JWT (JSON Web Tokens)** for authentication. Include the token in the `Authorization` header:

```
Authorization: Bearer <your-jwt-token>
```

### Response Format
All responses follow this format:

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful",
  "timestamp": "2025-07-24T00:00:00.000Z"
}
```

### HTTP Status Codes
- `200` - OK: Successful operation
- `201` - Created: Resource created
- `400` - Bad Request: Invalid data
- `401` - Unauthorized: Not authenticated
- `403` - Forbidden: Not authorized
- `404` - Not Found: Resource not found
- `500` - Internal Server Error: Server error

## 🔐 Authentication

### POST /api/auth/login
User login.

**Request Body:**
```json
{
  "email": "admin@frontposw.com",
  "password": "admin12345678"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "1",
      "email": "admin@frontposw.com",
      "fullName": "Administrator",
      "role": "admin"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "message": "Login successful"
}
```

### POST /api/auth/register
Register new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "fullName": "John Doe"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "2",
      "email": "user@example.com",
      "fullName": "John Doe",
      "role": "user"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "message": "User registered successfully"
}
```

### POST /api/auth/logout
Logout.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Logout successful"
}
```

### GET /api/auth/me
Get current user information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "1",
    "email": "admin@frontposw.com",
    "fullName": "Administrator",
    "role": "admin",
    "createdAt": "2025-07-24T00:00:00.000Z"
  }
}
```

## 📦 Products

### GET /api/products
Get product list.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (number): Page number (default: 1)
- `limit` (number): Items per page (default: 10)
- `search` (string): Search by name
- `category` (string): Filter by category
- `status` (string): Filter by status

**Response:**
```json
{
  "success": true,
  "data": {
    "products": [
      {
        "id": 1,
        "name": "Cabinet with Doors",
        "description": "Office cabinet with sliding doors",
        "sku": "CAB-001",
        "category": "Furniture",
        "price": 180,
        "stock": 25,
        "status": "active",
        "images": ["https://picsum.photos/400/300?random=1"],
        "createdAt": "2025-07-24T00:00:00.000Z",
        "updatedAt": "2025-07-24T00:00:00.000Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 1,
      "pages": 1
    }
  }
}
```

### POST /api/products
Create new product.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Request Body (FormData):**
```
name: "New Product"
description: "Product description"
price: 99.99
stock: 10
category: "Electronics"
status: "active"
images: [File1, File2, ...]
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "name": "New Product",
    "description": "Product description",
    "sku": "SKU-2",
    "category": "Electronics",
    "price": 99.99,
    "stock": 10,
    "status": "active",
    "images": ["uploads/products/image1.jpg"],
    "createdAt": "2025-07-24T00:00:00.000Z"
  },
  "message": "Product created successfully"
}
```

### GET /api/products/:id
Get specific product.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Cabinet with Doors",
    "description": "Office cabinet with sliding doors",
    "sku": "CAB-001",
    "category": "Furniture",
    "price": 180,
    "stock": 25,
    "status": "active",
    "images": ["https://picsum.photos/400/300?random=1"],
    "createdAt": "2025-07-24T00:00:00.000Z",
    "updatedAt": "2025-07-24T00:00:00.000Z"
  }
}
```

### PUT /api/products/:id
Update product.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Request Body (FormData):**
```
name: "Updated Product"
description: "Updated description"
price: 199.99
stock: 15
category: "Electronics"
status: "active"
images: [File1, File2, ...]
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Updated Product",
    "description": "Updated description",
    "sku": "CAB-001",
    "category": "Electronics",
    "price": 199.99,
    "stock": 15,
    "status": "active",
    "images": ["uploads/products/updated-image.jpg"],
    "updatedAt": "2025-07-24T00:00:00.000Z"
  },
  "message": "Product updated successfully"
}
```

### DELETE /api/products/:id
Delete product.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Product deleted successfully"
}
```

## 💰 Sales

### GET /api/sales
Get sales list.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (number): Page number
- `limit` (number): Items per page
- `startDate` (string): Start date (ISO)
- `endDate` (string): End date (ISO)
- `status` (string): Filter by status

**Response:**
```json
{
  "success": true,
  "data": {
    "sales": [
      {
        "id": 1,
        "userId": "1",
        "products": [
          {
            "productId": 1,
            "name": "Cabinet with Doors",
            "quantity": 2,
            "price": 180
          }
        ],
        "total": 360,
        "paymentMethod": "credit_card",
        "status": "completed",
        "createdAt": "2025-07-24T00:00:00.000Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 1,
      "pages": 1
    }
  }
}
```

### POST /api/sales
Create new sale.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "products": [
    {
      "productId": 1,
      "quantity": 2
    }
  ],
  "paymentMethod": "credit_card",
  "customerInfo": {
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "userId": "1",
    "products": [
      {
        "productId": 1,
        "name": "Cabinet with Doors",
        "quantity": 2,
        "price": 180
      }
    ],
    "total": 360,
    "paymentMethod": "credit_card",
    "status": "completed",
    "createdAt": "2025-07-24T00:00:00.000Z"
  },
  "message": "Sale created successfully"
}
```

### GET /api/sales/:id
Get specific sale.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "userId": "1",
    "user": {
      "fullName": "Administrator"
    },
    "products": [
      {
        "productId": 1,
        "name": "Cabinet with Doors",
        "quantity": 2,
        "price": 180
      }
    ],
    "total": 360,
    "paymentMethod": "credit_card",
    "status": "completed",
    "createdAt": "2025-07-24T00:00:00.000Z"
  }
}
```

## 📊 Inventory

### GET /api/inventory
Get inventory status.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "totalProducts": 10,
    "lowStockProducts": 3,
    "outOfStockProducts": 1,
    "totalValue": 2500.50,
    "categories": [
      {
        "name": "Furniture",
        "count": 5,
        "value": 1200.00
      }
    ]
  }
}
```

### GET /api/inventory/movements
Get inventory movements.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (number): Page number
- `limit` (number): Items per page
- `productId` (number): Filter by product
- `type` (string): Movement type (in/out)

**Response:**
```json
{
  "success": true,
  "data": {
    "movements": [
      {
        "id": 1,
        "productId": 1,
        "productName": "Cabinet with Doors",
        "type": "out",
        "quantity": 2,
        "reason": "sale",
        "userId": "1",
        "createdAt": "2025-07-24T00:00:00.000Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 1,
      "pages": 1
    }
  }
}
```

### POST /api/inventory/movements
Record inventory movement.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "productId": 1,
  "type": "in",
  "quantity": 10,
  "reason": "restock",
  "notes": "Restock from supplier"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "productId": 1,
    "productName": "Cabinet with Doors",
    "type": "in",
    "quantity": 10,
    "reason": "restock",
    "userId": "1",
    "createdAt": "2025-07-24T00:00:00.000Z"
  },
  "message": "Inventory movement recorded"
}
```

## 🔍 OCR

### POST /api/ocr/upload
Upload document for OCR processing.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Request Body (FormData):**
```
document: [File]
type: "invoice" | "receipt" | "document"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "jobId": "ocr-job-123",
    "status": "processing",
    "estimatedTime": 30
  },
  "message": "Document uploaded for processing"
}
```

### GET /api/ocr/status/:jobId
Get OCR processing status.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "jobId": "ocr-job-123",
    "status": "completed",
    "progress": 100,
    "result": {
      "text": "Extracted text from document",
      "data": {
        "total": 150.00,
        "items": [
          {
            "name": "Product 1",
            "quantity": 2,
            "price": 75.00
          }
        ]
      }
    }
  }
}
```

### GET /api/ocr/history
Get OCR history.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (number): Page number
- `limit` (number): Items per page
- `status` (string): Filter by status

**Response:**
```json
{
  "success": true,
  "data": {
    "history": [
      {
        "id": 1,
        "jobId": "ocr-job-123",
        "filename": "invoice.pdf",
        "type": "invoice",
        "status": "completed",
        "createdAt": "2025-07-24T00:00:00.000Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 1,
      "pages": 1
    }
  }
}
```

## 🔌 Plugins

### GET /api/plugins
Get available plugins list.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "plugins": [
      {
        "id": "smart-inventory",
        "name": "Smart Inventory",
        "description": "AI-powered inventory management",
        "version": "1.0.0",
        "isActive": true,
        "settings": {
          "aiEnabled": true,
          "predictionDays": 30
        }
      }
    ]
  }
}
```

### POST /api/plugins/:id/toggle
Activate/deactivate plugin.

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "isActive": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "smart-inventory",
    "isActive": true
  },
  "message": "Plugin toggled successfully"
}
```

## 🏥 Health Checks

### GET /health
Basic system health check.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-07-24T00:00:00.000Z",
  "version": "2.0.0",
  "uptime": 3600
}
```

### GET /api/health
Detailed API health check.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-07-24T00:00:00.000Z",
  "version": "2.0.0",
  "services": {
    "database": "ok",
    "fileSystem": "ok",
    "plugins": "ok"
  },
  "uptime": 3600,
  "memory": {
    "used": "45.2 MB",
    "total": "512 MB"
  }
}
```

## 🚨 Error Codes

### Common Errors

**400 - Bad Request**
```json
{
  "success": false,
  "error": "VALIDATION_ERROR",
  "message": "Invalid input data",
  "details": {
    "email": "Invalid email format",
    "password": "Password must be at least 8 characters"
  }
}
```

**401 - Unauthorized**
```json
{
  "success": false,
  "error": "AUTHENTICATION_ERROR",
  "message": "Invalid or expired token"
}
```

**403 - Forbidden**
```json
{
  "success": false,
  "error": "AUTHORIZATION_ERROR",
  "message": "Insufficient permissions"
}
```

**404 - Not Found**
```json
{
  "success": false,
  "error": "NOT_FOUND",
  "message": "Resource not found"
}
```

**500 - Internal Server Error**
```json
{
  "success": false,
  "error": "INTERNAL_ERROR",
  "message": "An unexpected error occurred"
}
```

## 📝 Usage Examples

### JavaScript/Node.js
```javascript
const axios = require('axios');

const api = axios.create({
  baseURL: 'http://localhost:4444',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});

// Login
const login = async (email, password) => {
  const response = await api.post('/api/auth/login', {
    email,
    password
  });
  return response.data;
};

// Get products
const getProducts = async () => {
  const response = await api.get('/api/products');
  return response.data;
};

// Create product
const createProduct = async (productData) => {
  const formData = new FormData();
  Object.keys(productData).forEach(key => {
    formData.append(key, productData[key]);
  });
  
  const response = await api.post('/api/products', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  return response.data;
};
```

### cURL
```bash
# Login
curl -X POST http://localhost:4444/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@frontposw.com","password":"admin12345678"}'

# Get products (with token)
curl -X GET http://localhost:4444/api/products \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Create product
curl -X POST http://localhost:4444/api/products \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "name=New Product" \
  -F "price=99.99" \
  -F "stock=10" \
  -F "images=@product-image.jpg"
```

---

**ZatoBox v2.0 API** - Complete documentation 📡

*For more information, consult the development documentation.* 