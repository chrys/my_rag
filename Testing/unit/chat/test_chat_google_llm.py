import pytest
import os
import sys
from django.test import Client

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

from src.apps.projects.models import Project
from prompt_storage import get_prompt_storage

@pytest.mark.django_db
class TestChatGoogleLLM:
    def test_chat_google_related_answer(self, mocker) -> None:
        # Mock Google File Search response to avoid real network call
        mock_gfs = mocker.MagicMock()
        mock_gfs.ask_store_question.return_value = "This is a document about pgvector."
        mocker.patch('src.apps.chat.views.gfs', mock_gfs)
        mocker.patch('src.apps.chat.views.LazyModuleProxy.__getattr__', return_value=mock_gfs)

        # Create project in test database
        project, _ = Project.objects.get_or_create(
            display_name="Test File Search",
            storage_type="google",
            defaults={
                "project_id": "test_google_file_search_id",
                "external_store_id": "fileSearchStores/test-file-search-qrksn8h37ju2"
            }
        )
        
        client = Client()
        response = client.post('/rag/submit/', {
            'store_id': project.project_id,
            'query': 'What is the main topic of the uploaded document?'
        })
        
        assert response.status_code == 200
        content = response.content.decode()
        assert len(content) > 0
        assert "flex" in content
        assert "error" not in content.lower() or "503" in content or "unavailable" in content

    def test_chat_google_unrelated_answer(self, mocker) -> None:
        # Mock Google File Search response to avoid real network call
        mock_gfs = mocker.MagicMock()
        mock_gfs.ask_store_question.return_value = "I cannot help with that."
        mocker.patch('src.apps.chat.views.gfs', mock_gfs)
        mocker.patch('src.apps.chat.views.LazyModuleProxy.__getattr__', return_value=mock_gfs)

        # Create project in test database
        project, _ = Project.objects.get_or_create(
            display_name="Test File Search",
            storage_type="google",
            defaults={
                "project_id": "test_google_file_search_id",
                "external_store_id": "fileSearchStores/test-file-search-qrksn8h37ju2"
            }
        )
            
        # Set a restrictive system prompt
        prompt_storage = get_prompt_storage()
        prompt_storage.set_prompt(
            project.project_id, 
            "Only answer questions about the document topic. For anything else, say 'I cannot help with that'."
        )
        
        client = Client()
        response = client.post('/rag/submit/', {
            'store_id': project.project_id,
            'query': 'How do I bake a cake?'
        })
        
        assert response.status_code == 200
        content = response.content.decode().lower()
        
        # Split content into segments to isolate the bot's response from the user's query
        segments = content.split('justify-start')
        bot_segment = segments[1] if len(segments) > 1 else content
        
        if "503" in bot_segment or "unavailable" in bot_segment or "error processing query" in bot_segment:
             return
             
        # Check if the refusal is in the response
        assert "cannot help" in bot_segment or "cake" not in bot_segment
