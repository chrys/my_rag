"""
Custom Admin Site configuration for the my_rag_project.
Integrates django-unfold and overrides permission rules to allow regular authenticated users.
"""

from django.contrib.auth.forms import AuthenticationForm as DjangoAuthenticationForm
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_not_required
from django.contrib.auth.views import LoginView
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import path, reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache
from unfold.sites import UnfoldAdminSite
from unfold.widgets import BASE_INPUT_CLASSES


class CustomUnfoldAuthenticationForm(DjangoAuthenticationForm):
    """
    Authentication form styled for Unfold that allows any active user to log in.
    """
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.fields["username"].widget.attrs["autofocus"] = ""
        self.fields["username"].widget.attrs["class"] = " ".join(BASE_INPUT_CLASSES)
        self.fields["password"].widget.attrs["class"] = " ".join(BASE_INPUT_CLASSES)


class CustomLoginView(LoginView):
    """
    Standard login view redirecting admin/staff users to Django admin
    and standard users to the Pico.css dashboard.
    """
    template_name = "registration/login.html"
    redirect_authenticated_user = True

    def get_success_url(self) -> str:
        user = self.request.user
        if user.is_authenticated and (user.is_staff or user.is_superuser):
            return reverse("admin:index")
        redirect_to = self.get_redirect_url()
        if not redirect_to or redirect_to in ["/rag/", "/", "/rag/dashboard/", "/rag/dashboard", "/rag/unfold/", "/rag/unfold"]:
            return reverse("projects:dashboard")
        return redirect_to


class CustomDashboardLoginView(LoginView):
    """
    Dashboard login view redirecting admin users to Django admin
    and non-admin users to the Pico.css dashboard.
    """
    def get_success_url(self) -> str:
        user = self.request.user
        if user.is_authenticated and (user.is_staff or user.is_superuser):
            return reverse("admin:index")
        redirect_to = self.get_redirect_url()
        if not redirect_to or redirect_to in ["/rag/", "/", "/rag/dashboard/", "/rag/dashboard", "/rag/unfold/", "/rag/unfold"]:
            return reverse("projects:dashboard")
        return redirect_to


class CustomUnfoldAdminSite(UnfoldAdminSite):
    """
    Custom administration site utilizing django-unfold theme.
    Overrides standard permissions to allow regular authenticated users access to the dashboard.
    """
    login_form = CustomUnfoldAuthenticationForm

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

    @method_decorator(never_cache)
    @login_not_required
    def login(self, request: HttpRequest, extra_context=None):
        """
        Display the login form for the given HttpRequest.
        Redirects admins to the Django admin page.
        """
        if request.method == "GET" and self.has_permission(request):
            if request.user.is_staff or request.user.is_superuser:
                return HttpResponseRedirect(reverse("admin:index"))
            index_path = reverse("admin:index", current_app=self.name)
            return HttpResponseRedirect(index_path)

        context = {
            **self.each_context(request),
            "title": _("Log in"),
            "subtitle": None,
            "app_path": request.get_full_path(),
            "username": request.user.get_username(),
        }
        if (
            REDIRECT_FIELD_NAME not in request.GET
            and REDIRECT_FIELD_NAME not in request.POST
        ):
            context[REDIRECT_FIELD_NAME] = reverse("admin:index", current_app=self.name)
        context.update(extra_context or {})

        defaults = {
            "extra_context": context,
            "authentication_form": self.login_form or AuthenticationForm,
            "template_name": self.login_template or "admin/login.html",
        }
        request.current_app = self.name
        return CustomDashboardLoginView.as_view(**defaults)(request)

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
        from src.apps.evaluate.admin_views import (
            EvaluationWorkflowView,
            QaSetupWorkflowView,
            RunEvaluationView,
            CreateManualEvaluationRunView,
            GenerateManualAnswerView,
            BatchGenerateManualAnswersView,
            RateManualItemView,
            LocalLLMModelListView,
            RunLocalLLMBenchmarkView,
            LocalLLMBenchmarkStatusView,
            ExportLocalLLMCSVEvaluationView,
        )
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
            path(
                "evaluate/qa-setup/<str:project_id>/",
                self.admin_view(QaSetupWorkflowView.as_view(model_admin=project_admin)),
                name="qa-setup-workflow",
            ),
            path(
                "evaluate/run/",
                self.admin_view(RunEvaluationView.as_view(model_admin=project_admin)),
                name="run-evaluation",
            ),
            path(
                "evaluate/manual/create/",
                self.admin_view(CreateManualEvaluationRunView.as_view(model_admin=project_admin)),
                name="manual-eval-create",
            ),
            path(
                "evaluate/manual/generate-answer/<uuid:item_id>/",
                self.admin_view(GenerateManualAnswerView.as_view(model_admin=project_admin)),
                name="manual-eval-generate-answer",
            ),
            path(
                "evaluate/manual/generate-all/<uuid:run_id>/",
                self.admin_view(BatchGenerateManualAnswersView.as_view(model_admin=project_admin)),
                name="manual-eval-generate-all",
            ),
            path(
                "evaluate/manual/rate/<uuid:item_id>/",
                self.admin_view(RateManualItemView.as_view(model_admin=project_admin)),
                name="manual-eval-rate",
            ),
            path(
                "evaluate/local-llm/models/",
                self.admin_view(LocalLLMModelListView.as_view(model_admin=project_admin)),
                name="local-llm-models",
            ),
            path(
                "evaluate/local-llm/run/",
                self.admin_view(RunLocalLLMBenchmarkView.as_view(model_admin=project_admin)),
                name="local-llm-run",
            ),
            path(
                "evaluate/local-llm/<uuid:run_id>/status/",
                self.admin_view(LocalLLMBenchmarkStatusView.as_view(model_admin=project_admin)),
                name="local-llm-status",
            ),
            path(
                "evaluate/local-llm/<uuid:run_id>/export-csv/",
                self.admin_view(ExportLocalLLMCSVEvaluationView.as_view(model_admin=project_admin)),
                name="local-llm-export-csv",
            ),
        ]
        return custom_urls + urls


custom_admin_site = CustomUnfoldAdminSite(name="custom_admin")
