from django.contrib import admin
from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('project', 'message_type', 'user', 'created_at')
    list_filter = ('message_type', 'project', 'created_at')
    search_fields = ('content', 'project__display_name', 'user__username', 'session_id')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Message Info', {'fields': ('project', 'user', 'message_type', 'session_id')}),
        ('Content', {'fields': ('content', 'response_html')}),
        ('Context', {'fields': ('context_documents', 'system_prompt_used')}),
        ('Timestamps', {'fields': ('created_at',)}),
    )
