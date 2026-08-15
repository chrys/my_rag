import pytest
import os
import sys
import json
from django.test import RequestFactory, Client
from django.contrib.auth.models import User, AnonymousUser
from django.utils import timezone

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))

from src.apps.projects.models import Project
from src.apps.api.models import APIKey
from src.apps.chat.views import chat
from src.apps.projects.views import (
    project_api_keys,
    create_project_api_key,
    toggle_project_api_key,
    delete_project_api_key,
)


@pytest.mark.django_db
class TestProjectScopedAPIKeyModel:
    """Tests for APIKey model with project scoping"""

    def test_create_project_scoped_apikey(self):
        user = User.objects.create_user(username="keyowner", password="password")
        project = Project.objects.create(
            project_id="postgres_test_key_proj",
            display_name="Key Test Project",
            storage_type="postgres",
            user=user
        )

        api_key = APIKey.objects.create(
            user=user,
            project=project,
            name="Production Website Key"
        )

        assert api_key.key.startswith("rag_key_")
        assert api_key.project == project
        assert api_key.is_active is True
        assert "Key Test Project" in str(api_key)


@pytest.mark.django_db
class TestProjectAPIKeyHTMXViews:
    """Tests for HTMX API Key management views within Project Admin"""

    def test_list_project_api_keys(self):
        user = User.objects.create_user(username="viewuser", password="password")
        project = Project.objects.create(
            project_id="postgres_list_proj",
            display_name="List Project",
            storage_type="postgres",
            user=user
        )
        APIKey.objects.create(user=user, project=project, name="Key 1")
        APIKey.objects.create(user=user, project=project, name="Key 2")

        factory = RequestFactory()
        request = factory.get(f"/rag/projects/{project.project_id}/api-keys/")
        request.user = user

        response = project_api_keys(request, store_id=project.project_id)
        assert response.status_code == 200
        assert b"Key 1" in response.content
        assert b"Key 2" in response.content
        assert b"Project API Keys" in response.content

    def test_create_project_api_key(self):
        user = User.objects.create_user(username="createuser", password="password")
        project = Project.objects.create(
            project_id="postgres_create_proj",
            display_name="Create Project",
            storage_type="postgres",
            user=user
        )

        factory = RequestFactory()
        request = factory.post(
            f"/rag/projects/{project.project_id}/api-keys/create/",
            {"name": "Frontend Widget Key"}
        )
        request.user = user

        response = create_project_api_key(request, store_id=project.project_id)
        assert response.status_code == 200
        assert b"Frontend Widget Key" in response.content
        assert b"New API Key Generated" in response.content

        created_key = APIKey.objects.filter(project=project, name="Frontend Widget Key").first()
        assert created_key is not None
        assert created_key.key.startswith("rag_key_")

    def test_toggle_project_api_key(self):
        user = User.objects.create_user(username="toggleuser", password="password")
        project = Project.objects.create(
            project_id="postgres_toggle_proj",
            display_name="Toggle Project",
            storage_type="postgres",
            user=user
        )
        api_key = APIKey.objects.create(user=user, project=project, name="Toggle Key", is_active=True)

        factory = RequestFactory()
        request = factory.post(f"/rag/projects/{project.project_id}/api-keys/{api_key.id}/toggle/")
        request.user = user

        response = toggle_project_api_key(request, store_id=project.project_id, key_id=api_key.id)
        assert response.status_code == 200
        api_key.refresh_from_db()
        assert api_key.is_active is False

    def test_delete_project_api_key(self):
        user = User.objects.create_user(username="deleteuser", password="password")
        project = Project.objects.create(
            project_id="postgres_delete_proj",
            display_name="Delete Project",
            storage_type="postgres",
            user=user
        )
        api_key = APIKey.objects.create(user=user, project=project, name="To Delete Key")

        factory = RequestFactory()
        request = factory.post(f"/rag/projects/{project.project_id}/api-keys/{api_key.id}/delete/")
        request.user = user

        response = delete_project_api_key(request, store_id=project.project_id, key_id=api_key.id)
        assert response.status_code == 200
        assert not APIKey.objects.filter(id=api_key.id).exists()


@pytest.mark.django_db
class TestChatAPIKeyAuthenticationAndScoping:
    """Tests for Chat API authentication via X-API-Key and project scoping"""

    def test_chat_with_valid_project_scoped_x_api_key(self, mocker):
        user = User.objects.create_user(username="chatuser", password="password")
        project = Project.objects.create(
            project_id="local_scoped_chat_test",
            display_name="Scoped Local Project",
            storage_type="local",
            user=user
        )
        api_key = APIKey.objects.create(user=user, project=project, name="Chat Key")

        mock_engine = mocker.Mock()
        mock_engine.query.return_value = "API Key query successful."
        mocker.patch("src.apps.chat.views.get_rag_engine", return_value=mock_engine)

        client = Client()
        response = client.post(
            "/rag/api/chat/",
            data=json.dumps({
                "store_id": "local_scoped_chat_test",
                "query": "Hello via API Key"
            }),
            content_type="application/json",
            HTTP_X_API_KEY=api_key.key
        )

        assert response.status_code == 200
        data = response.json()
        assert data["bot_response"] == "API Key query successful."

        api_key.refresh_from_db()
        assert api_key.last_used_at is not None

    def test_chat_with_bearer_token_authorization(self, mocker):
        user = User.objects.create_user(username="beareruser", password="password")
        project = Project.objects.create(
            project_id="local_bearer_chat_test",
            display_name="Bearer Local Project",
            storage_type="local",
            user=user
        )
        api_key = APIKey.objects.create(user=user, project=project, name="Bearer Key")

        mock_engine = mocker.Mock()
        mock_engine.query.return_value = "Bearer token response."
        mocker.patch("src.apps.chat.views.get_rag_engine", return_value=mock_engine)

        client = Client()
        response = client.post(
            "/rag/api/chat/",
            data=json.dumps({
                "store_id": "local_bearer_chat_test",
                "query": "Hello via Bearer Token"
            }),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {api_key.key}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["bot_response"] == "Bearer token response."

    def test_chat_rejects_cross_project_api_key(self, mocker):
        user = User.objects.create_user(username="crossprojuser", password="password")
        project_a = Project.objects.create(
            project_id="local_proj_a",
            display_name="Project A",
            storage_type="local",
            user=user
        )
        project_b = Project.objects.create(
            project_id="local_proj_b",
            display_name="Project B",
            storage_type="local",
            user=user
        )
        # API Key strictly scoped to Project A
        api_key_a = APIKey.objects.create(user=user, project=project_a, name="Project A Only Key")

        client = Client()
        # Attempt to query Project B using Project A's key
        response = client.post(
            "/rag/api/chat/",
            data=json.dumps({
                "store_id": "local_proj_b",
                "query": "Sneaky query to Project B"
            }),
            content_type="application/json",
            HTTP_X_API_KEY=api_key_a.key
        )

        assert response.status_code == 403
        data = response.json()
        assert "not authorized for this project" in data["error"]

    def test_chat_rejects_inactive_api_key(self, mocker):
        user = User.objects.create_user(username="inactiveuser", password="password")
        project = Project.objects.create(
            project_id="local_inactive_proj",
            display_name="Inactive Key Project",
            storage_type="local",
            user=user
        )
        inactive_key = APIKey.objects.create(
            user=user,
            project=project,
            name="Deactivated Key",
            is_active=False
        )

        client = Client()
        response = client.post(
            "/rag/api/chat/",
            data=json.dumps({
                "store_id": "local_inactive_proj",
                "query": "Query with inactive key"
            }),
            content_type="application/json",
            HTTP_X_API_KEY=inactive_key.key
        )

        assert response.status_code == 401
        data = response.json()
        assert "Invalid or inactive API key" in data["error"]
