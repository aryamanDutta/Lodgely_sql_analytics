import logging
import pymysql
import pymysql.cursors
from config import Config

logger = logging.getLogger(__name__)

def get_db_connection():
    """Establish and return a MySQL connection using PyMySQL with DictCursor."""
    try:
        connection = pymysql.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=Config.DB_CONNECT_TIMEOUT,
            autocommit=False
        )
        return connection
    except pymysql.MySQLError as e:
        logger.error("Database connection failure to %s:%s - %s", Config.DB_HOST, Config.DB_PORT, str(e))
        raise

def query_all(sql, params=None):
    """Execute a parameterized SELECT query and return all matching rows as dictionaries."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            results = cursor.fetchall()
            return results
    finally:
        conn.close()

def query_one(sql, params=None):
    """Execute a parameterized SELECT query and return a single row dictionary (or None)."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            result = cursor.fetchone()
            return result
    finally:
        conn.close()

from contextlib import contextmanager

def execute_commit(sql, params=None):
    """Execute an INSERT, UPDATE, or DELETE statement with transaction commit."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params or ())
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        logger.error("Error executing statement: %s", str(e))
        raise
    finally:
        conn.close()

@contextmanager
def transaction_context():
    """Context manager for multi-statement atomic transactions.
    Yields a cursor. Automatically commits on successful block execution,
    rolls back on error, and guarantees connection return.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error("Transaction rolled back due to error: %s", str(e))
        raise
    finally:
        conn.close()

def check_db_connection():
    """Test if database is reachable and hotel_management database is initialized."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 AS ok")
            row = cursor.fetchone()
            return row is not None and row.get('ok') == 1
    except Exception as e:
        logger.warning("Database health check failed: %s", str(e))
        return False
    finally:
        try:
            conn.close()
        except Exception:
            pass

def init_db_from_file(sql_file_path):
    """Execute an SQL initialization script with multiple statements."""
    conn = pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        charset='utf8mb4',
        client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS
    )
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        with conn.cursor() as cursor:
            cursor.execute(sql_script)
            conn.commit()
        logger.info("Successfully executed SQL script: %s", sql_file_path)
    finally:
        conn.close()
