const express = require('express');
const { body, validationResult, query } = require('express-validator');
const Product = require('../models/Product');
const InventoryMovement = require('../models/InventoryMovement');
const { auth } = require('../middleware/auth');

const router = express.Router();

// Get inventory with filters
router.get('/', [
  query('search').optional().isString(),
  query('category').optional().isString(),
  query('status').optional().isIn(['active', 'inactive']),
  query('lowStock').optional().isBoolean(),
  query('page').optional().isInt({ min: 1 }),
  query('limit').optional().isInt({ min: 1, max: 100 })
], auth, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { search, category, status, lowStock, page = 1, limit = 20 } = req.query;
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

    if (lowStock === 'true') {
      whereClause.stock = { [require('sequelize').Op.lte]: require('sequelize').col('lowStockAlert') };
    }

    const products = await Product.findAndCountAll({
      where: whereClause,
      limit: parseInt(limit),
      offset: parseInt(offset),
      order: [['name', 'ASC']]
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
    console.error('Get inventory error:', error);
    res.status(500).json({ error: 'Failed to get inventory' });
  }
});

// Get low stock products
router.get('/low-stock', auth, async (req, res) => {
  try {
    const products = await Product.findAll({
      where: {
        userId: req.user.id,
        stock: { [require('sequelize').Op.lte]: require('sequelize').col('lowStockAlert') },
        status: 'active'
      },
      order: [['stock', 'ASC']]
    });

    res.json({ products });
  } catch (error) {
    console.error('Get low stock error:', error);
    res.status(500).json({ error: 'Failed to get low stock products' });
  }
});

// Update product stock
router.put('/:id/stock', [
  body('quantity').isInt({ min: 1 }),
  body('type').isIn(['add', 'subtract', 'set']),
  body('reason').notEmpty().trim(),
  body('notes').optional().isString()
], auth, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { quantity, type, reason, notes } = req.body;

    const product = await Product.findOne({
      where: {
        id: req.params.id,
        userId: req.user.id
      }
    });

    if (!product) {
      return res.status(404).json({ error: 'Product not found' });
    }

    const previousStock = product.stock;
    let newStock;

    switch (type) {
      case 'add':
        newStock = previousStock + quantity;
        break;
      case 'subtract':
        newStock = previousStock - quantity;
        if (newStock < 0) {
          return res.status(400).json({ error: 'Stock cannot be negative' });
        }
        break;
      case 'set':
        newStock = quantity;
        if (newStock < 0) {
          return res.status(400).json({ error: 'Stock cannot be negative' });
        }
        break;
    }

    await product.update({ stock: newStock });

    // Create inventory movement
    const movementType = type === 'add' ? 'in' : type === 'subtract' ? 'out' : 'adjustment';
    await InventoryMovement.create({
      productId: product.id,
      userId: req.user.id,
      type: movementType,
      quantity: type === 'set' ? Math.abs(newStock - previousStock) : quantity,
      previousStock,
      newStock,
      reason,
      notes
    });

    res.json({
      message: 'Stock updated successfully',
      product
    });
  } catch (error) {
    console.error('Update stock error:', error);
    res.status(500).json({ error: 'Failed to update stock' });
  }
});

// Get inventory movements
router.get('/movements', [
  query('productId').optional().isInt(),
  query('type').optional().isIn(['in', 'out', 'adjustment']),
  query('page').optional().isInt({ min: 1 }),
  query('limit').optional().isInt({ min: 1, max: 100 }),
  query('startDate').optional().isISO8601(),
  query('endDate').optional().isISO8601()
], auth, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { productId, type, page = 1, limit = 20, startDate, endDate } = req.query;
    const offset = (page - 1) * limit;

    // Build where clause
    const whereClause = { userId: req.user.id };
    
    if (productId) {
      whereClause.productId = productId;
    }
    
    if (type) {
      whereClause.type = type;
    }
    
    if (startDate || endDate) {
      whereClause.createdAt = {};
      if (startDate) whereClause.createdAt[require('sequelize').Op.gte] = new Date(startDate);
      if (endDate) whereClause.createdAt[require('sequelize').Op.lte] = new Date(endDate);
    }

    const movements = await InventoryMovement.findAndCountAll({
      where: whereClause,
      include: [{
        model: Product,
        as: 'product',
        attributes: ['id', 'name', 'sku']
      }],
      limit: parseInt(limit),
      offset: parseInt(offset),
      order: [['createdAt', 'DESC']]
    });

    res.json({
      movements: movements.rows,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total: movements.count,
        pages: Math.ceil(movements.count / limit)
      }
    });
  } catch (error) {
    console.error('Get movements error:', error);
    res.status(500).json({ error: 'Failed to get inventory movements' });
  }
});

// Get inventory statistics
router.get('/stats/summary', auth, async (req, res) => {
  try {
    const totalProducts = await Product.count({ where: { userId: req.user.id } });
    const activeProducts = await Product.count({ 
      where: { userId: req.user.id, status: 'active' } 
    });
    const inactiveProducts = await Product.count({ 
      where: { userId: req.user.id, status: 'inactive' } 
    });
    
    const lowStockProducts = await Product.count({
      where: {
        userId: req.user.id,
        stock: { [require('sequelize').Op.lte]: require('sequelize').col('lowStockAlert') },
        status: 'active'
      }
    });

    const outOfStockProducts = await Product.count({
      where: {
        userId: req.user.id,
        stock: 0,
        status: 'active'
      }
    });

    const totalStockValue = await Product.sum('stock * price', {
      where: { userId: req.user.id, status: 'active' }
    });

    res.json({
      summary: {
        totalProducts,
        activeProducts,
        inactiveProducts,
        lowStockProducts,
        outOfStockProducts,
        totalStockValue: totalStockValue || 0
      }
    });
  } catch (error) {
    console.error('Get inventory stats error:', error);
    res.status(500).json({ error: 'Failed to get inventory statistics' });
  }
});

// Bulk stock update
router.post('/bulk-update', [
  body('updates').isArray({ min: 1 }),
  body('updates.*.productId').isInt(),
  body('updates.*.quantity').isInt({ min: 1 }),
  body('updates.*.type').isIn(['add', 'subtract', 'set']),
  body('reason').notEmpty().trim(),
  body('notes').optional().isString()
], auth, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { updates, reason, notes } = req.body;

    const results = [];
    const updateErrors = [];

    for (const update of updates) {
      try {
        const product = await Product.findOne({
          where: {
            id: update.productId,
            userId: req.user.id
          }
        });

        if (!product) {
          updateErrors.push(`Product ${update.productId} not found`);
          continue;
        }

        const previousStock = product.stock;
        let newStock;

        switch (update.type) {
          case 'add':
            newStock = previousStock + update.quantity;
            break;
          case 'subtract':
            newStock = previousStock - update.quantity;
            if (newStock < 0) {
              updateErrors.push(`Insufficient stock for ${product.name}`);
              continue;
            }
            break;
          case 'set':
            newStock = update.quantity;
            if (newStock < 0) {
              updateErrors.push(`Invalid stock value for ${product.name}`);
              continue;
            }
            break;
        }

        await product.update({ stock: newStock });

        // Create inventory movement
        const movementType = update.type === 'add' ? 'in' : update.type === 'subtract' ? 'out' : 'adjustment';
        await InventoryMovement.create({
          productId: product.id,
          userId: req.user.id,
          type: movementType,
          quantity: update.type === 'set' ? Math.abs(newStock - previousStock) : update.quantity,
          previousStock,
          newStock,
          reason,
          notes
        });

        results.push({
          productId: product.id,
          name: product.name,
          previousStock,
          newStock,
          success: true
        });
      } catch (error) {
        updateErrors.push(`Error updating product ${update.productId}: ${error.message}`);
      }
    }

    res.json({
      message: 'Bulk update completed',
      results,
      errors: updateErrors.length > 0 ? updateErrors : undefined
    });
  } catch (error) {
    console.error('Bulk update error:', error);
    res.status(500).json({ error: 'Failed to perform bulk update' });
  }
});

module.exports = router; 