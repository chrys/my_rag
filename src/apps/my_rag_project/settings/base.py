"""
Base Django settings for my_rag project.
Common settings shared across all environments.
"""

import os
import sys

# Force pure-Python implementation of Protobuf to bypass Python 3.14 C-extension incompatibility
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
sys.modules["google._upb._message"] = None
sys.modules["google._upb"] = None

from pathlib import Path
from django.urls import reverse_lazy
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# Robustly find the project root by locating manage.py
current_dir = Path(__file__).resolve().parent
while not (current_dir / 'manage.py').exists() and current_dir.parent != current_dir:
    current_dir = current_dir.parent

if (current_dir / 'manage.py').exists():
    BASE_DIR = current_dir
else:
    # Fallback to the original logic
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent

# Add apps directory to Python path for imports
APPS_DIR = BASE_DIR / 'src' / 'apps'
sys.path.insert(0, str(APPS_DIR))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-key-change-in-production')

# Application definition
INSTALLED_APPS = [
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party
    'rest_framework',
    'corsheaders',
    
    # Local apps
    'src.apps.chat.apps.ChatConfig',
    'src.apps.projects.apps.ProjectsConfig',
    'src.apps.documents.apps.DocumentsConfig',
    'src.apps.evaluate.apps.EvaluateConfig',
    'src.apps.api.apps.ApiConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS middleware - must be before common
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'src.apps.my_rag_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'src.apps.my_rag_project.wsgi.application'

# Database - default to SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

# Media files (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'uploads'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# File upload settings - matching Flask's 20MB max
DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024  # 20MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024  # 20MB

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Application settings from Flask config
ALLOW_FILE_UPLOADS = True
JSON_SORT_KEYS = False

# Auth routes for the dashboard live under /rag/.
LOGIN_URL = '/rag/accounts/login/'
LOGIN_REDIRECT_URL = '/rag/'

# Remote PostgreSQL configuration for local RAG projects (VPS)
REMOTE_POSTGRES_CONFIG = {
    'NAME': os.getenv('postgres_name', 'rag_dashboard'),
    'USER': os.getenv('postgres_user', 'rag_user2'),
    'PASSWORD': os.getenv('postgres_password', 'ThinkRAG2026!'),
    'HOST': os.getenv('postgres_host', 'localhost'),
    'PORT': os.getenv('postgres_port', '5432'),
}

# django-unfold administration configuration
UNFOLD = {
    "SITE_TITLE": "RAG Dashboard",
    "SITE_HEADER": "RAG Administration",
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Navigation",
                "items": [
                    {
                        "title": "Projects",
                        "icon": "folder",
                        "link": reverse_lazy("custom_admin:projects_project_changelist"),
                    },
                    {
                        "title": "Chat Workflow",
                        "icon": "chat",
                        "link": reverse_lazy("custom_admin:chat-workflow"),
                    },
                    {
                        "title": "Evaluation Workflow",
                        "icon": "star",
                        "link": reverse_lazy("custom_admin:evaluation-workflow"),
                    },
                ],
            },
        ],
    },
}


