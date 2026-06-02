from django.contrib import admin
from .models import EvaluationDataset, EvaluationRun, EvaluationResultMetrics


@admin.register(EvaluationDataset)
class EvaluationDatasetAdmin(admin.ModelAdmin):
    list_display = ("question", "project", "document", "source", "created_at")
    list_filter = ("source", "project", "created_at")
    search_fields = ("question", "ground_truth", "project__display_name")
    readonly_fields = ("created_at",)


@admin.register(EvaluationRun)
class EvaluationRunAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "status", "started_at", "completed_at")
    list_filter = ("status", "project", "started_at")
    search_fields = ("id", "project__display_name")
    readonly_fields = ("started_at",)


@admin.register(EvaluationResultMetrics)
class EvaluationResultMetricsAdmin(admin.ModelAdmin):
    list_display = ("run", "dataset_item", "context_recall", "context_precision", "faithfulness", "answer_relevancy")
    list_filter = ("run__project",)
