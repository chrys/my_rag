import pytest
from src.apps.projects.models import Project, SystemPrompt
from src.apps.projects.admin import ProjectAdminForm

@pytest.mark.django_db
class TestProjectAdminForm:
    def test_form_initial_state_with_prompt(self) -> None:
        project = Project.objects.create(project_id="test_admin_proj", display_name="Admin Test", custom_prompt=True)
        SystemPrompt.objects.create(project=project, content="This is an admin prompt")

        # Manually invoke the logic that sets custom_prompt_text
        form = ProjectAdminForm(instance=project)
        # Note: the form __init__ pulls from SystemPrompt
        assert form.fields['custom_prompt_text'].initial == "This is an admin prompt" or form.initial.get('custom_prompt_text') == "This is an admin prompt"

    def test_form_validation_custom_prompt_text_required(self) -> None:
        form = ProjectAdminForm(data={
            'project_id': 'proj_valid',
            'display_name': 'Test Project',
            'storage_type': 'postgres',
            'document_parsing': 'markitdown',
            'chunking': 'fixed-size',
            'embedding_model': 'models/gemini-embedding-001',
            'llm_model': 'gemini-2.5-flash-lite',
            'response_mode': 'compact',
            'document_count': 0,
            'custom_prompt': True,
            'custom_prompt_text': ''
        })
        assert not form.is_valid()
        assert 'custom_prompt_text' in form.errors

    def test_form_save_with_prompt(self) -> None:
        form = ProjectAdminForm(data={
            'project_id': 'proj_save',
            'display_name': 'Test Save',
            'storage_type': 'postgres',
            'document_parsing': 'markitdown',
            'chunking': 'fixed-size',
            'embedding_model': 'models/gemini-embedding-001',
            'llm_model': 'gemini-2.5-flash-lite',
            'response_mode': 'compact',
            'document_count': 0,
            'custom_prompt': True,
            'custom_prompt_text': 'Valid admin prompt'
        })
        assert form.is_valid()
        project = form.save(commit=True)

        assert SystemPrompt.objects.filter(project=project).exists()
        assert SystemPrompt.objects.get(project=project).content == 'Valid admin prompt'

    def test_form_validation_custom_prompt_text_missing_but_checked(self) -> None:
        form = ProjectAdminForm(data={
            'project_id': 'proj_valid2',
            'display_name': 'Test Project',
            'storage_type': 'postgres',
            'document_parsing': 'markitdown',
            'chunking': 'fixed-size',
            'embedding_model': 'models/gemini-embedding-001',
            'llm_model': 'gemini-2.5-flash-lite',
            'response_mode': 'compact',
            'document_count': 0,
            'custom_prompt': False,
            'custom_prompt_text': 'Here is text but disabled checkbox'
        })
        assert form.is_valid()
        assert form.cleaned_data['custom_prompt'] is True

    def test_form_save_commit_false(self) -> None:
        form = ProjectAdminForm(data={
            'project_id': 'proj_save_false',
            'display_name': 'Test Save False',
            'storage_type': 'postgres',
            'document_parsing': 'markitdown',
            'chunking': 'fixed-size',
            'embedding_model': 'models/gemini-embedding-001',
            'llm_model': 'gemini-2.5-flash-lite',
            'response_mode': 'compact',
            'document_count': 0,
            'custom_prompt': True,
            'custom_prompt_text': 'Pending prompt'
        })
        assert form.is_valid()
        project = form.save(commit=False)
        project.save()
        form.save_m2m()

        assert SystemPrompt.objects.filter(project=project).exists()
        assert SystemPrompt.objects.get(project=project).content == 'Pending prompt'
