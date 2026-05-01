"""
Project views for managing file search stores and projects
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import sys
import os

# Add src to path to import Flask modules (temporarily)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))

from src.local_project_storage import get_local_project_storage
from src.optional_dependencies import LazyModuleProxy
from src.prompt_storage import get_prompt_storage

from .models import Project, SystemPrompt
from .serializers import ProjectSerializer, SystemPromptSerializer


gfs = LazyModuleProxy(
    "google_file_search",
    "Google File Search dependencies are not installed in this environment.",
)


def _user_can_access_project(project, user):
    """Return whether the current user can access the given project."""
    if not project or project.user_id is None:
        return True

    return bool(getattr(user, 'is_authenticated', False) and user.id == project.user_id)


def get_combined_stores(request=None):
    """Get list of projects for the current user from Django database"""
    if request and request.user.is_authenticated:
        projects = Project.objects.filter(user=request.user).order_by('-created_at')
    else:
        # Show projects without an owner for unauthenticated users (legacy behavior)
        projects = Project.objects.filter(user__isnull=True).order_by('-created_at')
    
    # Convert to store-like objects for template compatibility
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


@login_required
@require_http_methods(["GET"])
def list_projects(request):
    """List all projects/stores"""
    stores = get_combined_stores(request)
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
    user = request.user if request.user.is_authenticated else None
    
    if display_name:
        if storage_type == 'local':
            project_id = storage.create_project(display_name)
            # Also create Django model record
            Project.objects.create(
                project_id=project_id,
                display_name=display_name,
                storage_type='local',
                user=user
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
                storage_type='postgres',
                user=user
            )
        else:
            # Create Google File Search store
            try:
                store_id = gfs.create_new_file_search_store(display_name)
            except Exception as e:
                print(f"Warning: could not create Google File Search store: {e}")
                store_id = None
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
                    external_store_id=store_id,
                    user=user
                )
    
    stores = get_combined_stores(request)
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
            try:
                if project.storage_type == 'local':
                    storage.delete_project(project.project_id)
                elif project.storage_type == 'postgres':
                    from src.postgres_rag import cleanup_project_artifacts

                    document_names = sorted(project.documents.values_list('document_name', flat=True))
                    cleanup_project_artifacts(project.project_id, document_names)
                else:
                    # Delete from Google File Search
                    if project.external_store_id:
                        gfs.delete_file_search_store(project.external_store_id)
            except Exception as cleanup_error:
                print(f"Warning: external cleanup failed for {store_id}: {cleanup_error}")

            # Always delete the Django database record
            project.delete()
    except Exception as e:
        print(f"Error deleting project {store_id}: {e}")
    
    stores = get_combined_stores(request)
    return render(request, 'partials/project_list.html', {'stores': stores})


@require_http_methods(["GET", "POST"])
@csrf_exempt
def manage_prompt(request, store_id):
    """Get or set system prompt for a project"""
    project = Project.objects.filter(project_id=store_id).first()

    if not _user_can_access_project(project, getattr(request, 'user', None)):
        return JsonResponse({'error': 'Forbidden'}, status=403)

    if project and project.storage_type == 'postgres':
        if request.method == 'GET':
            prompt = getattr(project.system_prompt, 'content', '') if hasattr(project, 'system_prompt') else ''
            return JsonResponse({'prompt': prompt})

        content = request.POST.get('content', '')
        SystemPrompt.objects.update_or_create(
            project=project,
            defaults={'content': content}
        )
        return JsonResponse({'status': 'success', 'prompt': content})

    prompt_storage = get_prompt_storage()
    
    if request.method == 'GET':
        prompt = prompt_storage.get_prompt(store_id)
        return JsonResponse({'prompt': prompt})
    
    # POST - set prompt
    content = request.POST.get('content', '')
    prompt_storage.set_prompt(store_id, content)
    
    return JsonResponse({'status': 'success', 'prompt': content})
