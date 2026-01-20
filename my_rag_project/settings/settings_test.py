"""
Django settings for testing environment.
Extends base settings with testing-specific overrides.
"""

from .base import *

# Override testing-specific settings
DEBUG = True

ALLOWED_HOSTS = ['*']

# Use in-memory database for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# CORS settings - allow all origins in testing
CORS_ALLOW_ALL_ORIGINS = True

# Disable migrations for faster tests (optional)
# Uncomment if you want to skip migrations during testing
# class DisableMigrations:
#     def __contains__(self, item):
#         return True
#     def __getitem__(self, item):
#         return None
# MIGRATION_MODULES = DisableMigrations()

# Email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Password hasher for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}
