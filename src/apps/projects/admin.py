from django.contrib import admin
from unfold.admin import ModelAdmin
from src.apps.my_rag_project.admin import custom_admin_site
from .models import Project, SystemPrompt


@admin.register(Project, site=custom_admin_site)
class ProjectAdmin(ModelAdmin):
    list_display = ("display_name", "storage_type", "document_count", "created_at", "is_active")
    list_filter = ("storage_type", "is_active", "created_at")
    search_fields = ("display_name", "project_id", "external_store_id")
    readonly_fields = ("project_id", "created_at", "updated_at", "document_uploader_and_list")
    fieldsets = (
        (
            "Parameters",
            {
                "classes": ("tab",),
                "fields": (
                    "project_id",
                    "display_name",
                    "description",
                    "is_active",
                    "synthesizer",
                    "document_parsing",
                    "chunking",
                    "embedding_model",
                    "custom_prompt",
                ),
            },
        ),
        (
            "Sources",
            {
                "classes": ("tab",),
                "fields": (
                    "storage_type",
                    "external_store_id",
                    "document_count",
                    "last_indexed_at",
                    "created_at",
                    "updated_at",
                    "document_uploader_and_list",
                ),
            },
        ),
    )

    def document_uploader_and_list(self, obj):
        """
        Custom admin field to render the document uploader and document list manager 
        using HTMX dynamic endpoints inside the Sources tab.
        """
        if not obj or not obj.id:
            return "Please save the project first to manage documents."
        from django.template.loader import render_to_string
        from django.utils.safestring import mark_safe
        return mark_safe(render_to_string("admin/projects/project_sources_tab.html", {"project": obj}))
    document_uploader_and_list.short_description = "Document Manager"


@admin.register(SystemPrompt, site=custom_admin_site)
class SystemPromptAdmin(ModelAdmin):
    list_display = ("project", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("project__display_name",)
    readonly_fields = ("created_at", "updated_at")
