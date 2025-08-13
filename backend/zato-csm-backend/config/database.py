import pymysql
import psycopg2
import psycopg2.extras

# MySQL connection config
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'yourpassword',
    'database': 'zatobox',
    'cursorclass': pymysql.cursors.DictCursor
}

# PostgreSQL connections config
POSTGRES_CONFIG = {
    'host': 'localhost',
    'user': 'postgres',
    'password': 'mateo2510',
    'database': 'zatobox_csm_db',
    'port': 5432
}

def get_mysql_db():
    conn = pymysql.connect(**MYSQL_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

def get_postgres_db():
    conn = psycopg2.connect(**POSTGRES_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

def get_db_connection(db_type: str='postgres'):
    db_type = db_type
    if db_type == "mysql":
        return get_mysql_db()
    return get_postgres_db()