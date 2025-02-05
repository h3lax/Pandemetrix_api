class Config:
    """Base configuration for the application."""

    SECRET_KEY = "my_secret_key"  # You can keep this for Flask sessions if needed
    SQLALCHEMY_DATABASE_URI = "postgresql://api_user:api_password@postgresql_api:5432/api_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True  # Set to False in production

class DevelopmentConfig(Config):
    """Development-specific configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production-specific configuration."""
    DEBUG = False
