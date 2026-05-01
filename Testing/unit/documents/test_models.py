"""
Unit tests for documents app models
Tests Document model with relationships, state management, and constraints
"""

import pytest
from django.utils import timezone
from src.apps.projects.models import Project
from src.apps.documents.models import Document


@pytest.fixture
def project():
    """Fixture for creating a project"""
    return Project.objects.create(
        project_id='doc_test_proj',
        display_name='Document Test Project'
    )


@pytest.mark.django_db
class TestDocumentModel:
    """Test cases for Document model"""
    
    def test_create_document_minimal(self, project):
        """Test creating a document with minimal fields"""
        document = Document.objects.create(
            project=project,
            document_name='report.pdf'
        )
        
        assert document.id is not None
        assert document.project == project
        assert document.document_name == 'report.pdf'
        assert document.state == 'PENDING'
        assert document.mime_type == 'application/octet-stream'
    
    def test_create_document_full(self, project):
        """Test creating a document with all fields"""
        document = Document.objects.create(
            project=project,
            document_name='docs/report.pdf',
            display_name='Quarterly Report',
            external_document_id='google_doc_123',
            mime_type='application/pdf',
            file_size=1024000,
            state='INDEXED'
        )
        
        assert document.display_name == 'Quarterly Report'
        assert document.external_document_id == 'google_doc_123'
        assert document.mime_type == 'application/pdf'
        assert document.file_size == 1024000
        assert document.state == 'INDEXED'
    
    def test_document_timestamps(self, project):
        """Test document timestamps"""
        document = Document.objects.create(
            project=project,
            document_name='test.txt'
        )
        
        assert document.created_at is not None
        assert isinstance(document.created_at, timezone.datetime)
    
    def test_indexed_at_optional(self, project):
        """Test indexed_at is optional"""
        document = Document.objects.create(
            project=project,
            document_name='test.txt',
            state='PENDING'
        )
        
        assert document.indexed_at is None
    
    def test_indexed_at_set(self, project):
        """Test setting indexed_at when document is indexed"""
        indexed_time = timezone.now()
        document = Document.objects.create(
            project=project,
            document_name='indexed.txt',
            state='INDEXED',
            indexed_at=indexed_time
        )
        
        assert document.indexed_at == indexed_time
    
    def test_document_string_representation(self, project):
        """Test document string representation"""
        document = Document.objects.create(
            project=project,
            document_name='docs/report.pdf',
            display_name='Quarterly Report'
        )
        
        str_repr = str(document)
        assert 'Quarterly Report' in str_repr
        assert project.display_name in str_repr
    
    def test_document_string_without_display_name(self, project):
        """Test string representation without display_name"""
        document = Document.objects.create(
            project=project,
            document_name='docs/report.pdf'
        )
        
        str_repr = str(document)
        assert 'docs/report.pdf' in str_repr
        assert project.display_name in str_repr
    
    def test_valid_index_states(self, project):
        """Test all valid indexing states"""
        states = ['PENDING', 'INDEXING', 'INDEXED', 'FAILED']
        
        for state in states:
            document = Document.objects.create(
                project=project,
                document_name=f'doc_{state}.txt',
                state=state
            )
            assert document.state == state
    
    def test_unique_together_project_name(self, project):
        """Test unique_together constraint on project and document_name"""
        Document.objects.create(
            project=project,
            document_name='unique.pdf'
        )
        
        with pytest.raises(Exception):  # IntegrityError
            Document.objects.create(
                project=project,
                document_name='unique.pdf'
            )
    
    def test_unique_together_different_projects(self, project):
        """Test same name allowed in different projects"""
        other_project = Project.objects.create(
            project_id='other_doc_proj',
            display_name='Other Project'
        )
        
        doc1 = Document.objects.create(
            project=project,
            document_name='shared_name.pdf'
        )
        doc2 = Document.objects.create(
            project=other_project,
            document_name='shared_name.pdf'
        )
        
        assert doc1.id != doc2.id
    
    def test_error_message_empty(self, project):
        """Test error_message is empty by default"""
        document = Document.objects.create(
            project=project,
            document_name='test.txt',
            state='INDEXED'
        )
        
        assert document.error_message == ''
    
    def test_error_message_set(self, project):
        """Test storing error message for failed indexing"""
        error = "Failed to index: PDF is corrupted"
        document = Document.objects.create(
            project=project,
            document_name='bad.pdf',
            state='FAILED',
            error_message=error
        )
        
        assert document.error_message == error
    
    def test_external_document_id_optional(self, project):
        """Test external_document_id is optional"""
        document = Document.objects.create(
            project=project,
            document_name='local.pdf'
        )
        
        assert document.external_document_id is None
    
    def test_display_name_optional(self, project):
        """Test display_name is optional"""
        document = Document.objects.create(
            project=project,
            document_name='docs/report.pdf'
        )
        
        assert document.display_name == ''
    
    def test_file_size_optional(self, project):
        """Test file_size is optional"""
        document = Document.objects.create(
            project=project,
            document_name='test.txt'
        )
        
        assert document.file_size is None
    
    def test_document_ordering(self, project):
        """Test documents ordered by -created_at"""
        doc1 = Document.objects.create(
            project=project,
            document_name='doc1.txt'
        )
        doc2 = Document.objects.create(
            project=project,
            document_name='doc2.txt'
        )
        
        documents = Document.objects.all()
        assert documents[0].id == doc2.id
        assert documents[1].id == doc1.id
    
    def test_queryset_filter_by_project(self, project):
        """Test filtering documents by project"""
        other_project = Project.objects.create(
            project_id='other_proj_2',
            display_name='Other'
        )
        
        doc1 = Document.objects.create(
            project=project,
            document_name='in_project.pdf'
        )
        doc2 = Document.objects.create(
            project=other_project,
            document_name='in_other.pdf'
        )
        
        filtered = Document.objects.filter(project=project)
        assert filtered.count() == 1
        assert filtered.first().id == doc1.id
    
    def test_queryset_filter_by_state(self, project):
        """Test filtering documents by state"""
        indexed_doc = Document.objects.create(
            project=project,
            document_name='indexed.pdf',
            state='INDEXED'
        )
        pending_doc = Document.objects.create(
            project=project,
            document_name='pending.pdf',
            state='PENDING'
        )
        
        indexed = Document.objects.filter(state='INDEXED')
        assert indexed.count() == 1
        assert indexed.first().id == indexed_doc.id
    
    def test_queryset_filter_by_project_and_state(self, project):
        """Test filtering by project and state"""
        Document.objects.create(
            project=project,
            document_name='indexed.pdf',
            state='INDEXED'
        )
        Document.objects.create(
            project=project,
            document_name='pending.pdf',
            state='PENDING'
        )
        
        filtered = Document.objects.filter(project=project, state='INDEXED')
        assert filtered.count() == 1
        assert filtered.first().state == 'INDEXED'
    
    def test_cascade_delete_project(self, project):
        """Test documents deleted when project deleted"""
        document = Document.objects.create(
            project=project,
            document_name='delete_me.pdf'
        )
        
        doc_id = document.id
        project.delete()
        
        assert not Document.objects.filter(id=doc_id).exists()
    
    def test_project_related_access(self, project):
        """Test accessing documents from project"""
        doc1 = Document.objects.create(
            project=project,
            document_name='doc1.pdf'
        )
        doc2 = Document.objects.create(
            project=project,
            document_name='doc2.pdf'
        )
        
        documents = project.documents.all()
        assert documents.count() == 2
        assert doc1 in documents
        assert doc2 in documents
    
    def test_mime_type_default(self, project):
        """Test mime_type defaults to octet-stream"""
        document = Document.objects.create(
            project=project,
            document_name='unknown.xyz'
        )
        
        assert document.mime_type == 'application/octet-stream'
    
    def test_update_document_state(self, project):
        """Test updating document state"""
        document = Document.objects.create(
            project=project,
            document_name='update_test.pdf',
            state='PENDING'
        )
        
        document.state = 'INDEXING'
        document.save()
        
        refreshed = Document.objects.get(id=document.id)
        assert refreshed.state == 'INDEXING'
    
    def test_update_error_message(self, project):
        """Test updating error message"""
        document = Document.objects.create(
            project=project,
            document_name='error_test.pdf',
            state='FAILED'
        )
        
        error = "Indexing timeout"
        document.error_message = error
        document.save()
        
        refreshed = Document.objects.get(id=document.id)
        assert refreshed.error_message == error
