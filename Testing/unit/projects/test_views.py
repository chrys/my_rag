import pytest
from django.urls import reverse
from django.test import RequestFactory, Client
from django.contrib.auth.models import AnonymousUser, User
from src.apps.projects.models import Project, SystemPrompt
from src.apps.projects.views import list_projects, create_project, delete_project, manage_prompt

@pytest.mark.django_db
class TestProjectViews:
    def setup_method(self) -> None:
        self.user = User.objects.create_user(username='view_user', password='password')
        self.client = Client()
        self.client.force_login(self.user)
        self.factory = RequestFactory()

    def test_list_projects(self, mocker) -> None:
        Project.objects.create(project_id="test_list", display_name="Test List", user=self.user)
        mocker.patch('src.local_project_storage.LocalProjectStorage.list_projects', return_value=[])
        request = self.factory.get('/projects/')
        request.user = self.user
        response = list_projects(request)
        assert response.status_code == 200
        assert b"Test List" in response.content

    def test_create_project_success(self, mocker) -> None:
        mocker.patch('src.apps.projects.views.test_postgres_connection', return_value=(True, ""))
        request = self.factory.post('/projects/create/', {
            'display_name': 'New PostGres Proj',
            'storage_type': 'postgres'
        })
        request.user = self.user
        response = create_project(request)
        assert response.status_code == 200
        assert Project.objects.filter(display_name='New PostGres Proj').exists()

    def test_create_project_validation_failure(self) -> None:
        request = self.factory.post('/projects/create/', {
            'display_name': 'New PostGres Proj',
            'storage_type': 'local'
        })
        request.user = self.user
        response = create_project(request)
        assert response.status_code == 200
        assert b"not been implemented" in response.content

    def test_delete_project(self, mocker) -> None:
        project = Project.objects.create(project_id="delete_me", display_name="Delete", storage_type="postgres", user=self.user)
        mocker.patch('src.postgres_rag.cleanup_project_artifacts', return_value=True)
        request = self.factory.delete(f'/projects/{project.project_id}/delete/')
        request.user = self.user
        response = delete_project(request, project.project_id)
        assert response.status_code == 200
        assert not Project.objects.filter(id=project.id).exists()

    def test_manage_prompt(self) -> None:
        project = Project.objects.create(project_id="prompt_test", display_name="Prompt", storage_type="postgres", user=self.user)
        request = self.factory.post(f'/projects/{project.project_id}/prompt/', {
            'content': 'Test custom prompt'
        })
        request.user = self.user
        response = manage_prompt(request, project.project_id)
        assert response.status_code == 200
        assert SystemPrompt.objects.get(project=project).content == 'Test custom prompt'

    def test_manage_prompt_get(self) -> None:
        project = Project.objects.create(project_id="prompt_test_get", display_name="Prompt", storage_type="postgres", user=self.user)
        SystemPrompt.objects.create(project=project, content="Existing prompt")
        request = self.factory.get(f'/projects/{project.project_id}/prompt/')
        request.user = self.user
        response = manage_prompt(request, project.project_id)
        assert response.status_code == 200
        import json
        data = json.loads(response.content)
        assert data['prompt'] == 'Existing prompt'
