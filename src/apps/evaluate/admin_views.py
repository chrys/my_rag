"""
Admin views for the evaluate application, integrated with django-unfold.
"""

import csv
import io
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from unfold.views import UnfoldModelAdminViewMixin
from src.apps.projects.models import Project
from src.apps.evaluate.models import EvaluationDataset, EvaluationRun, EvaluationResultMetrics


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
        Add active projects with their Ragas metrics to the template context.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments.

        Returns
        -------
        dict
            The updated context dict containing projects_data.
        """
        context = super().get_context_data(**kwargs)
        projects_qs = Project.objects.filter(is_active=True)
        projects_data = []

        for project in projects_qs:
            qa_count = EvaluationDataset.objects.filter(project=project).count()
            latest_run = EvaluationRun.objects.filter(project=project).order_by("-started_at").first()
            
            avg_metrics = {}
            if latest_run and latest_run.status == "SUCCESS":
                metrics = EvaluationResultMetrics.objects.filter(run=latest_run)
                if metrics.exists():
                    avg_metrics = {
                        "recall": sum(m.context_recall or 0 for m in metrics) / metrics.count(),
                        "precision": sum(m.context_precision or 0 for m in metrics) / metrics.count(),
                        "faithfulness": sum(m.faithfulness or 0 for m in metrics) / metrics.count(),
                        "relevancy": sum(m.answer_relevancy or 0 for m in metrics) / metrics.count(),
                    }

            projects_data.append({
                "project": project,
                "qa_count": qa_count,
                "latest_run": latest_run,
                "avg_metrics": avg_metrics
            })

        context["projects"] = projects_qs
        context["projects_data"] = projects_data
        context["url_prefix"] = "/rag"
        return context


@method_decorator(csrf_exempt, name="dispatch")
class QaSetupWorkflowView(UnfoldModelAdminViewMixin, TemplateView):
    """
    Custom administration view representing the Dataset Configuration workspace,
    preserving django-unfold sidebars and main navigation.
    """

    title = "Dataset Configuration"
    permission_required = ()
    template_name = "evaluate/manual_qa.html"

    def get_context_data(self, **kwargs) -> dict:
        """
        Add project and existing dataset items to template context.
        """
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get("project_id")
        project = get_object_or_404(Project, project_id=project_id)
        dataset_items = EvaluationDataset.objects.filter(project=project)
        
        context["project"] = project
        context["dataset_items"] = dataset_items
        context["url_prefix"] = "/rag"
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle QA submissions (manual inputs, CSV imports, background generation).
        """
        project_id = self.kwargs.get("project_id")
        project = get_object_or_404(Project, project_id=project_id)
        input_method = request.POST.get("input_method")

        if input_method == "manual":
            # Process manual QAs
            questions = request.POST.getlist("question[]")
            answers = request.POST.getlist("answer[]")

            count = 0
            for q, a in zip(questions, answers):
                if q.strip() and a.strip():
                    EvaluationDataset.objects.create(
                        project=project,
                        document=None,
                        question=q.strip(),
                        ground_truth=a.strip(),
                        source="MANUAL"
                    )
                    count += 1

            if request.headers.get("HX-Request"):
                return HttpResponse(f'<div class="p-4 bg-green-50 text-green-700 rounded-lg">✓ Successfully saved {count} custom QA items!</div>')
            return redirect(reverse("custom_admin:evaluation-workflow"))

        elif input_method == "csv":
            # Process CSV upload
            csv_file = request.FILES.get("csv_file")
            if not csv_file:
                return HttpResponseBadRequest("No CSV file uploaded.")

            try:
                data_set = csv_file.read().decode("utf-8")
                io_string = io.StringIO(data_set)
                reader = csv.DictReader(io_string)

                # Case-insensitive headers lookup
                headers = {h.lower().strip(): h for h in reader.fieldnames or []}
                q_col = headers.get("question")
                a_col = headers.get("answer")

                if not q_col or not a_col:
                    err_msg = "CSV must contain 'Question' and 'Answer' column headers."
                    if request.headers.get("HX-Request"):
                        return HttpResponse(f'<div class="p-4 bg-red-50 text-red-700 rounded-lg">✗ {err_msg}</div>')
                    return HttpResponseBadRequest(err_msg)

                count = 0
                for row in reader:
                    q_val = row.get(q_col, "").strip()
                    a_val = row.get(a_col, "").strip()
                    if q_val and a_val:
                        EvaluationDataset.objects.create(
                            project=project,
                            document=None,
                            question=q_val,
                            ground_truth=a_val,
                            source="CSV_UPLOAD"
                        )
                        count += 1

                if request.headers.get("HX-Request"):
                    return HttpResponse(f'<div class="p-4 bg-green-50 text-green-700 rounded-lg">✓ Imported {count} items from CSV!</div>')
                return redirect(reverse("custom_admin:evaluation-workflow"))

            except Exception as e:
                err_msg = f"Error parsing CSV: {e}"
                if request.headers.get("HX-Request"):
                    return HttpResponse(f'<div class="p-4 bg-red-50 text-red-700 rounded-lg">✗ {err_msg}</div>')
                return HttpResponseBadRequest(err_msg)

        elif input_method == "generate":
            # Process automatic QA generation
            num_questions = int(request.POST.get("num_questions", 5))
            from src.apps.evaluate.eval_services import start_async_qa_generation
            start_async_qa_generation(project.project_id, num_questions)
            
            from django.shortcuts import render
            context = {
                "project": project,
                "status": "RUNNING",
                "mode": "qa_generation"
            }
            return render(request, "evaluate/run_progress.html", context)

