import pytest
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from src.apps.projects.views import create_project, delete_project
from src.apps.projects.models import Project
from src.apps.documents.models import Document

@pytest.mark.django_db
class TestAdminProjectViews:
    def test_create_project_google(self):
        factory = RequestFactory()
        request = factory.post('/fake-url/', {
            'display_name': 'Test Google Project',
            'storage_type': 'google'
        })
        request.user = AnonymousUser()
        
        response = create_project(request)
        
        assert response.status_code == 200
        assert b"This functionality has not been implemented yet." in response.content
        assert not Project.objects.filter(display_name='Test Google Project').exists()

    def test_create_project_postgres(self, mocker):
        mocker.patch('src.apps.projects.views.test_postgres_connection', return_value=(True, ""))
        factory = RequestFactory()
        request = factory.post('/fake-url/', {
            'display_name': 'Test Postgres Project',
            'storage_type': 'postgres'
        })
        request.user = AnonymousUser()
        
        response = create_project(request)
        
        assert response.status_code == 200
        
        project = Project.objects.get(display_name='Test Postgres Project')
        assert project.storage_type == 'postgres'
        assert not project.external_store_id

    def test_delete_project_google(self, mocker):
        project = Project.objects.create(
            project_id='test_google_id',
            display_name='Test Delete Google',
            storage_type='google',
            external_store_id='ext_store_123'
        )
        mock_delete = mocker.patch('src.apps.projects.views.gfs.delete_file_search_store')
        
        factory = RequestFactory()
        request = factory.delete('/fake-url/')
        request.user = AnonymousUser()
        
        response = delete_project(request, 'test_google_id')
        
        assert response.status_code == 200
        mock_delete.assert_called_once_with('ext_store_123')
        assert not Project.objects.filter(project_id='test_google_id').exists()

    def test_delete_project_postgres(self, mocker):
        project = Project.objects.create(
            project_id='test_postgres_id',
            display_name='Test Delete Postgres',
            storage_type='postgres'
        )
        Document.objects.create(project=project, document_name='doc1.txt', state='INDEXED')
        Document.objects.create(project=project, document_name='doc2.txt', state='INDEXED')
        mock_cleanup = mocker.patch('src.postgres_rag.cleanup_project_artifacts')
        mock_delete = mocker.patch('src.apps.projects.views.gfs.delete_file_search_store')
        
        factory = RequestFactory()
        request = factory.delete('/fake-url/')
        request.user = AnonymousUser()
        
        response = delete_project(request, 'test_postgres_id')
        
        assert response.status_code == 200
        mock_delete.assert_not_called()
        mock_cleanup.assert_called_once_with('test_postgres_id', ['doc1.txt', 'doc2.txt'])
        assert not Project.objects.filter(project_id='test_postgres_id').exists()

    def test_delete_project_postgres_without_optional_ai_dependencies(self, mocker):
        project = Project.objects.create(
            project_id='test_postgres_missing_deps',
            display_name='Test Delete Postgres Missing Deps',
            storage_type='postgres'
        )
        Document.objects.create(project=project, document_name='doc1.txt', state='INDEXED')
        mocker.patch(
            'src.postgres_rag.cleanup_project_artifacts',
            side_effect=ImportError('google-genai required')
        )

        factory = RequestFactory()
        request = factory.delete('/fake-url/')
        request.user = AnonymousUser()

        response = delete_project(request, 'test_postgres_missing_deps')

        assert response.status_code == 200
        assert not Project.objects.filter(project_id='test_postgres_missing_deps').exists()

    def test_delete_project_google_without_gfs_deps_still_deletes_db_record(self, mocker):
        """When gfs cleanup raises (e.g. missing deps), the Django record must still be deleted."""
        project = Project.objects.create(
            project_id='test_google_missing_deps',
            display_name='Test Delete Google Missing Deps',
            storage_type='google',
            external_store_id='ext_store_456'
        )
        mocker.patch(
            'src.apps.projects.views.gfs.delete_file_search_store',
            side_effect=Exception('Google File Search dependencies are not installed in this environment.')
        )

        factory = RequestFactory()
        request = factory.delete('/fake-url/')
        request.user = AnonymousUser()

        response = delete_project(request, 'test_google_missing_deps')

        assert response.status_code == 200
        assert not Project.objects.filter(project_id='test_google_missing_deps').exists()
