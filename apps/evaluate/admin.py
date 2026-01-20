from django.contrib import admin
from .models import EvaluationDataset, EvaluationResult


@admin.register(EvaluationDataset)
class EvaluationDatasetAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'state', 'num_questions', 'created_at')
    list_filter = ('state', 'project', 'created_at')
    search_fields = ('name', 'description', 'project__display_name')
    readonly_fields = ('created_at', 'generated_at')
    fieldsets = (
        ('Basic Info', {'fields': ('project', 'user', 'name', 'description')}),
        ('Configuration', {'fields': ('num_questions', 'question_generation_params')}),
        ('Status', {'fields': ('state', 'error_message')}),
        ('Results', {'fields': ('qa_pairs',)}),
        ('Timestamps', {'fields': ('created_at', 'generated_at')}),
    )


@admin.register(EvaluationResult)
class EvaluationResultAdmin(admin.ModelAdmin):
    list_display = ('dataset', 'evaluator_name', 'created_at')
    list_filter = ('evaluator_name', 'dataset', 'created_at')
    search_fields = ('evaluator_name', 'dataset__name', 'project__display_name')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('References', {'fields': ('dataset', 'project')}),
        ('Evaluation', {'fields': ('evaluator_name', 'metrics', 'individual_scores')}),
        ('Timestamps', {'fields': ('created_at',)}),
    )
