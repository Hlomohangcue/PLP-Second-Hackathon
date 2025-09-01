import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database configuration
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///flashcards.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    
    # Hugging Face API configuration
    HUGGING_FACE_API_TOKEN = os.environ.get('HUGGING_FACE_API_TOKEN')
    
    # API rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    
    # Session configuration
    SESSION_TIMEOUT_DAYS = 30
    
    # AI model configuration
    AVAILABLE_MODELS = [
        "https://api-inference.huggingface.co/models/gpt2",
        "https://api-inference.huggingface.co/models/facebook/bart-large-cnn",
        "https://api-inference.huggingface.co/models/distilbert-base-cased-distilled-squad",
        "https://api-inference.huggingface.co/models/google/flan-t5-small"
    ]
    
    # Content limits
    MIN_CONTENT_LENGTH = 50
    MAX_CONTENT_LENGTH = 2000
    DEFAULT_FLASHCARD_COUNT = 5
    
class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Log SQL queries in development

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_ECHO = False

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}