import os

class Config:
    DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://user:testpass123@db:5432/tododb?options=-c client_encoding%3DUTF8')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'my_secret_key')

class TestConfig(Config):
    TESTING = True
    
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' 
    SQLALCHEMY_TRACK_MODIFICATIONS = False # 警告を避けるため
    
    WTF_CSRF_ENABLED = False 
    SECRET_KEY = 'test_secret_key_for_testing'