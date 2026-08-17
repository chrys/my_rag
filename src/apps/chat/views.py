"""
Chat views for handling conversations
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.utils.html import escape
import markdown
import json
import time

from src.optional_dependencies import LazyModuleProxy
from src.prompt_storage import get_prompt_storage

from .models import ChatMessage
from src.apps.projects.models import Project, SystemPrompt


gfs = LazyModuleProxy(
    "src.google_file_search",
    "Google File Search dependencies are not installed in this environment.",
)


def get_rag_engine(*args, **kwargs):
    from src.local_rag import get_rag_engine as local_get_rag_engine

    return local_get_rag_engine(*args, **kwargs)


def _user_can_access_project(project: Project | None, user) -> bool:
    """Return whether the current user can access the given project."""
    if not project or project.user_id is None:
        return True

    return bool(getattr(user, 'is_authenticated', False) and user.id == project.user_id)


def _get_project_system_prompt(project: Project | None, store_id: str) -> str:
    """Return the persisted system prompt for the given project/store."""
    if project and project.storage_type == 'postgres':
        prompt = SystemPrompt.objects.filter(project=project).values_list('content', flat=True).first()
        return prompt or ''

    prompt_storage = get_prompt_storage()
    return prompt_storage.get_prompt(store_id)


def _extract_source_documents(source_nodes) -> list[str]:
    """Return a deduplicated list of document names from engine source metadata."""
    document_names: list[str] = []

    for source in source_nodes or []:
        if isinstance(source, dict):
            document_name = (
                source.get('document') 
                or source.get('name') 
                or source.get('id') 
                or source.get('file_name')
            )
        else:
            document_name = str(source) if source else ''

        if document_name and document_name not in document_names:
            document_names.append(str(document_name))

    return document_names





@require_http_methods(["POST"])
@csrf_exempt
def chat(request):
    """Handle chat messages and generate responses"""
    # Extract API Key from headers (X-API-Key or Bearer token)
    api_key_value = request.META.get('HTTP_X_API_KEY')
    if not api_key_value and 'HTTP_AUTHORIZATION' in request.META:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '').strip()
        if auth_header.startswith('Bearer ') or auth_header.startswith('Api-Key '):
            api_key_value = auth_header.split(' ', 1)[1].strip()

    # Programmatic fallback for Basic Authentication
    if not api_key_value and not getattr(request.user, 'is_authenticated', False) and 'HTTP_AUTHORIZATION' in request.META:
        import base64
        from django.contrib.auth import authenticate
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Basic '):
            try:
                encoded_credentials = auth_header.split(' ', 1)[1]
                decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
                username, password = decoded_credentials.split(':', 1)
                user = authenticate(username=username, password=password)
                if user is not None:
                    request.user = user
            except Exception:
                pass

    try:
        start_time = time.time()
        data = json.loads(request.body)
        store_id = data.get('store_id')
        query = data.get('query')
        system_prompt = data.get('system_prompt', '')
        customer_profile = data.get('customer_profile')
        
        if not store_id or not query:
            return JsonResponse({'error': 'Missing store_id or query'}, status=400)

        # Look up project for storage type
        project = Project.objects.filter(project_id=store_id).first()

        # If API key was provided, validate it and enforce project scoping
        if api_key_value:
            from src.apps.api.models import APIKey
            from django.utils import timezone
            api_key_obj = APIKey.objects.filter(key=api_key_value, is_active=True).select_related('user', 'project').first()
            if not api_key_obj:
                return JsonResponse({'error': 'Invalid or inactive API key'}, status=401)
            
            # Enforce project scoping
            if api_key_obj.project and api_key_obj.project.project_id != store_id:
                return JsonResponse({'error': 'API key is not authorized for this project'}, status=403)
            
            request.user = api_key_obj.user
            APIKey.objects.filter(id=api_key_obj.id).update(last_used_at=timezone.now())

        if not _user_can_access_project(project, request.user):
            return JsonResponse({'error': 'Forbidden'}, status=403)
        
        # Get prompt if not provided
        if not system_prompt:
            system_prompt = _get_project_system_prompt(project, store_id)
        
        # Query the appropriate backend
        if store_id.startswith('local_'):
            rag_engine = get_rag_engine(store_id)
            bot_response = rag_engine.query(query, system_prompt=system_prompt)
            source_documents = _extract_source_documents(bot_response.get('source_nodes', [])) if isinstance(bot_response, dict) else []
            if isinstance(bot_response, dict):
                bot_response = bot_response.get('response', 'Error generating response.')
        elif store_id.startswith('rag_') or store_id.startswith('postgres_'):
            from llama_index.core import VectorStoreIndex, Settings
            from llama_index.embeddings.google import GeminiEmbedding
            from llama_index.llms.google_genai import GoogleGenAI
            from src.apps.documents.services import get_vector_store
            from .llm_router import generate_llm_response
            import os
            
            vector_store = get_vector_store(store_id)
            embed_model = GeminiEmbedding(
                model_name="models/gemini-embedding-001",
                api_key=os.getenv("GOOGLE_API_KEY")
            )
            target_llm = getattr(project, 'llm_model', 'gemini-2.5-flash-lite') if project else 'gemini-2.5-flash-lite'
            disable_thinking = getattr(project, 'disable_thinking', False) if project else False
            if "gemma" in target_llm.lower() or "mlx" in target_llm.lower() or ":" in target_llm:
                from llama_index.llms.ollama import Ollama
                ollama_url = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434/api/generate")
                base_url = ollama_url.split('/api/generate')[0]
                ollama_kwargs = {
                    "model": target_llm,
                    "base_url": base_url,
                    "request_timeout": 60.0,
                }
                if disable_thinking:
                    ollama_kwargs["thinking"] = False
                    ollama_kwargs["additional_kwargs"] = {"thinking": False}
                llm = Ollama(**ollama_kwargs)
            else:
                llm = GoogleGenAI(
                    model=target_llm,
                    api_key=os.getenv("GOOGLE_API_KEY")
                )
            from llama_index.core.embeddings import BaseEmbedding
            from llama_index.core.llms import LLM
            if isinstance(embed_model, BaseEmbedding):
                Settings.embed_model = embed_model
            if isinstance(llm, LLM):
                Settings.llm = llm
            
            index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)
            mode = getattr(project, 'response_mode', 'compact') if project else 'compact'
            query_engine = index.as_query_engine(llm=llm, response_mode=mode)
            
            from .services import generate_adaptive_hyde_passage
            search_query = generate_adaptive_hyde_passage(query, model_id=target_llm, disable_thinking=disable_thinking) if (project and getattr(project, 'use_hyde', False)) else query

            prompt = system_prompt or "You are a helpful assistant."
            response = None
            try:
                response = query_engine.query(f"System Context: {prompt}\n\nQuery: {search_query}")
                bot_response = str(response)
            except Exception as q_err:
                err_str = str(q_err).lower()
                if any(k in err_str for k in ['ollama', '11434', 'failed to connect', 'connection refused']):
                    raise RuntimeError("Local Ollama server is not running or accessible. Please start Ollama on your machine (http://localhost:11434).") from q_err
                bot_response = "Empty Response"

            # If vector store yields no matching nodes (LlamaIndex returns "Empty Response"), fall back to LLM router
            if not bot_response or bot_response.strip().lower() == "empty response":
                bot_response = generate_llm_response(prompt=query, model_id=target_llm, system_prompt=prompt, disable_thinking=disable_thinking)

            source_documents = []
            if response and hasattr(response, 'source_nodes'):
                source_documents = _extract_source_documents([node.node.metadata for node in response.source_nodes])
        else:
            google_store_id = project.external_store_id if project and project.external_store_id else store_id
            bot_response = gfs.ask_store_question(
                google_store_id,
                query,
                system_prompt=system_prompt
            )
            source_documents = []
        
        # Convert markdown to HTML
        bot_response_html = markdown.markdown(bot_response)
        
        elapsed_seconds = round(time.time() - start_time, 2)
        response_time_str = f"{elapsed_seconds:.2f}s"
        
        # Extract conversation/session ID if provided
        session_id = (
            data.get('session_id')
            or data.get('conversation_id')
            or request.META.get('HTTP_X_SESSION_ID')
            or request.META.get('HTTP_X_CONVERSATION_ID')
            or ''
        )

        # Store in database
        from django.db import transaction
        user_for_msg = request.user if getattr(request.user, 'is_authenticated', False) else None
        user_msg = None
        bot_msg = None
        try:
            with transaction.atomic():
                user_msg = ChatMessage.objects.create(
                    project=project,
                    user=user_for_msg,
                    session_id=session_id,
                    message_type='user',
                    content=query
                )
                bot_msg = ChatMessage.objects.create(
                    project=project,
                    user=user_for_msg,
                    session_id=session_id,
                    message_type='assistant',
                    content=bot_response,
                    response_html=bot_response_html
                )
        except Exception as db_err:
            import logging
            logging.getLogger(__name__).warning("Failed to store ChatMessage: %s", db_err)
        
        return JsonResponse({
            'message_id': str(bot_msg.id) if bot_msg else '',
            'conversation_id': session_id,
            'user_message': query,
            'bot_response': bot_response,
            'bot_response_html': bot_response_html,
            'source_documents': source_documents,
            'response_time': response_time_str,
            'response_time_seconds': elapsed_seconds,
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        err_msg = str(e)
        if any(k in err_msg.lower() for k in ['ollama', '11434', 'failed to connect', 'connection refused']):
            err_msg = "⚠️ Local Ollama server is not running or accessible. Please start Ollama on your machine (http://localhost:11434) and try again."
        return JsonResponse({'error': err_msg}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def chat_submit(request):
    """
    Handle HTMX/form chat submissions and return rendered HTML partials.
    Supports local, postgres, and google-backed projects.
    """
    start_time = time.time()
    # Standard POST or JSON extraction
    if request.content_type == "application/json":
        try:
            data = json.loads(request.body)
        except Exception:
            data = {}
    else:
        data = request.POST

    store_id = data.get("store_id")
    query = data.get("query")
    system_prompt = data.get("system_prompt", "")

    if not store_id or not query:
        from django.http import HttpResponse
        return HttpResponse("Missing store_id or query", status=400)

    # Look up project
    project = Project.objects.filter(project_id=store_id).first()

    if not _user_can_access_project(project, request.user):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Forbidden")

    # Get prompt if not provided
    if not system_prompt:
        system_prompt = _get_project_system_prompt(project, store_id)

    # Query the appropriate backend
    try:
        if store_id.startswith("local_"):
            rag_engine = get_rag_engine(store_id)
            bot_response = rag_engine.query(query, system_prompt=system_prompt)
            source_documents = _extract_source_documents(bot_response.get("source_nodes", [])) if isinstance(bot_response, dict) else []
            if isinstance(bot_response, dict):
                bot_response = bot_response.get("response", "Error generating response.")
        elif store_id.startswith("rag_") or store_id.startswith("postgres_"):
            from llama_index.core import VectorStoreIndex, Settings
            from llama_index.embeddings.google import GeminiEmbedding
            from llama_index.llms.google_genai import GoogleGenAI
            from src.apps.documents.services import get_vector_store
            import os
            
            vector_store = get_vector_store(store_id)
            embed_model = GeminiEmbedding(
                model_name="models/gemini-embedding-001",
                api_key=os.getenv("GOOGLE_API_KEY")
            )
            target_llm = getattr(project, 'llm_model', 'gemini-2.5-flash-lite') if project else 'gemini-2.5-flash-lite'
            disable_thinking = getattr(project, 'disable_thinking', False) if project else False
            if "gemma" in target_llm.lower() or "mlx" in target_llm.lower() or ":" in target_llm:
                from llama_index.llms.ollama import Ollama
                ollama_url = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434/api/generate")
                base_url = ollama_url.split('/api/generate')[0]
                ollama_kwargs = {
                    "model": target_llm,
                    "base_url": base_url,
                    "request_timeout": 60.0,
                }
                if disable_thinking:
                    ollama_kwargs["thinking"] = False
                    ollama_kwargs["additional_kwargs"] = {"thinking": False}
                llm = Ollama(**ollama_kwargs)
            else:
                llm = GoogleGenAI(
                    model=target_llm,
                    api_key=os.getenv("GOOGLE_API_KEY")
                )
            from llama_index.core.embeddings import BaseEmbedding
            from llama_index.core.llms import LLM
            if isinstance(embed_model, BaseEmbedding):
                Settings.embed_model = embed_model
            if isinstance(llm, LLM):
                Settings.llm = llm
            
            index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)
            mode = getattr(project, 'response_mode', 'compact') if project else 'compact'
            query_engine = index.as_query_engine(llm=llm, response_mode=mode)
            
            from .services import generate_adaptive_hyde_passage
            search_query = generate_adaptive_hyde_passage(query, model_id=target_llm, disable_thinking=disable_thinking) if (project and getattr(project, 'use_hyde', False)) else query

            prompt = system_prompt or "You are a helpful assistant."
            response = None
            try:
                response = query_engine.query(f"System Context: {prompt}\n\nQuery: {search_query}")
                bot_response = str(response)
            except Exception as q_err:
                err_str = str(q_err).lower()
                if any(k in err_str for k in ['ollama', '11434', 'failed to connect', 'connection refused']):
                    raise RuntimeError("Local Ollama server is not running or accessible. Please start Ollama on your machine (http://localhost:11434).") from q_err
                bot_response = "Empty Response"

            if not bot_response or bot_response.strip().lower() == "empty response":
                from .llm_router import generate_llm_response
                bot_response = generate_llm_response(prompt=query, model_id=target_llm, system_prompt=prompt, disable_thinking=disable_thinking)

            source_documents = []
            if response and hasattr(response, "source_nodes"):
                source_documents = _extract_source_documents([node.node.metadata for node in response.source_nodes])
        else:
            google_store_id = project.external_store_id if project and project.external_store_id else store_id
            bot_response = gfs.ask_store_question(
                google_store_id,
                query,
                system_prompt=system_prompt
            )
            source_documents = []

        # Convert markdown to HTML
        bot_response_html = markdown.markdown(bot_response)

        elapsed_seconds = round(time.time() - start_time, 2)
        response_time_str = f"{elapsed_seconds:.2f}s"

        # Append source attribution if we have sources
        sources_meta = ""
        if source_documents:
            sources_meta += f'<div class="mt-2 text-xs text-gray-500"><strong>Sources:</strong> {", ".join(source_documents)}</div>'
        sources_meta += f'<div class="mt-1 text-xs text-gray-400 font-mono">⏱️ Response Time: {response_time_str}</div>'
        bot_response_html += sources_meta

        # Store in database if user is authenticated
        if request.user.is_authenticated:
            from django.db import transaction
            with transaction.atomic():
                ChatMessage.objects.create(
                    project=project,
                    user=request.user,
                    message_type="user",
                    content=query
                )
                ChatMessage.objects.create(
                    project=project,
                    user=request.user,
                    message_type="assistant",
                    content=bot_response,
                    response_html=bot_response_html
                )

        from django.http import HttpResponse
        
        user_html = render_to_string("partials/chat_message.html", {
            "sender": "user",
            "message": escape(query),
        })
        
        bot_html = render_to_string("partials/chat_message.html", {
            "sender": "bot",
            "message": bot_response_html,
        })

        return HttpResponse(user_html + bot_html)

    except Exception as e:
        import traceback
        traceback.print_exc()
        from django.http import HttpResponse
        return HttpResponse(f"Error: {str(e)}", status=500)


@require_http_methods(["POST"])
@csrf_exempt
def chatbot_feedback(request):
    """
    Ingest user feedback (thumbs up / thumbs down) for chat messages.
    Supports authentication via X-API-Key, Authorization: Bearer <key>, Basic Auth, or Session.
    """
    # Extract API Key from headers if provided
    api_key_value = request.META.get('HTTP_X_API_KEY')
    if not api_key_value and 'HTTP_AUTHORIZATION' in request.META:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '').strip()
        if auth_header.startswith('Bearer ') or auth_header.startswith('Api-Key '):
            api_key_value = auth_header.split(' ', 1)[1].strip()

    # Programmatic fallback for Basic Authentication
    if not api_key_value and not getattr(request.user, 'is_authenticated', False) and 'HTTP_AUTHORIZATION' in request.META:
        import base64
        from django.contrib.auth import authenticate
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Basic '):
            try:
                encoded_credentials = auth_header.split(' ', 1)[1]
                decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
                username, password = decoded_credentials.split(':', 1)
                user = authenticate(username=username, password=password)
                if user is not None:
                    request.user = user
            except Exception:
                pass

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    message_id = data.get('message_id')
    value = (data.get('value') or '').lower().strip()
    conversation_id = data.get('conversation_id', '')
    customer_id = str(data.get('customer_id', '') or '')
    timestamp_str = data.get('timestamp')
    store_id = (
        data.get('store_id')
        or data.get('project_id')
        or request.GET.get('store_id')
        or request.GET.get('project_id')
        or request.META.get('HTTP_X_STORE_ID')
        or request.META.get('HTTP_X_PROJECT_ID')
    )

    if not message_id:
        return JsonResponse({'error': 'Missing required field: message_id'}, status=400)

    if value not in ['up', 'down']:
        return JsonResponse({'error': 'Invalid feedback value. Expected "up" or "down"'}, status=400)

    # Resolve project
    project = None
    if api_key_value:
        from src.apps.api.models import APIKey
        from django.utils import timezone
        api_key_obj = APIKey.objects.filter(key=api_key_value, is_active=True).select_related('user', 'project').first()
        if not api_key_obj:
            return JsonResponse({'error': 'Invalid or inactive API key'}, status=401)
        if api_key_obj.project:
            project = api_key_obj.project
            if store_id and project.project_id != store_id:
                return JsonResponse({'error': 'API key is not authorized for this project'}, status=403)
        APIKey.objects.filter(id=api_key_obj.id).update(last_used_at=timezone.now())

    if not project and store_id:
        project = Project.objects.filter(project_id=store_id).first()

    # Fallback: check if message_id exists in ChatMessage to get its project
    if not project and str(message_id).isdigit():
        msg_obj = ChatMessage.objects.filter(id=int(message_id)).select_related('project').first()
        if msg_obj:
            project = msg_obj.project

    # Fallback: if only 1 project exists in the system
    if not project:
        projects_count = Project.objects.count()
        if projects_count == 1:
            project = Project.objects.first()

    if not project:
        if store_id:
            return JsonResponse({'error': f'Project "{store_id}" not found'}, status=404)
        return JsonResponse({'error': 'Could not identify target project. Please provide store_id or use a project-scoped API key.'}, status=400)

    # Extract query and reply if sent in payload
    user_query = (
        data.get('query')
        or data.get('user_message')
        or data.get('prompt')
        or data.get('question')
        or data.get('message')
        or ''
    )
    bot_reply = (
        data.get('reply')
        or data.get('response')
        or data.get('bot_response')
        or data.get('answer')
        or data.get('assistant_message')
        or ''
    )

    # 1. Fallback by numeric message_id
    if (not user_query or not bot_reply) and str(message_id).isdigit():
        msg_obj = ChatMessage.objects.filter(id=int(message_id)).first()
        if msg_obj:
            if not bot_reply and msg_obj.message_type == 'assistant':
                bot_reply = msg_obj.content
            elif not user_query and msg_obj.message_type == 'user':
                user_query = msg_obj.content
            if msg_obj.session_id:
                if not user_query:
                    umsg = ChatMessage.objects.filter(session_id=msg_obj.session_id, message_type='user', created_at__lte=msg_obj.created_at).order_by('-created_at').first()
                    if umsg:
                        user_query = umsg.content
                if not bot_reply:
                    bmsg = ChatMessage.objects.filter(session_id=msg_obj.session_id, message_type='assistant', created_at__gte=msg_obj.created_at).order_by('created_at').first()
                    if bmsg:
                        bot_reply = bmsg.content

    # 2. Fallback by conversation_id
    if (not user_query or not bot_reply) and conversation_id:
        conv_msgs = ChatMessage.objects.filter(session_id=conversation_id).order_by('-created_at')
        for m in conv_msgs:
            if not bot_reply and m.message_type == 'assistant':
                bot_reply = m.content
            elif not user_query and m.message_type == 'user':
                user_query = m.content

    # 3. Fallback by message_id as session_id string
    if (not user_query or not bot_reply) and message_id:
        conv_msgs = ChatMessage.objects.filter(session_id=message_id).order_by('-created_at')
        for m in conv_msgs:
            if not bot_reply and m.message_type == 'assistant':
                bot_reply = m.content
            elif not user_query and m.message_type == 'user':
                user_query = m.content

    # 4. Fallback: most recent messages in this project
    if (not user_query or not bot_reply) and project:
        latest_msgs = ChatMessage.objects.filter(project=project).order_by('-created_at')[:4]
        for m in latest_msgs:
            if not bot_reply and m.message_type == 'assistant':
                bot_reply = m.content
            elif not user_query and m.message_type == 'user':
                user_query = m.content

    # Parse timestamp if given
    parsed_timestamp = None
    if timestamp_str:
        try:
            from django.utils.dateparse import parse_datetime
            parsed_timestamp = parse_datetime(timestamp_str)
        except Exception:
            pass

    from src.apps.chat.models import ChatFeedback
    feedback = ChatFeedback.objects.create(
        project=project,
        message_id=message_id,
        conversation_id=conversation_id,
        customer_id=customer_id,
        value=value,
        query=user_query,
        reply=bot_reply,
        timestamp=parsed_timestamp
    )

    return JsonResponse({
        'status': 'success',
        'feedback_id': feedback.id,
        'project_id': project.project_id,
        'message_id': feedback.message_id,
        'value': feedback.value,
        'query': feedback.query,
        'reply': feedback.reply,
        'created_at': feedback.created_at.isoformat()
    }, status=201)


