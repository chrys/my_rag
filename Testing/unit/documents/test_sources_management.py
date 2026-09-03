import pytest
import os
import tempfile
from django.contrib.auth.models import User
from src.apps.projects.models import Project
from src.apps.documents.models import Document
from src.apps.documents.services import (
    compute_file_sha256,
    compute_text_simhash,
    simhash_similarity,
    check_near_duplicate,
)

@pytest.mark.django_db
class TestSourcesManagement:
    def test_simhash_similarity_computation(self):
        text_a = "The quick brown fox jumps over the lazy dog in the summer morning."
        text_b = "The fast brown fox jumps over the lazy dog in the summer morning."
        text_c = "Completely unrelated text about quantum computing and neural networks."

        h_a = compute_text_simhash(text_a)
        h_b = compute_text_simhash(text_b)
        h_c = compute_text_simhash(text_c)

        sim_ab = simhash_similarity(h_a, h_b)
        sim_ac = simhash_similarity(h_a, h_c)

        assert sim_ab >= 0.85, f"Expected high similarity for near-duplicate, got {sim_ab}"
        assert sim_ac < 0.70, f"Expected low similarity for different topics, got {sim_ac}"

    def test_filter_sources_view_by_name_and_type(self, client):
        user = User.objects.create_user(username="filteruser", password="password123")
        client.login(username="filteruser", password="password123")
        project = Project.objects.create(
            project_id="filter_test_proj",
            display_name="Filter Test",
            user=user,
            storage_type="postgres"
        )

        doc1 = Document.objects.create(
            project=project,
            document_name="architecture_guide.md",
            display_name="Architecture Guide",
            state="INDEXED"
        )
        doc2 = Document.objects.create(
            project=project,
            document_name="service_handler.py",
            display_name="Service Handler",
            state="INDEXED"
        )
        doc3 = Document.objects.create(
            project=project,
            document_name="financial_report.pdf",
            display_name="Financial Report",
            state="FAILED"
        )

        # Test name search
        res = client.get(f"/rag/projects/{project.project_id}/sources/filter/?search=architecture")
        assert res.status_code == 200
        assert b"Architecture Guide" in res.content
        assert b"Service Handler" not in res.content

        # Test file type filter (code)
        res = client.get(f"/rag/projects/{project.project_id}/sources/filter/?file_type=code")
        assert res.status_code == 200
        assert b"Service Handler" in res.content
        assert b"Financial Report" not in res.content

        # Test status filter (FAILED)
        res = client.get(f"/rag/projects/{project.project_id}/sources/filter/?status=FAILED")
        assert res.status_code == 200
        assert b"Financial Report" in res.content
        assert b"Architecture Guide" not in res.content

    def test_single_and_bulk_document_delete(self, client):
        user = User.objects.create_user(username="deluser", password="password123")
        client.login(username="deluser", password="password123")
        project = Project.objects.create(
            project_id="del_test_proj",
            display_name="Delete Test",
            user=user,
            storage_type="postgres"
        )

        doc1 = Document.objects.create(project=project, document_name="doc1.md", state="INDEXED")
        doc2 = Document.objects.create(project=project, document_name="doc2.md", state="INDEXED")
        doc3 = Document.objects.create(project=project, document_name="doc3.md", state="INDEXED")

        # Single delete
        res = client.post(f"/rag/projects/{project.project_id}/sources/{doc1.id}/delete/")
        assert res.status_code == 200
        assert not Document.objects.filter(id=doc1.id).exists()

        # Bulk delete
        res = client.post(
            f"/rag/projects/{project.project_id}/sources/bulk-delete/",
            {"document_ids": [doc2.id, doc3.id]}
        )
        assert res.status_code == 200
        assert res.json()["deleted_count"] == 2
        assert not Document.objects.filter(id__in=[doc2.id, doc3.id]).exists()

    def test_inspect_document_view(self, client):
        user = User.objects.create_user(username="inspuser", password="password123")
        client.login(username="inspuser", password="password123")
        project = Project.objects.create(
            project_id="insp_test_proj",
            display_name="Inspect Test",
            user=user,
            storage_type="postgres"
        )

        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".md") as tmp:
            tmp.write("# Sample Header\nThis is inspectable test text content.")
            tmp_path = tmp.name

        doc = Document.objects.create(
            project=project,
            document_name="inspect_test.md",
            display_name="Inspect Test Document",
            content_hash="abc123456789",
            state="INDEXED"
        )

        res = client.get(f"/rag/projects/{project.project_id}/inspect-document/?document_id={doc.id}")
        assert res.status_code == 200
        assert b"Document Chunk Node Inspector" in res.content

    def test_upload_exact_duplicate_detection(self, client):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from src.apps.documents.services import compute_file_sha256

        user = User.objects.create_user(username="dupuser", password="password123")
        client.login(username="dupuser", password="password123")
        project = Project.objects.create(
            project_id="dup_test_proj",
            display_name="Duplicate Test Proj",
            user=user,
            storage_type="postgres"
        )

        content = b"This is unique test file content for deduplication."
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        content_hash = compute_file_sha256(tmp_path)
        os.unlink(tmp_path)

        Document.objects.create(
            project=project,
            document_name="original.txt",
            display_name="original.txt",
            content_hash=content_hash,
            state="INDEXED"
        )

        upload_file = SimpleUploadedFile("duplicate.txt", content, content_type="text/plain")
        res = client.post(
            f"/rag/documents/{project.project_id}/upload/",
            {"file": upload_file},
            HTTP_HX_TARGET="dashboard-workspace"
        )
        assert res.status_code == 200
        assert b"Duplicate Document Detected" in res.content
