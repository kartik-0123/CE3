import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# API Configuration
API_BASE_URL = 'http://localhost:5000/api'
API_TIMEOUT = 30  # seconds

# Flask Backend Configuration
FLASK_SECRET_KEY = 'your-secret-key-here'  # Change this in production
FLASK_DATABASE_URI = 'sqlite:///hello.db'

# Django Configuration
SECRET_KEY = 'django-insecure-your-secret-key-here'  # Change this in production
DEBUG = True

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Session Configuration
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True 