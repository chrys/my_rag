import pytest
from django.test import RequestFactory
from django.contrib.auth.models import User
from src.apps.projects.models import Project, SystemPrompt
from src.apps.projects.views import manage_prompt
from src.apps.chat.views import chat_submit

@pytest.mark.django_db
class TestAdminPromptViews:
    def test_postgres_prompt_rejects_non_owner(self):
        owner = User.objects.create_user(username='promptowner', password='password')
        intruder = User.objects.create_user(username='promptintruder', password='password')
        Project.objects.create(
            project_id='postgres_owned_prompt_store',
            display_name='Owned Postgres Prompt Project',
            storage_type='postgres',
            user=owner,
        )

        factory = RequestFactory()
        request = factory.post('/fake-url/', {'content': 'You should not save this.'})
        request.user = intruder

        response = manage_prompt(request, 'postgres_owned_prompt_store')

        assert response.status_code == 403
        assert not SystemPrompt.objects.exists()

    def test_add_custom_prompt_postgres_uses_system_prompt_model(self):
        project = Project.objects.create(
            project_id='postgres_prompt_store',
            display_name='Postgres Prompt Project',
            storage_type='postgres'
        )

        factory = RequestFactory()
        request = factory.post('/fake-url/', {'content': 'You are a postgres assistant.'})

        response = manage_prompt(request, 'postgres_prompt_store')

        assert response.status_code == 200

        prompt = SystemPrompt.objects.get(project=project)
        assert prompt.content == 'You are a postgres assistant.'

    def test_add_custom_prompt(self, mocker):
        project = Project.objects.create(
            project_id='test_prompt_store',
            display_name='Test Prompt Project',
            storage_type='google'
        )
        mock_storage = mocker.Mock()
        mock_get_storage = mocker.patch('src.apps.projects.views.get_prompt_storage', return_value=mock_storage)
        
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
        mock_get_storage = mocker.patch('src.apps.projects.views.get_prompt_storage', return_value=mock_storage)
        
        factory = RequestFactory()
        request = factory.post('/fake-url/', {'content': 'Updated New Prompt'})
        
        response = manage_prompt(request, 'edit_prompt_store')
        
        assert response.status_code == 200
        mock_storage.set_prompt.assert_called_once_with('edit_prompt_store', 'Updated New Prompt')

    def test_system_prompt_passed_to_llm(self, mocker):
        project = Project.objects.create(
            project_id='chat_prompt_store',
            display_name='Chat Prompt Project',
            storage_type='google',
            external_store_id='ext_chat_789'
        )
        
        # Mock prompt storage to return a specific prompt
        mock_storage = mocker.Mock()
        mock_storage.get_prompt.return_value = "System Prompt: Only talk about cats."
        mocker.patch('src.apps.chat.views.get_prompt_storage', return_value=mock_storage)
        
        # Mock Google File Search backend
        mock_ask = mocker.patch('src.apps.chat.views.gfs.ask_store_question', return_value="Meow.", create=True)
        
        factory = RequestFactory()
        request = factory.post('/fake-url/', {
            'store_id': 'chat_prompt_store',
            'query': 'Tell me about dogs.'
        })
        # Mock user
        request.user = mocker.Mock()
        request.user.is_authenticated = False
        
        response = chat_submit(request)
        
        assert response.status_code == 200
        mock_ask.assert_called_once_with(
            'ext_chat_789',
            'Tell me about dogs.',
            system_prompt="System Prompt: Only talk about cats."
        )

    def test_project_admin_form_saves_custom_prompt_text(self):
        from src.apps.projects.admin import ProjectAdminForm
        project = Project.objects.create(
            project_id='admin_form_prompt_store',
            display_name='Admin Form Prompt Project',
            storage_type='postgres'
        )

        form_data = {
            'project_id': project.project_id,
            'display_name': project.display_name,
            'storage_type': project.storage_type,
            'is_active': True,
            'custom_prompt': True,
            'custom_prompt_text': 'Act as a senior Django engineer.',
            'synthesizer': False,
            'document_parsing': 'markitdown',
            'chunking': 'fixed-size',
            'embedding_model': 'gemini-1',
            'use_markitdown': False,
            'use_structural_grading': True,
            'document_count': 0,
        }
        form = ProjectAdminForm(data=form_data, instance=project)
        assert form.is_valid(), form.errors
        form.save()

        saved_prompt = SystemPrompt.objects.get(project=project)
        assert saved_prompt.content == 'Act as a senior Django engineer.'
        assert project.custom_prompt is True

    def test_project_admin_form_disables_immutable_fields_when_sources_exist(self):
        from src.apps.projects.admin import ProjectAdminForm
        project = Project.objects.create(
            project_id='admin_form_sources_exist',
            display_name='Admin Form Sources Exist',
            storage_type='postgres',
            document_count=3
        )

        form = ProjectAdminForm(instance=project)
        assert form.fields['embedding_model'].disabled is True
        assert form.fields['document_parsing'].disabled is True
        assert form.fields['use_markitdown'].disabled is True
        assert "Locked" in form.fields['embedding_model'].help_text

        empty_project = Project.objects.create(
            project_id='admin_form_no_sources',
            display_name='Admin Form No Sources',
            storage_type='postgres',
            document_count=0
        )
        empty_form = ProjectAdminForm(instance=empty_project)
        assert empty_form.fields['embedding_model'].disabled is False
        assert empty_form.fields['document_parsing'].disabled is False
        assert empty_form.fields['use_markitdown'].disabled is False


