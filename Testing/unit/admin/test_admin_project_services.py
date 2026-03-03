import pytest
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from apps.projects.views import create_project, delete_project
from apps.projects.models import Project

@pytest.mark.django_db
class TestAdminProjectServices:
    def test_create_project_service_call(self, mocker):
        mock_create = mocker.patch('apps.projects.views.gfs.create_new_file_search_store', return_value='service_store_id')
        
        factory = RequestFactory()
        request = factory.post('/fake-url/', {
            'display_name': 'Service Level Project',
            'storage_type': 'google'
        })
        request.user = AnonymousUser()
        
        create_project(request)
        
        mock_create.assert_called_once_with('Service Level Project')

    def test_delete_project_service_call(self, mocker):
        Project.objects.create(
            project_id='test_service_id',
            display_name='Test Service Delete',
            storage_type='google',
            external_store_id='ext_service_123'
        )
        mock_delete = mocker.patch('apps.projects.views.gfs.delete_file_search_store')
        
        factory = RequestFactory()
        request = factory.delete('/fake-url/')
        request.user = AnonymousUser()
        
        delete_project(request, 'test_service_id')
        
        mock_delete.assert_called_once_with('ext_service_123')
