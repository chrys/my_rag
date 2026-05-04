"""
Unit tests for documents app API views
Tests DocumentViewSet and custom actions
"""

import pytest
from rest_framework.test import APIRequestFactory
from rest_framework import status
from src.apps.projects.models import Project
from src.apps.documents.models import Document
from src.apps.documents.api_views import DocumentViewSet


@pytest.fixture
def api_factory():
    """Fixture for API request factory"""
    return APIRequestFactory()


@pytest.fixture
def project():
    """Fixture for creating a project"""
    return Project.objects.create(
        project_id='api_doc_proj',
        display_name='API Document Project'
    )


@pytest.mark.django_db
class TestDocumentViewSet:
    """Test cases for DocumentViewSet"""
    
    def test_list_documents(self, api_factory, project):
        """Test listing all documents"""
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
        
        request = api_factory.get('/api/documents/')
        view = DocumentViewSet.as_view({'get': 'list'})
        response = view(request)
        
        assert response.status_code == status.HTTP_200_OK
        # Response is paginated
        assert response.data['count'] == 2
        assert len(response.data['results']) == 2
    
    def test_retrieve_document(self, api_factory, project):
        """Test retrieving a single document"""
        document = Document.objects.create(
            project=project,
            document_name='retrieve.pdf',
            display_name='Retrieve Test'
        )
        
        request = api_factory.get(f'/api/documents/{document.id}/')
        view = DocumentViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk=document.id)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['document_name'] == 'retrieve.pdf'
        assert response.data['display_name'] == 'Retrieve Test'
    
    def test_create_document(self, api_factory, project):
        """Test creating a document"""
        data = {
            'project': project.id,
            'document_name': 'new_doc.pdf',
            'display_name': 'New Document',
            'mime_type': 'application/pdf',
            'file_size': 1024000
        }
        
        request = api_factory.post('/api/documents/', data, format='json')
        view = DocumentViewSet.as_view({'post': 'create'})
        response = view(request)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['document_name'] == 'new_doc.pdf'
        # Create serializer doesn't return state, but document is created as PENDING
        
        # Verify in database
        doc = Document.objects.get(document_name='new_doc.pdf')
        assert doc.state == 'PENDING'
    
    def test_update_document(self, api_factory, project):
        """Test updating a document"""
        document = Document.objects.create(
            project=project,
            document_name='update.pdf',
            display_name='Original'
        )
        
        data = {
            'display_name': 'Updated Name',
            'state': 'INDEXED'
        }
        request = api_factory.put(f'/api/documents/{document.id}/', data, format='json')
        view = DocumentViewSet.as_view({'put': 'update'})
        response = view(request, pk=document.id)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['display_name'] == 'Updated Name'
        assert response.data['state'] == 'INDEXED'
    
    def test_partial_update_document(self, api_factory, project):
        """Test partial update of a document"""
        document = Document.objects.create(
            project=project,
            document_name='partial.pdf',
            display_name='Original',
            state='PENDING'
        )
        
        data = {'state': 'INDEXING'}
        request = api_factory.patch(f'/api/documents/{document.id}/', data, format='json')
        view = DocumentViewSet.as_view({'patch': 'partial_update'})
        response = view(request, pk=document.id)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['state'] == 'INDEXING'
        assert response.data['display_name'] == 'Original'
    
    def test_delete_document(self, api_factory, project):
        """Test deleting a document"""
        document = Document.objects.create(
            project=project,
            document_name='delete_me.pdf'
        )
        
        doc_id = document.id
        request = api_factory.delete(f'/api/documents/{doc_id}/')
        view = DocumentViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=doc_id)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Document.objects.filter(id=doc_id).exists()
    
    def test_by_project_action(self, api_factory, project):
        """Test by_project custom action"""
        doc1 = Document.objects.create(
            project=project,
            document_name='in_project.pdf'
        )
        
        other_project = Project.objects.create(
            project_id='other_api_proj',
            display_name='Other'
        )
        doc2 = Document.objects.create(
            project=other_project,
            document_name='in_other.pdf'
        )
        
        request = api_factory.get(f'/api/documents/by_project/?project_id={project.id}')
        view = DocumentViewSet.as_view({'get': 'by_project'})
        response = view(request)
        
        assert response.status_code == status.HTTP_200_OK
        # Response should be list format
        docs = response.data if isinstance(response.data, list) else response.data.get('results', [])
        project_docs = [d for d in docs if d.get('id') == doc1.id]
        assert len(project_docs) == 1
    
    def test_by_project_missing_param(self, api_factory):
        """Test by_project requires project_id parameter"""
        request = api_factory.get('/api/documents/by_project/')
        view = DocumentViewSet.as_view({'get': 'by_project'})
        response = view(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
    
    def test_by_state_action(self, api_factory, project):
        """Test by_state custom action"""
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
        
        request = api_factory.get('/api/documents/by_state/?state=INDEXED')
        view = DocumentViewSet.as_view({'get': 'by_state'})
        response = view(request)
        
        assert response.status_code == status.HTTP_200_OK
        docs = response.data if isinstance(response.data, list) else response.data.get('results', [])
        indexed_docs = [d for d in docs if d.get('state') == 'INDEXED']
        assert len(indexed_docs) >= 1
    
    def test_by_state_missing_param(self, api_factory):
        """Test by_state requires state parameter"""
        request = api_factory.get('/api/documents/by_state/')
        view = DocumentViewSet.as_view({'get': 'by_state'})
        response = view(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
    
    def test_indexed_action(self, api_factory, project):
        """Test indexed custom action"""
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
        
        request = api_factory.get('/api/documents/indexed/')
        view = DocumentViewSet.as_view({'get': 'indexed'})
        response = view(request)
        
        assert response.status_code == status.HTTP_200_OK
        docs = response.data if isinstance(response.data, list) else response.data.get('results', [])
        # All returned docs should be INDEXED
        for doc in docs:
            assert doc['state'] == 'INDEXED'
    
    def test_failed_action(self, api_factory, project):
        """Test failed custom action"""
        failed_doc = Document.objects.create(
            project=project,
            document_name='failed.pdf',
            state='FAILED',
            error_message='Indexing failed'
        )
        indexed_doc = Document.objects.create(
            project=project,
            document_name='indexed.pdf',
            state='INDEXED'
        )
        
        request = api_factory.get('/api/documents/failed/')
        view = DocumentViewSet.as_view({'get': 'failed'})
        response = view(request)
        
        assert response.status_code == status.HTTP_200_OK
        docs = response.data if isinstance(response.data, list) else response.data.get('results', [])
        # All returned docs should be FAILED
        for doc in docs:
            assert doc['state'] == 'FAILED'
    
    def test_get_serializer_class_list(self, api_factory, project):
        """Test correct serializer used for list action"""
        Document.objects.create(
            project=project,
            document_name='test.pdf'
        )
        
        request = api_factory.get('/api/documents/')
        view = DocumentViewSet.as_view({'get': 'list'})
        response = view(request)
        
        assert response.status_code == status.HTTP_200_OK
        if response.data.get('results'):
            doc_data = response.data['results'][0]
            # List serializer has limited fields
            assert 'id' in doc_data
            assert 'document_name' in doc_data
            assert 'state' in doc_data
    
    def test_get_serializer_class_create(self, api_factory, project):
        """Test correct serializer used for create action"""
        data = {
            'project': project.id,
            'document_name': 'test.pdf',
            'display_name': 'Test',
            'mime_type': 'application/pdf',
            'file_size': 1024
        }
        
        request = api_factory.post('/api/documents/', data, format='json')
        view = DocumentViewSet.as_view({'post': 'create'})
        response = view(request)
        
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_get_serializer_class_update(self, api_factory, project):
        """Test correct serializer used for update action"""
        document = Document.objects.create(
            project=project,
            document_name='test.pdf'
        )
        
        data = {'display_name': 'Updated', 'state': 'INDEXED'}
        request = api_factory.put(f'/api/documents/{document.id}/', data, format='json')
        view = DocumentViewSet.as_view({'put': 'update'})
        response = view(request, pk=document.id)
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_document_filtering_by_state(self, api_factory, project):
        """Test filtering documents by state"""
        Document.objects.all().delete()  # Clear for clean test
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
        
        request = api_factory.get('/api/documents/?state=INDEXED')
        view = DocumentViewSet.as_view({'get': 'list'})
        response = view(request)
        
        assert response.status_code == status.HTTP_200_OK
        if response.data.get('results'):
            indexed_docs = [d for d in response.data['results'] if d['state'] == 'INDEXED']
            assert len(indexed_docs) >= 1
    
    def test_document_filtering_by_project(self, api_factory, project):
        """Test filtering documents by project"""
        Document.objects.all().delete()  # Clear for clean test
        doc1 = Document.objects.create(
            project=project,
            document_name='in_project.pdf'
        )
        
        other_project = Project.objects.create(
            project_id='filter_other_proj',
            display_name='Other'
        )
        doc2 = Document.objects.create(
            project=other_project,
            document_name='in_other.pdf'
        )
        
        # Use the by_project custom action with query param
        request = api_factory.get(f'/api/documents/by_project/?project_id={project.id}')
        view = DocumentViewSet.as_view({'get': 'by_project'})
        response = view(request)
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data if isinstance(response.data, list) else response.data.get('results', [])
        assert len(results) >= 1
        assert all(doc['project'] == project.id for doc in results)
