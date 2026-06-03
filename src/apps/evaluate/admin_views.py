"""
Admin views for the evaluate application, integrated with django-unfold.
"""

import csv
import io
from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect, render
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
                dataset_items = EvaluationDataset.objects.filter(project=project)
                return render(request, "evaluate/qa_list_partial.html", {
                    "project": project,
                    "dataset_items": dataset_items,
                    "message": f"✓ Successfully saved {count} custom QA items!"
                })
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
                    dataset_items = EvaluationDataset.objects.filter(project=project)
                    return render(request, "evaluate/qa_list_partial.html", {
                        "project": project,
                        "dataset_items": dataset_items,
                        "message": f"✓ Imported {count} items from CSV!"
                    })
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
            context = {
                "project": project,
                "status": "RUNNING",
                "mode": "qa_generation"
            }
            return render(request, "evaluate/run_progress.html", context)


@method_decorator(csrf_exempt, name="dispatch")
class RunEvaluationView(UnfoldModelAdminViewMixin, View):
    """
    POST endpoint to execute retrieval accuracy evaluations.
    """
    permission_required = ()

    def post(self, request, *args, **kwargs):
        project_id = request.POST.get("project_id")
        document_id = request.POST.get("document_id")
        eval_method = request.POST.get("eval_method")

        if eval_method == "open_rag":
            return HttpResponse('<div class="p-4 bg-yellow-50 text-yellow-700 rounded-md border border-yellow-100">Open RAG Eval is not implemented yet.</div>')

        if not project_id or not document_id:
            return HttpResponse('<div class="p-4 bg-red-50 text-red-700 rounded-md border border-red-100">Error: Missing project or document configuration.</div>')

        project = get_object_or_404(Project, project_id=project_id)

        from src.apps.documents.models import Document
        try:
            document = Document.objects.get(project=project, id=document_id)
        except (Document.DoesNotExist, ValueError):
            document = get_object_or_404(Document, project=project, document_name=document_id)

        from src.apps.evaluate.eval_services import SyntheticQAEvaluator
        evaluator = SyntheticQAEvaluator(project.project_id)
        results = evaluator.evaluate_retrieval_recall(document.document_name)

        context = {
            "results": results,
            "project": project,
            "document": document,
            "url_prefix": "/rag",
        }
        return render(request, "admin/evaluation_scorecard.html", context)


