import os
import django
from django.conf import settings
from django.template.loader import render_to_string
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.apps.my_rag_project.settings')
django.setup()

def check(tpl):
    try:
        render_to_string(tpl)
        print(f"SUCCESS: {tpl}")
    except Exception as e:
        print(f"FAILED: {tpl} - {type(e).__name__}: {str(e)}")

check('chat/chat.html')
check('evaluate/evaluate.html')
check('projects/admin.html')
check('partials/project_list.html')
check('partials/document_list.html')
