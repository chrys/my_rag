import csv
import io
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from src.apps.projects.models import Project
from src.apps.documents.models import Document
from .models import EvaluationDataset, EvaluationRun, EvaluationResultMetrics
from .eval_services import (
    start_async_qa_generation,
    start_async_evaluation_run,
    QA_GEN_STATUS,
)

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["GET"])
def evaluation_dashboard(request):
    """
    Redirects to the central modern Unfold evaluation dashboard.
    """
    return redirect("/rag/dashboard/evaluate/")


@login_required
def qa_setup(request, project_id):
    """
    Redirects standard QA Setup view to the Unfold Admin QaSetupWorkflowView.
    """
    return redirect(reverse("custom_admin:qa-setup-workflow", kwargs={"project_id": project_id}))


@login_required
@require_http_methods(["GET"])
def qa_generation_status(request, project_id):
    """
    Polling endpoint for automatic QA generation.
    """
    status_data = QA_GEN_STATUS.get(project_id, {"status": "PENDING", "error": "", "count": 0})
    project = get_object_or_404(Project, project_id=project_id)

    if status_data["status"] == "SUCCESS":
        dataset_items = EvaluationDataset.objects.filter(project=project)
        return render(request, "evaluate/qa_list_partial.html", {
            "project": project,
            "dataset_items": dataset_items,
            "count": status_data.get("count", 0)
        })
    elif status_data["status"] == "FAILED":
        return HttpResponse(f'<div class="p-4 bg-red-50 text-red-700 rounded-lg">✗ Generation failed: {status_data["error"]}</div>')
    else:
        # Still running
        context = {
            "project": project,
            "status": "RUNNING",
            "mode": "qa_generation"
        }
        return render(request, "evaluate/run_progress.html", context)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def run_evaluation(request, project_id):
    """
    Creates an EvaluationRun and triggers background RAG Ragas evaluation.
    """
    project = get_object_or_404(Project, project_id=project_id)
    run = EvaluationRun.objects.create(
        project=project,
        status="PENDING"
    )

    # Start async thread
    start_async_evaluation_run(run.id)

    context = {
        "project": project,
        "run": run,
        "status": "RUNNING",
        "mode": "evaluation"
    }
    return render(request, "evaluate/run_progress.html", context)


@login_required
@require_http_methods(["GET"])
def evaluation_run_status(request, run_id):
    """
    Polling endpoint for evaluation runs.
    """
    run = get_object_or_404(EvaluationRun, id=run_id)

    if run.status == "SUCCESS":
        # Redirect to results grid view
        return HttpResponse(f'<div hx-get="{reverse("evaluate:results", args=[run.id])}" hx-trigger="load" hx-target="#evaluation-content-pane"></div>')
    elif run.status == "FAILED":
        return HttpResponse(f'<div class="p-4 bg-red-50 text-red-700 rounded-lg">✗ Evaluation failed: {run.error_message}</div>')
    else:
        # Still running / pending
        context = {
            "project": run.project,
            "run": run,
            "status": "RUNNING",
            "mode": "evaluation"
        }
        return render(request, "evaluate/run_progress.html", context)


@login_required
@require_http_methods(["GET"])
def evaluation_results(request, run_id):
    """
    Fetches evaluation metrics and renders the grid results table.
    """
    run = get_object_or_404(EvaluationRun, id=run_id)
    metrics = EvaluationResultMetrics.objects.filter(run=run).select_related("dataset_item")

    if not metrics.exists():
        return HttpResponse('<div class="p-4 text-gray-500">No evaluation metrics recorded for this run.</div>')

    avg_recall = sum(m.context_recall or 0 for m in metrics) / metrics.count()
    avg_precision = sum(m.context_precision or 0 for m in metrics) / metrics.count()
    avg_faithfulness = sum(m.faithfulness or 0 for m in metrics) / metrics.count()
    avg_relevancy = sum(m.answer_relevancy or 0 for m in metrics) / metrics.count()
    avg_total = (avg_recall + avg_precision + avg_faithfulness + avg_relevancy) / 4

    def get_color(score):
        if score >= 0.85:
            return "green"
        elif score >= 0.70:
            return "yellow"
        return "red"

    # Traces data for detailed drill-down
    traces = []
    # Use LlamaIndex to query top matching contexts for debugging display
    for item in metrics:
        # RAG Tracing Context display
        traces.append({
            "metric": item,
            "question": item.dataset_item.question if item.dataset_item else "N/A",
            "ground_truth": item.dataset_item.ground_truth if item.dataset_item else "N/A",
            "recall_color": get_color(item.context_recall or 0),
            "precision_color": get_color(item.context_precision or 0),
            "faithfulness_color": get_color(item.faithfulness or 0),
            "relevancy_color": get_color(item.answer_relevancy or 0)
        })

    context = {
        "run": run,
        "avg_recall": avg_recall,
        "avg_precision": avg_precision,
        "avg_faithfulness": avg_faithfulness,
        "avg_relevancy": avg_relevancy,
        "avg_total": avg_total,
        "recall_color": get_color(avg_recall),
        "precision_color": get_color(avg_precision),
        "faithfulness_color": get_color(avg_faithfulness),
        "relevancy_color": get_color(avg_relevancy),
        "total_color": get_color(avg_total),
        "traces": traces,
        "url_prefix": "/rag"
    }
    return render(request, "evaluate/metrics_grid.html", context)



@login_required
@require_http_methods(["POST", "DELETE"])
@csrf_exempt
def delete_qa_item(request, item_id):
    """
    Deletes a specific QA dataset item from the database.
    If HTMX request, returns the updated QA list partial.
    """
    item = get_object_or_404(EvaluationDataset, id=item_id)
    project = item.project
    item.delete()

    if request.headers.get("HX-Request"):
        dataset_items = EvaluationDataset.objects.filter(project=project)
        return render(request, "evaluate/qa_list_partial.html", {
            "project": project,
            "dataset_items": dataset_items,
            "message": "✓ QA item deleted successfully."
        })

    return redirect(reverse("custom_admin:qa-setup-workflow", kwargs={"project_id": project.project_id}))

