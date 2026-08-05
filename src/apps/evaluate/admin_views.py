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
from src.apps.evaluate.models import (
    EvaluationDataset,
    EvaluationRun,
    EvaluationResultMetrics,
    ManualEvaluationRun,
    ManualEvaluationItem,
)
from src.apps.evaluate.eval_services import (
    generate_answer_for_manual_item,
    batch_generate_manual_answers,
)


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

            from django.db import transaction
            count = 0
            with transaction.atomic():
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

                from django.db import transaction
                count = 0
                with transaction.atomic():
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

        from django.db import transaction
        from django.db.utils import OperationalError
        try:
            with transaction.atomic():
                project = Project.objects.select_for_update(nowait=True).get(project_id=project_id)

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
        except OperationalError:
            return HttpResponse('<div class="p-4 bg-red-50 text-red-700 rounded-md border border-red-100">Error: Evaluation is already running for this project.</div>')
        except Project.DoesNotExist:
            raise Http404("No Project matches the given query.")


def get_manual_workspace_context(run: ManualEvaluationRun) -> dict:
    """
    Helper function to build summary metrics context for manual evaluation workspace.
    """
    items = run.items.all()
    total_count = items.count()
    green_count = items.filter(rating="GREEN").count()
    orange_count = items.filter(rating="ORANGE").count()
    red_count = items.filter(rating="RED").count()
    unrated_count = items.filter(rating="UNRATED").count()
    pending_gen_count = items.filter(status__in=["PENDING", "FAILED"]).count()

    return {
        "run": run,
        "project": run.project,
        "items": items,
        "total_count": total_count,
        "green_count": green_count,
        "orange_count": orange_count,
        "red_count": red_count,
        "unrated_count": unrated_count,
        "pending_gen_count": pending_gen_count,
        "url_prefix": "/rag",
    }


@method_decorator(csrf_exempt, name="dispatch")
class CreateManualEvaluationRunView(UnfoldModelAdminViewMixin, View):
    """
    POST endpoint to initialize a Manual Evaluation Run from text inputs or CSV file upload.
    """
    permission_required = ()

    def post(self, request, *args, **kwargs):
        project_id = request.POST.get("project_id")
        input_method = request.POST.get("input_method", "manual")

        if not project_id:
            return HttpResponse('<div class="p-4 bg-red-50 text-red-700 rounded-lg">✗ Error: Target project ID is required.</div>', status=400)

        project = get_object_or_404(Project, project_id=project_id)
        questions = []
        source_type = "MANUAL_INPUT"

        if input_method == "manual":
            raw_text = request.POST.get("manual_questions", "")
            questions = [q.strip() for q in raw_text.split("\n") if q.strip()]
        elif input_method == "csv":
            source_type = "CSV_UPLOAD"
            csv_file = request.FILES.get("csv_file")
            if not csv_file:
                return HttpResponse('<div class="p-4 bg-red-50 text-red-700 rounded-lg">✗ No CSV file uploaded.</div>', status=400)

            try:
                data_set = csv_file.read().decode("utf-8")
                io_string = io.StringIO(data_set)
                reader = csv.DictReader(io_string)

                # Look for 'questions' or 'question' header (case-insensitive)
                headers = {h.lower().strip(): h for h in reader.fieldnames or []}
                q_col = headers.get("questions") or headers.get("question")
                if not q_col:
                    return HttpResponse('<div class="p-4 bg-red-50 text-red-700 rounded-lg">✗ CSV must contain a "questions" or "question" column header.</div>', status=400)

                for row in reader:
                    q_val = row.get(q_col, "").strip()
                    if q_val:
                        questions.append(q_val)
            except Exception as exc:
                return HttpResponse(f'<div class="p-4 bg-red-50 text-red-700 rounded-lg">✗ Error parsing CSV: {exc}</div>', status=400)

        if not questions:
            return HttpResponse('<div class="p-4 bg-yellow-50 text-yellow-800 rounded-lg">⚠️ Please provide at least one valid question to evaluate.</div>', status=400)

        from django.db import transaction
        with transaction.atomic():
            run = ManualEvaluationRun.objects.create(
                project=project,
                source_type=source_type
            )
            for q in questions:
                ManualEvaluationItem.objects.create(
                    run=run,
                    question=q,
                    status="PENDING",
                    rating="UNRATED"
                )

        context = get_manual_workspace_context(run)
        return render(request, "evaluate/manual_eval_workspace.html", context)


@method_decorator(csrf_exempt, name="dispatch")
class GenerateManualAnswerView(UnfoldModelAdminViewMixin, View):
    """
    POST endpoint to generate RAG answer for a single ManualEvaluationItem.
    """
    permission_required = ()

    def post(self, request, item_id, *args, **kwargs):
        item = get_object_or_404(ManualEvaluationItem, id=item_id)
        generate_answer_for_manual_item(str(item.id))
        context = get_manual_workspace_context(item.run)
        return render(request, "evaluate/manual_eval_workspace.html", context)


@method_decorator(csrf_exempt, name="dispatch")
class BatchGenerateManualAnswersView(UnfoldModelAdminViewMixin, View):
    """
    POST endpoint to generate RAG answers for all pending items in a ManualEvaluationRun.
    """
    permission_required = ()

    def post(self, request, run_id, *args, **kwargs):
        from django.db import transaction
        from django.db.utils import OperationalError
        try:
            with transaction.atomic():
                run = ManualEvaluationRun.objects.select_for_update(nowait=True).get(id=run_id)
                batch_generate_manual_answers(str(run.id))
                context = get_manual_workspace_context(run)
                return render(request, "evaluate/manual_eval_workspace.html", context)
        except OperationalError:
            return HttpResponse('<div class="p-4 bg-yellow-50 text-yellow-800 rounded-lg">⚠️ Batch generation is already running. Please wait.</div>')
        except ManualEvaluationRun.DoesNotExist:
            raise Http404("No ManualEvaluationRun matches the given query.")


@method_decorator(csrf_exempt, name="dispatch")
class RateManualItemView(UnfoldModelAdminViewMixin, View):
    """
    POST endpoint to update the Red/Orange/Green rating of a ManualEvaluationItem.
    """
    permission_required = ()

    def post(self, request, item_id, *args, **kwargs):
        item = get_object_or_404(ManualEvaluationItem, id=item_id)
        rating = request.POST.get("rating", "UNRATED")
        if rating in ["GREEN", "ORANGE", "RED", "UNRATED"]:
            item.rating = rating
            item.save()
        context = get_manual_workspace_context(item.run)
        return render(request, "evaluate/manual_eval_workspace.html", context)



