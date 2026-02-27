"""
Regression test for Google File Search project creation bug

BUG DESCRIPTION:
Previously, creating a project with storage_type='google' would fail silently
because the Google File Search API call was commented out in the views.py file.

This test verifies that:
1. A Google File Search project can be created through the web interface
2. The project is saved to the Django database
3. The external_store_id is populated correctly
4. The Google File Search API is actually called

FIXED: 2026-02-27
"""

import pytest
from unittest.mock import patch, MagicMock
from django.test import Client
from apps.projects.models import Project


@pytest.mark.django_db
class TestGoogleFileSearchProjectCreationRegression:
    """
    Regression test suite for Google File Search project creation bug
    """
    
    def test_create_google_file_search_project_via_post(self):
        """
        Test that creating a Google File Search project through POST works correctly
        
        This is a regression test for the bug where Google File Search projects
        could not be created because the creation code was commented out.
        """
        client = Client()
        
        # Mock the Google File Search API call to avoid actual API calls
        with patch('apps.projects.views.gfs.create_new_file_search_store') as mock_create:
            # Mock returns a valid store ID
            mock_store_id = 'fileSearchStores/test-store-123'
            mock_create.return_value = mock_store_id
            
            # Make POST request to create a Google File Search project
            response = client.post(
                '/create/',
                data={
                    'display_name': 'Test Google Project',
                    'storage_type': 'google'
                }
            )
            
            # Verify the API was called
            mock_create.assert_called_once_with('Test Google Project')
            
            # Verify the response is successful
            assert response.status_code == 200
            
            # Verify the project was created in the database
            projects = Project.objects.filter(display_name='Test Google Project')
            assert projects.count() == 1
            
            project = projects.first()
            assert project.storage_type == 'google'
            assert project.external_store_id == mock_store_id
            assert project.is_active is True
    
    def test_google_project_creation_handles_api_failure(self):
        """
        Test that project creation handles Google API failures gracefully
        """
        client = Client()
        
        # Mock the Google File Search API to return empty string (failure)
        with patch('apps.projects.views.gfs.create_new_file_search_store') as mock_create:
            mock_create.return_value = ''  # Empty string indicates failure
            
            # Count projects before
            initial_count = Project.objects.count()
            
            # Make POST request
            response = client.post(
                '/create/',
                data={
                    'display_name': 'Failed Google Project',
                    'storage_type': 'google'
                }
            )
            
            # Verify response is successful even if API fails
            assert response.status_code == 200
            
            # Verify the API was called
            mock_create.assert_called_once_with('Failed Google Project')
            
            # Verify no project was created in database when API fails
            assert Project.objects.count() == initial_count
    
    def test_google_project_has_unique_project_id(self):
        """
        Test that Google projects get unique project_id values
        """
        client = Client()
        
        with patch('apps.projects.views.gfs.create_new_file_search_store') as mock_create:
            # Create first project
            mock_create.return_value = 'fileSearchStores/store-1'
            client.post(
                '/create/',
                data={
                    'display_name': 'Google Project 1',
                    'storage_type': 'google'
                }
            )
            
            # Create second project with same display name
            mock_create.return_value = 'fileSearchStores/store-2'
            client.post(
                '/create/',
                data={
                    'display_name': 'Google Project 1',
                    'storage_type': 'google'
                }
            )
            
            # Verify both projects exist with unique project_ids
            projects = Project.objects.filter(display_name='Google Project 1')
            assert projects.count() == 2
            
            project_ids = [p.project_id for p in projects]
            assert len(project_ids) == len(set(project_ids))  # All unique
            
            # Verify different external_store_ids
            store_ids = [p.external_store_id for p in projects]
            assert store_ids[0] != store_ids[1]
    
    def test_local_project_creation_still_works(self):
        """
        Test that local project creation is not affected by the fix
        """
        client = Client()
        
        # Mock local storage
        with patch('apps.projects.views.get_local_project_storage') as mock_storage:
            mock_storage_instance = MagicMock()
            mock_storage_instance.create_project.return_value = 'local_20260227_120000_test'
            mock_storage.return_value = mock_storage_instance
            
            # Make POST request to create local project
            response = client.post(
                '/create/',
                data={
                    'display_name': 'Test Local Project',
                    'storage_type': 'local'
                }
            )
            
            # Verify response is successful
            assert response.status_code == 200
            
            # Verify local storage was used
            mock_storage_instance.create_project.assert_called_once_with('Test Local Project')
            
            # Verify the project was created in database
            projects = Project.objects.filter(display_name='Test Local Project')
            assert projects.count() == 1
            
            project = projects.first()
            assert project.storage_type == 'local'
            assert project.external_store_id is None or project.external_store_id == ''
    
    def test_google_project_deletion_works(self):
        """
        Test that Google File Search projects can be deleted properly
        """
        # Create a Google project directly in the database
        project = Project.objects.create(
            project_id='google_test_delete',
            display_name='Delete Test',
            storage_type='google',
            external_store_id='fileSearchStores/delete-test'
        )
        
        client = Client()
        
        # Mock the Google File Search API delete call
        with patch('apps.projects.views.gfs.delete_file_search_store') as mock_delete:
            # Delete via the view
            response = client.delete(f'/delete/{project.project_id}/')
            
            # Verify response is successful
            assert response.status_code == 200
            
            # Verify the API was called with the correct store ID
            mock_delete.assert_called_once_with('fileSearchStores/delete-test')
            
            # Verify the project was deleted from database
            assert not Project.objects.filter(project_id=project.project_id).exists()
    
    def test_get_combined_stores_includes_google_projects(self):
        """
        Test that get_combined_stores returns both local and Google projects
        """
        # Create test projects
        Project.objects.create(
            project_id='local_test',
            display_name='Local Project',
            storage_type='local'
        )
        
        Project.objects.create(
            project_id='google_test',
            display_name='Google Project',
            storage_type='google',
            external_store_id='fileSearchStores/test'
        )
        
        client = Client()
        
        # Request the project list
        response = client.get('/list/')
        
        # Verify both projects appear in the response
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        assert 'Local Project' in content
        assert 'Google Project' in content


@pytest.mark.django_db
class TestGoogleFileSearchAPIIntegration:
    """
    Tests for the DRF API endpoints with Google File Search
    """
    
    def test_api_create_google_project_via_serializer(self):
        """
        Test creating a Google project through the DRF API
        
        Note: The API endpoint creates the database record but does NOT call
        the Google File Search API. This is by design for the REST API, which
        expects the external_store_id to be provided by the client.
        """
        from apps.projects.serializers import ProjectCreateSerializer
        
        # Create project via serializer (as API would)
        data = {
            'project_id': 'google_api_test',
            'display_name': 'API Google Project',
            'storage_type': 'google',
        }
        
        serializer = ProjectCreateSerializer(data=data)
        assert serializer.is_valid()
        
        project = serializer.save()
        
        assert project.storage_type == 'google'
        assert project.display_name == 'API Google Project'
        # external_store_id would be set separately when using API
