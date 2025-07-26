# BACKEND-FRONTEND CONNECTIONS - ZatoBox v2.0

## 📋 CONNECTION SUMMARY

### Backend (Port 4444)
- **Base URL**: http://localhost:4444
- **File**: `backend/test-server.js`
- **Persistence**: JSON file (`backend/users.json`)
- **Image Storage**: `backend/uploads/products/`
- **Status**: ✅ Running with improved validations

### Frontend (Port 5173)
- **Base URL**: http://localhost:5173
- **Framework**: React + TypeScript + Vite
- **Auth Context**: `src/contexts/AuthContext.tsx`
- **Status**: ✅ Running with implemented improvements

---

## 🔐 AUTHENTICATION SYSTEM

### Backend Authentication Middleware
```javascript
// backend/test-server.js - Lines 406-430
function authenticateToken(req, res, next) {
  const token = req.headers.authorization?.replace('Bearer ', '');
  
  if (!token) {
    return res.status(401).json({ 
      success: false, 
      message: 'No token provided' 
    });
  }
  
  // Extract user ID from token (format: test-token-{id}-{timestamp})
  const tokenParts = token.split('-');
  if (tokenParts.length >= 3) {
    const userId = parseInt(tokenParts[2]);
    const user = registeredUsers.find(u => u.id === userId);
    
    if (user) {
      req.user = user;
      return next();
    }
  }
  
  res.status(401).json({ 
    success: false, 
    message: 'Invalid token' 
  });
}
```

### Frontend Token Usage
```typescript
// Example from NewProductPage.tsx - Lines 295-305
const token = localStorage.getItem('token');

const response = await fetch('http://localhost:4444/api/products', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formDataToSend
});
```

---

## 📦 PRODUCT MANAGEMENT - DETAILED ENDPOINTS

### 1. CREATE PRODUCT (POST /api/products)

**Backend Implementation:**
```javascript
// backend/test-server.js - Lines 450-490
app.post('/api/products', authenticateToken, productImageUpload.array('images', 5), async (req, res) => {
  console.log('Create product request:', req.body);
  
  const { name, description, sku, category, price, stock } = req.body;
  
  if (!name || !price) {
    return res.status(400).json({
      success: false,
      message: 'Name and price are required'
    });
  }
  
  const newProduct = {
    id: nextProductId++,
    name,
    description: description || '',
    sku: sku || `SKU-${nextProductId}`,
    category: category || 'General',
    price: parseFloat(price),
    stock: parseInt(stock) || 0,
    status: 'active'
  };

  if (req.files && req.files.length > 0) {
    newProduct.images = req.files.map(file => `/uploads/products/${file.filename}`);
  }
  
  products.push(newProduct);
  
  console.log('Product created:', newProduct);
  res.json({
    success: true,
    message: 'Product created successfully',
    product: newProduct
  });
});
```

**Frontend Implementation:**
```typescript
// frontend/src/components/NewProductPage.tsx - Lines 265-330
const handleSave = async () => {
  if (!isAuthenticated) {
    setError('You must log in to create products');
    return;
  }

  if (!formData.name || !formData.price) {
    setError('Name and price are required');
    return;
  }

  try {
    setLoading(true);
    setError(null);

    // Create FormData for multipart/form-data request
    const formDataToSend = new FormData();
    formDataToSend.append('name', formData.name);
    formDataToSend.append('description', formData.description);
    formDataToSend.append('price', formData.price);
    formDataToSend.append('stock', (parseInt(formData.inventoryQuantity) || 0).toString());
    formDataToSend.append('category', selectedCategories[0] || 'General');
    if (formData.sku) {
      formDataToSend.append('sku', formData.sku);
    }

    // Add images to FormData
    selectedFiles.forEach((file) => {
      formDataToSend.append('images', file);
    });

    const token = localStorage.getItem('token');

    const response = await fetch('http://localhost:4444/api/products', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formDataToSend
    });

    const result = await response.json();
    
    if (result.success) {
      navigate('/inventory');
    } else {
      setError(result.message || 'Error creating product');
    }
  } catch (err) {
    setError('Error creating product');
  } finally {
    setLoading(false);
  }
};
```

### 2. LIST PRODUCTS (GET /api/products)

**Backend Implementation:**
```javascript
// backend/test-server.js - Lines 432-438
app.get('/api/products', authenticateToken, (req, res) => {
  console.log('Products requested by user:', req.user.email);
  res.json({
    success: true,
    products: products
  });
});
```

### 3. UPDATE PRODUCT (PUT /api/products/:id)

**Backend Implementation:**
```javascript
// backend/test-server.js - Lines 500-540
app.put('/api/products/:id', authenticateToken, productImageUpload.array('images', 5), (req, res) => {
  const productId = parseInt(req.params.id);
  console.log('Update product request:', productId, req.body);
  
  const productIndex = products.findIndex(p => p.id === productId);
  
  if (productIndex === -1) {
    return res.status(404).json({
      success: false,
      message: 'Product not found'
    });
  }
  
  const { name, description, sku, category, price, stock } = req.body;
  
  products[productIndex] = {
    ...products[productIndex],
    name: name || products[productIndex].name,
    description: description || products[productIndex].description,
    sku: sku || products[productIndex].sku,
    category: category || products[productIndex].category,
    price: price ? parseFloat(price) : products[productIndex].price,
    stock: stock ? parseInt(stock) : products[productIndex].stock
  };

  // Handle image uploads
  if (req.files && req.files.length > 0) {
    products[productIndex].images = req.files.map(file => `/uploads/products/${file.filename}`);
  }
  
  console.log('Product updated:', products[productIndex]);
  res.json({
    success: true,
    message: 'Product updated successfully',
    product: products[productIndex]
  });
});
```

### 4. DELETE PRODUCT (DELETE /api/products/:id)

**Backend Implementation:**
```javascript
// backend/test-server.js - Lines 542-570
app.delete('/api/products/:id', authenticateToken, (req, res) => {
  const productId = parseInt(req.params.id);
  console.log('=== DELETE PRODUCT REQUEST ===');
  console.log('Product ID:', productId);
  console.log('User:', req.user.email);
  
  const productIndex = products.findIndex(p => p.id === productId);
  
  if (productIndex === -1) {
    return res.status(404).json({
      success: false,
      message: 'Product not found'
    });
  }
  
  const deletedProduct = products.splice(productIndex, 1)[0];
  
  console.log('Product deleted:', deletedProduct);
  res.json({
    success: true,
    message: 'Product deleted successfully',
    product: deletedProduct
  });
});
```

---

## 🖼️ IMAGE UPLOAD SYSTEM

### Backend Multer Configuration
```javascript
// backend/test-server.js - Lines 100-130
const productImageStorage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = 'uploads/products';
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, 'product-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const productImageUpload = multer({
  storage: productImageStorage,
  limits: {
    fileSize: 5 * 1024 * 1024 // 5MB limit for product images
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = /jpeg|jpg|png|gif|webp/;
    const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = allowedTypes.test(file.mimetype);
    
    if (mimetype && extname) {
      return cb(null, true);
    } else {
      cb(new Error('Only image files are allowed!'));
    }
  }
});
```

### Frontend Image Handling
```typescript
// frontend/src/components/ProductCard.tsx - Image URL building
const getImageUrl = () => {
  if (product.image) {
    // If image already has http, use it as is
    if (product.image.startsWith('http')) {
      return product.image;
    }
    // If it's a relative URL, build the complete URL
    return `http://localhost:4444${product.image}`;
  }
  if (product.images && product.images.length > 0) {
    const imageUrl = product.images[0];
    if (imageUrl.startsWith('http')) {
      return imageUrl;
    }
    return `http://localhost:4444${imageUrl}`;
  }
  return null;
};
```

---

## 💰 SALES SYSTEM

### Create Sale (POST /api/sales)

**Backend Implementation:**
```javascript
// backend/test-server.js - Lines 620-700
app.post('/api/sales', authenticateToken, (req, res) => {
  console.log('Create sale request:', req.body);
  
  const { items, total, paymentMethod } = req.body;
  
  if (!items || !Array.isArray(items) || items.length === 0) {
    return res.status(400).json({
      success: false,
      message: 'Items array is required and cannot be empty'
    });
  }
  
  if (!total || total <= 0) {
    return res.status(400).json({
      success: false,
      message: 'Total must be greater than 0'
    });
  }
  
  try {
    // Check available stock and update inventory
    const updatedProducts = [];
    
    for (const item of items) {
      const product = products.find(p => p.id === item.productId);
      
      if (!product) {
        return res.status(404).json({
          success: false,
          message: `Product with ID ${item.productId} not found`
        });
      }
      
      if (product.stock < item.quantity) {
        return res.status(400).json({
          success: false,
          message: `Insufficient stock for product "${product.name}". Available: ${product.stock}, Requested: ${item.quantity}`
        });
      }
      
      // Update product stock
      product.stock -= item.quantity;
      updatedProducts.push(product);
    }
    
    // Create the sale
    const sale = {
      id: Date.now(),
      items: items.map(item => {
        const product = products.find(p => p.id === item.productId);
        return {
          productId: item.productId,
          productName: product.name,
          quantity: item.quantity,
          price: item.price
        };
      }),
      total: total,
      paymentMethod: paymentMethod || 'cash',
      status: 'completed',
      createdAt: new Date().toISOString(),
      userId: req.user.id
    };
    
    console.log('Sale created successfully:', sale);
    console.log('Updated products:', updatedProducts.map(p => ({ id: p.id, name: p.name, newStock: p.stock })));
    
    res.json({
      success: true,
      message: 'Sale created successfully',
      sale: sale,
      updatedProducts: updatedProducts
    });
    
  } catch (error) {
    console.error('Error creating sale:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error while creating sale'
    });
  }
});
```

---

## 🔐 AUTHENTICATION ENDPOINTS

### Register User (POST /api/auth/register)
```javascript
// backend/test-server.js - Lines 150-200
app.post('/api/auth/register', (req, res) => {
  const { email, password, fullName, phone } = req.body;
  
  // Validate required fields
  if (!email || !password || !fullName) {
    return res.status(400).json({ 
      success: false, 
      message: 'Email, password, and fullName are required' 
    });
  }
  
  // Validate email format
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return res.status(400).json({ 
      success: false, 
      message: 'Invalid email format' 
    });
  }
  
  // Validate password length
  if (password.length < 8) {
    return res.status(400).json({ 
      success: false, 
      message: 'Password must be at least 8 characters long' 
    });
  }
  
  // Check if email already exists
  const existingUser = registeredUsers.find(user => user.email === email);
  if (existingUser) {
    return res.status(400).json({ 
      success: false, 
      message: 'Email already registered' 
    });
  }
  
  // Create new user
  const newUser = {
    id: nextUserId++,
    email,
    password,
    fullName,
    role: 'user',
    phone: phone || '',
    address: ''
  };
  
  registeredUsers.push(newUser);
  saveUsers(registeredUsers);
  
  // Generate token
  const token = `test-token-${newUser.id}-${Date.now()}`;
  
  res.json({
    success: true,
    message: 'User registered successfully',
    user: {
      id: newUser.id,
      email: newUser.email,
      fullName: newUser.fullName,
      role: newUser.role
    },
    token: token
  });
});
```

### Login User (POST /api/auth/login)
```javascript
// backend/test-server.js - Lines 200-250
app.post('/api/auth/login', (req, res) => {
  const { email, password } = req.body;
  
  if (!email || !password) {
    return res.status(400).json({ 
      success: false, 
      message: 'Email and password are required' 
    });
  }
  
  const user = registeredUsers.find(u => u.email === email && u.password === password);
  
  if (!user) {
    return res.status(401).json({ 
      success: false, 
      message: 'Invalid email or password' 
    });
  }
  
  const token = `test-token-${user.id}-${Date.now()}`;
  
  res.json({
    success: true,
    message: 'Login successful',
    token: token,
    user: {
      id: user.id,
      email: user.email,
      fullName: user.fullName,
      role: user.role
    }
  });
});
```

---

## 🛠️ DEPLOYMENT COMMANDS (PowerShell)

> **Note:** In PowerShell, do not use '&&' to chain commands. Run each command on a separate line. If you copy commands from bash/cmd, replace '&&' with line breaks or ';'.

### Backend:
```powershell
cd backend
node test-server.js
```

### Frontend:
```powershell
cd frontend
npm run dev
```

### OCR Service:
```powershell
cd ..
$env:PATH += ";C:\Program Files\Tesseract-OCR"
py app-light-fixed.py
```

### Verify services:
```powershell
# Backend
netstat -ano | findstr "4444"

# Frontend  
netstat -ano | findstr "5173"

# OCR
netstat -ano | findstr "5000"
```

---

## 🔧 TROUBLESHOOTING

- If you see errors about '&&' not being valid, you are using PowerShell. Use line breaks instead.
- If you see Unicode or emoji errors in PowerShell scripts, use the latest version of the scripts (emojis have been removed for compatibility).
- If a port is busy, stop the process using it:
```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 4444).OwningProcess | Stop-Process -Force
```
- If Tesseract is not found, ensure it is installed at `C:\Program Files\Tesseract-OCR` and added to your PATH.
- Always use `py` instead of `python` if you have both installed and `python` is not recognized.

---

## 🔒 SECURITY SUMMARY

### PUBLIC Endpoints (no authentication):
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /health` - Server health check

### PRIVATE Endpoints (require token):
- `GET /api/auth/me` - Verify authentication
- `POST /api/auth/logout` - Logout
- `GET /api/products` - List products
- `POST /api/products` - Create product (with images)
- `PUT /api/products/:id` - Update product (with images)
- `DELETE /api/products/:id` - Delete product
- `POST /api/products/:id/images` - Upload images to product
- `GET /api/inventory` - Get inventory
- `PUT /api/inventory/:id` - Update stock
- `POST /api/sales` - Create sale
- `GET /api/sales` - Sales history
- `GET /api/profile` - Get profile
- `PUT /api/profile` - Update profile

### 🔑 Security Flow:
1. **Registration/Login** → Gets token
2. **Token is saved** in frontend localStorage
3. **All private requests** include `Authorization: Bearer {token}`
4. **Backend validates** token in each request
5. **If invalid token** → Returns 401 Unauthorized

---

## 📁 FILE STRUCTURE (Relevant parts)

```
ZatoBox-main/
├── backend/
│   ├── test-server.js          # Main server with all endpoints
│   ├── users.json              # Persisted users
│   └── uploads/
│       └── products/           # Product images storage
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── NewProductPage.tsx    # Product creation
│   │   │   ├── InventoryPage.tsx     # Product listing
│   │   │   ├── EditProductPage.tsx   # Product editing
│   │   │   └── ProductCard.tsx       # Product display
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx       # Authentication
│   │   └── App.tsx
├── app-light-fixed.py          # OCR server (Python)
├── requirements-light.txt      # Python dependencies
├── start-zatobox.ps1           # Startup script (PowerShell)
└── install-zatobox.ps1         # Install script (PowerShell)
```

---

## 🧪 TESTS & VERIFICATION

- **Backend health:** http://localhost:4444/health
- **Frontend:** http://localhost:5173
- **OCR health:** http://localhost:5000/health
- **Test users:** http://localhost:4444/api/users
- **Test products:** http://localhost:4444/api/products
- **Test sales:** http://localhost:4444/api/sales

---

## ⚠️ KNOWN ISSUES & RECOMMENDATIONS

- Do not use '&&' in PowerShell, use line breaks.
- If you see Unicode/emoji errors in PowerShell, update your scripts to the latest version.
- Always check that all dependencies are installed and ports are free before starting services.
- For any issues, consult the README and this technical guide.

---

**ZatoBox v2.0** - Modern Inventory and Sales Management System 