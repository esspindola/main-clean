import pymysql
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

# MySQL connection config
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST','localhost'),
    'user': os.getenv('MYSQL_USER','root'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE'),
    'cursorclass': pymysql.cursors.DictCursor
}

# PostgreSQL connections config
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST','localhost'),
    'user': os.getenv('POSTGRES_USER','postgres'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'database': os.getenv('POSTGRES_DATABASE','zatobox_csm_db'),
    'port': int(os.getenv('POSTGRES_PORT','5432'))
}

def get_mysql_db():
    if not MYSQL_CONFIG['password']:
        raise Exception("MYSQL_PASSWORD enviroment variable is required")

    conn = pymysql.connect(**MYSQL_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

def get_postgres_db():
    if not POSTGRES_CONFIG['password']:
        raise Exception("POSTGRES_PASSWORD enviroment variable is required")

    conn = psycopg2.connect(**POSTGRES_CONFIG)
    try:
        yield conn
    finally:
        conn.close()

def get_db_connection(db_type: str=None):
    if db_type is None:
        db_type = os.getenv('DATABASE_TYPE', 'postgres')

    if db_type == "mysql":
        return get_mysql_db()
    return get_postgres_db()