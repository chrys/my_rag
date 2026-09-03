import pytest
from django.contrib.auth.models import User
from src.apps.projects.models import Project, SystemPrompt
from src.apps.api.models import APIKey

@pytest.mark.django_db
class TestDashboardViews:
    def test_dashboard_view_renders_for_authenticated_user(self, client):
        user = User.objects.create_user(username="dashuser", password="password123")
        client.login(username="dashuser", password="password123")
        project = Project.objects.create(
            project_id="dash_test_proj",
            display_name="Dashboard Test Project",
            user=user,
            storage_type="postgres"
        )

        response = client.get("/rag/dashboard/")
        assert response.status_code == 200
        assert b"My RAG Studio" in response.content
        assert b"Dashboard Test Project" in response.content

    def test_parameters_view_get_and_post(self, client):
        user = User.objects.create_user(username="paramuser", password="password123")
        client.login(username="paramuser", password="password123")
        project = Project.objects.create(
            project_id="param_test_proj",
            display_name="Initial Name",
            user=user,
            storage_type="postgres"
        )

        # GET
        response = client.get(f"/rag/projects/{project.project_id}/parameters/")
        assert response.status_code == 200
        assert b"Initial Name" in response.content

        # POST
        response = client.post(
            f"/rag/projects/{project.project_id}/parameters/",
            {
                "display_name": "Updated Name",
                "llm_model": "gemini/gemini-2.5-flash-lite",
                "response_mode": "refine",
                "use_hyde": "on",
                "is_active": "on",
            },
            HTTP_HX_REQUEST="true"
        )
        assert response.status_code == 200
        assert b"saved successfully" in response.content

        project.refresh_from_db()
        assert project.display_name == "Updated Name"
        assert project.response_mode == "refine"
        assert project.use_hyde is True

    def test_prompt_view_get_and_post(self, client):
        user = User.objects.create_user(username="promptuser", password="password123")
        client.login(username="promptuser", password="password123")
        project = Project.objects.create(
            project_id="prompt_test_proj",
            display_name="Prompt Project",
            user=user,
            storage_type="postgres"
        )

        # POST custom prompt
        response = client.post(
            f"/rag/projects/{project.project_id}/prompt/",
            {
                "custom_prompt": "on",
                "prompt_text": "You are a specialized code reviewer.",
            },
            HTTP_HX_REQUEST="true"
        )
        assert response.status_code == 200
        assert b"saved successfully" in response.content

        project.refresh_from_db()
        assert project.custom_prompt is True
        prompt = SystemPrompt.objects.filter(project=project).first()
        assert prompt is not None
        assert prompt.content == "You are a specialized code reviewer."

    def test_api_keys_view_get(self, client):
        user = User.objects.create_user(username="apikeyuser", password="password123")
        client.login(username="apikeyuser", password="password123")
        project = Project.objects.create(
            project_id="apikey_test_proj",
            display_name="API Key Project",
            user=user,
            storage_type="postgres"
        )
        key = APIKey.objects.create(user=user, project=project, name="Test Key")

        response = client.get(f"/rag/projects/{project.project_id}/api-keys-tab/")
        assert response.status_code == 200
        assert b"Test Key" in response.content
        assert b"apikey_test_proj" in response.content
        assert b"Available Store IDs" in response.content
