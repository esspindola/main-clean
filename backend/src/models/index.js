const User = require('./User');
const Product = require('./Product');
const Sale = require('./Sale');
const InventoryMovement = require('./InventoryMovement');

// Importar las asociaciones
require('../config/associations');

module.exports = {
  User,
  Product,
  Sale,
  InventoryMovement
}; 