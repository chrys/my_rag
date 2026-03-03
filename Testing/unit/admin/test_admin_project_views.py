import pytest
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from apps.projects.views import create_project
from apps.projects.models import Project

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

    def test_delete_project_google(self):
        assert False, "test_delete_project_google not implemented"

    def test_delete_project_postgres(self):
        assert False, "test_delete_project_postgres not implemented"
