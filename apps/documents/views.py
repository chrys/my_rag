"""
Document views for managing indexed documents
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.utils.text import get_valid_filename
import sys
import os
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))

from local_project_storage import get_local_project_storage
from optional_dependencies import LazyModuleProxy
from urllib.parse import unquote

from .models import Document
from apps.projects.models import Project


SUPPORTED_TEXT_FILE_EXTENSIONS = {'.pdf', '.txt', '.md'}

gfs = LazyModuleProxy(
    "google_file_search",
    "Google File Search dependencies are not installed in this environment.",
)


def get_rag_engine(*args, **kwargs):
    from local_rag import get_rag_engine as local_get_rag_engine

    return local_get_rag_engine(*args, **kwargs)


def _sanitize_uploaded_filename(filename: str) -> str:
    """Return a filesystem-safe upload filename without requiring Werkzeug."""
    normalized_name = filename.replace("\\", "/").split("/")[-1].strip()
    if not normalized_name:
        return "upload"

    sanitized_name = get_valid_filename(normalized_name)
    return sanitized_name or "upload"


def _doc_adapter(doc):
    """Return a dict that matches the interface expected by document templates."""
    return {
        'name': doc.document_name,
        'display_name': doc.display_name or doc.document_name,
        'mime_type': doc.mime_type,
        'indexed_at': doc.indexed_at,
        'state': type('State', (), {'name': doc.state})(),
    }


@require_http_methods(["GET"])
def list_documents(request, store_id):
    """List documents in a project, returning an HTML partial."""
    doc_type = request.GET.get('type', 'admin')

    # Look up project by project_id in the Django database
    project = Project.objects.filter(project_id=store_id).first()

    if project:
        if project.storage_type == 'google':
            # For Google projects, fetch from the API using external_store_id
            documents = gfs.list_documents_in_store(project.external_store_id)
        else:
            # For local projects, use Django ORM
            docs_qs = Document.objects.filter(project=project)
            documents = [_doc_adapter(d) for d in docs_qs]
        
        project_name = project.display_name
        storage_type = project.storage_type
    else:
        # Fallback: project not in DB yet — try legacy local_project_storage
        storage = get_local_project_storage()
        local_projects = storage.list_projects()
        legacy = next((p for p in local_projects if p['id'] == store_id), None)
        if legacy:
            documents = [
                {
                    'name': doc_name,
                    'display_name': doc_name,
                    'mime_type': 'document',
                    'indexed_at': doc_info.get('indexed_at') if isinstance(doc_info, dict) else None,
                    'state': type('State', (), {'name': 'INDEXED'})(),
                }
                for doc_name, doc_info in (
                    ((d, legacy['documents'].get(d)) if isinstance(legacy['documents'], dict) else (d, {}))
                    for d in legacy.get('documents', []) if d
                )
            ]
            project_name = legacy['display_name']
            storage_type = 'local'
        else:
            documents = []
            project_name = store_id
            storage_type = 'unknown'

    if doc_type == 'evaluate':
        return render(request, 'partials/evaluate_document_items.html', {'documents': documents})

    return render(request, 'partials/document_list.html', {
        'documents': documents,
        'store_id': store_id,
        'project_name': project_name,
        'storage_type': storage_type,
        'url_prefix': '/rag',
    })


@require_http_methods(["POST"])
@csrf_exempt
def upload_document(request, store_id):
    """Upload and index a document"""
    storage = get_local_project_storage()
    
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file provided'}, status=400)
    
    file = request.FILES['file']
    if not file or file.name == '':
        return JsonResponse({'error': 'Invalid file'}, status=400)
    
    try:
        filename = _sanitize_uploaded_filename(file.name)
        file_ext = os.path.splitext(filename)[1].lower()

        if (store_id.startswith('rag_') or store_id.startswith('postgres_')) and file_ext not in SUPPORTED_TEXT_FILE_EXTENSIONS:
            return JsonResponse(
                {'error': f'Unsupported file type: {file_ext or "[none]"}. Supported file types are: .pdf, .txt, .md'},
                status=400,
            )
        
        # Save to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            for chunk in file.chunks():
                tmp.write(chunk)
            filepath = tmp.name
        
        try:
            if store_id.startswith('local_'):
                # Local project indexing
                rag_engine = get_rag_engine(store_id)
                success = rag_engine.index_document(filepath, filename)
                
                if success:
                    storage.add_document(store_id, filename)
                else:
                    os.unlink(filepath)
                    return JsonResponse({'error': 'Failed to index document'}, status=500)
            elif store_id.startswith('rag_') or store_id.startswith('postgres_'):
                # RAG project indexing
                from postgres_rag import PostgresRAGEngine
                from django.utils import timezone
                project = Project.objects.filter(project_id=store_id).first()

                try:
                    rag_engine = PostgresRAGEngine(store_id)
                    success = rag_engine.index_document(filepath, filename)
                except Exception as exc:
                    if project:
                        Document.objects.update_or_create(
                            project=project,
                            document_name=filename,
                            defaults={
                                'display_name': filename,
                                'state': 'FAILED',
                                'error_message': str(exc),
                                'indexed_at': None,
                            }
                        )
                    return JsonResponse({'error': f'Upload failed: {str(exc)}'}, status=500)
                
                if success:
                    if project:
                        Document.objects.update_or_create(
                            project=project,
                            document_name=filename,
                            defaults={
                                'display_name': filename,
                                'state': 'INDEXED',
                                'error_message': '',
                                'indexed_at': timezone.now(),
                            }
                        )
                else:
                    if project:
                        Document.objects.update_or_create(
                            project=project,
                            document_name=filename,
                            defaults={
                                'display_name': filename,
                                'state': 'FAILED',
                                'error_message': 'Failed to index document in RAG project',
                                'indexed_at': None,
                            }
                        )
                    return JsonResponse({'error': 'Failed to index document in RAG project'}, status=500)
            else:
                # Google store - look up the project to get the external_store_id
                project = Project.objects.filter(project_id=store_id).first()
                if project and project.external_store_id:
                    # Use the actual Google store ID
                    google_store_id = project.external_store_id
                else:
                    # Fallback to store_id (for backward compatibility)
                    google_store_id = store_id
                    
                gfs.add_document_to_store(google_store_id, filepath)
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)
        
        # Return updated documents list
        project = Project.objects.filter(project_id=store_id).first()
        if project and project.storage_type == 'google':
            # For Google projects, fetch from API
            documents = gfs.list_documents_in_store(project.external_store_id)
        elif project and project.storage_type == 'postgres':
            # For RAG projects, fetch from Django DB
            docs_qs = Document.objects.filter(project=project)
            documents = [_doc_adapter(d) for d in docs_qs]
        else:
            # For local projects, check local storage first
            local_projects = storage.list_projects()
            proj = next((p for p in local_projects if p['id'] == store_id), None)
            
            if proj:
                documents = [
                    {
                        'name': doc_name,
                        'display_name': doc_name,
                        'mime_type': 'document',
                        'indexed_at': doc_info.get('indexed_at') if isinstance(doc_info, dict) else None,
                        'state': type('State', (), {'name': 'INDEXED'})()
                    }
                    for doc_name, doc_info in (
                        ((d, proj['documents'].get(d)) if isinstance(proj['documents'], dict) else (d, {}))
                        for d in proj.get('documents', []) if d
                    )
                ]
            else:
                documents = []
        
        return render(request, 'partials/document_items.html', {
            'documents': documents,
            'store_id': store_id,
            'url_prefix': '/rag',
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'Upload failed: {str(e)}'}, status=500)


@require_http_methods(["DELETE"])
@csrf_exempt
def delete_document(request, document_id):
    """Delete a document"""
    storage = get_local_project_storage()
    document_id = unquote(document_id)
    # Strip trailing slash if any (from URL matching)
    document_id = document_id.rstrip('/')
    store_id = request.GET.get('store_id')
    
    try:
        if store_id and store_id.startswith('local_'):
            # Local document deletion
            rag_engine = get_rag_engine(store_id)
            success = rag_engine.delete_document(document_id)
            
            if success:
                storage.remove_document(store_id, document_id)
        elif store_id and (store_id.startswith('rag_') or store_id.startswith('postgres_')):
            project = Project.objects.filter(project_id=store_id).first()
            if project:
                from postgres_rag import PostgresRAGEngine
                rag_engine = PostgresRAGEngine(store_id, require_llm=False)
                rag_engine.delete_document(document_id)
                Document.objects.filter(project=project, document_name=document_id).delete()
        else:
            # Google document deletion - look up project to get external_store_id
            project = Project.objects.filter(project_id=store_id).first()
            if project and project.external_store_id:
                google_store_id = project.external_store_id
                gfs.delete_document_from_store(google_store_id, document_id)
            elif '/' in document_id:
                # Fallback: extract store from document_id if it contains the store reference
                parts = document_id.split('/')
                if len(parts) >= 2:
                    store_id_from_doc = parts[1]
                    gfs.delete_document_from_store(store_id_from_doc, document_id)
        
        # Return refreshed document list HTML for HTMX to swap in
        from django.http import HttpResponse
        response = HttpResponse(status=200)
        response['HX-Trigger'] = 'documentListChanged'
        return response
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
