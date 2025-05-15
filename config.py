class Config:
    """Base configuration for the application."""

    SECRET_KEY = "my_secret_key"
    SQLALCHEMY_DATABASE_URI = "postgresql://api_user:api_password@postgresql_api:5432/api_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True

    POSTGRES_RAW_CONFIG = {
        'host': 'postgresql_raw',
        'database': 'raw_db',
        'username': 'raw_user',
        'password': 'raw_password',
        'port': '5432'
    }

    POSTGRES_API_CONFIG = {
        'host': 'postgresql_api',
        'database': 'api_db',
        'username': 'api_user',
        'password': 'api_password',
        'port': '5432'
    }

    MONGODB_CONFIG = {
        'host': 'mongodb',
        'port': 27017,
        'username': 'mongo_user',
        'password': 'mongo_password',
        'database': 'api_db',
    }

class DevelopmentConfig(Config):
    """Development-specific configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production-specific configuration."""
    DEBUG = False