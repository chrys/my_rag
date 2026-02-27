"""
Project views for managing file search stores and projects
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import sys
import os

# Add src to path to import Flask modules (temporarily)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))

import google_file_search as gfs
from local_project_storage import get_local_project_storage
from prompt_storage import get_prompt_storage

from .models import Project, SystemPrompt
from .serializers import ProjectSerializer, SystemPromptSerializer


def get_combined_stores():
    """Get combined list of Google and local projects from Django database"""
    # Get all projects from Django database
    projects = Project.objects.all().order_by('-created_at')
    
    # Convert to store-like objects for template compatibility
    # Always use project_id as the identifier to avoid issues with slashes in external_store_id
    stores = [
        type('Store', (), {
            'name': project.project_id,  # Use project_id consistently for both types
            'display_name': project.display_name,
            'create_time': project.created_at,
            'storage_type': project.storage_type
        })()
        for project in projects
    ]
    
    return stores


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
            project_id = storage.create_project(display_name)
            # Also create Django model record
            Project.objects.create(
                project_id=project_id,
                display_name=display_name,
                storage_type='local'
            )
        elif storage_type == 'postgres':
            from datetime import datetime
            import time
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            microseconds = int(time.time() * 1000000) % 1000000
            safe_name = display_name.lower().replace(' ', '_')[:30]
            project_id = f"postgres_{timestamp}_{microseconds}_{safe_name}"
            Project.objects.create(
                project_id=project_id,
                display_name=display_name,
                storage_type='postgres'
            )
        else:
            # Create Google File Search store
            store_id = gfs.create_new_file_search_store(display_name)
            if store_id:
                # Create Django model record with external store ID
                from datetime import datetime
                import time
                # Use timestamp with microseconds and counter to ensure uniqueness
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                microseconds = int(time.time() * 1000000) % 1000000
                safe_name = display_name.lower().replace(' ', '_')[:30]
                project_id = f"google_{timestamp}_{microseconds}_{safe_name}"
                Project.objects.create(
                    project_id=project_id,
                    display_name=display_name,
                    storage_type='google',
                    external_store_id=store_id
                )
    
    stores = get_combined_stores()
    return render(request, 'partials/project_list.html', {'stores': stores})


@require_http_methods(["DELETE"])
@csrf_exempt
def delete_project(request, store_id):
    """Delete a project"""
    storage = get_local_project_storage()
    
    # Try to find the project in Django database
    try:
        # Find by project_id or external_store_id
        project = Project.objects.filter(
            models.Q(project_id=store_id) | models.Q(external_store_id=store_id)
        ).first()
        
        if project:
            if project.storage_type == 'local':
                storage.delete_project(project.project_id)
            elif project.storage_type == 'postgres':
                # Postgres deletion logic: can drop embeddings or let them persist
                # We will implement embedding cleanup later if needed, for now just delete the project record
                pass
            else:
                # Delete from Google File Search
                if project.external_store_id:
                    gfs.delete_file_search_store(project.external_store_id)
            
            # Delete from Django database
            project.delete()
    except Exception as e:
        print(f"Error deleting project {store_id}: {e}")
    
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
