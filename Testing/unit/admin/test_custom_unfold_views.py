import pytest
from django.test import RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from src.apps.chat.admin_views import ChatWorkflowView
from src.apps.evaluate.admin_views import EvaluationWorkflowView
from src.apps.projects.models import Project
from src.apps.my_rag_project.admin import custom_admin_site

@pytest.mark.django_db
class TestCustomUnfoldViews:
    """Test cases for Custom Unfold Views in the admin panel"""

    def test_chat_workflow_view_context(self) -> None:
        """Test ChatWorkflowView context includes active projects"""
        project = Project.objects.create(
            project_id="test_chat_view_1",
            display_name="Active Project",
            is_active=True
        )
        inactive = Project.objects.create(
            project_id="test_chat_view_2",
            display_name="Inactive Project",
            is_active=False
        )

        project_admin = custom_admin_site._registry.get(Project)
        view_func = ChatWorkflowView.as_view(model_admin=project_admin)
        
        factory = RequestFactory()
        request = factory.get("/dashboard/chat/")
        request.user = User.objects.create_user(username="test_admin_user", is_active=True)
        
        response = view_func(request)
        assert response.status_code == 200
        
        context = response.context_data
        assert "projects" in context
        active_list = list(context["projects"])
        assert project in active_list
        assert inactive not in active_list

    def test_evaluation_workflow_view_context(self) -> None:
        """Test EvaluationWorkflowView context includes active projects"""
        project = Project.objects.create(
            project_id="test_eval_view_1",
            display_name="Active Project",
            is_active=True
        )

        project_admin = custom_admin_site._registry.get(Project)
        view_func = EvaluationWorkflowView.as_view(model_admin=project_admin)
        
        factory = RequestFactory()
        request = factory.get("/dashboard/evaluate/")
        request.user = User.objects.create_user(username="test_admin_user_2", is_active=True)
        
        response = view_func(request)
        assert response.status_code == 200
        
        context = response.context_data
        assert "projects" in context
        active_list = list(context["projects"])
        assert project in active_list
