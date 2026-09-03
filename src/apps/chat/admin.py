from django.contrib import admin
from django.contrib.admin import ModelAdmin
from src.apps.my_rag_project.admin import custom_admin_site
from .models import ChatMessage, ChatFeedback


@admin.register(ChatMessage, site=custom_admin_site)
class ChatMessageAdmin(ModelAdmin):
    list_display = ('project', 'message_type', 'user', 'created_at')
    list_filter = ('message_type', 'project', 'created_at')
    search_fields = ('content', 'project__display_name', 'user__username', 'session_id')
    readonly_fields = ('created_at',)
    autocomplete_fields = ('project',)
    fieldsets = (
        ('Message Info', {'fields': ('project', 'user', 'message_type', 'session_id')}),
        ('Content', {'fields': ('content', 'response_html')}),
        ('Context', {'fields': ('context_documents', 'system_prompt_used')}),
        ('Timestamps', {'fields': ('created_at',)}),
    )


@admin.register(ChatFeedback, site=custom_admin_site)
class ChatFeedbackAdmin(ModelAdmin):
    list_display = ('project', 'value', 'customer_id', 'query_preview', 'timestamp', 'created_at')
    list_filter = ('value', 'project', 'created_at')
    search_fields = ('message_id', 'conversation_id', 'customer_id', 'query', 'reply', 'project__display_name')
    readonly_fields = ('created_at',)
    autocomplete_fields = ('project',)
    fieldsets = (
        ('Feedback Info', {'fields': ('project', 'value', 'message_id')}),
        ('Customer & Session', {'fields': ('conversation_id', 'customer_id')}),
        ('Interaction Content', {'fields': ('query', 'reply')}),
        ('Timestamps', {'fields': ('timestamp', 'created_at')}),
    )

    def query_preview(self, obj):
        if obj.query:
            return obj.query[:40] + '...' if len(obj.query) > 40 else obj.query
        return '-'
    query_preview.short_description = 'Query'


try:
    admin.site.register(ChatMessage, ChatMessageAdmin)
    admin.site.register(ChatFeedback, ChatFeedbackAdmin)
except admin.sites.AlreadyRegistered:
    pass



