"""
Chat views for handling conversations
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import markdown
import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))

# TODO: These imports are disabled as part of Flask-to-Django migration
# import google_file_search as gfs
from local_project_storage import get_local_project_storage
from local_rag import get_rag_engine
from prompt_storage import get_prompt_storage

from .models import ChatMessage


@require_http_methods(["POST"])
@csrf_exempt
def chat(request):
    """Handle chat messages and generate responses"""
    try:
        data = json.loads(request.body)
        store_id = data.get('store_id')
        query = data.get('query')
        system_prompt = data.get('system_prompt', '')
        
        if not store_id or not query:
            return JsonResponse({'error': 'Missing store_id or query'}, status=400)
        
        # Get prompt if not provided
        if not system_prompt:
            prompt_storage = get_prompt_storage()
            system_prompt = prompt_storage.get_prompt(store_id)
        
        # Query the appropriate backend
        if store_id.startswith('local_'):
            rag_engine = get_rag_engine(store_id)
            bot_response = rag_engine.query(query, system_prompt=system_prompt)
        else:
            bot_response = gfs.ask_store_question(
                store_id,
                query,
                system_prompt=system_prompt
            )
        
        # Convert markdown to HTML
        bot_response_html = markdown.markdown(bot_response)
        
        # Store in database if user is authenticated
        if request.user.is_authenticated:
            ChatMessage.objects.create(
                project_id=store_id,  # This will need adjustment when Project model is populated
                user=request.user,
                message_type='user',
                content=query
            )
            ChatMessage.objects.create(
                project_id=store_id,
                user=request.user,
                message_type='assistant',
                content=bot_response,
                response_html=bot_response_html
            )
        
        return JsonResponse({
            'user_message': query,
            'bot_response': bot_response,
            'bot_response_html': bot_response_html
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)
