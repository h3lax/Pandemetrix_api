class Config:
    """Base configuration for the application."""

    SECRET_KEY = "my_secret_key"  # You can keep this for Flask sessions if needed
    SQLALCHEMY_DATABASE_URI = "postgresql://metabase:metabase_password@localhost:5431/metabase"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True  # Set to False in production

class DevelopmentConfig(Config):
    """Development-specific configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production-specific configuration."""
    DEBUG = False
