const { DataTypes } = require('sequelize');
const { sequelize } = require('../config/database');

const Product = sequelize.define('Product', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  name: {
    type: DataTypes.STRING,
    allowNull: false
  },
  description: {
    type: DataTypes.TEXT,
    allowNull: true
  },
  sku: {
    type: DataTypes.STRING,
    allowNull: false,
    unique: true
  },
  category: {
    type: DataTypes.STRING,
    allowNull: false
  },
  price: {
    type: DataTypes.DECIMAL(10, 2),
    allowNull: false,
    defaultValue: 0.00
  },
  stock: {
    type: DataTypes.INTEGER,
    allowNull: false,
    defaultValue: 0
  },
  lowStockAlert: {
    type: DataTypes.INTEGER,
    allowNull: false,
    defaultValue: 5
  },
  status: {
    type: DataTypes.ENUM('active', 'inactive'),
    defaultValue: 'active'
  },
  images: {
    type: DataTypes.JSON,
    defaultValue: []
  },
  variants: {
    type: DataTypes.JSON,
    defaultValue: {}
  },
  productType: {
    type: DataTypes.STRING,
    defaultValue: 'Producto físico'
  },
  location: {
    type: DataTypes.STRING,
    allowNull: true
  },
  unit: {
    type: DataTypes.STRING,
    defaultValue: 'Por artículo'
  },
  weight: {
    type: DataTypes.DECIMAL(8, 2),
    allowNull: true
  },
  userId: {
    type: DataTypes.INTEGER,
    allowNull: false,
    references: {
      model: 'users',
      key: 'id'
    }
  }
}, {
  tableName: 'products'
});

// Instance methods
Product.prototype.isLowStock = function() {
  return this.stock <= this.lowStockAlert;
};

Product.prototype.updateStock = async function(quantity, type = 'add') {
  const newStock = type === 'add' ? this.stock + quantity : this.stock - quantity;
  if (newStock < 0) {
    throw new Error('Stock cannot be negative');
  }
  this.stock = newStock;
  return await this.save();
};

module.exports = Product; 