import pytest
from django.test import RequestFactory
from apps.projects.models import Project, SystemPrompt
from apps.projects.views import manage_prompt

@pytest.mark.django_db
class TestAdminPromptViews:
    def test_add_custom_prompt(self, mocker):
        project = Project.objects.create(
            project_id='test_prompt_store',
            display_name='Test Prompt Project',
            storage_type='google'
        )
        mock_storage = mocker.Mock()
        mock_get_storage = mocker.patch('apps.projects.views.get_prompt_storage', return_value=mock_storage)
        
        factory = RequestFactory()
        request = factory.post('/fake-url/', {'content': 'You are a helpful assistant.'})
        
        response = manage_prompt(request, 'test_prompt_store')
        
        assert response.status_code == 200
        mock_storage.set_prompt.assert_called_once_with('test_prompt_store', 'You are a helpful assistant.')

    def test_edit_custom_prompt(self, mocker):
        project = Project.objects.create(
            project_id='edit_prompt_store',
            display_name='Edit Prompt Project',
            storage_type='google'
        )
        # Create existing prompt in DB (though the view uses prompt_storage)
        SystemPrompt.objects.create(project=project, content='Old Prompt')
        
        mock_storage = mocker.Mock()
        mock_get_storage = mocker.patch('apps.projects.views.get_prompt_storage', return_value=mock_storage)
        
        factory = RequestFactory()
        request = factory.post('/fake-url/', {'content': 'Updated New Prompt'})
        
        response = manage_prompt(request, 'edit_prompt_store')
        
        assert response.status_code == 200
        mock_storage.set_prompt.assert_called_once_with('edit_prompt_store', 'Updated New Prompt')

    def test_system_prompt_passed_to_llm(self):
        assert False, "test_system_prompt_passed_to_llm not implemented"
