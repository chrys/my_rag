"""
Unit tests for documents app serializers
Tests Document serializers with validation and data flow
"""

import pytest
from src.apps.projects.models import Project
from src.apps.documents.models import Document
from src.apps.documents.serializers import (
    DocumentSerializer,
    DocumentCreateSerializer,
    DocumentUpdateSerializer,
    DocumentListSerializer,
)


@pytest.fixture
def project():
    """Fixture for creating a project"""
    return Project.objects.create(
        project_id='serializer_doc_proj',
        display_name='Serializer Doc Project'
    )


@pytest.mark.django_db
class TestDocumentSerializer:
    """Test DocumentSerializer"""
    
    def test_serialize_pending_document(self, project):
        """Test serializing a pending document"""
        document = Document.objects.create(
            project=project,
            document_name='draft.pdf',
            display_name='Draft Report',
            state='PENDING'
        )
        
        serializer = DocumentSerializer(document)
        data = serializer.data
        
        assert data['id'] == document.id
        assert data['project'] == project.id
        assert data['document_name'] == 'draft.pdf'
        assert data['display_name'] == 'Draft Report'
        assert data['state'] == 'PENDING'
    
    def test_serialize_indexed_document(self, project):
        """Test serializing an indexed document"""
        document = Document.objects.create(
            project=project,
            document_name='indexed.pdf',
            display_name='Final Report',
            external_document_id='google_123',
            mime_type='application/pdf',
            file_size=2048000,
            state='INDEXED'
        )
        
        serializer = DocumentSerializer(document)
        data = serializer.data
        
        assert data['external_document_id'] == 'google_123'
        assert data['mime_type'] == 'application/pdf'
        assert data['file_size'] == 2048000
        assert data['state'] == 'INDEXED'
    
    def test_serialize_failed_document(self, project):
        """Test serializing a failed document"""
        error_msg = "PDF is corrupted"
        document = Document.objects.create(
            project=project,
            document_name='bad.pdf',
            state='FAILED',
            error_message=error_msg
        )
        
        serializer = DocumentSerializer(document)
        data = serializer.data
        
        assert data['state'] == 'FAILED'
        assert data['error_message'] == error_msg
    
    def test_serializer_read_only_fields(self, project):
        """Test that created_at and indexed_at are read-only"""
        document = Document.objects.create(
            project=project,
            document_name='test.pdf'
        )
        
        serializer = DocumentSerializer(document)
        assert 'created_at' in serializer.data
        assert 'indexed_at' in serializer.data
        assert 'created_at' in serializer.Meta.read_only_fields
        assert 'indexed_at' in serializer.Meta.read_only_fields


@pytest.mark.django_db
class TestDocumentCreateSerializer:
    """Test DocumentCreateSerializer"""
    
    def test_create_document(self, project):
        """Test creating document via serializer"""
        data = {
            'project': project.id,
            'document_name': 'new_doc.pdf',
            'display_name': 'New Document',
            'mime_type': 'application/pdf',
            'file_size': 512000
        }
        
        serializer = DocumentCreateSerializer(data=data)
        assert serializer.is_valid()
        
        document = serializer.save()
        assert document.project.id == project.id
        assert document.document_name == 'new_doc.pdf'
        assert document.display_name == 'New Document'
        assert document.state == 'PENDING'
    
    def test_create_required_fields(self, project):
        """Test required fields validation"""
        data = {
            'project': project.id,
            # Missing document_name
        }
        
        serializer = DocumentCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'document_name' in serializer.errors
    
    def test_create_optional_fields(self, project):
        """Test optional fields"""
        data = {
            'project': project.id,
            'document_name': 'minimal.txt'
        }
        
        serializer = DocumentCreateSerializer(data=data)
        assert serializer.is_valid()
        
        document = serializer.save()
        assert document.display_name == ''
        assert document.file_size is None
    
    def test_create_always_pending(self, project):
        """Test created documents always start in PENDING"""
        data = {
            'project': project.id,
            'document_name': 'doc.txt'
        }
        
        serializer = DocumentCreateSerializer(data=data)
        assert serializer.is_valid()
        document = serializer.save()
        assert document.state == 'PENDING'


@pytest.mark.django_db
class TestDocumentUpdateSerializer:
    """Test DocumentUpdateSerializer"""
    
    def test_update_display_name(self, project):
        """Test updating display_name"""
        document = Document.objects.create(
            project=project,
            document_name='doc.pdf',
            display_name='Old Name'
        )
        
        data = {'display_name': 'New Name'}
        serializer = DocumentUpdateSerializer(document, data=data, partial=True)
        assert serializer.is_valid()
        
        updated = serializer.save()
        assert updated.display_name == 'New Name'
    
    def test_update_state(self, project):
        """Test updating state"""
        document = Document.objects.create(
            project=project,
            document_name='doc.pdf',
            state='PENDING'
        )
        
        data = {'state': 'INDEXED'}
        serializer = DocumentUpdateSerializer(document, data=data, partial=True)
        assert serializer.is_valid()
        
        updated = serializer.save()
        assert updated.state == 'INDEXED'
    
    def test_update_error_message(self, project):
        """Test updating error message"""
        document = Document.objects.create(
            project=project,
            document_name='doc.pdf',
            state='FAILED'
        )
        
        error = "Network timeout during indexing"
        data = {'error_message': error}
        serializer = DocumentUpdateSerializer(document, data=data, partial=True)
        assert serializer.is_valid()
        
        updated = serializer.save()
        assert updated.error_message == error
    
    def test_update_multiple_fields(self, project):
        """Test updating multiple fields at once"""
        document = Document.objects.create(
            project=project,
            document_name='doc.pdf',
            display_name='Old',
            state='PENDING'
        )
        
        data = {
            'display_name': 'Updated',
            'state': 'INDEXING'
        }
        serializer = DocumentUpdateSerializer(document, data=data, partial=True)
        assert serializer.is_valid()
        
        updated = serializer.save()
        assert updated.display_name == 'Updated'
        assert updated.state == 'INDEXING'


@pytest.mark.django_db
class TestDocumentListSerializer:
    """Test DocumentListSerializer"""
    
    def test_list_serializer_fields(self, project):
        """Test list serializer has correct fields"""
        document = Document.objects.create(
            project=project,
            document_name='doc.pdf',
            display_name='Display Name',
            state='INDEXED'
        )
        
        serializer = DocumentListSerializer(document)
        data = serializer.data
        
        # Check included fields
        assert 'id' in data
        assert 'document_name' in data
        assert 'display_name' in data
        assert 'state' in data
        assert 'created_at' in data
        
        # Check excluded fields
        assert 'project' not in data
        assert 'mime_type' not in data
        assert 'file_size' not in data
        assert 'error_message' not in data
    
    def test_list_serializer_multiple(self, project):
        """Test serializing multiple documents"""
        doc1 = Document.objects.create(
            project=project,
            document_name='doc1.pdf',
            state='INDEXED'
        )
        doc2 = Document.objects.create(
            project=project,
            document_name='doc2.pdf',
            state='PENDING'
        )
        doc3 = Document.objects.create(
            project=project,
            document_name='doc3.pdf',
            state='FAILED'
        )
        
        serializer = DocumentListSerializer(
            [doc1, doc2, doc3],
            many=True
        )
        
        assert len(serializer.data) == 3
        assert serializer.data[0]['state'] == 'INDEXED'
        assert serializer.data[1]['state'] == 'PENDING'
        assert serializer.data[2]['state'] == 'FAILED'
    
    def test_list_serializer_data_integrity(self, project):
        """Test serializer preserves document data"""
        document = Document.objects.create(
            project=project,
            document_name='docs/important.pdf',
            display_name='Important Document',
            state='INDEXED'
        )
        
        serializer = DocumentListSerializer(document)
        data = serializer.data
        
        assert data['document_name'] == 'docs/important.pdf'
        assert data['display_name'] == 'Important Document'
        assert data['state'] == 'INDEXED'
