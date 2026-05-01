"""
Django settings entry point for my_rag_project.

This module imports settings from the appropriate settings module in my_rag_project/settings/
based on the DJANGO_ENV environment variable (or defaults to development).

For development: DJANGO_ENV=development
For production: DJANGO_ENV=production
For testing: DJANGO_ENV=testing
"""

# Import all settings from the settings package
from src.apps.my_rag_project.settings import *  # noqa
