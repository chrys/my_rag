"""
Integration tests for Pre-Retrieval Intent Pipeline and Chat History Persistence (Task 3)
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from src.apps.projects.models import Project
from src.apps.chat.models import ChatMessage


@pytest.fixture
def test_user(db):
    return User.objects.create_user(username="chat_intent_user", password="password123")


@pytest.fixture
def test_project(db, test_user):
    return Project.objects.create(
        user=test_user,
        project_id="proj_chat_intent",
        display_name="Chat Intent Project",
        storage_type="postgres",
    )


@pytest.mark.django_db
class TestChatIntentIntegration:
    @patch("src.apps.documents.services.get_vector_store")
    def test_greeting_query_bypasses_vector_store_and_logs_history(
        self, mock_get_store, test_user, test_project
    ):
        """Scenario 9: Casual greeting executes 0 vector searches and logs to ChatMessage."""
        client = APIClient()
        client.force_login(user=test_user)

        session_id = "session_intent_001"
        response = client.post(
            "/rag/api/chat/",
            json.dumps({
                "store_id": test_project.project_id,
                "query": "Hello there!",
                "session_id": session_id,
            }),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["response"] is not None
        assert "assist" in data["response"].lower() or "help" in data["response"].lower()
        
        # Verify 0 vector queries were triggered
        mock_get_store.assert_not_called()

        # Verify chat history logged both user and assistant turns
        history = ChatMessage.objects.filter(session_id=session_id).order_by("created_at")
        assert history.count() == 2
        assert history[0].message_type == "user"
        assert history[0].content == "Hello there!"
        assert history[1].message_type == "assistant"
        assert history[1].content == data["response"]

    @patch("src.apps.documents.services.get_vector_store")
    def test_vague_query_returns_clarification_prompt_with_zero_retrieval(
        self, mock_get_store, test_user, test_project
    ):
        """Scenario 10: Vague / ambiguous query prompts clarification with 0 vector searches."""
        client = APIClient()
        client.force_login(user=test_user)

        session_id = "session_intent_002"
        response = client.post(
            "/rag/api/chat/",
            json.dumps({
                "store_id": test_project.project_id,
                "query": "?",
                "session_id": session_id,
            }),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert "brief" in data["response"].lower() or "specify" in data["response"].lower() or "question" in data["response"].lower()

        # Zero vector searches
        mock_get_store.assert_not_called()

        # Turns logged
        history = ChatMessage.objects.filter(session_id=session_id)
        assert history.count() == 2

    @patch("llama_index.embeddings.google.GeminiEmbedding")
    @patch("llama_index.llms.google_genai.GoogleGenAI")
    @patch("src.apps.chat.intent_service.classify_query_intent", return_value={"intent": "VECTOR_SEARCH", "requires_retrieval": True, "response": None})
    @patch("llama_index.core.VectorStoreIndex.from_vector_store")
    @patch("src.apps.documents.services.get_vector_store")
    def test_informational_query_executes_retrieval_and_logs_history(
        self, mock_get_store, mock_vector_index, mock_intent, mock_llm, mock_embed, test_user, test_project
    ):
        mock_engine = MagicMock()
        mock_engine.query.return_value = "The project roadmap includes Q4 delivery."
        mock_index = MagicMock()
        mock_index.as_query_engine.return_value = mock_engine
        mock_vector_index.return_value = mock_index

        client = APIClient()
        client.force_login(user=test_user)

        session_id = "session_intent_003"
        response = client.post(
            "/rag/api/chat/",
            json.dumps({
                "store_id": test_project.project_id,
                "query": "What is scheduled in the project roadmap?",
                "session_id": session_id,
            }),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert "roadmap" in data["response"].lower()

        # Vector store was retrieved
        mock_get_store.assert_called_once_with(test_project.project_id)

        # Turns logged
        history = ChatMessage.objects.filter(session_id=session_id)
        assert history.count() == 2

    @patch("src.apps.documents.services.get_vector_store")
    def test_chat_submit_htmx_greeting_intent(
        self, mock_get_store, test_user, test_project
    ):
        """Web UI HTMX submit view intercepts greetings with 0 retrieval."""
        from django.test import RequestFactory
        from src.apps.chat.views import chat_submit

        factory = RequestFactory()
        request = factory.post(
            "/submit/",
            {
                "store_id": test_project.project_id,
                "query": "Good morning!",
            },
        )
        request.user = test_user

        response = chat_submit(request)
        assert response.status_code == 200
        assert b"Good morning" in response.content or b"assist" in response.content or b"help" in response.content
        mock_get_store.assert_not_called()

    @patch("llama_index.embeddings.google.GeminiEmbedding")
    @patch("llama_index.llms.google_genai.GoogleGenAI")
    @patch("src.apps.chat.intent_service.classify_query_intent")
    @patch("llama_index.core.VectorStoreIndex.from_vector_store")
    @patch("src.apps.documents.services.get_vector_store")
    def test_multiturn_intent_conversation_persistence(
        self, mock_get_store, mock_vector_index, mock_intent, mock_llm, mock_embed, test_user, test_project
    ):
        """A multi-turn conversation (greeting -> vague -> retrieval) saves all 6 turns."""
        mock_engine = MagicMock()
        mock_engine.query.return_value = "Detailed architecture answer."
        mock_index = MagicMock()
        mock_index.as_query_engine.return_value = mock_engine
        mock_vector_index.return_value = mock_index

        client = APIClient()
        client.force_login(user=test_user)
        session_id = "session_multiturn_100"

        # Turn 1: Greeting (bypasses LLM, handled by heuristics)
        res1 = client.post(
            "/rag/api/chat/",
            json.dumps({"store_id": test_project.project_id, "query": "Hello", "session_id": session_id}),
            content_type="application/json",
        )
        assert res1.status_code == 200

        # Turn 2: Vague query (handled by heuristics/clarification)
        res2 = client.post(
            "/rag/api/chat/",
            json.dumps({"store_id": test_project.project_id, "query": "?", "session_id": session_id}),
            content_type="application/json",
        )
        assert res2.status_code == 200

        # Turn 3: Vector search query
        mock_intent.return_value = {"intent": "VECTOR_SEARCH", "requires_retrieval": True, "response": None}
        res3 = client.post(
            "/rag/api/chat/",
            json.dumps({"store_id": test_project.project_id, "query": "Explain system architecture", "session_id": session_id}),
            content_type="application/json",
        )
        assert res3.status_code == 200

        # Verify all 6 messages are saved in chronological order
        msgs = ChatMessage.objects.filter(session_id=session_id).order_by("created_at")
        assert msgs.count() == 6
        assert msgs[0].message_type == "user" and msgs[0].content == "Hello"
        assert msgs[1].message_type == "assistant"
        assert msgs[2].message_type == "user" and msgs[2].content == "?"
        assert msgs[3].message_type == "assistant"
        assert msgs[4].message_type == "user" and msgs[4].content == "Explain system architecture"
        assert msgs[5].message_type == "assistant" and msgs[5].content == "Detailed architecture answer."
