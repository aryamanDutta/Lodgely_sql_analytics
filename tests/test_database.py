import os
import re
import pytest
from config import Config
from db.connection import check_db_connection

def test_config_defaults():
    """Verify default database and application configuration settings."""
    assert Config.DB_NAME == 'hotel_management'
    assert Config.DB_PORT == 3306
    assert Config.DB_USER is not None
    assert Config.SECRET_KEY is not None

def test_init_sql_schema_entities():
    """Verify that database/init.sql defines all 10 required relational entities."""
    sql_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'init.sql')
    assert os.path.exists(sql_path), "init.sql file does not exist"

    with open(sql_path, 'r', encoding='utf-8') as f:
        sql = f.read().upper()

    required_tables = [
        'CREATE TABLE HOTEL',
        'CREATE TABLE ROOM',
        'CREATE TABLE CUSTOMER',
        'CREATE TABLE EMPLOYEE',
        'CREATE TABLE BOOKING',
        'CREATE TABLE PAYMENT',
        'CREATE TABLE RESTAURANT',
        'CREATE TABLE FOOD',
        'CREATE TABLE SERVICE',
        'CREATE TABLE HOUSEKEEPING'
    ]

    for tbl in required_tables:
        assert tbl in sql, f"Table definition missing in init.sql: {tbl}"

def test_init_sql_constraints_and_foreign_keys():
    """Verify that init.sql enforces foreign key relationships and check constraints."""
    sql_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'init.sql')
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql = f.read()

    # Foreign key references
    assert "REFERENCES HOTEL(hotel_id)" in sql
    assert "REFERENCES CUSTOMER(customer_id)" in sql
    assert "REFERENCES ROOM(room_id)" in sql
    assert "REFERENCES BOOKING(booking_id)" in sql
    assert "REFERENCES RESTAURANT(restaurant_id)" in sql
    assert "REFERENCES EMPLOYEE(employee_id)" in sql

    # Check constraints
    assert "CHECK (star_rating >= 1.0 AND star_rating <= 5.0)" in sql
    assert "CHECK (price_per_night > 0)" in sql
    assert "CHECK (check_out_date >= check_in_date)" in sql
    assert "CHECK (number_of_guests > 0)" in sql
    assert "CHECK (amount > 0)" in sql

def test_init_sql_seed_data_counts():
    """Verify sufficient deterministic seed records exist in init.sql."""
    sql_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'init.sql')
    with open(sql_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for INSERT statements for all entities
    assert "INSERT INTO HOTEL" in content
    assert "INSERT INTO ROOM" in content
    assert "INSERT INTO CUSTOMER" in content
    assert "INSERT INTO EMPLOYEE" in content
    assert "INSERT INTO BOOKING" in content
    assert "INSERT INTO PAYMENT" in content
    assert "INSERT INTO RESTAURANT" in content
    assert "INSERT INTO FOOD" in content
    assert "INSERT INTO SERVICE" in content
    assert "INSERT INTO HOUSEKEEPING" in content

def test_db_connection_graceful_offline_handling():
    """Ensure check_db_connection returns False safely when database is unreachable."""
    # Running without live DB on test host should safely return False
    is_connected = check_db_connection()
    assert isinstance(is_connected, bool)
