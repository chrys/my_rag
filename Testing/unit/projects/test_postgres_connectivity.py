import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse
from django.test import RequestFactory
from django.http import HttpResponse
from django.core.files.uploadedfile import SimpleUploadedFile
from src.apps.projects.models import Project
from src.apps.documents.models import Document
from src.apps.projects.db_utils import test_postgres_connection as pg_conn_test

@pytest.mark.django_db
class TestPostgresConnectivity:
    """Test suite for PostgreSQL connectivity checks and views integration"""

    @patch("psycopg2.connect")
    def test_postgres_connection_success(self, mock_connect) -> None:
        """Test test_postgres_connection utility returns True on successful connection"""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        success, error = pg_conn_test()

        assert success is True
        assert error == ""
        mock_connect.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("psycopg2.connect")
    def test_postgres_connection_failure(self, mock_connect) -> None:
        """Test test_postgres_connection utility returns False and error message on connection error"""
        mock_connect.side_effect = Exception("Connection timed out")

        success, error = pg_conn_test()

        assert success is False
        assert "Connection timed out" in error
        mock_connect.assert_called_once()

    @patch("src.apps.projects.views.test_postgres_connection")
    def test_create_project_postgres_connection_failure(self, mock_test_conn, client) -> None:
        """Test that project creation fails and returns hx-swap-oob when database connection check fails"""
        mock_test_conn.return_value = (False, "Fatal: database 'db.sqlite3' does not exist")
        
        # Count projects before request
        initial_count = Project.objects.count()

        # Send project creation request
        response = client.post(
            reverse("projects:create"),
            {"display_name": "Test Connection Fail", "storage_type": "postgres"}
        )

        # Assertions
        assert response.status_code == 200
        assert Project.objects.count() == initial_count  # No project created
        assert 'hx-swap-oob="true"' in response.content.decode("utf-8")
        assert "Fatal: database 'db.sqlite3' does not exist" in response.content.decode("utf-8")
        assert "Connection failed" in response.content.decode("utf-8")

    @patch("src.apps.projects.views.test_postgres_connection")
    def test_create_project_postgres_connection_success(self, mock_test_conn, client) -> None:
        """Test that project creation succeeds and returns HX-Trigger header when database connection is OK"""
        mock_test_conn.return_value = (True, "")
        
        initial_count = Project.objects.count()

        response = client.post(
            reverse("projects:create"),
            {"display_name": "Test Connection Success", "storage_type": "postgres"}
        )

        # Assertions
        assert response.status_code == 200
        assert Project.objects.count() == initial_count + 1  # Project created
        
        # Verify the created project attributes
        new_project = Project.objects.filter(display_name="Test Connection Success").first()
        assert new_project is not None
        assert new_project.storage_type == "postgres"
        
        response_content = response.content.decode("utf-8")
        assert 'hx-swap-oob="true"' in response_content
        assert 'id="project-error-container"' in response_content
        assert response.headers.get("HX-Trigger") == "projectCreated"

    @patch("src.apps.documents.views.test_postgres_connection")
    def test_upload_document_postgres_connection_failure(self, mock_test_conn, client) -> None:
        """Test that document upload fails and marks the document state as FAILED in the Django database if the connection check fails"""
        mock_test_conn.return_value = (False, "Network unreachable on port 5432")
        
        # Create a test project record in SQLite
        project = Project.objects.create(
            project_id="postgres_test_project_id_123",
            display_name="Test Postgres Upload Proj",
            storage_type="postgres"
        )
        
        # Prepare a mock text file
        mock_file = SimpleUploadedFile("test_doc.txt", b"Hello World from test document.", content_type="text/plain")

        # Send request
        response = client.post(
            reverse("documents:upload", args=[project.project_id]),
            {"file": mock_file}
        )

        # Assertions
        assert response.status_code == 200
        assert b"FAILED" in response.content

        # Verify Document state in local SQLite database
        document = Document.objects.filter(project=project, document_name="test_doc.txt").first()
        assert document is not None
        assert document.state == "FAILED"
        assert "PostgreSQL VPS Connection failed: Network unreachable on port 5432" in document.error_message
