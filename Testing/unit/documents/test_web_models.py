"""
Unit tests for WebSource and WebPage models in documents app.
"""

import pytest
from django.db import IntegrityError
from src.apps.projects.models import Project
from src.apps.documents.models import WebSource, WebPage


@pytest.mark.django_db
class TestWebModels:
    """Test cases for WebSource and WebPage models."""

    def test_create_web_source_defaults(self):
        project = Project.objects.create(
            project_id="web_model_test_01",
            display_name="Web Model Test",
            storage_type="postgres",
        )
        source = WebSource.objects.create(
            project=project,
            root_url="https://docs.example.com/guides/",
            allowed_domain="docs.example.com",
        )

        assert source.id is not None
        assert source.project == project
        assert source.root_url == "https://docs.example.com/guides/"
        assert source.allowed_domain == "docs.example.com"
        assert source.subpath_only is True
        assert source.max_depth == 4
        assert source.max_pages == 100
        assert source.sync_status == "IDLE"
        assert source.total_pages_count == 0
        assert source.indexed_pages_count == 0
        assert source.pending_pages_count == 0
        assert source.failed_pages_count == 0
        assert "docs.example.com" in str(source)

    def test_create_web_page(self):
        project = Project.objects.create(
            project_id="web_page_test_02",
            display_name="Web Page Test",
            storage_type="postgres",
        )
        source = WebSource.objects.create(
            project=project,
            root_url="https://docs.example.com/",
            allowed_domain="docs.example.com",
        )
        page = WebPage.objects.create(
            web_source=source,
            url="https://docs.example.com/intro",
            title="Introduction",
            depth=1,
            status="PENDING",
        )

        assert page.id is not None
        assert page.web_source == source
        assert page.url == "https://docs.example.com/intro"
        assert page.title == "Introduction"
        assert page.depth == 1
        assert page.status == "PENDING"
        assert page.content_hash == ""
        assert "https://docs.example.com/intro" in str(page)

    def test_web_page_unique_together(self):
        project = Project.objects.create(
            project_id="web_page_test_03",
            display_name="Web Page Test Unique",
            storage_type="postgres",
        )
        source = WebSource.objects.create(
            project=project,
            root_url="https://docs.example.com/",
            allowed_domain="docs.example.com",
        )
        WebPage.objects.create(
            web_source=source,
            url="https://docs.example.com/duplicate",
            title="First",
        )

        with pytest.raises(IntegrityError):
            WebPage.objects.create(
                web_source=source,
                url="https://docs.example.com/duplicate",
                title="Second",
            )
