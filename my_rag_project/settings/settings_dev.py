"""
Django settings for development environment.
Extends base settings with development-specific overrides.
"""

from .base import *

# Override development-specific settings
DEBUG = True

ALLOWED_HOSTS = ['*']

# CORS settings - allow all origins in development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

CORS_ALLOW_ALL_ORIGINS = True

# For development, show all settings
DEBUG_PROPAGATE_EXCEPTIONS = True

# Development database (can override with environment variable if needed)
# DATABASES['default'] inherited from base.py (SQLite)

# Email backend for development (console output)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Enable Django Debug Toolbar if available
try:
    import debug_toolbar
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']
except ImportError:
    pass
