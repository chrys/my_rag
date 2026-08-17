from django.contrib import admin
from .models import (
    EvaluationDataset,
    EvaluationRun,
    EvaluationResultMetrics,
    LocalLLMEvaluationRun,
    LocalLLMResultMetric,
)


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


@admin.register(LocalLLMEvaluationRun)
class LocalLLMEvaluationRunAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "dataset_name", "total_questions", "best_model", "best_overall_score", "status", "started_at")
    list_filter = ("status", "project", "started_at")
    search_fields = ("id", "project__display_name", "best_model")
    readonly_fields = ("started_at", "completed_at")


@admin.register(LocalLLMResultMetric)
class LocalLLMResultMetricAdmin(admin.ModelAdmin):
    list_display = ("model_name", "run", "question_preview", "overall_score", "tokens_per_second", "reply_time", "created_at")
    list_filter = ("model_name", "run__project", "created_at")
    search_fields = ("model_name", "question", "ground_truth", "model_answer")
    readonly_fields = ("created_at",)

    def question_preview(self, obj):
        return obj.question[:40] + "..." if len(obj.question) > 40 else obj.question
    question_preview.short_description = "Question"
