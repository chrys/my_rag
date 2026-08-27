"""
Unit tests for Document Tenant Isolation (Task 2)
"""

import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from src.apps.projects.models import Project
from src.apps.documents.models import Document


@pytest.fixture
def user_a(db):
    return User.objects.create_user(username="doc_user_a", password="password123")


@pytest.fixture
def user_b(db):
    return User.objects.create_user(username="doc_user_b", password="password123")


@pytest.fixture
def staff_admin(db):
    return User.objects.create_user(username="doc_staff_admin", password="password123", is_staff=True)


@pytest.fixture
def project_a(db, user_a):
    return Project.objects.create(
        user=user_a,
        project_id="proj_doc_a",
        display_name="Doc Project A",
        storage_type="postgres",
    )


@pytest.fixture
def project_b(db, user_b):
    return Project.objects.create(
        user=user_b,
        project_id="proj_doc_b",
        display_name="Doc Project B",
        storage_type="postgres",
    )


@pytest.fixture
def doc_in_project_b(db, project_b):
    return Document.objects.create(
        project=project_b,
        document_name="secret_b.pdf",
        display_name="Secret B",
        state="INDEXED",
    )


@pytest.mark.django_db
class TestDocumentTenantIsolation:
    def test_user_a_cannot_view_user_b_documents_in_viewset(self, user_a, doc_in_project_b):
        client = APIClient()
        client.force_authenticate(user=user_a)

        res = client.get("/api/documents/")
        assert res.status_code == 200
        data = res.json()
        results = data.get("results", data) if isinstance(data, dict) else data
        assert not any(d["document_name"] == "secret_b.pdf" for d in results)

    def test_user_a_cannot_create_document_in_user_b_project(self, user_a, project_b):
        client = APIClient()
        client.force_authenticate(user=user_a)

        payload = {
            "project": project_b.id,
            "document_name": "injected.pdf",
            "display_name": "Injected PDF",
        }
        res = client.post("/rag/api/documents/", payload)
        assert res.status_code == 403

    @patch("src.postgres_rag.PostgresRAGEngine")
    def test_user_a_cannot_delete_user_b_document_via_route(
        self, mock_postgres_engine, user_a, project_b, doc_in_project_b
    ):
        client = APIClient()
        client.force_login(user=user_a)

        res = client.delete(f"/rag/api/documents/secret_b.pdf?store_id={project_b.project_id}")
        assert res.status_code == 403
        assert Document.objects.filter(pk=doc_in_project_b.pk).exists()

    @patch("src.postgres_rag.PostgresRAGEngine")
    def test_staff_admin_can_delete_document_across_projects(
        self, mock_postgres_engine, staff_admin, project_b, doc_in_project_b
    ):
        mock_inst = MagicMock()
        mock_postgres_engine.return_value = mock_inst

        client = APIClient()
        client.force_login(user=staff_admin)

        res = client.delete(f"/rag/api/documents/secret_b.pdf?store_id={project_b.project_id}")
        assert res.status_code == 200
        assert not Document.objects.filter(pk=doc_in_project_b.pk).exists()

    @patch("src.postgres_rag.PostgresRAGEngine")
    def test_owner_can_delete_own_document_via_route(
        self, mock_postgres_engine, user_b, project_b, doc_in_project_b
    ):
        mock_inst = MagicMock()
        mock_postgres_engine.return_value = mock_inst

        client = APIClient()
        client.force_login(user=user_b)

        res = client.delete(f"/rag/api/documents/secret_b.pdf?store_id={project_b.project_id}")
        assert res.status_code == 200
        assert not Document.objects.filter(pk=doc_in_project_b.pk).exists()

    def test_anonymous_user_cannot_delete_document_via_route(
        self, project_b, doc_in_project_b
    ):
        client = APIClient()

        res = client.delete(f"/rag/api/documents/secret_b.pdf?store_id={project_b.project_id}")
        assert res.status_code in [401, 403]
        assert Document.objects.filter(pk=doc_in_project_b.pk).exists()
