from django.contrib import admin
from .models import Document, ObsidianSource, ObsidianFile


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


@admin.register(ObsidianSource)
class ObsidianSourceAdmin(admin.ModelAdmin):
    list_display = ('project', 'source_type', 'vault_path', 'last_synced_at', 'created_at')
    list_filter = ('source_type', 'created_at')
    search_fields = ('project__display_name', 'vault_path')
    readonly_fields = ('created_at', 'updated_at', 'last_synced_at')


@admin.register(ObsidianFile)
class ObsidianFileAdmin(admin.ModelAdmin):
    list_display = ('relative_path', 'obsidian_source', 'folder_name', 'status', 'last_indexed_at')
    list_filter = ('status', 'folder_name', 'created_at')
    search_fields = ('relative_path', 'folder_name', 'obsidian_source__project__display_name')
    readonly_fields = ('created_at', 'updated_at', 'last_indexed_at')
