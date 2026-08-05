import pytest
from django.urls import reverse
from django.test import RequestFactory, Client
from src.apps.projects.models import Project
from src.apps.documents.models import Document
from src.apps.documents.views import list_documents, upload_document, delete_document

@pytest.mark.django_db
class TestDocumentViews:
    def test_list_documents_local(self, client) -> None:
        project = Project.objects.create(
            project_id='view_test_local',
            display_name='View Test Local',
            storage_type='postgres'
        )
        Document.objects.create(project=project, document_name='test1.txt', state='INDEXED')

        response = client.get(f'/rag/documents/{project.project_id}/')
        assert response.status_code == 200
        assert b'test1.txt' in response.content
        assert b'INDEXED' in response.content

    def test_list_documents_google(self, client, mocker) -> None:
        project = Project.objects.create(
            project_id='view_test_google',
            display_name='View Test Google',
            storage_type='google',
            external_store_id='ext_store_123'
        )

        # Mock Google File Search
        mock_gfs = mocker.MagicMock()
        mock_gfs.list_documents_in_store.return_value = [
            {'name': 'google_doc.pdf', 'display_name': 'Google Doc', 'state': type('State', (), {'name': 'ACTIVE'})()}
        ]
        mocker.patch('src.apps.documents.views.gfs', mock_gfs)

        response = client.get(f'/rag/documents/{project.project_id}/')
        assert response.status_code == 200
        assert b'google_doc.pdf' in response.content

    def test_delete_document_view(self, client, mocker) -> None:
        project = Project.objects.create(
            project_id='postgres_delete_test',
            display_name='Delete Test',
            storage_type='postgres'
        )
        doc = Document.objects.create(project=project, document_name='delete_me.txt', state='INDEXED')

        mock_rag = mocker.MagicMock()
        mocker.patch('src.postgres_rag.PostgresRAGEngine', return_value=mock_rag)

        request = RequestFactory().delete(f'/delete/{doc.document_name}/?store_id={project.project_id}')
        request.GET = {'store_id': project.project_id}
        response = delete_document(request, doc.document_name)
        assert response.status_code == 200
        assert not Document.objects.filter(id=doc.id).exists()

    def test_delete_document_view_local(self, client, mocker) -> None:
        project = Project.objects.create(
            project_id='local_delete_test',
            display_name='Delete Test',
            storage_type='local'
        )
        doc = Document.objects.create(project=project, document_name='delete_me.txt', state='INDEXED')

        mock_rag = mocker.MagicMock()
        mock_rag.delete_document.return_value = True
        mocker.patch('src.apps.documents.views.get_rag_engine', return_value=mock_rag)

        request = RequestFactory().delete(f'/delete/{doc.document_name}/?store_id={project.project_id}')
        request.GET = {'store_id': project.project_id}
        response = delete_document(request, doc.document_name)
        assert response.status_code == 200

    def test_delete_document_view_google(self, client, mocker) -> None:
        project = Project.objects.create(
            project_id='delete_test_google',
            display_name='Delete Test Google',
            storage_type='google',
            external_store_id='ext_store_123'
        )

        mock_gfs = mocker.MagicMock()
        mocker.patch('src.apps.documents.views.gfs', mock_gfs)

        request = RequestFactory().delete(f'/delete/delete_me.pdf/?store_id={project.project_id}')
        request.GET = {'store_id': project.project_id}
        response = delete_document(request, "delete_me.pdf")
        assert response.status_code == 200
        mock_gfs.delete_document_from_store.assert_called_with('ext_store_123', 'delete_me.pdf')

    def test_upload_document_view(self, client, mocker) -> None:
        project = Project.objects.create(
            project_id='postgres_upload_test',
            display_name='Upload Test',
            storage_type='postgres'
        )

        mocker.patch('src.apps.documents.views.LazyModuleProxy.__getattr__', return_value=mocker.MagicMock())
        mocker.patch('src.apps.documents.services.LlamaIndexIngestionPipeline')
        from django.core.files.uploadedfile import SimpleUploadedFile
        test_file = SimpleUploadedFile("test_file.txt", b"file_content")

        request = RequestFactory().post(f'/rag/documents/{project.project_id}/upload/', {'file': test_file})
        response = upload_document(request, project.project_id)
        assert response.status_code == 200
        assert Document.objects.filter(project=project, document_name='test_file.txt').exists()

    def test_upload_document_view_google(self, client, mocker) -> None:
        import os
        project = Project.objects.create(
            project_id='google_upload_test',
            display_name='Upload Test Google',
            storage_type='google',
            external_store_id='ext_store_123'
        )

        # Avoid the optional dependency lazy load triggering actual imports that require API keys
        mocker.patch.dict(os.environ, {"GOOGLE_API_KEY": "fake_key"})
        mock_gfs = mocker.MagicMock()
        mocker.patch('src.apps.documents.views.LazyModuleProxy.__getattr__', return_value=mock_gfs)
        mocker.patch('src.apps.documents.views.gfs', mock_gfs)

        # In src.apps.documents.views.upload_document line 315 it imports GoogleFileSearchPermissionError directly
        # We need to mock that specific import or bypass it.
        # Actually a better approach is patching 'src.google_file_search' module completely.
        import sys
        mock_gfs_module = mocker.MagicMock()
        mock_gfs_module.GoogleFileSearchPermissionError = Exception
        sys.modules['src.google_file_search'] = mock_gfs_module

        from django.core.files.uploadedfile import SimpleUploadedFile
        test_file = SimpleUploadedFile("test_file.txt", b"file_content")

        request = RequestFactory().post(f'/rag/documents/{project.project_id}/upload/', {'file': test_file})
        response = upload_document(request, project.project_id)
        assert response.status_code == 200
