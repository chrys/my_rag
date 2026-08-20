"""
Unit tests for GFS Core Services and Store Provisioning
"""

import pytest
from unittest.mock import MagicMock, patch
from django.test import RequestFactory
from src.apps.projects.models import Project
from src.apps.projects.views import create_project
from src.google_file_search import (
    create_file_search_store,
    add_document_to_store,
    ask_store_question,
    GoogleFileSearchPermissionError,
)


@pytest.mark.django_db
class TestGFSCoreServices:
    """Test GFS core SDK integration functions"""

    @patch("src.google_file_search.client")
    def test_create_file_search_store_success(self, mock_client):
        """Test creating a GFS store successfully returns store resource name"""
        mock_store = MagicMock()
        mock_store.name = "fileSearchStores/test-store-123"
        mock_client.file_search_stores.create.return_value = mock_store

        store_name = create_file_search_store("My Test Project")
        assert store_name == "fileSearchStores/test-store-123"
        mock_client.file_search_stores.create.assert_called_once_with(
            config={"display_name": "My Test Project"}
        )

    @patch("src.google_file_search.client")
    def test_create_file_search_store_permission_error(self, mock_client):
        """Test permission error raised properly on 403"""
        from google.genai import errors as genai_errors

        error = genai_errors.ClientError(code=403, response_json={})
        mock_client.file_search_stores.create.side_effect = error

        with pytest.raises(GoogleFileSearchPermissionError):
            create_file_search_store("Forbidden Project")

    @patch("src.google_file_search.client")
    def test_add_document_to_store_with_custom_metadata(self, mock_client, tmp_path):
        """Test uploading document passes custom_metadata in config"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello GFS")

        mock_op = MagicMock()
        mock_op.done = True
        mock_client.file_search_stores.upload_to_file_search_store.return_value = mock_op

        mock_doc = MagicMock()
        mock_doc.display_name = "test.txt"
        mock_doc.name = "fileSearchStores/store-1/documents/doc-1"
        mock_doc.create_time = 12345
        mock_client.file_search_stores.documents.list.return_value = [mock_doc]

        metadata = [
            {"key": "department", "string_value": "finance"},
            {"key": "file_size_kb", "numeric_value": 12.4},
        ]

        doc_name = add_document_to_store(
            store_id="fileSearchStores/store-1",
            file_path=str(test_file),
            custom_metadata=metadata,
        )

        assert doc_name == "fileSearchStores/store-1/documents/doc-1"
        mock_client.file_search_stores.upload_to_file_search_store.assert_called_once_with(
            file=str(test_file),
            file_search_store_name="fileSearchStores/store-1",
            config={"display_name": "test.txt", "custom_metadata": metadata},
        )

    @patch("src.google_file_search.client")
    def test_ask_store_question_dynamic_model_and_filter(self, mock_client):
        """Test querying GFS with custom model and metadata filter"""
        mock_response = MagicMock()
        mock_response.candidates = [MagicMock()]
        mock_response.text = "Answer grounded in GFS"
        mock_response.candidates[0].grounding_metadata = None
        mock_client.models.generate_content.return_value = mock_response

        answer = ask_store_question(
            store_id="fileSearchStores/store-1",
            query="What is Q2 revenue?",
            system_prompt="Be concise.",
            model="gemini-3.7-flash",
            metadata_filters='department == "finance"',
        )

        assert "Answer grounded in GFS" in answer
        call_kwargs = mock_client.models.generate_content.call_args.kwargs
        assert call_kwargs["model"] == "gemini-3.7-flash"


@pytest.mark.django_db
class TestGFSProjectCreationView:
    """Test project creation view for Google File Search storage type"""

    @patch("src.apps.projects.views.gfs.create_file_search_store")
    def test_create_google_project_view_success(self, mock_create_store, rf):
        """Test creating a GFS project calls create_file_search_store and creates DB record"""
        mock_create_store.return_value = "fileSearchStores/new-store-999"

        request = rf.post(
            "/rag/projects/create/",
            {
                "display_name": "New Google Project",
                "storage_type": "google",
                "llm_model": "gemini-3.5-flash-lite",
            },
        )
        request.user = MagicMock(is_authenticated=False)

        response = create_project(request)
        assert response.status_code == 200

        project = Project.objects.filter(display_name="New Google Project").first()
        assert project is not None
        assert project.storage_type == "google"
        assert project.external_store_id == "fileSearchStores/new-store-999"
        assert project.llm_model == "gemini-3.5-flash-lite"
        mock_create_store.assert_called_once_with(display_name="New Google Project")

    @patch("src.apps.projects.views.gfs.create_file_search_store")
    def test_create_google_project_view_failure_banner(self, mock_create_store, rf):
        """Test that failure to create remote store returns error banner without creating DB record"""
        mock_create_store.side_effect = GoogleFileSearchPermissionError("Invalid Google API key")

        request = rf.post(
            "/rag/projects/create/",
            {
                "display_name": "Failed Google Project",
                "storage_type": "google",
            },
        )
        request.user = MagicMock(is_authenticated=False)

        response = create_project(request)
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "Google File Search Provisioning Failed" in content
        assert "Invalid Google API key" in content
        assert Project.objects.filter(display_name="Failed Google Project").count() == 0
