const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const multer = require('multer');

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
  origin: true, // Permitir todos los orígenes en desarrollo
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
  optionsSuccessStatus: 200
}));

// Middleware para manejar preflight requests
app.options('*', cors());

// Middleware para logging de requests
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});

app.use(express.json());

// Serve static files from uploads directory
app.use('/uploads', express.static('uploads'));

// Configure multer for OCR file uploads
const ocrStorage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = 'uploads/ocr';
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, 'ocr-' + uniqueSuffix + path.extname(file.originalname));
  }
});

// Configure multer for product image uploads
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

const ocrUpload = multer({
  storage: ocrStorage,
  limits: {
    fileSize: 10 * 1024 * 1024 // 10MB limit
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = /jpeg|jpg|png|gif|pdf/;
    const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = allowedTypes.test(file.mimetype);
    
    if (mimetype && extname) {
      return cb(null, true);
    } else {
      cb(new Error('Only image and PDF files are allowed!'));
    }
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
  console.log('=== REGISTER REQUEST ===');
  console.log('Headers:', req.headers);
  console.log('Body:', req.body);
  console.log('Content-Type:', req.headers['content-type']);
  console.log('Method:', req.method);
  console.log('URL:', req.url);
  
  const { email, password, fullName, phone } = req.body;
  
  // Validar que todos los campos requeridos estén presentes
  if (!email || !password || !fullName) {
    console.log('Missing required fields:', { email: !!email, password: !!password, fullName: !!fullName });
    return res.status(400).json({ 
      success: false, 
      message: 'Email, password, and fullName are required' 
    });
  }
  
  // Validar formato de email
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    console.log('Invalid email format:', email);
    return res.status(400).json({ 
      success: false, 
      message: 'Invalid email format' 
    });
  }
  
  // Validar longitud de contraseña
  if (password.length < 8) {
    console.log('Password too short:', password.length);
    return res.status(400).json({ 
      success: false, 
      message: 'Password must be at least 8 characters long' 
    });
  }
  
  // Verificar si el email ya existe
  const existingUser = registeredUsers.find(user => user.email === email);
  if (existingUser) {
    console.log('Email already exists:', email);
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

// In-memory storage for products
let products = [
  {
    id: 1,
    name: 'Cabinet with Doors',
    description: 'Office cabinet with sliding doors',
    sku: 'CAB-001',
    category: 'Furniture',
    price: 180.00,
    stock: 25,
    status: 'active',
    images: ['https://picsum.photos/400/300?random=1']
  },
  {
    id: 2,
    name: 'Executive Desk',
    description: 'Wooden desk for executives',
    sku: 'ESC-001',
    category: 'Furniture',
    price: 250.00,
    stock: 8,
    status: 'active',
    images: ['https://picsum.photos/400/300?random=2']
  },
  {
    id: 3,
    name: 'Ergonomic Chair',
    description: 'Ergonomic office chair',
    sku: 'SIL-001',
    category: 'Furniture',
    price: 120.00,
    stock: 15,
    status: 'active',
    images: ['https://picsum.photos/400/300?random=3']
  },
  {
    id: 4,
    name: '24-inch Monitor',
    description: '24-inch LED monitor',
    sku: 'MON-001',
    category: 'Electronics',
    price: 180.00,
    stock: 6,
    status: 'active',
    images: ['https://picsum.photos/400/300?random=4']
  },
  {
    id: 5,
    name: 'Mechanical Keyboard',
    description: 'Gaming mechanical keyboard',
    sku: 'TEC-001',
    category: 'Electronics',
    price: 85.00,
    stock: 20,
    status: 'active',
    images: ['https://picsum.photos/400/300?random=5']
  },
  {
    id: 6,
    name: 'LED Lamp',
    description: 'LED desk lamp',
    sku: 'LAM-001',
    category: 'Lighting',
    price: 35.00,
    stock: 0,
    status: 'inactive',
    images: ['https://picsum.photos/400/300?random=6']
  }
];

let nextProductId = 7;

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

app.delete('/api/products/:id', authenticateToken, (req, res) => {
  const productId = parseInt(req.params.id);
  console.log('=== DELETE PRODUCT REQUEST ===');
  console.log('Product ID:', productId);
  console.log('User:', req.user.email);
  console.log('Headers:', req.headers);
  
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

// Upload images to existing product
app.post('/api/products/:id/images', authenticateToken, productImageUpload.array('images', 5), (req, res) => {
  const productId = parseInt(req.params.id);
  console.log('Upload images request for product:', productId);
  
  const productIndex = products.findIndex(p => p.id === productId);
  
  if (productIndex === -1) {
    return res.status(404).json({
      success: false,
      message: 'Product not found'
    });
  }

  if (!req.files || req.files.length === 0) {
    return res.status(400).json({
      success: false,
      message: 'No images uploaded'
    });
  }

  // Initialize images array if it doesn't exist
  if (!products[productIndex].images) {
    products[productIndex].images = [];
  }

  // Add new images
  const newImages = req.files.map(file => `/uploads/products/${file.filename}`);
  products[productIndex].images = [...products[productIndex].images, ...newImages];

  console.log('Images uploaded for product:', productId, newImages);
  res.json({
    success: true,
    message: 'Images uploaded successfully',
    product: products[productIndex]
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

// OCR endpoints
app.post('/api/ocr/process-document', authenticateToken, ocrUpload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    // Simulate OCR processing
    const mockOcrResult = {
      success: true,
      data: {
        documentType: 'invoice',
        vendor: 'Proveedor ABC',
        date: '2024-01-15',
        total: 1250.00,
        items: [
          {
            description: 'Cabinet with Doors',
            quantity: 5,
            unitPrice: 180.00,
            total: 900.00
          },
          {
            description: 'Escritorio Ejecutivo',
            quantity: 2,
            unitPrice: 250.00,
            total: 500.00
          }
        ],
        tax: 187.50,
        subtotal: 1062.50,
        confidence: 0.95
      },
      file: {
        originalName: req.file.originalname,
        filename: req.file.filename,
        path: req.file.path,
        size: req.file.size
      }
    };

    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 2000));

    res.json(mockOcrResult);
  } catch (error) {
    console.error('OCR processing error:', error);
    res.status(500).json({ 
      error: 'Failed to process document',
      details: error.message 
    });
  }
});

app.get('/api/ocr/history', authenticateToken, async (req, res) => {
  try {
    const history = [
      {
        id: 1,
        filename: 'invoice-001.pdf',
        documentType: 'invoice',
        processedAt: '2024-01-15T10:30:00Z',
        status: 'completed',
        confidence: 0.95
      },
      {
        id: 2,
        filename: 'receipt-002.jpg',
        documentType: 'receipt',
        processedAt: '2024-01-14T15:45:00Z',
        status: 'completed',
        confidence: 0.88
      }
    ];

    res.json({ history });
  } catch (error) {
    console.error('Get OCR history error:', error);
    res.status(500).json({ error: 'Failed to get OCR history' });
  }
});

app.get('/api/ocr/status/:jobId', authenticateToken, async (req, res) => {
  try {
    const { jobId } = req.params;
    
    const status = {
      jobId,
      status: 'completed',
      progress: 100,
      result: {
        documentType: 'invoice',
        vendor: 'Proveedor ABC',
        total: 1250.00
      }
    };

    res.json(status);
  } catch (error) {
    console.error('Get OCR status error:', error);
    res.status(500).json({ error: 'Failed to get OCR status' });
  }
});

app.listen(PORT, () => {
  console.log(`🚀 Test server running on port ${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
}); 