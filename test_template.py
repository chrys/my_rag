import os
import django
from django.conf import settings
from django.template.loader import render_to_string

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.apps.my_rag_project.settings')
django.setup()

try:
    render_to_string('chat/chat.html')
    print("SUCCESS")
except Exception as e:
    print("FAILED:", type(e).__name__, str(e))
