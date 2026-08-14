"""
Unit tests for Google Calendar services in src/apps/documents/google_calendar_services.py
"""

import os
import pytest
from src.apps.projects.models import Project
from src.apps.documents.models import GoogleCalendarSource, GoogleCalendarEvent
from src.apps.documents.google_calendar_services import (
    get_google_client_config,
    get_oauth_authorization_url,
    convert_event_to_markdown,
    run_google_calendar_sync_lifecycle,
)


@pytest.mark.django_db
class TestGoogleCalendarServices:

    def test_get_google_client_config(self):
        config = get_google_client_config()
        assert "client_id" in config
        assert "client_secret" in config
        assert config["client_id"].startswith("728282639009-")

    def test_get_oauth_authorization_url(self):
        auth_url = get_oauth_authorization_url(project_id="test_proj_123", redirect_uri="http://127.0.0.1:8000/rag/google/oauth2callback/")
        assert "accounts.google.com" in auth_url
        assert "client_id=" in auth_url
        assert "test_proj_123" in auth_url

    def test_convert_event_to_markdown(self, tmp_path):
        event_dict = {
            "id": "evt_abc_123",
            "summary": "Architecture Review",
            "description": "Discussing vector database schema and RAG pipeline.",
            "start": {"dateTime": "2026-08-05T10:00:00Z"},
            "end": {"dateTime": "2026-08-05T11:00:00Z"},
            "organizer": {"email": "lead@example.com"},
            "attendees": [{"email": "dev1@example.com"}, {"email": "dev2@example.com"}],
            "location": "Conference Room B"
        }
        rel_path, full_path, markdown_content = convert_event_to_markdown(event_dict, store_id="test_store", base_dir=str(tmp_path))

        assert rel_path == "Calendar/2026-08-05_Architecture_Review.md"
        assert os.path.exists(full_path)
        assert "---" in markdown_content
        assert "event_id: \"evt_abc_123\"" in markdown_content
        assert "summary: \"Architecture Review\"" in markdown_content
        assert "organizer: \"lead@example.com\"" in markdown_content
        assert "# Architecture Review" in markdown_content

    def test_run_google_calendar_sync_lifecycle_mocked(self, mocker, tmp_path):
        mocker.patch('src.apps.documents.google_calendar_services.fetch_events_from_google_api', return_value=[
            {
                "id": "mock_evt_1",
                "summary": "Mock Meeting 1",
                "start": {"dateTime": "2026-08-05T14:00:00Z"},
                "end": {"dateTime": "2026-08-05T15:00:00Z"},
            },
            {
                "id": "mock_evt_2",
                "summary": "Mock Meeting 2",
                "start": {"dateTime": "2026-08-06T14:00:00Z"},
                "end": {"dateTime": "2026-08-06T15:00:00Z"},
            }
        ])

        project = Project.objects.create(
            project_id='sync_service_test',
            display_name='Sync Service Test',
            storage_type='postgres'
        )
        source = GoogleCalendarSource.objects.create(
            project=project,
            access_token='ya29.mock_token',
            refresh_token='mock_refresh'
        )

        result = run_google_calendar_sync_lifecycle(source, mode='sync', base_dir=str(tmp_path))

        assert result['total_events'] == 2
        assert result['pending_events'] == 2
        assert GoogleCalendarEvent.objects.filter(calendar_source=source).count() == 2
        assert source.reload().sync_status == 'COMPLETED' if hasattr(source, 'reload') else GoogleCalendarSource.objects.get(pk=source.pk).sync_status == 'COMPLETED'
