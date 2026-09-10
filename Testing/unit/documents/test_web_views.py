"""
Unit tests for WebSource HTMX views and endpoints.
"""

import pytest
from unittest.mock import MagicMock
from django.contrib.auth.models import User
from src.apps.projects.models import Project
from src.apps.documents.models import WebSource, WebPage


@pytest.fixture
def auth_user(client):
    user = User.objects.create_user(username="web_tester", password="password123")
    client.login(username="web_tester", password="password123")
    return user


@pytest.fixture
def other_user():
    return User.objects.create_user(username="intruder", password="password123")


@pytest.fixture
def web_project(auth_user):
    project = Project.objects.create(
        project_id="web_view_test_01",
        display_name="Web View Test Project",
        storage_type="postgres",
        user=auth_user,
    )
    source = WebSource.objects.create(
        project=project,
        root_url="https://docs.example.com/guides",
        allowed_domain="docs.example.com",
        subpath_only=True,
        max_pages=100,
        sync_status="IDLE",
    )
    return project, source


@pytest.mark.django_db
class TestWebViews:
    """Tests for WebSource HTMX endpoints and status polling."""

    def test_web_status_view_idle(self, client, web_project):
        project, source = web_project
        response = client.get(f"/rag/projects/{project.project_id}/web/status/")
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "web-status-poll" in content
        assert "IDLE" in content or "Idle" in content or "Completed" in content

    def test_web_status_view_discovering_polling(self, client, web_project):
        project, source = web_project
        source.sync_status = "DISCOVERING"
        source.save()

        response = client.get(f"/rag/projects/{project.project_id}/web/status/")
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert 'hx-trigger="every 2s"' in content
        assert "Discovering" in content or "DISCOVERING" in content

    def test_web_status_view_indexing_progress(self, client, web_project):
        project, source = web_project
        source.sync_status = "INDEXING"
        source.total_pages_count = 10
        source.indexed_pages_count = 5
        source.save()

        response = client.get(f"/rag/projects/{project.project_id}/web/status/")
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert 'hx-trigger="every 2s"' in content
        assert "50%" in content or "Indexing" in content

    def test_web_sync_triggers_background(self, client, web_project, monkeypatch):
        project, source = web_project
        mock_thread_start = MagicMock()
        monkeypatch.setattr("threading.Thread.start", mock_thread_start)

        response = client.post(f"/rag/projects/{project.project_id}/web/sync/")
        assert response.status_code == 200
        assert mock_thread_start.called
        source.refresh_from_db()
        assert source.sync_status in ("DISCOVERING", "INDEXING", "IDLE")

    def test_web_index_new_triggers_background(self, client, web_project, monkeypatch):
        project, source = web_project
        mock_thread_start = MagicMock()
        monkeypatch.setattr("threading.Thread.start", mock_thread_start)

        response = client.post(f"/rag/projects/{project.project_id}/web/index-new/")
        assert response.status_code == 200
        assert mock_thread_start.called

    def test_web_reindex_triggers_background(self, client, web_project, monkeypatch):
        project, source = web_project
        mock_thread_start = MagicMock()
        monkeypatch.setattr("threading.Thread.start", mock_thread_start)

        response = client.post(f"/rag/projects/{project.project_id}/web/reindex/")
        assert response.status_code == 200
        assert mock_thread_start.called

    def test_web_views_permission_denied_for_other_user(self, client, web_project, other_user):
        project, source = web_project
        client.login(username="intruder", password="password123")

        response = client.get(f"/rag/projects/{project.project_id}/web/status/")
        assert response.status_code in (403, 404)
