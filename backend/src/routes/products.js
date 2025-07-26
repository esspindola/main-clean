const express = require('express');
const { body, validationResult, query } = require('express-validator');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const Product = require('../models/Product');
const { auth } = require('../middleware/auth');

const router = express.Router();

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = 'uploads/products';
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({
  storage,
  limits: {
    fileSize: 5 * 1024 * 1024 // 5MB limit
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

// Get all products with filters
router.get('/', [
  query('search').optional().isString(),
  query('category').optional().isString(),
  query('status').optional().isIn(['active', 'inactive']),
  query('page').optional().isInt({ min: 1 }),
  query('limit').optional().isInt({ min: 1, max: 100 })
], auth, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { search, category, status, page = 1, limit = 20 } = req.query;
    const offset = (page - 1) * limit;

    // Build where clause
    const whereClause = { userId: req.user.id };
    
    if (search) {
      whereClause.name = { [require('sequelize').Op.iLike]: `%${search}%` };
    }
    
    if (category) {
      whereClause.category = category;
    }
    
    if (status) {
      whereClause.status = status;
    }

    const products = await Product.findAndCountAll({
      where: whereClause,
      limit: parseInt(limit),
      offset: parseInt(offset),
      order: [['createdAt', 'DESC']]
    });

    res.json({
      products: products.rows,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total: products.count,
        pages: Math.ceil(products.count / limit)
      }
    });
  } catch (error) {
    console.error('Get products error:', error);
    res.status(500).json({ error: 'Failed to get products' });
  }
});

// Get single product
router.get('/:id', auth, async (req, res) => {
  try {
    const product = await Product.findOne({
      where: {
        id: req.params.id,
        userId: req.user.id
      }
    });

    if (!product) {
      return res.status(404).json({ error: 'Product not found' });
    }

    res.json({ product });
  } catch (error) {
    console.error('Get product error:', error);
    res.status(500).json({ error: 'Failed to get product' });
  }
});

// Create product
router.post('/', [
  body('name').notEmpty().trim(),
  body('description').optional().isString(),
  body('sku').notEmpty().trim(),
  body('category').notEmpty().trim(),
  body('price').isFloat({ min: 0 }),
  body('stock').isInt({ min: 0 }),
  body('lowStockAlert').isInt({ min: 0 }),
  body('status').optional().isIn(['active', 'inactive']),
  body('productType').optional().isString(),
  body('location').optional().isString(),
  body('unit').optional().isString(),
  body('weight').optional().isFloat({ min: 0 }),
  body('variants').optional().isObject()
], auth, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    // Check if SKU already exists
    const existingProduct = await Product.findOne({
      where: { sku: req.body.sku }
    });

    if (existingProduct) {
      return res.status(400).json({ error: 'SKU already exists' });
    }

    const product = await Product.create({
      ...req.body,
      userId: req.user.id
    });

    res.status(201).json({
      message: 'Product created successfully',
      product
    });
  } catch (error) {
    console.error('Create product error:', error);
    res.status(500).json({ error: 'Failed to create product' });
  }
});

// Update product
router.put('/:id', [
  body('name').optional().notEmpty().trim(),
  body('description').optional().isString(),
  body('category').optional().notEmpty().trim(),
  body('price').optional().isFloat({ min: 0 }),
  body('stock').optional().isInt({ min: 0 }),
  body('lowStockAlert').optional().isInt({ min: 0 }),
  body('status').optional().isIn(['active', 'inactive']),
  body('productType').optional().isString(),
  body('location').optional().isString(),
  body('unit').optional().isString(),
  body('weight').optional().isFloat({ min: 0 }),
  body('variants').optional().isObject()
], auth, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const product = await Product.findOne({
      where: {
        id: req.params.id,
        userId: req.user.id
      }
    });

    if (!product) {
      return res.status(404).json({ error: 'Product not found' });
    }

    await product.update(req.body);

    res.json({
      message: 'Product updated successfully',
      product
    });
  } catch (error) {
    console.error('Update product error:', error);
    res.status(500).json({ error: 'Failed to update product' });
  }
});

// Delete product
router.delete('/:id', auth, async (req, res) => {
  try {
    const product = await Product.findOne({
      where: {
        id: req.params.id,
        userId: req.user.id
      }
    });

    if (!product) {
      return res.status(404).json({ error: 'Product not found' });
    }

    await product.destroy();

    res.json({ message: 'Product deleted successfully' });
  } catch (error) {
    console.error('Delete product error:', error);
    res.status(500).json({ error: 'Failed to delete product' });
  }
});

// Upload product images
router.post('/:id/images', auth, upload.array('images', 5), async (req, res) => {
  try {
    const product = await Product.findOne({
      where: {
        id: req.params.id,
        userId: req.user.id
      }
    });

    if (!product) {
      return res.status(404).json({ error: 'Product not found' });
    }

    if (!req.files || req.files.length === 0) {
      return res.status(400).json({ error: 'No images uploaded' });
    }

    const imageUrls = req.files.map(file => `/uploads/products/${file.filename}`);
    const currentImages = product.images || [];
    const updatedImages = [...currentImages, ...imageUrls];

    await product.update({ images: updatedImages });

    res.json({
      message: 'Images uploaded successfully',
      images: updatedImages
    });
  } catch (error) {
    console.error('Upload images error:', error);
    res.status(500).json({ error: 'Failed to upload images' });
  }
});

// Get categories
router.get('/categories/list', auth, async (req, res) => {
  try {
    const categories = await Product.findAll({
      attributes: [[require('sequelize').fn('DISTINCT', require('sequelize').col('category')), 'category']],
      where: { userId: req.user.id },
      raw: true
    });

    const categoryList = categories.map(cat => cat.category).filter(Boolean);

    res.json({ categories: categoryList });
  } catch (error) {
    console.error('Get categories error:', error);
    res.status(500).json({ error: 'Failed to get categories' });
  }
});

module.exports = router; 