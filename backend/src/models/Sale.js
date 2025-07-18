const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const Sale = sequelize.define('Sale', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  userId: {
    type: DataTypes.INTEGER,
    allowNull: false,
    references: {
      model: 'users',
      key: 'id'
    }
  },
  total: {
    type: DataTypes.DECIMAL(10, 2),
    allowNull: false,
    defaultValue: 0.00
  },
  subtotal: {
    type: DataTypes.DECIMAL(10, 2),
    allowNull: false,
    defaultValue: 0.00
  },
  tax: {
    type: DataTypes.DECIMAL(10, 2),
    allowNull: false,
    defaultValue: 0.00
  },
  paymentMethod: {
    type: DataTypes.STRING,
    allowNull: false
  },
  status: {
    type: DataTypes.ENUM('pending', 'completed', 'cancelled', 'refunded'),
    defaultValue: 'pending'
  },
  items: {
    type: DataTypes.JSON,
    allowNull: false,
    defaultValue: []
  },
  customerInfo: {
    type: DataTypes.JSON,
    allowNull: true
  },
  notes: {
    type: DataTypes.TEXT,
    allowNull: true
  },
  transactionId: {
    type: DataTypes.STRING,
    allowNull: true
  }
}, {
  tableName: 'sales'
});

// Instance methods
Sale.prototype.calculateTotals = function() {
  const subtotal = this.items.reduce((sum, item) => sum + (item.quantity * item.price), 0);
  this.subtotal = subtotal;
  this.tax = subtotal * 0.15; // 15% tax
  this.total = subtotal + this.tax;
  return this;
};

Sale.prototype.addItem = function(item) {
  if (!this.items) this.items = [];
  this.items.push(item);
  this.calculateTotals();
  return this;
};

Sale.prototype.removeItem = function(itemId) {
  if (!this.items) return this;
  this.items = this.items.filter(item => item.id !== itemId);
  this.calculateTotals();
  return this;
};

module.exports = Sale; 