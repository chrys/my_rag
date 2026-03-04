import pytest
from django.test import RequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.projects.models import Project
from apps.documents.models import Document
from apps.documents.views import upload_document, delete_document

@pytest.mark.django_db
class TestAdminDocumentViews:
    def test_upload_document_google(self, mocker):
        project = Project.objects.create(
            project_id='google_test_id',
            display_name='Test Upload Google',
            storage_type='google',
            external_store_id='ext_google_123'
        )
        mock_add = mocker.patch('apps.documents.views.gfs.add_document_to_store')
        mocker.patch('apps.documents.views.gfs.list_documents_in_store', return_value=[])
        
        file_content = b"test document content"
        uploaded_file = SimpleUploadedFile("test_doc.txt", file_content, content_type="text/plain")
        
        factory = RequestFactory()
        request = factory.post('/fake-url/', {'file': uploaded_file})
        
        response = upload_document(request, 'google_test_id')
        
        assert response.status_code == 200
        mock_add.assert_called_once()
        args, _ = mock_add.call_args
        assert args[0] == 'ext_google_123'

    def test_upload_document_postgres(self, mocker):
        project = Project.objects.create(
            project_id='postgres_test_id',
            display_name='Test Upload Postgres',
            storage_type='postgres'
        )
        mock_index = mocker.patch('postgres_rag.PostgresRAGEngine.index_document', return_value=True)
        
        file_content = b"test postgres content"
        uploaded_file = SimpleUploadedFile("test_pg_doc.txt", file_content, content_type="text/plain")
        
        factory = RequestFactory()
        request = factory.post('/fake-url/', {'file': uploaded_file})
        
        response = upload_document(request, 'postgres_test_id')
        
        assert response.status_code == 200
        mock_index.assert_called_once()
        
        doc = Document.objects.get(project=project, document_name="test_pg_doc.txt")
        assert doc.state == 'INDEXED'

    def test_delete_document_google(self, mocker):
        project = Project.objects.create(
            project_id='google_del_id',
            display_name='Test Delete Google Doc',
            storage_type='google',
            external_store_id='ext_google_456'
        )
        mock_delete = mocker.patch('apps.documents.views.gfs.delete_document_from_store')
        
        factory = RequestFactory()
        # The document_id is passed in the URL, and store_id in the query params
        request = factory.delete('/fake-url/?store_id=google_del_id')
        
        response = delete_document(request, 'document_name_123')
        
        assert response.status_code == 200
        mock_delete.assert_called_once_with('ext_google_456', 'document_name_123')

    def test_delete_document_postgres(self, mocker):
        project = Project.objects.create(
            project_id='postgres_del_id',
            display_name='Test Delete Postgres Doc',
            storage_type='postgres'
        )
        doc = Document.objects.create(
            project=project,
            document_name='test_to_delete.txt',
            state='INDEXED'
        )
        
        factory = RequestFactory()
        request = factory.delete('/fake-url/?store_id=postgres_del_id')
        
        response = delete_document(request, 'test_to_delete.txt')
        
        assert response.status_code == 200
        assert not Document.objects.filter(id=doc.id).exists()
