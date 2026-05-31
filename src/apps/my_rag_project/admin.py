"""
Custom Admin Site configuration for the my_rag_project.
Integrates django-unfold and overrides permission rules to allow regular authenticated users.
"""

from django.http import HttpRequest
from django.urls import path
from unfold.sites import UnfoldAdminSite


class CustomUnfoldAdminSite(UnfoldAdminSite):
    """
    Custom administration site utilizing django-unfold theme.
    Overrides standard permissions to allow regular authenticated users access to the dashboard.
    """

    def has_permission(self, request: HttpRequest) -> bool:
        """
        Check if the user has permission to access this admin site.
        Allows any active authenticated user.

        Parameters
        ----------
        request : HttpRequest
            The incoming HTTP request object.

        Returns
        -------
        bool
            True if the user is authenticated and active, False otherwise.
        """
        return bool(request.user and request.user.is_authenticated and request.user.is_active)

    def get_urls(self) -> list:
        """
        Overridden to inject custom chat and evaluation workflow views
        into the admin site's URL structure.

        Returns
        -------
        list
            The complete list of admin URL patterns.
        """
        urls = super().get_urls()
        from src.apps.chat.admin_views import ChatWorkflowView
        from src.apps.evaluate.admin_views import EvaluationWorkflowView
        from src.apps.projects.models import Project

        # Fetch the registered Project ModelAdmin instance from the registry
        project_admin = self._registry.get(Project)
        if not project_admin:
            from src.apps.projects.admin import ProjectAdmin
            project_admin = ProjectAdmin(Project, self)

        custom_urls = [
            path(
                "chat/",
                self.admin_view(ChatWorkflowView.as_view(model_admin=project_admin)),
                name="chat-workflow",
            ),
            path(
                "evaluate/",
                self.admin_view(EvaluationWorkflowView.as_view(model_admin=project_admin)),
                name="evaluation-workflow",
            ),
        ]
        return custom_urls + urls


custom_admin_site = CustomUnfoldAdminSite(name="custom_admin")
