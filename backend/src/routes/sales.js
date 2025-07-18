const express = require('express');
const { body, validationResult, query } = require('express-validator');
const Sale = require('../models/Sale');
const Product = require('../models/Product');
const InventoryMovement = require('../models/InventoryMovement');
const { auth } = require('../middleware/auth');

const router = express.Router();

// Get all sales with filters
router.get('/', [
  query('status').optional().isIn(['pending', 'completed', 'cancelled', 'refunded']),
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

    const { status, page = 1, limit = 20, startDate, endDate } = req.query;
    const offset = (page - 1) * limit;

    // Build where clause
    const whereClause = { userId: req.user.id };
    
    if (status) {
      whereClause.status = status;
    }
    
    if (startDate || endDate) {
      whereClause.createdAt = {};
      if (startDate) whereClause.createdAt[require('sequelize').Op.gte] = new Date(startDate);
      if (endDate) whereClause.createdAt[require('sequelize').Op.lte] = new Date(endDate);
    }

    const sales = await Sale.findAndCountAll({
      where: whereClause,
      limit: parseInt(limit),
      offset: parseInt(offset),
      order: [['createdAt', 'DESC']]
    });

    res.json({
      sales: sales.rows,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total: sales.count,
        pages: Math.ceil(sales.count / limit)
      }
    });
  } catch (error) {
    console.error('Get sales error:', error);
    res.status(500).json({ error: 'Failed to get sales' });
  }
});

// Get single sale
router.get('/:id', auth, async (req, res) => {
  try {
    const sale = await Sale.findOne({
      where: {
        id: req.params.id,
        userId: req.user.id
      }
    });

    if (!sale) {
      return res.status(404).json({ error: 'Sale not found' });
    }

    res.json({ sale });
  } catch (error) {
    console.error('Get sale error:', error);
    res.status(500).json({ error: 'Failed to get sale' });
  }
});

// Create sale
router.post('/', [
  body('items').isArray({ min: 1 }),
  body('items.*.id').isInt(),
  body('items.*.quantity').isInt({ min: 1 }),
  body('paymentMethod').notEmpty().trim(),
  body('customerInfo').optional().isObject(),
  body('notes').optional().isString()
], auth, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { items, paymentMethod, customerInfo, notes } = req.body;

    // Validate products and check stock
    const productIds = items.map(item => item.id);
    const products = await Product.findAll({
      where: {
        id: productIds,
        userId: req.user.id
      }
    });

    if (products.length !== items.length) {
      return res.status(400).json({ error: 'Some products not found' });
    }

    // Check stock availability and prepare items with product data
    const saleItems = [];
    for (const item of items) {
      const product = products.find(p => p.id === item.id);
      if (product.stock < item.quantity) {
        return res.status(400).json({ 
          error: `Insufficient stock for ${product.name}. Available: ${product.stock}` 
        });
      }
      
      saleItems.push({
        id: product.id,
        name: product.name,
        price: parseFloat(product.price),
        quantity: item.quantity,
        total: parseFloat(product.price) * item.quantity
      });
    }

    // Create sale
    const sale = await Sale.create({
      userId: req.user.id,
      items: saleItems,
      paymentMethod,
      customerInfo,
      notes,
      status: 'completed'
    });

    // Calculate totals
    sale.calculateTotals();
    await sale.save();

    // Update product stock and create inventory movements
    for (const item of saleItems) {
      const product = products.find(p => p.id === item.id);
      const previousStock = product.stock;
      
      await product.updateStock(item.quantity, 'subtract');
      
      // Create inventory movement
      await InventoryMovement.create({
        productId: product.id,
        userId: req.user.id,
        type: 'out',
        quantity: item.quantity,
        previousStock,
        newStock: product.stock,
        reason: 'Sale',
        reference: `Sale #${sale.id}`
      });
    }

    res.status(201).json({
      message: 'Sale created successfully',
      sale
    });
  } catch (error) {
    console.error('Create sale error:', error);
    res.status(500).json({ error: 'Failed to create sale' });
  }
});

// Update sale status
router.patch('/:id/status', [
  body('status').isIn(['pending', 'completed', 'cancelled', 'refunded'])
], auth, async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const sale = await Sale.findOne({
      where: {
        id: req.params.id,
        userId: req.user.id
      }
    });

    if (!sale) {
      return res.status(404).json({ error: 'Sale not found' });
    }

    const { status } = req.body;
    const previousStatus = sale.status;

    // Handle status changes
    if (status === 'cancelled' && previousStatus === 'completed') {
      // Restore stock for cancelled sales
      for (const item of sale.items) {
        const product = await Product.findByPk(item.id);
        if (product) {
          const previousStock = product.stock;
          await product.updateStock(item.quantity, 'add');
          
          await InventoryMovement.create({
            productId: product.id,
            userId: req.user.id,
            type: 'in',
            quantity: item.quantity,
            previousStock,
            newStock: product.stock,
            reason: 'Sale cancellation',
            reference: `Sale #${sale.id}`
          });
        }
      }
    }

    await sale.update({ status });

    res.json({
      message: 'Sale status updated successfully',
      sale
    });
  } catch (error) {
    console.error('Update sale status error:', error);
    res.status(500).json({ error: 'Failed to update sale status' });
  }
});

// Get sales statistics
router.get('/stats/summary', auth, async (req, res) => {
  try {
    const { startDate, endDate } = req.query;
    
    const whereClause = { 
      userId: req.user.id,
      status: 'completed'
    };
    
    if (startDate || endDate) {
      whereClause.createdAt = {};
      if (startDate) whereClause.createdAt[require('sequelize').Op.gte] = new Date(startDate);
      if (endDate) whereClause.createdAt[require('sequelize').Op.lte] = new Date(endDate);
    }

    const totalSales = await Sale.count({ where: whereClause });
    const totalRevenue = await Sale.sum('total', { where: whereClause });
    const averageOrderValue = totalSales > 0 ? totalRevenue / totalSales : 0;

    // Get today's sales
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    const todaySales = await Sale.count({
      where: {
        ...whereClause,
        createdAt: {
          [require('sequelize').Op.gte]: today,
          [require('sequelize').Op.lt]: tomorrow
        }
      }
    });

    const todayRevenue = await Sale.sum('total', {
      where: {
        ...whereClause,
        createdAt: {
          [require('sequelize').Op.gte]: today,
          [require('sequelize').Op.lt]: tomorrow
        }
      }
    });

    res.json({
      summary: {
        totalSales,
        totalRevenue: totalRevenue || 0,
        averageOrderValue,
        todaySales,
        todayRevenue: todayRevenue || 0
      }
    });
  } catch (error) {
    console.error('Get sales stats error:', error);
    res.status(500).json({ error: 'Failed to get sales statistics' });
  }
});

module.exports = router; 