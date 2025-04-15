import os
from dotenv import load_dotenv

load_dotenv()

# Fix for Render PostgreSQL URLs
def get_database_url():
    url = os.getenv('DATABASE_URL', 'postgresql://postgres:12345678@localhost:5432/accident_detection')
    # Render uses postgres:// but SQLAlchemy requires postgresql://
    if url and url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    return url

class Config:
    # PostgreSQL configuration
    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Secret key for session management
    SECRET_KEY = os.getenv('SECRET_KEY', '12345678')
    
    # Other configurations
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    pass

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:12345678@localhost:5432/accident_detection_test'