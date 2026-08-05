"""
Settings package for my_rag project.
Dynamically loads appropriate settings based on DJANGO_SETTINGS_MODULE environment variable.
"""


import os

# If this is a test run (pytest usually sets something or we can check sys.argv), inject dummy key
import sys
if 'pytest' in sys.modules or 'test' in sys.argv:
    if 'SECRET_KEY' not in os.environ:
        os.environ['SECRET_KEY'] = 'django-insecure-test-key-only'

# Determine which settings module to use

ENV = os.getenv('DJANGO_ENV', 'development')

if ENV == 'production':
    from .settings_prod import *
elif ENV == 'testing':
    from .settings_test import *
else:  # development (default)
    from .settings_dev import *
