import pytest
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from apps.projects.views import create_project, delete_project
from apps.projects.models import Project
from apps.documents.models import Document

@pytest.mark.django_db
class TestAdminProjectViews:
    def test_create_project_google(self, mocker):
        # Mock the external Google File Search creation
        mock_create = mocker.patch(
            'apps.projects.views.gfs.create_new_file_search_store',
            return_value='mock_store_id'
        )
        
        factory = RequestFactory()
        request = factory.post('/fake-url/', {
            'display_name': 'Test Google Project',
            'storage_type': 'google'
        })
        request.user = AnonymousUser()
        
        response = create_project(request)
        
        assert response.status_code == 200
        mock_create.assert_called_once_with('Test Google Project')
        
        project = Project.objects.get(display_name='Test Google Project')
        assert project.storage_type == 'google'
        assert project.external_store_id == 'mock_store_id'

    def test_create_project_postgres(self):
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
        mock_delete = mocker.patch('apps.projects.views.gfs.delete_file_search_store')
        
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
        mock_engine = mocker.Mock()
        mocker.patch('postgres_rag.PostgresRAGEngine', return_value=mock_engine)
        mock_delete = mocker.patch('apps.projects.views.gfs.delete_file_search_store')
        
        factory = RequestFactory()
        request = factory.delete('/fake-url/')
        request.user = AnonymousUser()
        
        response = delete_project(request, 'test_postgres_id')
        
        assert response.status_code == 200
        mock_delete.assert_not_called()
        mock_engine.delete_project_artifacts.assert_called_once_with(['doc1.txt', 'doc2.txt'])
        assert not Project.objects.filter(project_id='test_postgres_id').exists()

    def test_delete_project_postgres_without_optional_ai_dependencies(self, mocker):
        project = Project.objects.create(
            project_id='test_postgres_missing_deps',
            display_name='Test Delete Postgres Missing Deps',
            storage_type='postgres'
        )
        Document.objects.create(project=project, document_name='doc1.txt', state='INDEXED')
        mocker.patch(
            'postgres_rag.PostgresRAGEngine',
            side_effect=ImportError('PostgresRAGEngine requires the optional AI dependencies')
        )

        factory = RequestFactory()
        request = factory.delete('/fake-url/')
        request.user = AnonymousUser()

        response = delete_project(request, 'test_postgres_missing_deps')

        assert response.status_code == 200
        assert not Project.objects.filter(project_id='test_postgres_missing_deps').exists()
