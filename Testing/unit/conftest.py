"""
Pytest configuration for Django tests
Pytest-django handles Django setup automatically when DJANGO_SETTINGS_MODULE is set
"""

import os
import sys

# Force pure-Python implementation of Protobuf to bypass Python 3.14 C-extension incompatibility
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
sys.modules["google._upb._message"] = None
sys.modules["google._upb"] = None

import pytest
