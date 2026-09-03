"""
Admin views for the chat application, integrated with django-unfold.
"""

from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from src.apps.projects.models import Project


class AdminViewMixin(PermissionRequiredMixin):
    model_admin = None

    def __init__(self, model_admin=None, **kwargs):
        self.model_admin = model_admin
        super().__init__(**kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.model_admin and hasattr(self.model_admin, 'admin_site'):
            context.update(self.model_admin.admin_site.each_context(self.request))
        context.update({"title": getattr(self, "title", "Admin"), "model_admin": self.model_admin})
        return context


class ChatWorkflowView(AdminViewMixin, TemplateView):
    """
    Custom administration view representing the Chat Workflow.
    """

    title = "Chat Workflow"
    permission_required = ()
    template_name = "admin/chat_workflow.html"

    def get_context_data(self, **kwargs) -> dict:
        """
        Add active projects to the template context.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments.

        Returns
        -------
        dict
            The updated context dict containing active projects.
        """
        context = super().get_context_data(**kwargs)
        context["projects"] = Project.objects.filter(is_active=True)
        return context
