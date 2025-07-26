const { sequelize } = require('./src/config/database');
const User = require('./src/models/User');
const Product = require('./src/models/Product');
const Sale = require('./src/models/Sale');
const InventoryMovement = require('./src/models/InventoryMovement');
const seedData = require('./src/utils/seedData');

async function initializeDatabase() {
  try {
    console.log('🔄 Initializing database...');
    
    // Sync models with database (without associations first)
    await sequelize.sync({ force: true });
    console.log('✅ Tables created successfully');
    
    // Configure associations after creating tables
    require('./src/config/associations');
    console.log('✅ Associations configured');
    
    // Populate with sample data
    console.log('🔄 Populating with sample data...');
    
    // Create users
    const users = await User.bulkCreate(seedData.users);
    console.log(`✅ ${users.length} users created`);
    
    // Create products
    const products = await Product.bulkCreate(seedData.products);
    console.log(`✅ ${products.length} products created`);
    
    // Create initial inventory movements
    const inventoryMovements = await InventoryMovement.bulkCreate(seedData.inventoryMovements);
    console.log(`✅ ${inventoryMovements.length} inventory movements created`);
    
    // Create some sample sales
    const sales = await Sale.bulkCreate(seedData.sales);
    console.log(`✅ ${sales.length} sample sales created`);
    
    console.log('\n🎉 Database initialized successfully!');
    console.log('\n📋 Sample credentials:');
    console.log('👤 Admin: admin@frontposw.com / admin12345678');
    console.log('👤 User: user@frontposw.com / user12345678');
    console.log('\n🚀 You can start the server with: npm start');
    
  } catch (error) {
    console.error('❌ Error initializing database:', error);
    process.exit(1);
  } finally {
    await sequelize.close();
  }
}

initializeDatabase(); 