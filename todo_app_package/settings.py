import os

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://user:testpass123@db:5432/tododb?options=-c client_encoding%3DUTF8')
SQLALCHEMY_DATABASE_URI = DATABASE_URL
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = os.environ.get('SECRET_KEY', 'my_secret_key')