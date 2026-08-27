"""
Unit tests for Tenant Isolation and API Key Scoping (Task 2)
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from src.apps.projects.models import Project
from src.apps.api.models import APIKey
from src.apps.documents.models import Document


@pytest.fixture
def user_a(db):
    return User.objects.create_user(username="user_tenant_a", password="password123")


@pytest.fixture
def user_b(db):
    return User.objects.create_user(username="user_tenant_b", password="password123")


@pytest.fixture
def project_a(db, user_a):
    return Project.objects.create(
        user=user_a,
        project_id="proj_tenant_a",
        display_name="Project Tenant A",
        storage_type="postgres",
    )


@pytest.fixture
def project_b(db, user_b):
    return Project.objects.create(
        user=user_b,
        project_id="proj_tenant_b",
        display_name="Project Tenant B",
        storage_type="postgres",
    )


@pytest.fixture
def key_for_project_a(db, user_a, project_a):
    return APIKey.objects.create(
        user=user_a,
        project=project_a,
        name="Key for Project A",
        key="key_secret_tenant_a",
        is_active=True,
    )


@pytest.fixture
def unscoped_key_regular_user(db, user_a):
    return APIKey.objects.create(
        user=user_a,
        project=None,
        name="Unscoped Regular Key",
        key="unscoped_key_regular",
        is_active=True,
    )


@pytest.mark.django_db
class TestTenantIsolationAndKeyScoping:
    @patch("llama_index.core.VectorStoreIndex.from_vector_store")
    @patch("src.apps.documents.services.get_vector_store")
    def test_api_key_scoped_to_assigned_project_succeeds(
        self, mock_get_store, mock_vector_index, key_for_project_a, project_a
    ):
        mock_engine = MagicMock()
        mock_engine.query.return_value = "Answer for project A"
        mock_index_inst = MagicMock()
        mock_index_inst.as_query_engine.return_value = mock_engine
        mock_vector_index.return_value = mock_index_inst

        client = APIClient()

        response = client.post(
            "/rag/api/chat/",
            json.dumps({"store_id": project_a.project_id, "query": "What is in project A?"}),
            content_type="application/json",
            HTTP_X_API_KEY=key_for_project_a.key,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Answer for project A"

    @patch("src.apps.documents.services.get_vector_store")
    def test_api_key_cross_tenant_access_blocked_immediately(
        self, mock_get_store, key_for_project_a, project_b
    ):
        """Key scoped to Project A trying to query Project B must return 403 with 0 retrieval."""
        client = APIClient()

        response = client.post(
            "/rag/api/chat/",
            json.dumps({"store_id": project_b.project_id, "query": "Steal data from project B"}),
            content_type="application/json",
            HTTP_X_API_KEY=key_for_project_a.key,
        )

        assert response.status_code == 403
        data = response.json()
        assert "not authorized" in data.get("error", "").lower()
        # Assert get_vector_store was never called for project B
        mock_get_store.assert_not_called()

    @patch("src.apps.documents.services.get_vector_store")
    def test_unscoped_api_key_rejected_for_non_admin(
        self, mock_get_store, unscoped_key_regular_user, project_a
    ):
        """Unscoped key from regular user is rejected for chat access."""
        client = APIClient()

        response = client.post(
            "/rag/api/chat/",
            json.dumps({"store_id": project_a.project_id, "query": "Query with unscoped key"}),
            content_type="application/json",
            HTTP_X_API_KEY=unscoped_key_regular_user.key,
        )

        assert response.status_code == 403
        mock_get_store.assert_not_called()

    def test_project_scoped_user_can_read_project_documents(self, user_a, project_a):
        Document.objects.create(
            project=project_a,
            document_name="guide.pdf",
            display_name="Guide PDF",
            state="INDEXED",
        )
        client = APIClient()
        client.force_authenticate(user=user_a)

        res = client.get(f"/rag/api/projects/{project_a.project_id}/documents/")
        assert res.status_code == 200
        docs = res.json()
        assert len(docs) == 1
        assert docs[0]["document_name"] == "guide.pdf"
