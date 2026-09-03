from django import forms
from django.contrib import admin
from unfold.admin import ModelAdmin
from src.apps.my_rag_project.admin import custom_admin_site
from .models import Project, SystemPrompt


class ProjectAdminForm(forms.ModelForm):
    custom_prompt_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 8,
            'placeholder': 'Enter system prompt rules, instructions, or role definition...',
            'style': 'width: 100%; font-family: monospace;',
        }),
        required=False,
        label="Custom Prompt Text",
        help_text="Custom system prompt content applied to chat queries when custom prompt is enabled."
    )

    class Meta:
        model = Project
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            prompt_obj = SystemPrompt.objects.filter(project=self.instance).first()
            if prompt_obj:
                self.fields['custom_prompt_text'].initial = prompt_obj.content

            # Check if project already has indexed sources
            has_sources = (self.instance.document_count > 0) or self.instance.documents.exists()
            if has_sources:
                locked_fields = ['embedding_model', 'document_parsing']
                for field_name in locked_fields:
                    if field_name in self.fields:
                        self.fields[field_name].disabled = True
                        self.fields[field_name].help_text = (
                            "🔒 Locked: Cannot be changed after the first source has been indexed."
                        )

    def clean(self):
        cleaned_data = super().clean()
        storage_type = cleaned_data.get('storage_type')
        if storage_type == 'google':
            cleaned_data['use_hyde'] = False
            cleaned_data['synthesizer'] = False
            cleaned_data['response_mode'] = 'compact'
            cleaned_data['embedding_model'] = 'models/gemini-embedding-001'

        custom_prompt = cleaned_data.get('custom_prompt', False)
        prompt_text = cleaned_data.get('custom_prompt_text', '').strip()
        if prompt_text and not custom_prompt:
            cleaned_data['custom_prompt'] = True
            self.instance.custom_prompt = True
        return cleaned_data

    def save(self, commit=True):
        project = super().save(commit=commit)
        custom_prompt = self.cleaned_data.get('custom_prompt', False)
        prompt_text = self.cleaned_data.get('custom_prompt_text', '').strip()

        if commit:
            self._save_system_prompt(project, custom_prompt, prompt_text)
        else:
            original_save_m2m = self.save_m2m
            def save_m2m():
                original_save_m2m()
                self._save_system_prompt(project, custom_prompt, prompt_text)
            self.save_m2m = save_m2m

        return project

    def _save_system_prompt(self, project, enabled, prompt_text):
        if enabled and prompt_text:
            SystemPrompt.objects.update_or_create(
                project=project,
                defaults={'content': prompt_text}
            )
        elif not enabled:
            # When custom prompt is disabled, keep system prompt or delete as needed
            pass


@admin.register(Project, site=custom_admin_site)
class ProjectAdmin(ModelAdmin):
    form = ProjectAdminForm
    list_display = ("display_name", "storage_type", "document_count", "created_at", "is_active")
    list_filter = ("storage_type", "is_active", "created_at")
    search_fields = ("display_name", "project_id", "external_store_id")
    readonly_fields = ("project_id", "created_at", "updated_at", "document_uploader_and_list", "api_key_manager", "feedback_manager")
    fieldsets = (
        (
            "Parameters",
            {
                "classes": ("tab",),
                "fields": (
                    "project_id",
                    "display_name",
                    "storage_type",
                    "response_mode",
                    "use_hyde",
                    "description",
                    "is_active",
                    "synthesizer",
                    "document_parsing",
                    "embedding_model",
                    "llm_model",
                    "disable_thinking",
                ),
            },
        ),
        (
            "Prompt",
            {
                "classes": ("tab",),
                "fields": (
                    "custom_prompt",
                    "custom_prompt_text",
                ),
            },
        ),
        (
            "Sources",
            {
                "classes": ("tab",),
                "fields": (
                    "external_store_id",
                    "document_count",
                    "last_indexed_at",
                    "created_at",
                    "updated_at",
                    "document_uploader_and_list",
                ),
            },
        ),
        (
            "API Keys",
            {
                "classes": ("tab",),
                "fields": (
                    "api_key_manager",
                ),
            },
        ),
        (
            "Feedback",
            {
                "classes": ("tab",),
                "fields": (
                    "feedback_manager",
                ),
            },
        ),
    )

    class Media:
        js = ("admin/js/custom_prompt_toggle.js",)

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

    def api_key_manager(self, obj):
        """
        Custom admin field to render the project-scoped API key manager 
        using HTMX dynamic endpoints inside the API Keys tab.
        """
        if not obj or not obj.id:
            return "Please save the project first to manage API keys."
        from django.template.loader import render_to_string
        from django.utils.safestring import mark_safe
        return mark_safe(render_to_string("admin/projects/project_apikey_tab.html", {"project": obj}))
    api_key_manager.short_description = "API Key Manager"

    def feedback_manager(self, obj):
        """
        Custom admin field to render customer feedback and ratings 
        using HTMX dynamic endpoints inside the Feedback tab.
        """
        if not obj or not obj.id:
            return "Please save the project first to view feedback."
        from django.template.loader import render_to_string
        from django.utils.safestring import mark_safe
        return mark_safe(render_to_string("admin/projects/project_feedback_tab.html", {"project": obj}))
    feedback_manager.short_description = "Feedback Manager"


@admin.register(SystemPrompt, site=custom_admin_site)
class SystemPromptAdmin(ModelAdmin):
    list_display = ("project", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("project__display_name",)
    readonly_fields = ("created_at", "updated_at")
