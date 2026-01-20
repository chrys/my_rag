from django.contrib import admin
from .models import Project, SystemPrompt


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'storage_type', 'document_count', 'created_at', 'is_active')
    list_filter = ('storage_type', 'is_active', 'created_at')
    search_fields = ('display_name', 'project_id', 'external_store_id')
    readonly_fields = ('project_id', 'created_at', 'updated_at')
    fieldsets = (
        ('Identifiers', {'fields': ('project_id', 'display_name')}),
        ('Storage Configuration', {'fields': ('storage_type', 'external_store_id')}),
        ('Metadata', {'fields': ('description', 'is_active')}),
        ('Statistics', {'fields': ('document_count', 'last_indexed_at')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(SystemPrompt)
class SystemPromptAdmin(admin.ModelAdmin):
    list_display = ('project', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('project__display_name',)
    readonly_fields = ('created_at', 'updated_at')
