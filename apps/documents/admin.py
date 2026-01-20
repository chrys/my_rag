from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'project', 'state', 'indexed_at', 'created_at')
    list_filter = ('state', 'project', 'created_at')
    search_fields = ('display_name', 'document_name', 'project__display_name')
    readonly_fields = ('created_at', 'indexed_at')
    fieldsets = (
        ('Project', {'fields': ('project',)}),
        ('Document Info', {'fields': ('document_name', 'display_name', 'external_document_id')}),
        ('File Metadata', {'fields': ('mime_type', 'file_size')}),
        ('Indexing Status', {'fields': ('state', 'indexed_at', 'error_message')}),
        ('Timestamps', {'fields': ('created_at',)}),
    )
