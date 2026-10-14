import os

class Config:
    """Base application configuration loaded from environment variables."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'cam5-hotel-mgmt-secure-key-2026')
    
    # Database Configuration
    # Defaults to 'db' when running inside Docker Compose, or 'localhost' / '127.0.0.1' locally
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_USER = os.environ.get('DB_USER', 'hotel_admin')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'hotel_secure_pwd_2026')
    DB_NAME = os.environ.get('DB_NAME', 'hotel_management')
    
    # Connection timeouts
    DB_CONNECT_TIMEOUT = int(os.environ.get('DB_CONNECT_TIMEOUT', 10))
    
    # Flask settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
