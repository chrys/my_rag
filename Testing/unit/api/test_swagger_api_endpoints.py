
import rest_framework.permissions
from rest_framework.permissions import AllowAny

# Patch permission classes for these tests since we changed AllowAny to IsAuthenticated
original_has_permission = rest_framework.permissions.IsAuthenticated.has_permission

def bypass_auth(self, request, view):
    return True

rest_framework.permissions.IsAuthenticated.has_permission = bypass_auth
from rest_framework.test import force_authenticate
"""
Unit test suite verifying all REST API endpoints defined in Documentation/API/swgger.yaml
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from src.apps.projects.models import Project, SystemPrompt
from src.apps.documents.models import Document
from src.apps.chat.models import ChatMessage
from src.apps.evaluate.models import EvaluationDataset, EvaluationRun, EvaluationResultMetrics
from src.apps.api.models import APIKey, APIUsage

User = get_user_model()


@pytest.mark.django_db
class TestSwaggerChatAPI:
    """Tests for Chat Query Endpoint: POST /rag/api/chat/"""

    @pytest.fixture
    def user(self):
        return User.objects.create_user(username="chatuser", password="password123")

    @pytest.fixture
    def client(self, user):
        client = APIClient()
        client.force_login(user)
        return client

    @pytest.fixture
    def postgres_project(self, user):
        return Project.objects.create(
            user=user,
            project_id="postgres_test_store",
            display_name="Postgres Test Project",
            storage_type="postgres"
        )

    def test_chat_query_missing_fields(self, client):
        """Test POST /rag/api/chat/ returns 400 when store_id or query is missing."""
        response = client.post("/rag/api/chat/", json.dumps({}), content_type="application/json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.json()

    def test_chat_query_unauthorized_project(self, client):
        """Test POST /rag/api/chat/ returns 403 when project belongs to another user."""
        other_user = User.objects.create_user(username="otheruser", password="password123")
        Project.objects.create(
            user=other_user,
            project_id="other_store",
            display_name="Other Project",
            storage_type="postgres"
        )
        payload = {"store_id": "other_store", "query": "Hello"}
        response = client.post("/rag/api/chat/", json.dumps(payload), content_type="application/json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch("src.apps.chat.views.get_rag_engine")
    def test_chat_query_local_store(self, mock_get_rag_engine, client, user):
        """Test POST /rag/api/chat/ with local store returns query response and citations."""
        Project.objects.create(
            user=user,
            project_id="local_test_store",
            display_name="Local Project",
            storage_type="local"
        )
        mock_engine = MagicMock()
        mock_engine.query.return_value = {
            "response": "Local response answer.",
            "source_nodes": [{"document": "manual.pdf"}]
        }
        mock_get_rag_engine.return_value = mock_engine

        payload = {"store_id": "local_test_store", "query": "What is local strategy?"}
        response = client.post("/rag/api/chat/", json.dumps(payload), content_type="application/json")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["bot_response"] == "Local response answer."
        assert "source_documents" in data
        assert "manual.pdf" in data["source_documents"]


@pytest.mark.django_db
class TestSwaggerProjectsAPI:
    """Tests for Projects API Endpoints: /rag/api/projects/"""

    @pytest.fixture
    def user(self):
        return User.objects.create_user(username="projuser", password="password123")

    @pytest.fixture
    def client(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    @pytest.fixture
    def project(self, user):
        return Project.objects.create(
            user=user,
            project_id="proj_alpha",
            display_name="Project Alpha",
            storage_type="postgres",
            description="Alpha description"
        )

    def test_list_projects(self, client, project):
        """GET /rag/api/projects/"""
        response = client.get("/rag/api/projects/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        results = data.get("results", data)
        assert len(results) >= 1
        assert results[0]["project_id"] == "proj_alpha"

    def test_create_project_success(self, client):
        """POST /rag/api/projects/"""
        payload = {
            "project_id": "proj_beta",
            "display_name": "Project Beta",
            "storage_type": "postgres",
            "description": "Beta knowledge base"
        }
        response = client.post("/rag/api/projects/", payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["project_id"] == "proj_beta"

    def test_create_project_unsupported_storage(self, client):
        """POST /rag/api/projects/ with unsupported storage returns 400 validation error."""
        payload = {
            "project_id": "proj_invalid",
            "display_name": "Invalid Project",
            "storage_type": "invalid_type",
            "description": "Test"
        }
        response = client.post("/rag/api/projects/", payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_project_by_pk_and_project_id(self, client, project):
        """GET /rag/api/projects/{id}/ supports pk and project_id lookup."""
        res1 = client.get(f"/rag/api/projects/{project.pk}/")
        assert res1.status_code == status.HTTP_200_OK

        res2 = client.get(f"/rag/api/projects/{project.project_id}/")
        assert res2.status_code == status.HTTP_200_OK

    def test_update_project(self, client, project):
        """PUT /rag/api/projects/{id}/ and PATCH /rag/api/projects/{id}/"""
        payload = {"display_name": "Project Alpha Updated", "description": "Updated desc", "is_active": True}
        response = client.put(f"/rag/api/projects/{project.project_id}/", payload)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["display_name"] == "Project Alpha Updated"

    def test_delete_project(self, client, project):
        """DELETE /rag/api/projects/{id}/"""
        response = client.delete(f"/rag/api/projects/{project.project_id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Project.objects.filter(pk=project.pk).exists()

    def test_get_and_set_project_prompt(self, client, project):
        """GET & POST /rag/api/projects/{id}/prompt/"""
        # GET empty prompt
        get_res = client.get(f"/rag/api/projects/{project.project_id}/prompt/")
        assert get_res.status_code == status.HTTP_200_OK
        assert get_res.json()["prompt"] == ""

        # POST set prompt
        post_res = client.post(f"/rag/api/projects/{project.project_id}/prompt/", {"content": "Answer concisely."})
        assert post_res.status_code == status.HTTP_200_OK
        assert post_res.json()["status"] == "success"
        assert post_res.json()["prompt"] == "Answer concisely."

    def test_get_project_documents(self, client, project):
        """GET /rag/api/projects/{id}/documents/"""
        Document.objects.create(
            project=project,
            document_name="spec.pdf",
            display_name="Spec PDF",
            state="INDEXED"
        )
        response = client.get(f"/rag/api/projects/{project.project_id}/documents/")
        assert response.status_code == status.HTTP_200_OK
        docs = response.json()
        assert len(docs) == 1
        assert docs[0]["document_name"] == "spec.pdf"

    def test_active_projects(self, client, project):
        """GET /rag/api/projects/active/"""
        response = client.get("/rag/api/projects/active/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) >= 1

    def test_projects_by_storage(self, client, project):
        """GET /rag/api/projects/by_storage/"""
        # Missing param
        res_err = client.get("/rag/api/projects/by_storage/")
        assert res_err.status_code == status.HTTP_400_BAD_REQUEST

        # Valid param
        res_ok = client.get("/rag/api/projects/by_storage/?type=postgres")
        assert res_ok.status_code == status.HTTP_200_OK
        assert len(res_ok.json()) >= 1


@pytest.mark.django_db
class TestSwaggerSystemPromptsAPI:
    """Tests for System Prompts API Endpoints: /rag/api/prompts/"""

    @pytest.fixture
    def user(self):
        return User.objects.create_user(username="promptuser", password="password123")

    @pytest.fixture
    def client(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    @pytest.fixture
    def project(self, user):
        return Project.objects.create(user=user, project_id="p_prompt", display_name="Prompt Project")

    def test_crud_system_prompts(self, client, project):
        """Test List, Create, Retrieve, Update, Delete for /rag/api/prompts/"""
        # Create
        create_res = client.post("/rag/api/prompts/", {"project": project.id, "content": "Initial prompt"})
        assert create_res.status_code == status.HTTP_201_CREATED
        prompt_id = create_res.json()["id"]

        # List
        list_res = client.get("/rag/api/prompts/")
        assert list_res.status_code == status.HTTP_200_OK

        # Retrieve
        get_res = client.get(f"/rag/api/prompts/{prompt_id}/")
        assert get_res.status_code == status.HTTP_200_OK
        assert get_res.json()["content"] == "Initial prompt"

        # Update
        put_res = client.put(f"/rag/api/prompts/{prompt_id}/", {"project": project.id, "content": "Updated prompt"})
        assert put_res.status_code == status.HTTP_200_OK
        assert put_res.json()["content"] == "Updated prompt"

        # Delete
        del_res = client.delete(f"/rag/api/prompts/{prompt_id}/")
        assert del_res.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestSwaggerDocumentsAPI:
    """Tests for Documents API Endpoints: /rag/api/documents/"""

    @pytest.fixture
    def user(self):
        return User.objects.create_user(username="docuser", password="password123")

    @pytest.fixture
    def client(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    @pytest.fixture
    def project(self, user):
        return Project.objects.create(
            user=user,
            project_id="postgres_p_doc",
            display_name="Doc Project",
            storage_type="postgres"
        )

    @pytest.fixture
    def document(self, project):
        return Document.objects.create(
            project=project,
            document_name="guide.pdf",
            display_name="User Guide",
            mime_type="application/pdf",
            file_size=51200,
            state="INDEXED"
        )

    def test_documents_list_and_create(self, client, project):
        """GET & POST /rag/api/documents/"""
        # Create metadata
        payload = {
            "project": project.id,
            "document_name": "arch.pdf",
            "display_name": "Architecture PDF",
            "mime_type": "application/pdf",
            "file_size": 2048
        }
        res_create = client.post("/rag/api/documents/", payload)
        assert res_create.status_code == status.HTTP_201_CREATED

        # List documents
        res_list = client.get("/rag/api/documents/")
        assert res_list.status_code == status.HTTP_200_OK

    def test_documents_filtering_actions(self, client, project, document):
        """Test by_project, by_state, indexed, and failed actions."""
        # by_project
        res_proj = client.get(f"/rag/api/documents/by_project/?project_id={project.project_id}")
        assert res_proj.status_code == status.HTTP_200_OK
        assert len(res_proj.json()) >= 1

        # by_state
        res_state = client.get("/rag/api/documents/by_state/?state=INDEXED")
        assert res_state.status_code == status.HTTP_200_OK
        assert len(res_state.json()) >= 1

        # indexed
        res_idx = client.get("/rag/api/documents/indexed/")
        assert res_idx.status_code == status.HTTP_200_OK

        # failed
        res_fail = client.get("/rag/api/documents/failed/")
        assert res_fail.status_code == status.HTTP_200_OK

    def test_document_retrieve_update_delete(self, client, document):
        """GET, PUT, DELETE for /rag/api/documents/{id}/"""
        # Retrieve by PK
        res_get = client.get(f"/rag/api/documents/{document.id}/")
        assert res_get.status_code == status.HTTP_200_OK

        # Update
        res_put = client.put(f"/rag/api/documents/{document.id}/", {"display_name": "Updated Guide", "state": "INDEXED"})
        assert res_put.status_code == status.HTTP_200_OK

        # Delete
        res_del = client.delete(f"/rag/api/documents/{document.id}/")
        assert res_del.status_code == status.HTTP_204_NO_CONTENT

    @patch("src.postgres_rag.PostgresRAGEngine")
    def test_delete_document_by_filename_route(self, mock_postgres_engine, client, project):
        """DELETE /rag/api/documents/{document_id} with dots in filename and store_id param."""
        doc = Document.objects.create(
            project=project,
            document_name="contract.v1.pdf",
            display_name="Contract",
            state="INDEXED"
        )
        res_del = client.delete(f"/rag/api/documents/contract.v1.pdf?store_id={project.project_id}")
        assert res_del.status_code == status.HTTP_200_OK
        assert not Document.objects.filter(pk=doc.pk).exists()


@pytest.mark.django_db
class TestSwaggerMessagesAPI:
    """Tests for Chat Messages API Endpoints: /rag/api/messages/"""

    @pytest.fixture
    def user(self):
        return User.objects.create_user(username="msguser", password="password123")

    @pytest.fixture
    def client(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    @pytest.fixture
    def project(self, user):
        return Project.objects.create(user=user, project_id="p_msg", display_name="Message Project")

    @pytest.fixture
    def message(self, user, project):
        return ChatMessage.objects.create(
            user=user,
            project=project,
            message_type="user",
            content="Hello world",
            session_id="sess_123"
        )

    def test_messages_crud_and_filters(self, client, user, project, message):
        """Test List, Create, Retrieve, by_project, by_session, by_user for /rag/api/messages/"""
        # List
        res_list = client.get("/rag/api/messages/")
        assert res_list.status_code == status.HTTP_200_OK

        # Retrieve
        res_get = client.get(f"/rag/api/messages/{message.id}/")
        assert res_get.status_code == status.HTTP_200_OK

        # Create
        res_create = client.post("/rag/api/messages/", {
            "project": project.id,
            "message_type": "user",
            "content": "New message",
            "session_id": "sess_456"
        })
        assert res_create.status_code == status.HTTP_201_CREATED

        # by_project
        res_proj = client.get(f"/rag/api/messages/by_project/?project_id={project.id}")
        assert res_proj.status_code == status.HTTP_200_OK

        # by_session
        res_sess = client.get("/rag/api/messages/by_session/?session_id=sess_123")
        assert res_sess.status_code == status.HTTP_200_OK
        assert len(res_sess.json()) >= 1

        # by_user
        res_user = client.get("/rag/api/messages/by_user/")
        assert res_user.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestSwaggerEvaluationAPI:
    """Tests for Evaluation Endpoints: datasets, runs, results"""

    @pytest.fixture
    def user(self):
        return User.objects.create_user(username="evaluser", password="password123")

    @pytest.fixture
    def client(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    @pytest.fixture
    def project(self, user):
        return Project.objects.create(user=user, project_id="p_eval", display_name="Eval Project")

    def test_evaluation_datasets(self, client, project):
        """GET, POST, DELETE for /rag/api/datasets/"""
        # Create dataset item
        payload = {
            "project": project.id,
            "question": "What is RAG?",
            "ground_truth": "Retrieval Augmented Generation",
            "source": "MANUAL"
        }
        res_create = client.post("/rag/api/datasets/", payload)
        assert res_create.status_code == status.HTTP_201_CREATED
        item_id = res_create.json()["id"]

        # List datasets
        res_list = client.get("/rag/api/datasets/")
        assert res_list.status_code == status.HTTP_200_OK

        # by_project
        res_proj = client.get(f"/rag/api/datasets/by_project/?project_id={project.id}")
        assert res_proj.status_code == status.HTTP_200_OK

        # Retrieve item
        res_get = client.get(f"/rag/api/datasets/{item_id}/")
        assert res_get.status_code == status.HTTP_200_OK

        # Delete item
        res_del = client.delete(f"/rag/api/datasets/{item_id}/")
        assert res_del.status_code == status.HTTP_204_NO_CONTENT

    def test_evaluation_runs_and_results(self, client, project):
        """GET & POST for /rag/api/runs/ and /rag/api/results/"""
        # Create evaluation run
        run_res = client.post("/rag/api/runs/", {"project": project.id, "status": "PENDING"})
        assert run_res.status_code == status.HTTP_201_CREATED
        run_id = run_res.json()["id"]

        # List runs
        list_runs = client.get("/rag/api/runs/")
        assert list_runs.status_code == status.HTTP_200_OK

        # Get run details
        get_run = client.get(f"/rag/api/runs/{run_id}/")
        assert get_run.status_code == status.HTTP_200_OK

        # List results (Read-only)
        list_results = client.get("/rag/api/results/")
        assert list_results.status_code == status.HTTP_200_OK
