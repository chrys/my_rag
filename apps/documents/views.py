"""
Document views for managing indexed documents
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from werkzeug.utils import secure_filename
import sys
import os
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))

# TODO: These imports are disabled as part of Flask-to-Django migration
# import google_file_search as gfs
from local_project_storage import get_local_project_storage
from local_rag import get_rag_engine
from urllib.parse import unquote

from .models import Document


@require_http_methods(["GET"])
def list_documents(request, store_id):
    """List documents in a project"""
    storage = get_local_project_storage()
    doc_type = request.GET.get('type', 'admin')
    
    if store_id.startswith('local_'):
        # Local project documents
        local_projects = storage.list_projects()
        project = next((p for p in local_projects if p['id'] == store_id), None)
        
        if not project:
            return JsonResponse({'error': 'Project not found'}, status=404)
        
        documents = [
            {
                'name': doc_name,
                'display_name': doc_name,
                'mime_type': 'document',
                'indexed_at': doc_info.get('indexed_at') if isinstance(doc_info, dict) else None,
                'state': type('State', (), {'name': 'INDEXED'})()
            }
            for doc_name, doc_info in (
                ((d, project['documents'].get(d)) if isinstance(project['documents'], dict) else (d, {}))
                for d in project.get('documents', []) if d
            )
        ]
        
        if doc_type == 'evaluate':
            return render(request, 'partials/evaluate_document_items.html', {'documents': documents})
        
        return render(request, 'partials/document_list.html', {
            'documents': documents,
            'store_id': store_id,
            'project_name': project['display_name'],
            'storage_type': 'local'
        })
    else:
        # Google store documents
        documents = gfs.list_documents_in_store(store_id)
        project_name = "Project Documents"
        
        stores = gfs.list_all_file_search_stores()
        for store in stores:
            if store.name == store_id:
                project_name = store.display_name
                break
        
        if doc_type == 'evaluate':
            return render(request, 'partials/evaluate_document_items.html', {'documents': documents})
        
        return render(request, 'partials/document_list.html', {
            'documents': documents,
            'store_id': store_id,
            'project_name': project_name,
            'storage_type': 'google'
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
        filename = secure_filename(file.name)
        
        # Save to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
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
            else:
                # Google store
                gfs.add_document_to_store(store_id, filepath)
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)
        
        # Return updated documents list
        local_projects = storage.list_projects()
        project = next((p for p in local_projects if p['id'] == store_id), None)
        
        if project:
            documents = [
                {
                    'name': doc_name,
                    'display_name': doc_name,
                    'mime_type': 'document',
                    'indexed_at': doc_info.get('indexed_at') if isinstance(doc_info, dict) else None,
                    'state': type('State', (), {'name': 'INDEXED'})()
                }
                for doc_name, doc_info in (
                    ((d, project['documents'].get(d)) if isinstance(project['documents'], dict) else (d, {}))
                    for d in project.get('documents', []) if d
                )
            ]
        else:
            documents = gfs.list_documents_in_store(store_id)
        
        return render(request, 'partials/document_items.html', {'documents': documents})
    
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
    store_id = request.GET.get('store_id')
    
    try:
        if store_id and store_id.startswith('local_'):
            # Local document deletion
            rag_engine = get_rag_engine(store_id)
            success = rag_engine.delete_document(document_id)
            
            if success:
                storage.remove_document(store_id, document_id)
        else:
            # Google document deletion
            if '/' in document_id:
                parts = document_id.split('/')
                if len(parts) >= 2:
                    store_id_from_doc = parts[1]
                    gfs.delete_document_from_store(store_id_from_doc, document_id)
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
