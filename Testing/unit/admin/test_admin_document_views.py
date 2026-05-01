import pytest
from django.test import RequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.projects.models import Project
from apps.documents.models import Document
from apps.documents.views import _sanitize_uploaded_filename, upload_document, delete_document, list_documents

@pytest.mark.django_db
class TestAdminDocumentViews:
    def test_sanitize_uploaded_filename_strips_path_segments(self):
        assert _sanitize_uploaded_filename('../../unsafe folder/test doc?.txt') == 'test_doc.txt'

    def test_list_documents_google(self, mocker):
        project = Project.objects.create(
            project_id='list_google_id',
            display_name='List Google Project',
            storage_type='google',
            external_store_id='ext_list_123'
        )
        mock_list = mocker.patch('apps.documents.views.gfs.list_documents_in_store', return_value=[
            {'name': 'doc1', 'display_name': 'Doc 1', 'mime_type': 'text/plain', 'indexed_at': None, 'state': mocker.Mock(name='INDEXED')}
        ])
        
        factory = RequestFactory()
        request = factory.get('/fake-url/')
        
        response = list_documents(request, 'list_google_id')
        
        assert response.status_code == 200
        mock_list.assert_called_once_with('ext_list_123')
        assert b'Doc 1' in response.content

    def test_list_documents_postgres(self, mocker):
        project = Project.objects.create(
            project_id='list_postgres_id',
            display_name='List Postgres Project',
            storage_type='postgres'
        )
        Document.objects.create(project=project, document_name='pg_doc.txt', display_name='PG Doc')
        
        factory = RequestFactory()
        request = factory.get('/fake-url/')
        
        response = list_documents(request, 'list_postgres_id')
        
        assert response.status_code == 200
        assert b'PG Doc' in response.content

    def test_list_documents_local_legacy(self, mocker):
        # Mock local storage to return a project with documents
        mock_storage = mocker.Mock()
        mock_storage.list_projects.return_value = [{
            'id': 'local_123',
            'display_name': 'Local Project',
            'documents': {'doc_local.txt': {'indexed_at': '2026-03-01'}}
        }]
        mocker.patch('apps.documents.views.get_local_project_storage', return_value=mock_storage)
        
        factory = RequestFactory()
        request = factory.get('/fake-url/')
        
        response = list_documents(request, 'local_123')
        
        assert response.status_code == 200
        assert b'doc_local.txt' in response.content

    def test_upload_document_local(self, mocker):
        mock_storage = mocker.Mock()
        mock_storage.list_projects.return_value = []
        mocker.patch('apps.documents.views.get_local_project_storage', return_value=mock_storage)
        
        mock_engine = mocker.Mock()
        mock_engine.index_document.return_value = True
        mocker.patch('apps.documents.views.get_rag_engine', return_value=mock_engine)
        
        file_content = b"local content"
        uploaded_file = SimpleUploadedFile("local_doc.txt", file_content, content_type="text/plain")
        
        factory = RequestFactory()
        request = factory.post('/fake-url/', {'file': uploaded_file})
        
        response = upload_document(request, 'local_456')
        
        assert response.status_code == 200
        mock_engine.index_document.assert_called_once()
        mock_storage.add_document.assert_called_once_with('local_456', 'local_doc.txt')

    def test_delete_document_local(self, mocker):
        mock_storage = mocker.Mock()
        mocker.patch('apps.documents.views.get_local_project_storage', return_value=mock_storage)
        
        mock_engine = mocker.Mock()
        mock_engine.delete_document.return_value = True
        mocker.patch('apps.documents.views.get_rag_engine', return_value=mock_engine)
        
        factory = RequestFactory()
        request = factory.delete('/fake-url/?store_id=local_456')
        
        response = delete_document(request, 'local_doc.txt')
        
        assert response.status_code == 200
        mock_engine.delete_document.assert_called_once_with('local_doc.txt')
        mock_storage.remove_document.assert_called_once_with('local_456', 'local_doc.txt')

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
        assert doc.indexed_at is not None
        assert doc.error_message == ''

    def test_upload_document_postgres_marks_failed_state(self, mocker):
        project = Project.objects.create(
            project_id='postgres_failed_test_id',
            display_name='Test Failed Upload Postgres',
            storage_type='postgres'
        )
        mocker.patch(
            'postgres_rag.PostgresRAGEngine.index_document',
            side_effect=ValueError('Postgres configuration missing')
        )

        file_content = b"test postgres failure"
        uploaded_file = SimpleUploadedFile("failed_pg_doc.txt", file_content, content_type="text/plain")

        factory = RequestFactory()
        request = factory.post('/fake-url/', {'file': uploaded_file})

        response = upload_document(request, 'postgres_failed_test_id')

        assert response.status_code == 500

        doc = Document.objects.get(project=project, document_name="failed_pg_doc.txt")
        assert doc.state == 'FAILED'
        assert doc.indexed_at is None
        assert 'Postgres configuration missing' in doc.error_message

    def test_upload_document_postgres_rate_limit_returns_503(self, mocker):
        from postgres_rag import EmbeddingRateLimitError

        project = Project.objects.create(
            project_id='postgres_rate_limit_test_id',
            display_name='Test Rate Limited Upload Postgres',
            storage_type='postgres'
        )
        mocker.patch(
            'postgres_rag.PostgresRAGEngine.index_document',
            side_effect=EmbeddingRateLimitError('Gemini embedding API is temporarily rate limited. Please try again in a minute.')
        )

        file_content = b"test postgres rate limited"
        uploaded_file = SimpleUploadedFile("rate_limited_pg_doc.txt", file_content, content_type="text/plain")

        factory = RequestFactory()
        request = factory.post('/fake-url/', {'file': uploaded_file})

        response = upload_document(request, 'postgres_rate_limit_test_id')

        assert response.status_code == 503

        doc = Document.objects.get(project=project, document_name="rate_limited_pg_doc.txt")
        assert doc.state == 'FAILED'
        assert doc.indexed_at is None
        assert 'temporarily rate limited' in doc.error_message

    def test_upload_document_postgres_rejects_unsupported_file_type(self, mocker):
        project = Project.objects.create(
            project_id='postgres_unsupported_test_id',
            display_name='Test Unsupported Upload Postgres',
            storage_type='postgres'
        )
        mock_index = mocker.patch('postgres_rag.PostgresRAGEngine.index_document', return_value=True)

        file_content = b"binary data"
        uploaded_file = SimpleUploadedFile("malware.exe", file_content, content_type="application/octet-stream")

        factory = RequestFactory()
        request = factory.post('/fake-url/', {'file': uploaded_file})

        response = upload_document(request, 'postgres_unsupported_test_id')

        assert response.status_code == 400
        assert b'Unsupported file type' in response.content
        mock_index.assert_not_called()
        assert not Document.objects.filter(project=project, document_name="malware.exe").exists()

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
        mock_engine = mocker.Mock()
        mock_engine.delete_document.return_value = True
        mocker.patch('postgres_rag.PostgresRAGEngine', return_value=mock_engine)
        doc = Document.objects.create(
            project=project,
            document_name='test_to_delete.txt',
            state='INDEXED'
        )
        
        factory = RequestFactory()
        request = factory.delete('/fake-url/?store_id=postgres_del_id')
        
        response = delete_document(request, 'test_to_delete.txt')
        
        assert response.status_code == 200
        mock_engine.delete_document.assert_called_once_with('test_to_delete.txt')
        assert not Document.objects.filter(id=doc.id).exists()
