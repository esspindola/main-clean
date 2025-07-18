const { sequelize } = require('./src/config/database');
const User = require('./src/models/User');
const Product = require('./src/models/Product');
const Sale = require('./src/models/Sale');
const InventoryMovement = require('./src/models/InventoryMovement');
const seedData = require('./src/utils/seedData');

async function initializeDatabase() {
  try {
    console.log('🔄 Inicializando base de datos...');
    
    // Sincronizar modelos con la base de datos (sin asociaciones primero)
    await sequelize.sync({ force: true });
    console.log('✅ Tablas creadas exitosamente');
    
    // Configurar asociaciones después de crear las tablas
    require('./src/config/associations');
    console.log('✅ Asociaciones configuradas');
    
    // Poblar con datos de ejemplo
    console.log('🔄 Poblando con datos de ejemplo...');
    
    // Crear usuarios
    const users = await User.bulkCreate(seedData.users);
    console.log(`✅ ${users.length} usuarios creados`);
    
    // Crear productos
    const products = await Product.bulkCreate(seedData.products);
    console.log(`✅ ${products.length} productos creados`);
    
    // Crear movimientos de inventario iniciales
    const inventoryMovements = await InventoryMovement.bulkCreate(seedData.inventoryMovements);
    console.log(`✅ ${inventoryMovements.length} movimientos de inventario creados`);
    
    // Crear algunas ventas de ejemplo
    const sales = await Sale.bulkCreate(seedData.sales);
    console.log(`✅ ${sales.length} ventas de ejemplo creadas`);
    
    console.log('\n🎉 Base de datos inicializada exitosamente!');
    console.log('\n📋 Credenciales de ejemplo:');
    console.log('👤 Admin: admin@frontposw.com / admin12345678');
    console.log('👤 Usuario: user@frontposw.com / user12345678');
    console.log('\n🚀 Puedes iniciar el servidor con: npm start');
    
  } catch (error) {
    console.error('❌ Error al inicializar la base de datos:', error);
    process.exit(1);
  } finally {
    await sequelize.close();
  }
}

initializeDatabase(); 