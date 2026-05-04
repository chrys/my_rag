"""
Chat views for handling conversations
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.utils.html import escape
import markdown
import sys
import os
import json

from src.local_project_storage import get_local_project_storage
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
            document_name = source.get('document') or source.get('name') or source.get('id')
        else:
            document_name = str(source) if source else ''

        if document_name and document_name not in document_names:
            document_names.append(str(document_name))

    return document_names


@require_http_methods(["POST"])
@csrf_exempt
def chat_submit(request):
    """Handle chat submission and return HTML message for htmx"""
    try:
        store_id = request.POST.get('store_id', '')
        query = request.POST.get('query', '')
        system_prompt = request.POST.get('system_prompt', '')
        
        if not store_id or not query:
            return JsonResponse({'error': 'Missing store_id or query'}, status=400)

        # Look up project for storage type
        project = Project.objects.filter(project_id=store_id).first()

        if not _user_can_access_project(project, request.user):
            return JsonResponse({'error': 'Forbidden'}, status=403)
        
        # Get or create prompt if not provided
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
            from llama_index.core import VectorStoreIndex
            from llama_index.vector_stores.postgres import PGVectorStore
            from llama_index.embeddings.google import GeminiEmbedding
            from llama_index.llms.google import Gemini
            from django.conf import settings
            import os
            
            vector_store = PGVectorStore.from_params(
                database=settings.DATABASES['default'].get('NAME', 'postgres'),
                host=settings.DATABASES['default'].get('HOST', 'localhost'),
                table_name=f"rag_project_{store_id}"
            )
            embed_model = GeminiEmbedding(
                model_name="models/embedding-001",
                api_key=os.getenv("GOOGLE_API_KEY")
            )
            llm = Gemini(
                model_name="models/gemini-1.5-flash",
                api_key=os.getenv("GOOGLE_API_KEY")
            )
            index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)
            query_engine = index.as_query_engine(llm=llm)
            
            prompt = system_prompt or "You are a helpful assistant."
            response = query_engine.query(f"System Context: {prompt}\n\nQuery: {query}")
            bot_response = str(response)
            source_documents = []
            if hasattr(response, 'source_nodes'):
                source_documents = _extract_source_documents([node.node.metadata for node in response.source_nodes])
        else:
            # Google store - look up the external_store_id
            if project and project.external_store_id:
                google_store_id = project.external_store_id
            else:
                google_store_id = store_id
            
            bot_response = gfs.ask_store_question(
                google_store_id,
                query,
                system_prompt=system_prompt
            )
            source_documents = []
        
        # Convert markdown to HTML
        bot_response_html = markdown.markdown(bot_response)
        
        # Store in database
        user_msg = ChatMessage.objects.create(
            project_id=project.id if project else 1,  # TODO: ensure project exists
            user=request.user if request.user.is_authenticated else None,
            message_type='user',
            content=query
        )
        bot_msg = ChatMessage.objects.create(
            project_id=project.id if project else 1,
            user=request.user if request.user.is_authenticated else None,
            message_type='assistant',
            content=bot_response,
            response_html=bot_response_html
        )
        
        # Build HTML directly instead of using templates
        user_html = f'''
<div class="flex justify-end mb-4">
    <div class="max-w-[80%] rounded-2xl bg-blue-600 text-white p-4 rounded-br-none">
        <p class="text-sm">{query}</p>
    </div>
</div>
'''
        
        sources_html = ''
        if source_documents:
            source_items = ''.join(
                f'<li class="text-xs text-gray-600">{escape(document_name)}</li>'
                for document_name in source_documents
            )
            sources_html = f'''
        <div class="mt-3 border-t border-gray-200 pt-3">
            <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">Sources</p>
            <ul class="mt-1 space-y-1">{source_items}</ul>
        </div>
'''

        bot_html = f'''
<div class="flex justify-start mb-4">
    <div class="max-w-[80%] rounded-2xl bg-gray-100 text-gray-800 p-4 rounded-bl-none">
        <div class="prose prose-sm text-gray-800">
            {bot_response_html}
        </div>
        {sources_html}
    </div>
</div>
'''
        
        # Return both messages as raw HTML
        from django.http import HttpResponse
        return HttpResponse(user_html + bot_html)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


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

        # Look up project for storage type
        project = Project.objects.filter(project_id=store_id).first()

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
            from llama_index.core import VectorStoreIndex
            from llama_index.vector_stores.postgres import PGVectorStore
            from llama_index.embeddings.google import GeminiEmbedding
            from llama_index.llms.google import Gemini
            from django.conf import settings
            import os
            
            vector_store = PGVectorStore.from_params(
                database=settings.DATABASES['default'].get('NAME', 'postgres'),
                host=settings.DATABASES['default'].get('HOST', 'localhost'),
                table_name=f"rag_project_{store_id}"
            )
            embed_model = GeminiEmbedding(
                model_name="models/embedding-001",
                api_key=os.getenv("GOOGLE_API_KEY")
            )
            llm = Gemini(
                model_name="models/gemini-1.5-flash",
                api_key=os.getenv("GOOGLE_API_KEY")
            )
            index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)
            query_engine = index.as_query_engine(llm=llm)
            
            prompt = system_prompt or "You are a helpful assistant."
            response = query_engine.query(f"System Context: {prompt}\n\nQuery: {query}")
            bot_response = str(response)
            source_documents = []
            if hasattr(response, 'source_nodes'):
                source_documents = _extract_source_documents([node.node.metadata for node in response.source_nodes])
        else:
            bot_response = gfs.ask_store_question(
                store_id,
                query,
                system_prompt=system_prompt
            )
            source_documents = []
        
        # Convert markdown to HTML
        bot_response_html = markdown.markdown(bot_response)
        
        # Store in database if user is authenticated
        if request.user.is_authenticated:
            ChatMessage.objects.create(
                project=project,
                user=request.user,
                message_type='user',
                content=query
            )
            ChatMessage.objects.create(
                project=project,
                user=request.user,
                message_type='assistant',
                content=bot_response,
                response_html=bot_response_html
            )
        
        return JsonResponse({
            'user_message': query,
            'bot_response': bot_response,
            'bot_response_html': bot_response_html,
            'source_documents': source_documents,
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)
