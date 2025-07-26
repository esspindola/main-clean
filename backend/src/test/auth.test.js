const request = require('supertest')
const express = require('express')
const bcrypt = require('bcryptjs')
const jwt = require('jsonwebtoken')

// Mock del servidor Express
const app = express()
app.use(express.json())

// Mock de datos de usuario
const mockUsers = [
  {
    id: 1,
    email: 'admin@zatobox.com',
    password: bcrypt.hashSync('admin12345678', 10),
    fullName: 'Admin User',
    role: 'admin'
  }
]

// Mock de middleware de autenticación
const authMiddleware = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1]
  if (!token) {
    return res.status(401).json({ message: 'Token requerido' })
  }
  
  try {
    const decoded = jwt.verify(token, 'test-secret')
    req.user = decoded
    next()
  } catch (error) {
    return res.status(401).json({ message: 'Token inválido' })
  }
}

// Rutas de prueba
app.post('/api/auth/register', (req, res) => {
  const { email, password, fullName } = req.body
  
  if (!email || !password || !fullName) {
    return res.status(400).json({ 
      success: false, 
      message: 'Email, password y fullName son requeridos' 
    })
  }
  
  const existingUser = mockUsers.find(user => user.email === email)
  if (existingUser) {
    return res.status(400).json({ 
      success: false, 
      message: 'Usuario con este email ya existe' 
    })
  }
  
  const hashedPassword = bcrypt.hashSync(password, 10)
  const newUser = {
    id: mockUsers.length + 1,
    email,
    password: hashedPassword,
    fullName,
    role: 'user'
  }
  
  mockUsers.push(newUser)
  
  const token = jwt.sign(
    { userId: newUser.id, email: newUser.email },
    'test-secret',
    { expiresIn: '24h' }
  )
  
  res.status(201).json({
    success: true,
    message: 'Usuario registrado exitosamente',
    token,
    user: {
      id: newUser.id,
      email: newUser.email,
      fullName: newUser.fullName,
      role: newUser.role
    }
  })
})

app.post('/api/auth/login', (req, res) => {
  const { email, password } = req.body
  
  if (!email || !password) {
    return res.status(400).json({ 
      success: false, 
      message: 'Email y password son requeridos' 
    })
  }
  
  const user = mockUsers.find(user => user.email === email)
  if (!user) {
    return res.status(401).json({ 
      success: false, 
      message: 'Credenciales inválidas' 
    })
  }
  
  const isValidPassword = bcrypt.compareSync(password, user.password)
  if (!isValidPassword) {
    return res.status(401).json({ 
      success: false, 
      message: 'Credenciales inválidas' 
    })
  }
  
  const token = jwt.sign(
    { userId: user.id, email: user.email },
    'test-secret',
    { expiresIn: '24h' }
  )
  
  res.json({
    success: true,
    message: 'Login exitoso',
    token,
    user: {
      id: user.id,
      email: user.email,
      fullName: user.fullName,
      role: user.role
    }
  })
})

app.get('/api/auth/me', authMiddleware, (req, res) => {
  const user = mockUsers.find(user => user.id === req.user.userId)
  if (!user) {
    return res.status(404).json({ 
      success: false, 
      message: 'Usuario no encontrado' 
    })
  }
  
  res.json({
    success: true,
    user: {
      id: user.id,
      email: user.email,
      fullName: user.fullName,
      role: user.role
    }
  })
})

describe('Auth Endpoints', () => {
  describe('POST /api/auth/register', () => {
    it('should register a new user successfully', async () => {
      const userData = {
        email: 'test@example.com',
        password: 'test123456',
        fullName: 'Test User'
      }
      
      const response = await request(app)
        .post('/api/auth/register')
        .send(userData)
        .expect(201)
      
      expect(response.body.success).toBe(true)
      expect(response.body.message).toBe('Usuario registrado exitosamente')
      expect(response.body.token).toBeDefined()
      expect(response.body.user.email).toBe(userData.email)
      expect(response.body.user.fullName).toBe(userData.fullName)
    })
    
    it('should return error for missing fields', async () => {
      const response = await request(app)
        .post('/api/auth/register')
        .send({ email: 'test@example.com' })
        .expect(400)
      
      expect(response.body.success).toBe(false)
      expect(response.body.message).toBe('Email, password y fullName son requeridos')
    })
    
    it('should return error for existing email', async () => {
      const userData = {
        email: 'admin@zatobox.com',
        password: 'test123456',
        fullName: 'Test User'
      }
      
      const response = await request(app)
        .post('/api/auth/register')
        .send(userData)
        .expect(400)
      
      expect(response.body.success).toBe(false)
      expect(response.body.message).toBe('Usuario con este email ya existe')
    })
  })
  
  describe('POST /api/auth/login', () => {
    it('should login successfully with valid credentials', async () => {
      const loginData = {
        email: 'admin@zatobox.com',
        password: 'admin12345678'
      }
      
      const response = await request(app)
        .post('/api/auth/login')
        .send(loginData)
        .expect(200)
      
      expect(response.body.success).toBe(true)
      expect(response.body.message).toBe('Login exitoso')
      expect(response.body.token).toBeDefined()
      expect(response.body.user.email).toBe(loginData.email)
    })
    
    it('should return error for invalid credentials', async () => {
      const loginData = {
        email: 'admin@zatobox.com',
        password: 'wrongpassword'
      }
      
      const response = await request(app)
        .post('/api/auth/login')
        .send(loginData)
        .expect(401)
      
      expect(response.body.success).toBe(false)
      expect(response.body.message).toBe('Credenciales inválidas')
    })
    
    it('should return error for missing fields', async () => {
      const response = await request(app)
        .post('/api/auth/login')
        .send({ email: 'test@example.com' })
        .expect(400)
      
      expect(response.body.success).toBe(false)
      expect(response.body.message).toBe('Email y password son requeridos')
    })
  })
  
  describe('GET /api/auth/me', () => {
    it('should return user data with valid token', async () => {
      // Primero hacer login para obtener token
      const loginResponse = await request(app)
        .post('/api/auth/login')
        .send({
          email: 'admin@zatobox.com',
          password: 'admin12345678'
        })
      
      const token = loginResponse.body.token
      
      const response = await request(app)
        .get('/api/auth/me')
        .set('Authorization', `Bearer ${token}`)
        .expect(200)
      
      expect(response.body.success).toBe(true)
      expect(response.body.user.email).toBe('admin@zatobox.com')
      expect(response.body.user.fullName).toBe('Admin User')
    })
    
    it('should return error without token', async () => {
      const response = await request(app)
        .get('/api/auth/me')
        .expect(401)
      
      expect(response.body.message).toBe('Token requerido')
    })
    
    it('should return error with invalid token', async () => {
      const response = await request(app)
        .get('/api/auth/me')
        .set('Authorization', 'Bearer invalid-token')
        .expect(401)
      
      expect(response.body.message).toBe('Token inválido')
    })
  })
}) 