"""
Configuration management for ImpactBridge
Supports multiple environments (development, production, testing)
"""

import os
from datetime import timedelta


class Config:
    """Base configuration"""
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production-immediately'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///impactbridge.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Application
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max request size
    
    # Pagination
    CASES_PER_PAGE = 50
    VOLUNTEERS_PER_PAGE = 50


class DevelopmentConfig(Config):
    """Development configuration"""
    
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = False  # Set to True to see SQL queries


class ProductionConfig(Config):
    """Production configuration"""
    
    DEBUG = False
    TESTING = False
    
    # Security - enforce in production
    SESSION_COOKIE_SECURE = True  # Requires HTTPS
    
    # Database - use PostgreSQL in production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://user:password@localhost/impactbridge'
    
    # Require secret key in production
    if not os.environ.get('SECRET_KEY'):
        raise ValueError('SECRET_KEY environment variable must be set in production')


class TestingConfig(Config):
    """Testing configuration"""
    
    DEBUG = False
    TESTING = True
    
    # Use in-memory database for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """
    Get configuration for specified environment
    
    Args:
        env: Environment name (development, production, testing)
        
    Returns:
        Config class
    """
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    
    return config.get(env, config['default'])
