# config.py - Configuration mise à jour avec Pandemetrix_ML
import os

class Config:
    """Base configuration for the application."""

    SECRET_KEY = os.getenv("SECRET_KEY", "my_secret_key")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", "postgresql://api_user:api_password@postgresql_api:5432/api_db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    # Configuration Pandemetrix_ML (service externe)
    PANDEMETRIX_ML_URL = os.getenv("PANDEMETRIX_ML_URL", "http://localhost:5001/api/v1/covid")
    PANDEMETRIX_ML_TIMEOUT = int(os.getenv("PANDEMETRIX_ML_TIMEOUT", "30"))

    POSTGRES_RAW_CONFIG = {
        'host': os.getenv("POSTGRES_RAW_HOST", "postgresql_raw"),
        'database': os.getenv("POSTGRES_RAW_DB", "raw_db"),
        'username': os.getenv("POSTGRES_RAW_USER", "raw_user"),
        'password': os.getenv("POSTGRES_RAW_PASSWORD", "raw_password"),
        'port': os.getenv("POSTGRES_RAW_PORT", "5432")
    }

    POSTGRES_API_CONFIG = {
        'host': os.getenv("POSTGRES_API_HOST", "postgresql_api"),
        'database': os.getenv("POSTGRES_API_DB", "api_db"),
        'username': os.getenv("POSTGRES_API_USER", "api_user"),
        'password': os.getenv("POSTGRES_API_PASSWORD", "api_password"),
        'port': os.getenv("POSTGRES_API_PORT", "5432")
    }

    MONGODB_CONFIG = {
        'host': os.getenv("MONGODB_HOST", "mongodb"),
        'port': int(os.getenv("MONGODB_PORT", "27017")),
        'username': os.getenv("MONGODB_USER", "mongo_user"),
        'password': os.getenv("MONGODB_PASSWORD", "mongo_password"),
        'database': os.getenv("MONGODB_DATABASE", "api_db"),
    }

class DevelopmentConfig(Config):
    """Development-specific configuration."""
    DEBUG = True
    # En développement, utiliser localhost pour Pandemetrix_ML
    PANDEMETRIX_ML_URL = os.getenv("PANDEMETRIX_ML_URL", "http://localhost:5001/api/v1/covid")

class ProductionConfig(Config):
    """Production-specific configuration."""
    DEBUG = False
    # En production, utiliser le nom du service Docker
    PANDEMETRIX_ML_URL = os.getenv("PANDEMETRIX_ML_URL", "http://pandemetrix-ml:5000/api/v1/covid")