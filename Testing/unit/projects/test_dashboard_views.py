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

    def test_create_website_project_success(self, client, monkeypatch):
        from unittest.mock import MagicMock
        from src.apps.documents.models import WebSource

        user = User.objects.create_user(username="webuser", password="password123")
        client.login(username="webuser", password="password123")

        mock_test_pg = MagicMock(return_value=(True, ""))
        monkeypatch.setattr("src.apps.projects.views.test_postgres_connection", mock_test_pg)

        mock_thread_start = MagicMock()
        monkeypatch.setattr("threading.Thread.start", mock_thread_start)

        response = client.post(
            "/rag/projects/create/",
            {
                "display_name": "Stripe Docs Project",
                "storage_type": "website",
                "web_root_url": "https://docs.stripe.com/api",
                "web_max_pages": "100",
                "web_subpath_only": "on",
            }
        )

        assert response.status_code == 200
        assert response["HX-Trigger"] == "projectCreated"

        project = Project.objects.filter(display_name="Stripe Docs Project").first()
        assert project is not None
        assert project.storage_type == "postgres"
        assert project.user == user

        web_source = WebSource.objects.filter(project=project).first()
        assert web_source is not None
        assert web_source.root_url == "https://docs.stripe.com/api"
        assert web_source.allowed_domain == "docs.stripe.com"
        assert web_source.subpath_only is True
        assert web_source.max_pages == 100
        assert mock_thread_start.called

    def test_create_website_project_missing_url_returns_error(self, client, monkeypatch):
        from unittest.mock import MagicMock

        user = User.objects.create_user(username="webuser2", password="password123")
        client.login(username="webuser2", password="password123")

        mock_test_pg = MagicMock(return_value=(True, ""))
        monkeypatch.setattr("src.apps.projects.views.test_postgres_connection", mock_test_pg)

        response = client.post(
            "/rag/projects/create/",
            {
                "display_name": "Invalid Website Project",
                "storage_type": "website",
                "web_root_url": "",
            }
        )

        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "project-error-container" in content
        assert "Website entrypoint URL is required" in content
        assert Project.objects.filter(display_name="Invalid Website Project").count() == 0

    def test_dashboard_view_renders_create_project_option(self, client):
        """Test dashboard base template renders the 'Create New Project' option in selector and modal container"""
        user = User.objects.create_user(username="dashuser", password="password123")
        client.login(username="dashuser", password="password123")

        project = Project.objects.create(
            project_id="test_dash_proj_selector",
            display_name="Selector Test Project",
            storage_type="postgres",
            user=user
        )

        response = client.get("/rag/dashboard/")
        assert response.status_code == 200
        content = response.content.decode("utf-8")

        # Verify selector option
        assert '__new_project__' in content
        assert '➕ Create New Project...' in content
        assert 'project-create-link' not in content

        # Verify modal elements
        assert 'id="create-project-modal"' in content
        assert 'modal-create-project-form' in content
        assert 'modal-project-display-name' in content

    def test_create_project_sets_session_active_project(self, client, monkeypatch):
        """Test project creation updates request.session active_project_id and provides X-Project-Id header"""
        from unittest.mock import MagicMock

        user = User.objects.create_user(username="sessionuser", password="password123")
        client.login(username="sessionuser", password="password123")

        mock_test_pg = MagicMock(return_value=(True, ""))
        monkeypatch.setattr("src.apps.projects.views.test_postgres_connection", mock_test_pg)

        response = client.post(
            "/rag/projects/create/",
            {
                "display_name": "Active Session Project",
                "storage_type": "postgres",
            }
        )

        assert response.status_code == 200
        assert response["HX-Trigger"] == "projectCreated"

        created_project = Project.objects.filter(display_name="Active Session Project").first()
        assert created_project is not None
        assert response.headers.get("X-Project-Id") == created_project.project_id
        assert client.session.get("active_project_id") == created_project.project_id

    def test_sources_view_renders_web_source_section(self, client):
        """Test sources tab renders the web source section and discovered pages when project has a WebSource"""
        from src.apps.documents.models import WebSource, WebPage

        user = User.objects.create_user(username="webpageuser", password="password123")
        client.login(username="webpageuser", password="password123")

        project = Project.objects.create(
            project_id="test_web_sources_proj",
            display_name="Web Sources Test Project",
            storage_type="postgres",
            user=user
        )
        web_source = WebSource.objects.create(
            project=project,
            root_url="https://example.com/docs/",
            allowed_domain="example.com",
            subpath_only=True,
            sync_status="COMPLETED",
            total_pages_count=2,
            indexed_pages_count=2,
        )
        WebPage.objects.create(
            web_source=web_source,
            url="https://example.com/docs/getting-started",
            title="Getting Started Guide",
            status="INDEXED",
        )

        response = client.get(f"/rag/projects/{project.project_id}/sources/")
        assert response.status_code == 200
        content = response.content.decode("utf-8")

        assert "web-source-section-container" in content
        assert "web-status-poll" in content
        assert "Getting Started Guide" in content
        assert "https://example.com/docs/getting-started" in content
        assert "WEB PAGES INDEXED" in content

