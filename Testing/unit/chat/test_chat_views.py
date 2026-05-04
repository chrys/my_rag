import pytest
import os
import sys
import json
from django.test import Client, RequestFactory
from django.contrib.auth.models import AnonymousUser

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

from src.apps.projects.models import Project
from src.apps.projects.models import SystemPrompt
from src.apps.chat.views import chat, chat_submit

from django.contrib.auth.models import User

@pytest.mark.django_db
class TestChatViews:
    def test_chat_submit_authenticated(self, mocker):
        user = User.objects.create_user(username='testuser', password='password')
        project = Project.objects.create(
            project_id='local_auth_test_id',
            display_name='Auth Project',
            storage_type='local'
        )
        
        mock_engine = mocker.Mock()
        mock_engine.query.return_value = "Auth response."
        mocker.patch('src.apps.chat.views.get_rag_engine', return_value=mock_engine)
        
        factory = RequestFactory()
        request = factory.post('/submit/', {
            'store_id': 'local_auth_test_id',
            'query': 'Auth query'
        })
        request.user = user
        
        response = chat_submit(request)
        
        assert response.status_code == 200
        assert b"Auth response." in response.content
        
        # Verify ChatMessage records created
        from src.apps.chat.models import ChatMessage
        assert ChatMessage.objects.filter(user=user, message_type='user').exists()
        assert ChatMessage.objects.filter(user=user, message_type='assistant').exists()

    def test_chat_submit_local(self, mocker):
        project = Project.objects.create(
            project_id='local_test_id',
            display_name='Local Project',
            storage_type='local'
        )
        
        mock_engine = mocker.Mock()
        mock_engine.query.return_value = "Local response."
        mocker.patch('src.apps.chat.views.get_rag_engine', return_value=mock_engine)
        
        factory = RequestFactory()
        request = factory.post('/submit/', {
            'store_id': 'local_test_id',
            'query': 'Tell me about local.'
        })
        request.user = AnonymousUser()
        
        response = chat_submit(request)
        
        assert response.status_code == 200
        assert b"Local response." in response.content

    def test_chat_api_local(self, mocker):
        project = Project.objects.create(
            project_id='local_api_id',
            display_name='Local API Project',
            storage_type='local'
        )
        
        mock_engine = mocker.Mock()
        mock_engine.query.return_value = "Local API response."
        mocker.patch('src.apps.chat.views.get_rag_engine', return_value=mock_engine)
        
        client = Client()
        response = client.post('/rag/api/chat/', data=json.dumps({
            'store_id': 'local_api_id',
            'query': 'API query'
        }), content_type='application/json')
        
        # Note: /rag/api/chat/ endpoint is views.chat
        
        assert response.status_code == 200
        data = response.json()
        assert data['bot_response'] == "Local API response."

    def test_chat_api_authenticated(self, mocker):
        user = User.objects.create_user(username='apiuser', password='password')
        project = Project.objects.create(
            project_id='local_api_auth_id',
            display_name='API Auth Project',
            storage_type='local'
        )
        
        mock_engine = mocker.Mock()
        mock_engine.query.return_value = "API Auth response."
        mocker.patch('src.apps.chat.views.get_rag_engine', return_value=mock_engine)
        
        client = Client()
        client.login(username='apiuser', password='password')
        response = client.post('/rag/api/chat/', data=json.dumps({
            'store_id': 'local_api_auth_id',
            'query': 'API auth query'
        }), content_type='application/json')
        
        assert response.status_code == 200
        from src.apps.chat.models import ChatMessage
        # Use project=project since the view should handle the lookup or we fix the view if it's broken
        assert ChatMessage.objects.filter(user=user, message_type='user').exists()

    def test_chat_submit_rag(self, mocker):
        project = Project.objects.create(
            project_id='postgres_test_submit',
            display_name='RAG Submit Project',
            storage_type='postgres'
        )
        
        mock_response = mocker.Mock()
        mock_response.__str__ = lambda x: "RAG response."
        mock_response.source_nodes = []
        mock_engine = mocker.Mock()
        mock_engine.query.return_value = mock_response
        mock_index = mocker.Mock()
        mock_index.as_query_engine.return_value = mock_engine
        mocker.patch("llama_index.embeddings.google.GeminiEmbedding", return_value=mocker.Mock())
        mocker.patch('llama_index.core.VectorStoreIndex.from_vector_store', return_value=mock_index)
        mocker.patch('llama_index.vector_stores.postgres.PGVectorStore.from_params', return_value=mocker.Mock())
        
        factory = RequestFactory()
        request = factory.post('/submit/', {
            'store_id': 'postgres_test_submit',
            'query': 'RAG query'
        })
        request.user = AnonymousUser()
        
        response = chat_submit(request)
        
        assert response.status_code == 200
        assert b"RAG response." in response.content

    def test_chat_submit_rag_includes_document_name_attribution(self, mocker):
        Project.objects.create(
            project_id='postgres_attribution_submit',
            display_name='Attributed RAG Submit Project',
            storage_type='postgres'
        )

        mock_response = mocker.Mock()
        mock_response.__str__ = lambda x: "RAG response with sources."
        node1 = mocker.Mock(); node1.node.metadata = {"document": "alpha.txt"}
        node2 = mocker.Mock(); node2.node.metadata = {"document": "beta.md"}
        mock_response.source_nodes = [node1, node2]
        mock_engine = mocker.Mock()
        mock_engine.query.return_value = mock_response
        mock_index = mocker.Mock()
        mock_index.as_query_engine.return_value = mock_engine
        mocker.patch("llama_index.embeddings.google.GeminiEmbedding", return_value=mocker.Mock())
        mocker.patch('llama_index.core.VectorStoreIndex.from_vector_store', return_value=mock_index)
        mocker.patch('llama_index.vector_stores.postgres.PGVectorStore.from_params', return_value=mocker.Mock())

        factory = RequestFactory()
        request = factory.post('/submit/', {
            'store_id': 'postgres_attribution_submit',
            'query': 'Attributed RAG query'
        })
        request.user = AnonymousUser()

        response = chat_submit(request)

        assert response.status_code == 200
        assert b"Sources" in response.content
        assert b"alpha.txt" in response.content
        assert b"beta.md" in response.content

    def test_chat_submit_rag_uses_project_system_prompt(self, mocker):
        project = Project.objects.create(
            project_id='postgres_prompted_submit',
            display_name='Prompted RAG Submit Project',
            storage_type='postgres'
        )
        SystemPrompt.objects.create(
            project=project,
            content='Use only the project system prompt.'
        )

        mock_response = mocker.Mock()
        mock_response.__str__ = lambda x: "Prompted RAG response."
        mock_response.source_nodes = []
        mock_engine = mocker.Mock()
        mock_engine.query.return_value = mock_response
        mock_index = mocker.Mock()
        mock_index.as_query_engine.return_value = mock_engine
        mocker.patch("llama_index.embeddings.google.GeminiEmbedding", return_value=mocker.Mock())
        mocker.patch('llama_index.core.VectorStoreIndex.from_vector_store', return_value=mock_index)
        mocker.patch('llama_index.vector_stores.postgres.PGVectorStore.from_params', return_value=mocker.Mock())

        factory = RequestFactory()
        request = factory.post('/submit/', {
            'store_id': 'postgres_prompted_submit',
            'query': 'Prompted RAG query'
        })
        request.user = AnonymousUser()

        response = chat_submit(request)

        assert response.status_code == 200
        mock_engine.query.assert_called_once_with(
            'System Context: Use only the project system prompt.\n\nQuery: Prompted RAG query'
        )

    def test_chat_submit_rag_rejects_non_owner(self, mocker):
        owner = User.objects.create_user(username='ragowner', password='password')
        intruder = User.objects.create_user(username='ragintruder', password='password')
        Project.objects.create(
            project_id='postgres_owned_submit',
            display_name='Owned RAG Submit Project',
            storage_type='postgres',
            user=owner,
        )

        mock_engine = mocker.Mock()
        mock_index = mocker.Mock()
        mock_index.as_query_engine.return_value = mock_engine
        mocker.patch("llama_index.embeddings.google.GeminiEmbedding", return_value=mocker.Mock())
        mocker.patch('llama_index.core.VectorStoreIndex.from_vector_store', return_value=mock_index)
        mocker.patch('llama_index.vector_stores.postgres.PGVectorStore.from_params', return_value=mocker.Mock())

        factory = RequestFactory()
        request = factory.post('/submit/', {
            'store_id': 'postgres_owned_submit',
            'query': 'Blocked RAG query'
        })
        request.user = intruder

        response = chat_submit(request)

        assert response.status_code == 403
        mock_engine.query.assert_not_called()

    def test_chat_api_rag_returns_document_name_attribution(self, mocker):
        Project.objects.create(
            project_id='postgres_attribution_api',
            display_name='Attributed RAG API Project',
            storage_type='postgres'
        )

        mock_response = mocker.Mock()
        mock_response.__str__ = lambda x: "API RAG response."
        node1 = mocker.Mock(); node1.node.metadata = {"document": "alpha.txt"}
        node2 = mocker.Mock(); node2.node.metadata = {"document": "alpha.txt"}
        node3 = mocker.Mock(); node3.node.metadata = {"document": "beta.md"}
        mock_response.source_nodes = [node1, node2, node3]
        mock_engine = mocker.Mock()
        mock_engine.query.return_value = mock_response
        mock_index = mocker.Mock()
        mock_index.as_query_engine.return_value = mock_engine
        mocker.patch("llama_index.embeddings.google.GeminiEmbedding", return_value=mocker.Mock())
        mocker.patch('llama_index.core.VectorStoreIndex.from_vector_store', return_value=mock_index)
        mocker.patch('llama_index.vector_stores.postgres.PGVectorStore.from_params', return_value=mocker.Mock())

        factory = RequestFactory()
        request = factory.post(
            '/rag/api/chat/',
            data=json.dumps({
                'store_id': 'postgres_attribution_api',
                'query': 'API attributed query'
            }),
            content_type='application/json'
        )
        request.user = AnonymousUser()

        response = chat(request)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['bot_response'] == 'API RAG response.'
        assert data['source_documents'] == ['alpha.txt', 'beta.md']

    def test_chat_api_missing_params(self):
        client = Client()
        response = client.post('/rag/api/chat/', data=json.dumps({
            'query': 'Missing store_id'
        }), content_type='application/json')
        
        assert response.status_code == 400
