"""
Unit tests for Google Calendar view endpoints in src/apps/documents/views.py
"""

import pytest
from django.urls import reverse
from src.apps.projects.models import Project
from src.apps.documents.models import GoogleCalendarSource, GoogleCalendarEvent


@pytest.mark.django_db
class TestGoogleCalendarViews:

    def test_google_calendar_connect_view(self, client):
        project = Project.objects.create(
            project_id='view_connect_test',
            display_name='View Connect Test',
            storage_type='postgres'
        )
        url = reverse('documents:google_calendar_connect', kwargs={'store_id': project.project_id})
        response = client.get(url)

        assert response.status_code == 302
        assert "accounts.google.com" in response.url

    def test_google_calendar_oauth_callback_view(self, client, mocker):
        mocker.patch('src.apps.documents.views.exchange_oauth_code_for_tokens', return_value={
            'access_token': 'ya29.mock_callback_access',
            'refresh_token': 'mock_callback_refresh',
            'expires_in': 3600,
        })
        project = Project.objects.create(
            project_id='view_callback_test',
            display_name='View Callback Test',
            storage_type='postgres'
        )
        url = reverse('documents:google_calendar_oauth_callback') + f"?code=mock_code_123&state={project.project_id}"
        response = client.get(url)

        assert response.status_code == 302
        assert f"/rag/documents/{project.project_id}/" in response.url

        source = GoogleCalendarSource.objects.get(project=project)
        assert source.access_token == 'ya29.mock_callback_access'
        assert source.refresh_token == 'mock_callback_refresh'

    def test_google_calendar_save_preferences_view(self, client):
        project = Project.objects.create(
            project_id='view_prefs_test',
            display_name='View Prefs Test',
            storage_type='postgres'
        )
        source = GoogleCalendarSource.objects.create(
            project=project,
            access_token='ya29.mock_token'
        )
        url = reverse('documents:google_calendar_save_preferences', kwargs={'store_id': project.project_id})
        response = client.post(url, {
            'selected_calendars': ['primary', 'work_123'],
            'lookback_days': '45',
            'lookahead_days': '180',
        })

        assert response.status_code == 200
        source.refresh_from_db()
        assert source.selected_calendars == ['primary', 'work_123']
        assert source.lookback_days == 45
        assert source.lookahead_days == 180

    def test_google_calendar_sync_view(self, client, mocker):
        mocker.patch('src.apps.documents.google_calendar_services.fetch_events_from_google_api', return_value=[])
        project = Project.objects.create(
            project_id='view_sync_test',
            display_name='View Sync Test',
            storage_type='postgres'
        )
        source = GoogleCalendarSource.objects.create(
            project=project,
            access_token='ya29.mock_token'
        )
        url = reverse('documents:google_calendar_sync', kwargs={'store_id': project.project_id})
        response = client.post(url)

        assert response.status_code == 200
        assert b"google-calendar-section-container" in response.content

    def test_google_calendar_status_view(self, client):
        project = Project.objects.create(
            project_id='view_status_test',
            display_name='View Status Test',
            storage_type='postgres'
        )
        source = GoogleCalendarSource.objects.create(
            project=project,
            access_token='ya29.mock_token',
            total_events_count=10,
            pending_events_count=3
        )
        url = reverse('documents:google_calendar_status', kwargs={'store_id': project.project_id})
        response = client.get(url)

        assert response.status_code == 200
        assert b"google-calendar-section-container" in response.content
