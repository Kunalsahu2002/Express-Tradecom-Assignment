"""
Application configuration classes.

All secrets and credentials are read from environment variables (loaded
from .env by python-dotenv). Nothing is hardcoded.
"""

import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load .env early so class-level attributes can read env vars at import time
load_dotenv()


class Config:
    """Base configuration."""

    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret-key')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'fallback-jwt-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Build MySQL connection string from individual env vars
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME', 'users')

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True


class TestingConfig(Config):
    """Testing configuration — uses a separate test database."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DATABASE_URI',
        'sqlite:///:memory:'
    )


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False


# Config selector mapping
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}
