"""
Project views for managing file search stores and projects
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import sys
import os

# Add src to path to import Flask modules (temporarily)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))

# TODO: These imports are disabled as part of Flask-to-Django migration
# import google_file_search as gfs
from local_project_storage import get_local_project_storage
from prompt_storage import get_prompt_storage

from .models import Project, SystemPrompt
from .serializers import ProjectSerializer, SystemPromptSerializer


def get_combined_stores():
    """Get combined list of Google and local projects"""
    storage = get_local_project_storage()
    
    # Get Google stores (commented out - Flask module)
    # google_stores = gfs.list_all_file_search_stores()
    google_stores = []
    
    # Get local projects and convert to store-like objects
    local_projects = storage.list_projects()
    local_stores = [
        type('Store', (), {
            'name': project['id'],
            'display_name': project['display_name'],
            'create_time': project['created_at'],
            'storage_type': 'local'
        })()
        for project in local_projects
    ]
    
    return google_stores + local_stores


@require_http_methods(["GET"])
def list_projects(request):
    """List all projects/stores"""
    stores = get_combined_stores()
    list_type = request.GET.get('type', 'admin')
    
    if list_type == 'chat':
        return render(request, 'partials/chat_project_list.html', {'stores': stores})
    elif list_type == 'evaluate':
        return render(request, 'partials/evaluate_project_list.html', {'stores': stores})
    
    return render(request, 'partials/project_list.html', {'stores': stores})


@require_http_methods(["POST"])
@csrf_exempt
def create_project(request):
    """Create a new project"""
    storage = get_local_project_storage()
    
    display_name = request.POST.get('display_name')
    storage_type = request.POST.get('storage_type', 'google')
    
    if display_name:
        if storage_type == 'local':
            storage.create_project(display_name)
        # else:
        #     gfs.create_new_file_search_store(display_name)
    
    stores = get_combined_stores()
    return render(request, 'partials/project_list.html', {'stores': stores})


@require_http_methods(["DELETE"])
@csrf_exempt
def delete_project(request, store_id):
    """Delete a project"""
    storage = get_local_project_storage()
    
    if store_id.startswith('local_'):
        storage.delete_project(store_id)
    # else:
    #     gfs.delete_file_search_store(store_id)
    
    stores = get_combined_stores()
    return render(request, 'partials/project_list.html', {'stores': stores})


@require_http_methods(["GET", "POST"])
@csrf_exempt
def manage_prompt(request, store_id):
    """Get or set system prompt for a project"""
    prompt_storage = get_prompt_storage()
    
    if request.method == 'GET':
        prompt = prompt_storage.get_prompt(store_id)
        return JsonResponse({'prompt': prompt})
    
    # POST - set prompt
    content = request.POST.get('content', '')
    prompt_storage.set_prompt(store_id, content)
    
    return JsonResponse({'status': 'success', 'prompt': content})
