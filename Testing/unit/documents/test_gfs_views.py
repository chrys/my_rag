"""
Unit tests for GFS Document Inspection & Upload Views with Deduplication (Task 5)
"""

import json
import pytest
from unittest.mock import MagicMock, patch
from django.test import RequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from src.apps.projects.models import Project
from src.apps.documents.models import Document
from src.apps.documents.views import inspect_document, upload_document


@pytest.fixture
def gfs_project():
    """Fixture for GFS Project"""
    return Project.objects.create(
        project_id="google_test_proj_001",
        display_name="GFS Project",
        storage_type="google",
        external_store_id="fileSearchStores/store-999",
        llm_model="gemini-2.5-flash-lite",
    )


@pytest.mark.django_db
class TestGFSInspectionAndUploadViews:
    """Test inspect_document and upload_document views with duplicate handling and metadata pipeline"""

    @patch("src.apps.documents.services.extract_ai_metadata_with_gemini_flash")
    def test_inspect_document_fresh_upload(self, mock_ai_meta, rf, gfs_project):
        """Test pre-upload inspection on a fresh file returns the upload review modal"""
        mock_ai_meta.return_value = [{"key": "department", "string_value": "Engineering"}]
        
        file_content = b"Fresh quarterly documentation."
        uploaded_file = SimpleUploadedFile("fresh_report.txt", file_content, content_type="text/plain")

        request = rf.post(
            f"/rag/projects/{gfs_project.project_id}/inspect-document/",
            {"file": uploaded_file},
        )
        request.user = MagicMock(is_authenticated=True, username="testuser")

        response = inspect_document(request, gfs_project.project_id)
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "fresh_report.txt" in content
        assert "department" in content or "metadata" in content.lower()

    def test_inspect_document_duplicate_detected(self, rf, gfs_project):
        """Test pre-upload inspection detects SHA-256 duplicate and returns duplicate modal"""
        file_content = b"Identical duplicate content."
        import hashlib
        file_hash = hashlib.sha256(file_content).hexdigest()

        # Create existing document record in DB
        Document.objects.create(
            project=gfs_project,
            document_name="existing_report.txt",
            content_hash=file_hash,
            store_file_id="fileSearchStores/store-999/documents/doc-1",
            state="INDEXED",
        )

        uploaded_file = SimpleUploadedFile("new_name_same_content.txt", file_content, content_type="text/plain")
        request = rf.post(
            f"/rag/projects/{gfs_project.project_id}/inspect-document/",
            {"file": uploaded_file},
        )
        request.user = MagicMock(is_authenticated=False)

        response = inspect_document(request, gfs_project.project_id)
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "Duplicate Document Detected" in content or "already exists" in content.lower()

    @patch("src.google_file_search.add_document_to_store")
    def test_upload_document_persists_to_local_state_registry(self, mock_add_doc, rf, gfs_project):
        """Test final upload indexes into GFS and persists to Document state registry"""
        mock_add_doc.return_value = "fileSearchStores/store-999/documents/doc-new"

        file_content = b"Final document to be indexed."
        uploaded_file = SimpleUploadedFile("final_doc.txt", file_content, content_type="text/plain")

        custom_metadata_json = json.dumps([
            {"key": "team", "value": "security"},
            {"key": "priority", "value": 1},
        ])

        request = rf.post(
            f"/rag/documents/{gfs_project.project_id}/upload/",
            {
                "file": uploaded_file,
                "custom_metadata": custom_metadata_json,
            },
        )
        request.user = MagicMock(is_authenticated=False)

        response = upload_document(request, gfs_project.project_id)
        assert response.status_code == 200

        doc = Document.objects.filter(project=gfs_project, document_name="final_doc.txt").first()
        assert doc is not None
        assert doc.store_file_id == "fileSearchStores/store-999/documents/doc-new"
        assert doc.state == "INDEXED"
        assert len(doc.content_hash) == 64
        assert doc.custom_metadata.get("team") == "security"

    @patch("src.google_file_search.delete_document_from_store")
    @patch("src.google_file_search.add_document_to_store")
    def test_upload_document_force_reupload(self, mock_add_doc, mock_del_doc, rf, gfs_project):
        """Test force re-upload deletes old store index and updates DB record"""
        mock_add_doc.return_value = "fileSearchStores/store-999/documents/doc-replaced"

        file_content = b"Reuploaded content."
        import hashlib
        file_hash = hashlib.sha256(file_content).hexdigest()

        old_doc = Document.objects.create(
            project=gfs_project,
            document_name="reupload.txt",
            content_hash=file_hash,
            store_file_id="fileSearchStores/store-999/documents/doc-old",
            state="INDEXED",
        )

        uploaded_file = SimpleUploadedFile("reupload.txt", file_content, content_type="text/plain")
        request = rf.post(
            f"/rag/documents/{gfs_project.project_id}/upload/",
            {
                "file": uploaded_file,
                "force_reupload": "true",
            },
        )
        request.user = MagicMock(is_authenticated=False)

        response = upload_document(request, gfs_project.project_id)
        assert response.status_code == 200

        mock_del_doc.assert_called_once_with("fileSearchStores/store-999/documents/doc-old")
        old_doc.refresh_from_db()
        assert old_doc.store_file_id == "fileSearchStores/store-999/documents/doc-replaced"
