"""
Unit tests for GoogleCalendarSource and GoogleCalendarEvent models in documents app
"""

import pytest
from src.apps.projects.models import Project
from src.apps.documents.models import ObsidianSource, GoogleCalendarSource, GoogleCalendarEvent


@pytest.mark.django_db
class TestGoogleCalendarModels:
    """Test cases for GoogleCalendarSource and GoogleCalendarEvent models"""

    def test_obsidian_source_types_includes_google_calendar(self):
        source_types = [choice[0] for choice in ObsidianSource.SOURCE_TYPES]
        assert 'google_calendar' in source_types

    def test_create_google_calendar_source(self):
        project = Project.objects.create(
            project_id='gcal_model_test',
            display_name='GCal Model Test',
            storage_type='postgres'
        )
        source = GoogleCalendarSource.objects.create(
            project=project,
            access_token='ya29.test_access_token',
            refresh_token='1//test_refresh_token',
            selected_calendars=['primary', 'work_cal_123'],
            lookback_days=30,
            lookahead_days=365,
            sync_token='sync_token_abc123'
        )

        assert source.id is not None
        assert source.project == project
        assert source.access_token == 'ya29.test_access_token'
        assert source.refresh_token == '1//test_refresh_token'
        assert source.selected_calendars == ['primary', 'work_cal_123']
        assert source.lookback_days == 30
        assert source.lookahead_days == 365
        assert source.sync_token == 'sync_token_abc123'
        assert source.sync_status == 'IDLE'

    def test_create_google_calendar_event(self):
        project = Project.objects.create(
            project_id='gcal_event_test',
            display_name='GCal Event Test',
            storage_type='postgres'
        )
        source = GoogleCalendarSource.objects.create(
            project=project,
            access_token='ya29.test_token'
        )
        event = GoogleCalendarEvent.objects.create(
            calendar_source=source,
            event_id='event_id_999',
            summary='Sprint Planning Sync',
            relative_path='Calendar/2026-08-05_Sprint_Planning_Sync.md',
            status='PENDING'
        )

        assert event.id is not None
        assert event.calendar_source == source
        assert event.event_id == 'event_id_999'
        assert event.summary == 'Sprint Planning Sync'
        assert event.relative_path == 'Calendar/2026-08-05_Sprint_Planning_Sync.md'
        assert event.status == 'PENDING'
