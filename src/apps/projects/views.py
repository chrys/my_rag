"""
Project views for managing file search stores and projects
"""

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import models

# Add src to path to import Flask modules (temporarily)
from src.local_project_storage import get_local_project_storage
from src.optional_dependencies import LazyModuleProxy

from .models import Project
from .db_utils import test_postgres_connection



gfs = LazyModuleProxy(
    "src.google_file_search",
    "Google File Search dependencies are not installed in this environment.",
)


def _user_can_access_project(project, user):
    """Return whether the current user can access the given project."""
    if not project or project.user_id is None:
        return True

    if bool(getattr(user, 'is_authenticated', False)):
        if getattr(user, 'is_superuser', False) or getattr(user, 'is_staff', False):
            return True
        return user.id == project.user_id

    return False


def get_combined_stores(request=None):
    """Get list of projects for the current user from Django database"""
    if request and getattr(request.user, 'is_authenticated', False):
        if getattr(request.user, 'is_superuser', False) or getattr(request.user, 'is_staff', False):
            projects = Project.objects.all().order_by('-created_at')
        else:
            projects = Project.objects.filter(
                models.Q(user=request.user) | models.Q(user__isnull=True)
            ).order_by('-created_at')
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
            error_html = (
                '<div id="project-error-container" hx-swap-oob="true" '
                'class="mb-4 p-3 bg-red-50 text-red-700 rounded-md border border-red-200 text-sm">'
                '<strong>Error:</strong> This functionality has not been implemented yet.'
                '</div>'
            )
            return HttpResponse(error_html)
        elif storage_type == 'google':
            llm_model = request.POST.get('llm_model', 'gemini-2.5-flash-lite')
            if llm_model not in ['gemini-2.5-flash-lite', 'gemini-3.5-flash-lite', 'gemini-3.7-flash']:
                llm_model = 'gemini-2.5-flash-lite'

            try:
                external_store_id = gfs.create_file_search_store(display_name=display_name)
            except Exception as e:
                error_html = (
                    f'<div id="project-error-container" hx-swap-oob="true" '
                    f'class="mb-4 p-3 bg-red-50 text-red-700 rounded-md border border-red-200 text-sm">'
                    f'<strong>Google File Search Provisioning Failed:</strong> {str(e)}'
                    f'</div>'
                )
                return HttpResponse(error_html)

            from datetime import datetime
            import time
            import uuid
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            microseconds = int(time.time() * 1000000) % 1000000
            safe_name = display_name.lower().replace(' ', '_')[:30]
            rand_suffix = uuid.uuid4().hex[:6]
            project_id = f"google_{timestamp}_{microseconds}_{safe_name}_{rand_suffix}"
            Project.objects.create(
                project_id=project_id,
                display_name=display_name,
                storage_type='google',
                external_store_id=external_store_id,
                llm_model=llm_model,
                user=user
            )
        elif storage_type == 'postgres':
            success, error_message = test_postgres_connection()
            if not success:
                error_html = (
                    f'<div id="project-error-container" hx-swap-oob="true" '
                    f'class="mb-4 p-3 bg-red-50 text-red-700 rounded-md border border-red-200 text-sm">'
                    f'<strong>Connection failed:</strong> {error_message}'
                    f'</div>'
                )
                return HttpResponse(error_html)

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
    
    stores = get_combined_stores(request)
    response_content = (
        '<div id="project-error-container" hx-swap-oob="true"></div>\n'
        + render(request, "partials/project_list.html", {"stores": stores}).content.decode("utf-8")
    )
    response = HttpResponse(response_content)
    response["HX-Trigger"] = "projectCreated"
    return response



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


@login_required
@require_http_methods(["GET"])
def project_api_keys(request, store_id):
    """Render the API Keys section for a specific project"""
    from django.shortcuts import get_object_or_404
    from src.apps.api.models import APIKey
    
    project = get_object_or_404(Project, project_id=store_id)
    if not _user_can_access_project(project, request.user):
        return HttpResponse("Forbidden", status=403)
    
    api_keys = APIKey.objects.filter(project=project).order_by('-created_at')
    
    return render(request, 'partials/project_apikey_section.html', {
        'project': project,
        'api_keys': api_keys,
    })


@login_required
@require_http_methods(["POST"])
def create_project_api_key(request, store_id):
    """Generate a new API key scoped to this project"""
    from django.shortcuts import get_object_or_404
    from src.apps.api.models import APIKey
    
    project = get_object_or_404(Project, project_id=store_id)
    if not _user_can_access_project(project, request.user):
        return HttpResponse("Forbidden", status=403)
    
    key_name = request.POST.get('name', '').strip() or f"{project.display_name} API Key"
    new_key = APIKey.objects.create(
        user=request.user if project.user is None else project.user,
        project=project,
        name=key_name,
        is_active=True
    )
    
    api_keys = APIKey.objects.filter(project=project).order_by('-created_at')
    
    return render(request, 'dashboard/partials/api_keys.html', {
        'project': project,
        'current_project': project,
        'projects': _get_user_projects(request),
        'active_tab': 'api_keys',
        'api_keys': api_keys,
        'just_created_key': new_key,
    })


@login_required
@require_http_methods(["POST"])
def toggle_project_api_key(request, store_id, key_id):
    """Toggle an API key between active and inactive"""
    from django.shortcuts import get_object_or_404
    from src.apps.api.models import APIKey
    
    project = get_object_or_404(Project, project_id=store_id)
    if not _user_can_access_project(project, request.user):
        return HttpResponse("Forbidden", status=403)
    
    api_key = get_object_or_404(APIKey, id=key_id, project=project)
    api_key.is_active = not api_key.is_active
    api_key.save(update_fields=['is_active'])
    
    api_keys = APIKey.objects.filter(project=project).order_by('-created_at')
    
    return render(request, 'dashboard/partials/api_keys.html', {
        'project': project,
        'current_project': project,
        'projects': _get_user_projects(request),
        'active_tab': 'api_keys',
        'api_keys': api_keys,
    })


@login_required
@require_http_methods(["POST", "DELETE"])
def delete_project_api_key(request, store_id, key_id):
    """Revoke and delete an API key"""
    from django.shortcuts import get_object_or_404
    from src.apps.api.models import APIKey
    
    project = get_object_or_404(Project, project_id=store_id)
    if not _user_can_access_project(project, request.user):
        return HttpResponse("Forbidden", status=403)
    
    api_key = get_object_or_404(APIKey, id=key_id, project=project)
    api_key.delete()
    
    api_keys = APIKey.objects.filter(project=project).order_by('-created_at')
    
    return render(request, 'dashboard/partials/api_keys.html', {
        'project': project,
        'current_project': project,
        'projects': _get_user_projects(request),
        'active_tab': 'api_keys',
        'api_keys': api_keys,
    })


def _filter_feedback_queryset(project, request):
    """Helper to apply date and rating filters on ChatFeedback queryset"""
    from django.utils.dateparse import parse_date, parse_datetime
    from django.utils import timezone
    import datetime
    from src.apps.chat.models import ChatFeedback

    start_date_str = request.GET.get('start_date', '').strip()
    end_date_str = request.GET.get('end_date', '').strip()
    rating_filter = request.GET.get('rating', '').strip().lower()

    queryset = ChatFeedback.objects.filter(project=project)

    if start_date_str:
        parsed_start = parse_datetime(start_date_str)
        if not parsed_start:
            d = parse_date(start_date_str)
            if d:
                parsed_start = timezone.make_aware(datetime.datetime.combine(d, datetime.time.min))
        elif timezone.is_naive(parsed_start):
            parsed_start = timezone.make_aware(parsed_start)

        if parsed_start:
            queryset = queryset.filter(
                models.Q(timestamp__gte=parsed_start) | (models.Q(timestamp__isnull=True) & models.Q(created_at__gte=parsed_start))
            )

    if end_date_str:
        parsed_end = parse_datetime(end_date_str)
        if not parsed_end:
            d = parse_date(end_date_str)
            if d:
                parsed_end = timezone.make_aware(datetime.datetime.combine(d, datetime.time.max))
        elif timezone.is_naive(parsed_end):
            parsed_end = timezone.make_aware(parsed_end)

        if parsed_end:
            queryset = queryset.filter(
                models.Q(timestamp__lte=parsed_end) | (models.Q(timestamp__isnull=True) & models.Q(created_at__lte=parsed_end))
            )

    if rating_filter in ['up', 'down']:
        queryset = queryset.filter(value=rating_filter)

    return queryset, start_date_str, end_date_str, rating_filter


@login_required
@require_http_methods(["GET"])
def project_feedback(request, store_id):
    """Render the Feedback section and metrics for a specific project with date and rating filters"""
    from django.shortcuts import get_object_or_404
    
    project = get_object_or_404(Project, project_id=store_id)
    if not _user_can_access_project(project, request.user):
        return HttpResponse("Forbidden", status=403)
    
    queryset, start_date_str, end_date_str, rating_filter = _filter_feedback_queryset(project, request)

    feedbacks = queryset.order_by('-created_at')
    total_count = feedbacks.count()
    up_count = feedbacks.filter(value='up').count()
    down_count = feedbacks.filter(value='down').count()
    up_pct = round((up_count / total_count * 100), 1) if total_count > 0 else 0
    down_pct = round((down_count / total_count * 100), 1) if total_count > 0 else 0

    from src.apps.chat.models import ChatMessage
    feedback_list = list(feedbacks)
    for fb in feedback_list:
        if not fb.query or not fb.reply:
            if fb.conversation_id:
                c_msgs = ChatMessage.objects.filter(session_id=fb.conversation_id).order_by('-created_at')
                for m in c_msgs:
                    if not fb.reply and m.message_type == 'assistant':
                        fb.reply = m.content
                    elif not fb.query and m.message_type == 'user':
                        fb.query = m.content
            if (not fb.query or not fb.reply) and str(fb.message_id).isdigit():
                m = ChatMessage.objects.filter(id=int(fb.message_id)).first()
                if m:
                    if not fb.reply and m.message_type == 'assistant':
                        fb.reply = m.content
                    elif not fb.query and m.message_type == 'user':
                        fb.query = m.content
            if (not fb.query or not fb.reply) and fb.message_id:
                c_msgs = ChatMessage.objects.filter(session_id=fb.message_id).order_by('-created_at')
                for m in c_msgs:
                    if not fb.reply and m.message_type == 'assistant':
                        fb.reply = m.content
                    elif not fb.query and m.message_type == 'user':
                        fb.query = m.content

    return render(request, 'partials/project_feedback_section.html', {
        'project': project,
        'feedbacks': feedback_list,
        'total_count': total_count,
        'up_count': up_count,
        'down_count': down_count,
        'up_pct': up_pct,
        'down_pct': down_pct,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'rating': rating_filter,
    })


@login_required
@require_http_methods(["GET"])
def export_feedback_csv(request, store_id):
    """Export feedback entries to CSV format (all feedback or filtered)"""
    import csv
    from django.http import HttpResponse
    from django.shortcuts import get_object_or_404
    from django.utils import timezone
    from src.apps.chat.models import ChatMessage

    project = get_object_or_404(Project, project_id=store_id)
    if not _user_can_access_project(project, request.user):
        return HttpResponse("Forbidden", status=403)

    queryset, _, _, _ = _filter_feedback_queryset(project, request)
    feedbacks = list(queryset.order_by('-created_at'))
    for fb in feedbacks:
        if not fb.query or not fb.reply:
            if fb.conversation_id:
                c_msgs = ChatMessage.objects.filter(session_id=fb.conversation_id).order_by('-created_at')
                for m in c_msgs:
                    if not fb.reply and m.message_type == 'assistant':
                        fb.reply = m.content
                    elif not fb.query and m.message_type == 'user':
                        fb.query = m.content
            if (not fb.query or not fb.reply) and str(fb.message_id).isdigit():
                m = ChatMessage.objects.filter(id=int(fb.message_id)).first()
                if m:
                    if not fb.reply and m.message_type == 'assistant':
                        fb.reply = m.content
                    elif not fb.query and m.message_type == 'user':
                        fb.query = m.content

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    timestamp_tag = timezone.now().strftime('%Y%m%d_%H%M%S')
    filename = f"feedback_{project.project_id}_{timestamp_tag}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow([
        'Feedback',
        'Customer ID',
        'Client Timestamp',
        'Recorded At',
        'Query',
        'Reply',
        'Message ID',
        'Conversation ID'
    ])

    for item in feedbacks:
        writer.writerow([
            item.value,
            item.customer_id,
            item.timestamp.isoformat() if item.timestamp else '',
            item.created_at.isoformat() if item.created_at else '',
            item.query,
            item.reply,
            item.message_id,
            item.conversation_id
        ])

    return response


def _get_project_or_404(request, store_id):
    """Helper to retrieve project by project_id and check access permissions"""
    from django.shortcuts import get_object_or_404
    project = get_object_or_404(Project, project_id=store_id)
    if not _user_can_access_project(project, request.user):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("Access denied.")
    return project


def _get_user_projects(request):
    """Get all projects accessible to the current user"""
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.is_staff:
            return Project.objects.all().order_by("-created_at")
        return Project.objects.filter(
            models.Q(user=request.user) | models.Q(user__isnull=True)
        ).order_by("-created_at")
    return Project.objects.filter(user__isnull=True).order_by("-created_at")


@login_required
def dashboard_view(request):
    """
    Main Pico.css dashboard view. Resolves the active project and active tab.
    Admins are routed to the Django admin UI, while regular users use Pico.css.
    """
    if (request.user.is_staff or request.user.is_superuser) and not request.GET.get("preview"):
        return redirect("/rag/admin/")

    projects = _get_user_projects(request)
    project_id = request.GET.get("project_id") or request.session.get("active_project_id")
    
    current_project = None
    if project_id:
        current_project = projects.filter(project_id=project_id).first()
    if not current_project and projects.exists():
        current_project = projects.first()
        
    if current_project:
        request.session["active_project_id"] = current_project.project_id
        
    active_tab = request.GET.get("tab", "parameters")
    
    context = {
        "projects": projects,
        "current_project": current_project,
        "active_tab": active_tab,
    }
    
    # Add tab-specific data if needed
    if current_project:
        if active_tab == "prompt":
            from .models import SystemPrompt
            prompt_obj = SystemPrompt.objects.filter(project=current_project).first()
            context["prompt_content"] = prompt_obj.content if prompt_obj else ""
        elif active_tab == "api_keys":
            from src.apps.api.models import APIKey
            context["api_keys"] = APIKey.objects.filter(project=current_project).order_by("-created_at")
        elif active_tab == "sources":
            context["documents"] = current_project.documents.all().order_by("-created_at")
            
    if request.headers.get("HX-Request") and not request.GET.get("project_id"):
        return render(request, "dashboard/workspace.html", context)
    return render(request, "dashboard/base.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def project_parameters_view(request, store_id):
    """1.1 Parameters tab view"""
    project = _get_project_or_404(request, store_id)
    request.session["active_project_id"] = project.project_id
    success_message = None

    if request.method == "POST":
        display_name = request.POST.get("display_name", "").strip()
        if display_name:
            project.display_name = display_name
        
        llm_model = request.POST.get("llm_model", "").strip()
        if llm_model:
            project.llm_model = llm_model
            
        response_mode = request.POST.get("response_mode")
        if response_mode and project.storage_type != "google":
            project.response_mode = response_mode
            
        project.use_hyde = bool(request.POST.get("use_hyde")) if project.storage_type != "google" else False
        project.disable_thinking = bool(request.POST.get("disable_thinking"))
        project.is_active = bool(request.POST.get("is_active"))
        project.save()
        success_message = "Project parameters saved successfully."

    context = {
        "projects": _get_user_projects(request),
        "current_project": project,
        "active_tab": "parameters",
        "success_message": success_message,
    }
    if request.headers.get("HX-Request"):
        return render(request, "dashboard/partials/parameters.html", context)
    return render(request, "dashboard/base.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def project_prompt_view(request, store_id):
    """1.2 Prompt tab view"""
    project = _get_project_or_404(request, store_id)
    request.session["active_project_id"] = project.project_id
    from .models import SystemPrompt
    prompt_obj = SystemPrompt.objects.filter(project=project).first()
    success_message = None

    if request.method == "POST":
        custom_enabled = bool(request.POST.get("custom_prompt"))
        prompt_text = request.POST.get("prompt_text", "").strip()
        project.custom_prompt = custom_enabled
        project.save()

        if custom_enabled:
            SystemPrompt.objects.update_or_create(
                project=project,
                defaults={"content": prompt_text}
            )
        prompt_obj = SystemPrompt.objects.filter(project=project).first()
        success_message = "System prompt saved successfully."

    context = {
        "projects": _get_user_projects(request),
        "current_project": project,
        "active_tab": "prompt",
        "prompt_content": prompt_obj.content if prompt_obj else "",
        "success_message": success_message,
    }
    if request.headers.get("HX-Request"):
        return render(request, "dashboard/partials/prompt.html", context)
    return render(request, "dashboard/base.html", context)


@login_required
@require_http_methods(["GET"])
def project_api_keys_view(request, store_id):
    """1.3 API Keys tab view"""
    project = _get_project_or_404(request, store_id)
    request.session["active_project_id"] = project.project_id
    from src.apps.api.models import APIKey
    api_keys = APIKey.objects.filter(project=project).order_by("-created_at")

    context = {
        "projects": _get_user_projects(request),
        "current_project": project,
        "active_tab": "api_keys",
        "api_keys": api_keys,
    }
    if request.headers.get("HX-Request"):
        return render(request, "dashboard/partials/api_keys.html", context)
    return render(request, "dashboard/base.html", context)


@login_required
@require_http_methods(["GET"])
def project_sources_view(request, store_id):
    """2.1 Sources tab view"""
    project = _get_project_or_404(request, store_id)
    request.session["active_project_id"] = project.project_id
    documents = project.documents.all().order_by("-created_at")

    context = {
        "projects": _get_user_projects(request),
        "current_project": project,
        "active_tab": "sources",
        "documents": documents,
    }
    if request.headers.get("HX-Request"):
        return render(request, "dashboard/partials/sources.html", context)
    return render(request, "dashboard/base.html", context)


@login_required
@require_http_methods(["GET"])
def project_chat_view(request, store_id):
    """3. Chat tab view"""
    project = _get_project_or_404(request, store_id)
    request.session["active_project_id"] = project.project_id

    context = {
        "projects": _get_user_projects(request),
        "current_project": project,
        "active_tab": "chat",
    }
    if request.headers.get("HX-Request"):
        return render(request, "dashboard/partials/chat.html", context)
    return render(request, "dashboard/base.html", context)


@login_required
@require_http_methods(["GET"])
def project_evaluate_view(request, store_id):
    """4. Evaluate tab view"""
    project = _get_project_or_404(request, store_id)
    request.session["active_project_id"] = project.project_id

    context = {
        "projects": _get_user_projects(request),
        "current_project": project,
        "active_tab": "evaluate",
    }
    if request.headers.get("HX-Request"):
        return render(request, "dashboard/partials/evaluate.html", context)
    return render(request, "dashboard/base.html", context)


@login_required
@require_http_methods(["GET"])
def project_monitor_view(request, store_id):
    """5. Monitor tab view"""
    project = _get_project_or_404(request, store_id)
    request.session["active_project_id"] = project.project_id

    context = {
        "projects": _get_user_projects(request),
        "current_project": project,
        "active_tab": "monitor",
    }
    if request.headers.get("HX-Request"):
        return render(request, "dashboard/partials/monitor.html", context)
    return render(request, "dashboard/base.html", context)







