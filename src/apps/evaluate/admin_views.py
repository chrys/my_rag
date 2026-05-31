"""
Admin views for the evaluate application, integrated with django-unfold.
"""

from django.views.generic import TemplateView
from unfold.views import UnfoldModelAdminViewMixin
from src.apps.projects.models import Project


class EvaluationWorkflowView(UnfoldModelAdminViewMixin, TemplateView):
    """
    Custom administration view representing the Evaluation Workflow dashboard,
    conforming to the django-unfold style guide.
    """

    title = "Evaluation Workflow"
    permission_required = ()
    template_name = "admin/evaluation_workflow.html"

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
