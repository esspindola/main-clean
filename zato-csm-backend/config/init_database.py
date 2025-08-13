from config.database import get_db_connection

def create_tables_sql(db_type: str='postgres'):
    return """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        full_name VARCHAR(255) NOT NULL,
        phone VARCHAR(30),
        address VARCHAR(255),
        role VARCHAR(20) DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_updated TIMESTAMP DEFAULT NOW()
    );
    
    CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        price DECIMAL(10,2) NOT NULL,
        stock INT NOT NULL,
        category VARCHAR(100),
        images TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_updated TIMESTAMP DEFAULT NOW()
    );
        
    CREATE TABLE IF NOT EXISTS inventory(
        id SERIAL PRIMARY KEY,
        product_id INT NOT NULL,
        product_name VARCHAR(255),
        quantity INT NOT NULL,
        min_stock INT DEFAULT 0,
        last_updated TIMESTAMP DEFAULT NOW(),
        FOREIGN KEY (product_id) REFERENCES products(id)
    );
    
    CREATE TABLE IF NOT EXISTS sales(
        id SERIAL PRIMARY KEY,
        items TEXT,
        total DECIMAL(10,2) NOT NULL,
        payment_method VARCHAR(50),
        user_id INT,
        status VARCHAR(20) DEFAULT 'completed',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """

def init_database():
    db_gen = get_db_connection()
    db = next(db_gen)

    try:
        cursor = db.cursor()
        
        # Executar cada statement separadamente
        sql_statements = create_tables_sql().split(';')
        # inject_data = default_data().split(';')
        
        for statement in sql_statements:
            if statement.strip():
                cursor.execute(statement.strip())

        db.commit()
        print("✅ Database initialized successfully!")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        db.close()