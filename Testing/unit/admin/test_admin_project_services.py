import pytest
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from src.apps.projects.views import create_project, delete_project
from src.apps.projects.models import Project

@pytest.mark.django_db
class TestAdminProjectServices:
    def test_create_project_service_call(self, mocker):
        mock_test_conn = mocker.patch('src.apps.projects.views.test_postgres_connection', return_value=(True, ""))
        
        factory = RequestFactory()
        request = factory.post('/fake-url/', {
            'display_name': 'Service Level Project',
            'storage_type': 'postgres'
        })
        request.user = AnonymousUser()
        
        create_project(request)
        
        mock_test_conn.assert_called_once()
        assert Project.objects.filter(display_name='Service Level Project', storage_type='postgres').exists()

    def test_delete_project_service_call(self, mocker):
        Project.objects.create(
            project_id='test_service_id',
            display_name='Test Service Delete',
            storage_type='google',
            external_store_id='ext_service_123'
        )
        mock_delete = mocker.patch('src.apps.projects.views.gfs.delete_file_search_store')
        
        factory = RequestFactory()
        request = factory.delete('/fake-url/')
        request.user = AnonymousUser()
        
        delete_project(request, 'test_service_id')
        
        mock_delete.assert_called_once_with('ext_service_123')
