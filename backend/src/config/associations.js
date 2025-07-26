const User = require('../models/User');
const Product = require('../models/Product');
const Sale = require('../models/Sale');
const InventoryMovement = require('../models/InventoryMovement');

// User associations
User.hasMany(Product, { foreignKey: 'userId', as: 'products' });
User.hasMany(Sale, { foreignKey: 'userId', as: 'sales' });
User.hasMany(InventoryMovement, { foreignKey: 'userId', as: 'inventoryMovements' });

// Product associations
Product.belongsTo(User, { foreignKey: 'userId', as: 'user' });
Product.hasMany(InventoryMovement, { foreignKey: 'productId', as: 'inventoryMovements' });

// Sale associations
Sale.belongsTo(User, { foreignKey: 'userId', as: 'user' });

// InventoryMovement associations
InventoryMovement.belongsTo(User, { foreignKey: 'userId', as: 'user' });
InventoryMovement.belongsTo(Product, { foreignKey: 'productId', as: 'product' });

module.exports = {
  User,
  Product,
  Sale,
  InventoryMovement
}; 