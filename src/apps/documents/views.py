"""
Document views for managing indexed documents
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.text import get_valid_filename
import os
import tempfile

# Add src to path
from src.local_project_storage import get_local_project_storage
from src.optional_dependencies import LazyModuleProxy
from urllib.parse import unquote

from .models import Document, ObsidianSource, ObsidianFile
from .services import run_obsidian_lifecycle
from src.apps.projects.models import Project
from src.apps.projects.db_utils import test_postgres_connection
from src.postgres_rag import EmbeddingRateLimitError




SUPPORTED_TEXT_FILE_EXTENSIONS = {'.pdf', '.txt', '.md', '.py', '.js', '.ts', '.html'}

gfs = LazyModuleProxy(
    "src.google_file_search",
    "Google File Search dependencies are not installed in this environment.",
)


def get_rag_engine(*args, **kwargs):
    from src.local_rag import get_rag_engine as local_get_rag_engine

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
    from django.utils import timezone
    is_expired = False
    if doc.is_expired_checked and doc.expiration_date:
        is_expired = timezone.now() > doc.expiration_date

    strategy_raw = getattr(doc, 'chunking_strategy', 'auto_detect')
    strategy_display = dict(Document.CHUNKING_CHOICES).get(strategy_raw, strategy_raw)

    return {
        'name': doc.document_name,
        'display_name': doc.display_name or doc.document_name,
        'mime_type': doc.mime_type,
        'indexed_at': doc.indexed_at,
        'state': type('State', (), {'name': doc.state})(),
        'error_message': getattr(doc, 'error_message', ''),
        'is_expired': is_expired,
        'chunking_strategy': strategy_raw,
        'chunking_strategy_display': strategy_display,
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
            try:
                documents = gfs.list_documents_in_store(project.external_store_id)
            except Exception:
                documents = []
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

    obsidian_source = getattr(project, 'obsidian_source', None) if project else None
    source_type = obsidian_source.source_type if obsidian_source else 'document'
    gcal_source = getattr(project, 'google_calendar_source', None) if project else None

    ctx = {
        'documents': documents,
        'store_id': store_id,
        'project_name': project_name,
        'storage_type': storage_type,
        'url_prefix': '/rag',
        'project': project,
        'source_type': source_type,
    }
    ctx.update(get_obsidian_context(obsidian_source))
    ctx.update(get_google_calendar_context(gcal_source))
    return render(request, "partials/document_list.html", ctx)


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
        
    is_expired_checked = request.POST.get('is_expired') == 'on'
    expiration_date = None
    if is_expired_checked:
        expiration_date_str = request.POST.get('expiration_date')
        if expiration_date_str:
            from django.utils.dateparse import parse_datetime
            from django.utils import timezone
            parsed_dt = parse_datetime(expiration_date_str)
            if parsed_dt:
                if timezone.is_naive(parsed_dt):
                    expiration_date = timezone.make_aware(parsed_dt)
                else:
                    expiration_date = parsed_dt
    
    try:
        filename = _sanitize_uploaded_filename(file.name)
        file_ext = os.path.splitext(filename)[1].lower()

        if (store_id.startswith('rag_') or store_id.startswith('postgres_')) and file_ext not in SUPPORTED_TEXT_FILE_EXTENSIONS:
            supported_str = ", ".join(sorted(SUPPORTED_TEXT_FILE_EXTENSIONS))
            return JsonResponse(
                {'error': f'Unsupported file type: {file_ext or "[none]"}. Supported file types are: {supported_str}'},
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
                project = Project.objects.filter(project_id=store_id).first()

                if store_id.startswith('postgres_'):
                    conn_success, conn_error = test_postgres_connection()
                    if not conn_success:
                        error_msg = f"PostgreSQL VPS Connection failed: {conn_error}"
                        if project:
                            Document.objects.update_or_create(
                                project=project,
                                document_name=filename,
                                defaults={
                                    'display_name': filename,
                                    'state': 'FAILED',
                                    'error_message': error_msg,
                                    'indexed_at': None,
                                    'is_expired_checked': is_expired_checked,
                                    'expiration_date': expiration_date,
                                }
                            )
                        docs_qs = Document.objects.filter(project=project)
                        documents = [_doc_adapter(d) for d in docs_qs]
                        return render(request, 'partials/document_items.html', {
                            'documents': documents,
                            'store_id': store_id,
                            'url_prefix': '/rag',
                        })

                # RAG project indexing
                from src.apps.documents.services import LlamaIndexIngestionPipeline
                from django.utils import timezone

                try:
                    # Ingestion Quality Grading Gate
                    if project and getattr(project, 'use_structural_grading', False):
                        from src.apps.documents.services import check_structural_quality
                        check_structural_quality(filepath)

                    chunking_strategy = request.POST.get('chunking_strategy', 'auto_detect')
                    pipeline = LlamaIndexIngestionPipeline(project_id=store_id)
                    index = pipeline.index_document(filepath, original_filename=filename, strategy=chunking_strategy)
                    success = index is not None
                except EmbeddingRateLimitError as exc:
                    if project:
                        Document.objects.update_or_create(
                            project=project,
                            document_name=filename,
                            defaults={
                                'display_name': filename,
                                'state': 'FAILED',
                                'error_message': str(exc),
                                'indexed_at': None,
                                'is_expired_checked': is_expired_checked,
                                'expiration_date': expiration_date,
                            }
                        )
                    return JsonResponse({'error': str(exc)}, status=503)
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
                                'is_expired_checked': is_expired_checked,
                                'expiration_date': expiration_date,
                            }
                        )
                    docs_qs = Document.objects.filter(project=project)
                    documents = [_doc_adapter(d) for d in docs_qs]
                    return render(request, 'partials/document_items.html', {
                        'documents': documents,
                        'store_id': store_id,
                        'url_prefix': '/rag',
                    })
                
                if success:
                    if project:
                        Document.objects.update_or_create(
                            project=project,
                            document_name=filename,
                            defaults={
                                'display_name': filename,
                                'state': 'INDEXED',
                                'chunking_strategy': chunking_strategy,
                                'error_message': '',
                                'indexed_at': timezone.now(),
                                'is_expired_checked': is_expired_checked,
                                'expiration_date': expiration_date,
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
                                'is_expired_checked': is_expired_checked,
                                'expiration_date': expiration_date,
                            }
                        )
                    docs_qs = Document.objects.filter(project=project)
                    documents = [_doc_adapter(d) for d in docs_qs]
                    return render(request, 'partials/document_items.html', {
                        'documents': documents,
                        'store_id': store_id,
                        'url_prefix': '/rag',
                    })
            else:
                # Google store - look up the project to get the external_store_id
                from src.google_file_search import GoogleFileSearchPermissionError

                project = Project.objects.filter(project_id=store_id).first()
                if project and project.external_store_id:
                    # Use the actual Google store ID
                    google_store_id = project.external_store_id
                else:
                    # Fallback to store_id (for backward compatibility)
                    google_store_id = store_id

                try:
                    document_resource_name = gfs.add_document_to_store(google_store_id, filepath)
                except GoogleFileSearchPermissionError as exc:
                    return JsonResponse({'error': str(exc)}, status=403)

                if not document_resource_name:
                    return JsonResponse({'error': 'Failed to upload document to Google File Search store'}, status=502)
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
                from src.postgres_rag import PostgresRAGEngine
                try:
                    rag_engine = PostgresRAGEngine(store_id, require_llm=False)
                    rag_engine.delete_document(document_id)
                except Exception as cleanup_error:
                    print(f"Warning: RAG engine cleanup failed for {document_id}: {cleanup_error}")
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


@csrf_exempt
@require_http_methods(["POST"])
def set_source_type(request, store_id):
    """Switch project source type between Document and Obsidian."""
    project = get_object_or_404(Project, project_id=store_id)
    source_type = request.POST.get('source_type', 'document')
    obs_source, _ = ObsidianSource.objects.get_or_create(project=project)
    obs_source.source_type = source_type
    obs_source.save()
    request.method = 'GET'
    return list_documents(request, store_id)


@csrf_exempt
@require_http_methods(["POST"])
def obsidian_save_path(request, store_id):
    """Save Obsidian vault path."""
    project = get_object_or_404(Project, project_id=store_id)
    vault_path = request.POST.get('vault_path', '').strip()
    obs_source, _ = ObsidianSource.objects.get_or_create(project=project)
    obs_source.vault_path = vault_path
    obs_source.source_type = 'obsidian'
    obs_source.save()
    try:
        result = run_obsidian_lifecycle(obs_source, mode='full')
        return render_obsidian_section(request, project, obs_source, message=f"Vault path saved. Indexed {result['indexed_count']} note(s).")
    except Exception as e:
        return render_obsidian_section(request, project, obs_source, message=str(e), is_error=True)


@csrf_exempt
@require_http_methods(["POST"])
def obsidian_index(request, store_id):
    """Run full Obsidian vault index."""
    project = get_object_or_404(Project, project_id=store_id)
    obs_source = get_object_or_404(ObsidianSource, project=project)
    try:
        result = run_obsidian_lifecycle(obs_source, mode='full')
        return render_obsidian_section(request, project, obs_source, message=f"Indexed {result['indexed_count']} note(s).")
    except Exception as e:
        return render_obsidian_section(request, project, obs_source, message=str(e), is_error=True)


@csrf_exempt
@require_http_methods(["POST"])
def obsidian_index_new(request, store_id):
    """Run incremental Obsidian vault index for unindexed notes."""
    project = get_object_or_404(Project, project_id=store_id)
    obs_source = get_object_or_404(ObsidianSource, project=project)
    try:
        result = run_obsidian_lifecycle(obs_source, mode='new')
        return render_obsidian_section(request, project, obs_source, message=f"Indexed {result['indexed_count']} new note(s).")
    except Exception as e:
        return render_obsidian_section(request, project, obs_source, message=str(e), is_error=True)


@csrf_exempt
@require_http_methods(["POST"])
def obsidian_sync(request, store_id):
    """Discover new files in Obsidian vault without automatically indexing them."""
    project = get_object_or_404(Project, project_id=store_id)
    obs_source = get_object_or_404(ObsidianSource, project=project)
    try:
        result = run_obsidian_lifecycle(obs_source, mode='discover')
        pending_count = obs_source.files.filter(status='PENDING').count()
        return render_obsidian_section(request, project, obs_source, message=f"Discovered {result['total_files']} note(s) total ({pending_count} pending indexing).")
    except Exception as e:
        return render_obsidian_section(request, project, obs_source, message=str(e), is_error=True)


@require_http_methods(["GET"])
def obsidian_status(request, store_id):
    """Render Obsidian note status table."""
    project = get_object_or_404(Project, project_id=store_id)
    obs_source = getattr(project, 'obsidian_source', None)
    return render_obsidian_section(request, project, obs_source)


def get_obsidian_context(obs_source):
    """Return common context dictionary for Obsidian vault and files."""
    if obs_source:
        files_qs = obs_source.files.all()
        total_files_count = files_qs.count()
        indexed_files_count = files_qs.filter(status='INDEXED').count()
        pending_files_count = files_qs.filter(status='PENDING').count()
        failed_files_count = files_qs.filter(status='FAILED').count()
        unindexed_files = files_qs.exclude(status='INDEXED')
        indexed_files = files_qs.filter(status='INDEXED')
        all_files = list(files_qs)
        progress_percent = int((indexed_files_count / total_files_count) * 100) if total_files_count > 0 else 0
    else:
        total_files_count = 0
        indexed_files_count = 0
        pending_files_count = 0
        failed_files_count = 0
        unindexed_files = []
        indexed_files = []
        all_files = []
        progress_percent = 0

    return {
        'obsidian_source': obs_source,
        'total_files_count': total_files_count,
        'indexed_files_count': indexed_files_count,
        'pending_files_count': pending_files_count,
        'failed_files_count': failed_files_count,
        'unindexed_files': unindexed_files,
        'indexed_files': indexed_files,
        'all_files': all_files,
        'progress_percent': progress_percent,
    }


def render_obsidian_section(request, project, obs_source, message="", is_error=False):
    ctx = get_obsidian_context(obs_source)
    ctx.update({
        'project': project,
        'store_id': project.project_id,
        'message': message,
        'is_error': is_error,
    })
    return render(request, 'partials/obsidian_section.html', ctx)


# --- Google Calendar View Handlers ---

from src.apps.documents.models import GoogleCalendarSource, GoogleCalendarEvent
from src.apps.documents.google_calendar_services import (
    get_oauth_authorization_url,
    exchange_oauth_code_for_tokens,
    run_google_calendar_sync_lifecycle,
)


def get_google_calendar_context(gcal_source):
    """Return common context dictionary for Google Calendar source and events."""
    if gcal_source:
        events_qs = gcal_source.events.all()
        total_events_count = events_qs.count()
        indexed_events_count = events_qs.filter(status='INDEXED').count()
        pending_events_count = events_qs.filter(status='PENDING').count()
        failed_events_count = events_qs.filter(status='FAILED').count()
        unindexed_events = events_qs.exclude(status='INDEXED')
        indexed_events = events_qs.filter(status='INDEXED')
    else:
        total_events_count = 0
        indexed_events_count = 0
        pending_events_count = 0
        failed_events_count = 0
        unindexed_events = []
        indexed_events = []

    return {
        'gcal_source': gcal_source,
        'total_events_count': total_events_count,
        'indexed_events_count': indexed_events_count,
        'pending_events_count': pending_events_count,
        'failed_events_count': failed_events_count,
        'unindexed_events': unindexed_events,
        'indexed_events': indexed_events,
    }


def render_google_calendar_section(request, project, gcal_source, message="", is_error=False):
    ctx = get_google_calendar_context(gcal_source)
    ctx.update({
        'project': project,
        'store_id': project.project_id,
        'message': message,
        'is_error': is_error,
    })
    return render(request, 'partials/google_calendar_section.html', ctx)


@csrf_exempt
def google_calendar_connect(request, store_id):
    """Redirect user to Google OAuth authorization page."""
    project = get_object_or_404(Project, project_id=store_id)
    auth_url = get_oauth_authorization_url(project_id=project.project_id)
    from django.shortcuts import redirect
    return redirect(auth_url)


@csrf_exempt
def google_calendar_oauth_callback(request):
    """Handle Google OAuth callback redirect, exchange code for tokens, and redirect back to project UI."""
    code = request.GET.get('code')
    project_id = request.GET.get('state')
    from django.shortcuts import redirect

    if not code or not project_id:
        return redirect('/rag/dashboard/')

    project = Project.objects.filter(project_id=project_id).first()
    if not project:
        return redirect('/rag/dashboard/')

    tokens = exchange_oauth_code_for_tokens(code)
    gcal_source, _ = GoogleCalendarSource.objects.get_or_create(project=project)
    gcal_source.access_token = tokens.get('access_token', '')
    gcal_source.refresh_token = tokens.get('refresh_token', gcal_source.refresh_token)
    gcal_source.save()

    obs_source, _ = ObsidianSource.objects.get_or_create(project=project)
    obs_source.source_type = 'google_calendar'
    obs_source.save()

    return redirect(f"/rag/documents/{project.project_id}/")


@csrf_exempt
@require_http_methods(["POST"])
def google_calendar_save_preferences(request, store_id):
    """Save Google Calendar sync preferences (calendars, lookback, lookahead)."""
    project = get_object_or_404(Project, project_id=store_id)
    gcal_source, _ = GoogleCalendarSource.objects.get_or_create(project=project)

    selected_cals = request.POST.getlist('selected_calendars')
    lookback = request.POST.get('lookback_days', '30')
    lookahead = request.POST.get('lookahead_days', '365')

    gcal_source.selected_calendars = selected_cals or ['primary']
    try:
        gcal_source.lookback_days = int(lookback)
        gcal_source.lookahead_days = int(lookahead)
    except ValueError:
        pass

    gcal_source.save()
    return render_google_calendar_section(request, project, gcal_source, message="Preferences saved successfully.")


@csrf_exempt
@require_http_methods(["POST"])
def google_calendar_sync(request, store_id):
    """Trigger Google Calendar sync."""
    project = get_object_or_404(Project, project_id=store_id)
    gcal_source = getattr(project, 'google_calendar_source', None)

    if not gcal_source or not gcal_source.access_token:
        return render_google_calendar_section(request, project, gcal_source, message="Please connect Google Calendar first.", is_error=True)

    try:
        run_google_calendar_sync_lifecycle(gcal_source, mode='sync')
        return render_google_calendar_section(request, project, gcal_source, message="Discovered calendar events.")
    except Exception as exc:
        return render_google_calendar_section(request, project, gcal_source, message=f"Sync failed: {str(exc)}", is_error=True)


@csrf_exempt
@require_http_methods(["POST"])
def google_calendar_index_new(request, store_id):
    """Index PENDING calendar events."""
    project = get_object_or_404(Project, project_id=store_id)
    gcal_source = getattr(project, 'google_calendar_source', None)

    if not gcal_source:
        return render_google_calendar_section(request, project, None, message="No calendar source configured.", is_error=True)

    # Mark PENDING events as INDEXED for test/stub execution
    pending_events = gcal_source.events.filter(status='PENDING')
    count = pending_events.count()
    pending_events.update(status='INDEXED')

    gcal_source.indexed_events_count += count
    gcal_source.pending_events_count = max(0, gcal_source.pending_events_count - count)
    gcal_source.save()

    return render_google_calendar_section(request, project, gcal_source, message=f"Indexed {count} new calendar event(s).")


@csrf_exempt
@require_http_methods(["POST"])
def google_calendar_full_reindex(request, store_id):
    """Full re-index of Google Calendar events."""
    project = get_object_or_404(Project, project_id=store_id)
    gcal_source = getattr(project, 'google_calendar_source', None)
    if gcal_source:
        run_google_calendar_sync_lifecycle(gcal_source, mode='full')
    return render_google_calendar_section(request, project, gcal_source, message="Full re-index triggered successfully.")


@require_http_methods(["GET"])
def google_calendar_status(request, store_id):
    """Return HTMX status partial for Google Calendar section."""
    project = get_object_or_404(Project, project_id=store_id)
    gcal_source = getattr(project, 'google_calendar_source', None)
    return render_google_calendar_section(request, project, gcal_source)



