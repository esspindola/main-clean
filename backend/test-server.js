const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 4444;

// Archivo para almacenar usuarios
const USERS_FILE = path.join(__dirname, 'users.json');

// Función para cargar usuarios desde archivo
function loadUsers() {
  try {
    if (fs.existsSync(USERS_FILE)) {
      const data = fs.readFileSync(USERS_FILE, 'utf8');
      return JSON.parse(data);
    }
  } catch (error) {
    console.error('Error loading users:', error);
  }
  
  // Usuarios por defecto si no existe el archivo
  return [
    {
      id: 1,
      email: 'admin@frontposw.com',
      password: 'admin12345678',
      fullName: 'Administrador',
      role: 'admin',
      phone: '+1234567890',
      address: '123 Main St, City, Country'
    },
    {
      id: 2,
      email: 'user@frontposw.com',
      password: 'user12345678',
      fullName: 'Usuario Regular',
      role: 'user',
      phone: '+1234567891',
      address: '456 Oak St, City, Country'
    }
  ];
}

// Función para guardar usuarios en archivo
function saveUsers(users) {
  try {
    fs.writeFileSync(USERS_FILE, JSON.stringify(users, null, 2));
    console.log('Users saved to file successfully');
  } catch (error) {
    console.error('Error saving users:', error);
  }
}

// Cargar usuarios al iniciar
let registeredUsers = loadUsers();
let nextUserId = Math.max(...registeredUsers.map(u => u.id)) + 1;

// Configurar CORS
app.use(cors({
  origin: function (origin, callback) {
    // Permitir requests sin origin (como aplicaciones móviles o Postman)
    if (!origin) return callback(null, true);
    
    const allowedOrigins = [
      'http://localhost:5173',
      'http://localhost:5174',
      'http://localhost:5175',
      'http://localhost:5176',
      'http://localhost:5177',
      'http://127.0.0.1:5173',
      'http://127.0.0.1:5174',
      'http://127.0.0.1:5175'
    ];
    
    if (allowedOrigins.indexOf(origin) !== -1) {
      callback(null, true);
    } else {
      console.log('CORS blocked origin:', origin);
      callback(new Error('Not allowed by CORS'));
    }
  },
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
  optionsSuccessStatus: 200
}));

app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    timestamp: new Date().toISOString(),
    message: 'Backend is running on port 4444!'
  });
});

// Auth endpoints
app.post('/api/auth/register', (req, res) => {
  console.log('Register request received:', req.body);
  
  const { email, password, fullName, phone } = req.body;
  
  // Verificar si el email ya existe
  const existingUser = registeredUsers.find(user => user.email === email);
  if (existingUser) {
    return res.status(400).json({ 
      success: false, 
      message: 'User with this email already exists' 
    });
  }
  
  // Crear nuevo usuario
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
  saveUsers(registeredUsers); // Guardar usuarios actualizados
  
  console.log('User registered successfully:', { email, fullName });
  console.log('Total users:', registeredUsers.length);
  
  res.json({ 
    success: true, 
    message: 'User registered successfully',
    user: {
      id: newUser.id,
      email: newUser.email,
      fullName: newUser.fullName,
      role: newUser.role
    },
    token: `test-token-${newUser.id}-${Date.now()}`
  });
});

app.post('/api/auth/login', (req, res) => {
  console.log('Login request received:', req.body);
  
  const { email, password } = req.body;
  
  // Buscar usuario en la lista de usuarios registrados
  const user = registeredUsers.find(u => u.email === email && u.password === password);
  
  if (user) {
    console.log('Login successful for:', email);
    res.json({ 
      success: true, 
      message: 'Login successful',
      token: `test-token-${user.id}-${Date.now()}`,
      user: {
        id: user.id,
        email: user.email,
        fullName: user.fullName,
        role: user.role
      }
    });
  } else {
    console.log('Login failed for:', email);
    res.status(401).json({ 
      success: false, 
      message: 'Invalid credentials' 
    });
  }
});

// Auth check endpoint (para verificar si el usuario está autenticado)
app.get('/api/auth/me', (req, res) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  
  if (!token) {
    return res.status(401).json({ 
      success: false, 
      message: 'No token provided' 
    });
  }
  
  // Extraer el ID del usuario del token (formato: test-token-{id}-{timestamp})
  const tokenParts = token.split('-');
  if (tokenParts.length >= 3) {
    const userId = parseInt(tokenParts[2]);
    const user = registeredUsers.find(u => u.id === userId);
    
    if (user) {
      res.json({
        success: true,
        user: {
          id: user.id,
          email: user.email,
          fullName: user.fullName,
          role: user.role
        }
      });
      return;
    }
  }
  
  res.status(401).json({ 
    success: false, 
    message: 'Invalid token' 
  });
});

app.post('/api/auth/logout', (req, res) => {
  res.json({ 
    success: true, 
    message: 'Logout successful' 
  });
});

// Endpoint para listar todos los usuarios (solo para desarrollo)
app.get('/api/users', (req, res) => {
  console.log('Users list requested. Total users:', registeredUsers.length);
  
  // Ocultar contraseñas por seguridad
  const usersWithoutPasswords = registeredUsers.map(user => ({
    id: user.id,
    email: user.email,
    fullName: user.fullName,
    role: user.role,
    phone: user.phone,
    address: user.address
  }));
  
  res.json({
    success: true,
    totalUsers: registeredUsers.length,
    users: usersWithoutPasswords
  });
});

// Almacenamiento en memoria para productos
let products = [
  {
    id: 1,
    name: 'Cabinet with Doors',
    description: 'Mueble de oficina con puertas corredizas',
    sku: 'CAB-001',
    category: 'Muebles',
    price: 180.00,
    stock: 25,
    status: 'active'
  },
  {
    id: 2,
    name: 'Escritorio Ejecutivo',
    description: 'Escritorio de madera para ejecutivos',
    sku: 'ESC-001',
    category: 'Muebles',
    price: 250.00,
    stock: 8,
    status: 'active'
  }
];

let nextProductId = 3;

// Función para verificar autenticación
function authenticateToken(req, res, next) {
  const token = req.headers.authorization?.replace('Bearer ', '');
  
  if (!token) {
    return res.status(401).json({ 
      success: false, 
      message: 'No token provided' 
    });
  }
  
  // Extraer el ID del usuario del token (formato: test-token-{id}-{timestamp})
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

// Products endpoints
app.get('/api/products', authenticateToken, (req, res) => {
  console.log('Products requested by user:', req.user.email);
  res.json({
    success: true,
    products: products
  });
});

app.get('/api/products/:id', authenticateToken, (req, res) => {
  const productId = parseInt(req.params.id);
  console.log('Get product request:', productId, 'by user:', req.user.email);
  
  const product = products.find(p => p.id === productId);
  
  if (!product) {
    return res.status(404).json({
      success: false,
      message: 'Product not found'
    });
  }
  
  res.json({
    success: true,
    product: product
  });
});

app.post('/api/products', authenticateToken, (req, res) => {
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
  
  products.push(newProduct);
  
  console.log('Product created:', newProduct);
  res.json({
    success: true,
    message: 'Product created successfully',
    product: newProduct
  });
});

app.put('/api/products/:id', authenticateToken, (req, res) => {
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
  
  console.log('Product updated:', products[productIndex]);
  res.json({
    success: true,
    message: 'Product updated successfully',
    product: products[productIndex]
  });
});

app.delete('/api/products/:id', authenticateToken, (req, res) => {
  const productId = parseInt(req.params.id);
  console.log('Delete product request:', productId);
  
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

// Profile endpoint
app.get('/api/profile', authenticateToken, (req, res) => {
  res.json({
    success: true,
    user: {
      id: req.user.id,
      email: req.user.email,
      fullName: req.user.fullName,
      role: req.user.role,
      phone: req.user.phone,
      address: req.user.address
    }
  });
});

// Sales endpoints
app.get('/api/sales', authenticateToken, (req, res) => {
  res.json({
    success: true,
    sales: [
      {
        id: 1,
        total: 480.00,
        status: 'completed',
        createdAt: new Date().toISOString()
      }
    ]
  });
});

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
    // Verificar stock disponible y actualizar inventario
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
      
      // Actualizar stock del producto
      product.stock -= item.quantity;
      updatedProducts.push(product);
    }
    
    // Crear la venta
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

// Inventory endpoints
app.get('/api/inventory', authenticateToken, (req, res) => {
  res.json({
    success: true,
    inventory: [
      {
        id: 1,
        name: 'Cabinet with Doors',
        stock: 25,
        lowStockAlert: 5
      }
    ]
  });
});

app.listen(PORT, () => {
  console.log(`🚀 Test server running on port ${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
}); 