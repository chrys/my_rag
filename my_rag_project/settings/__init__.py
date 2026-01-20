"""
Settings package for my_rag project.
Dynamically loads appropriate settings based on DJANGO_SETTINGS_MODULE environment variable.
"""

import os

# Determine which settings module to use
ENV = os.getenv('DJANGO_ENV', 'development')

if ENV == 'production':
    from .settings_prod import *
elif ENV == 'testing':
    from .settings_test import *
else:  # development (default)
    from .settings_dev import *
