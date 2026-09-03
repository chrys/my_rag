from django.contrib import admin
from django.contrib.admin import ModelAdmin
from src.apps.my_rag_project.admin import custom_admin_site
from .models import APIKey, APIUsage


@admin.register(APIKey, site=custom_admin_site)
class APIKeyAdmin(ModelAdmin):
    list_display = ('name', 'store_id', 'project', 'user', 'is_active', 'created_at', 'last_used_at')
    list_filter = ('project', 'is_active', 'created_at')
    search_fields = ('name', 'user__username', 'project__display_name', 'project__project_id', 'key')
    readonly_fields = ('store_id', 'key', 'created_at', 'last_used_at')
    autocomplete_fields = ('project',)
    fieldsets = (
        ('Scope & Ownership', {'fields': ('project', 'store_id', 'user')}),
        ('Key Info', {'fields': ('name', 'key', 'is_active')}),
        ('Activity', {'fields': ('created_at', 'last_used_at')}),
    )

    @admin.display(description='Store ID')
    def store_id(self, obj):
        return obj.project.project_id if obj.project else '-'



@admin.register(APIUsage, site=custom_admin_site)
class APIUsageAdmin(ModelAdmin):
    list_display = ('endpoint', 'method', 'status_code', 'response_time_ms', 'created_at')
    list_filter = ('method', 'status_code', 'endpoint', 'created_at')
    search_fields = ('endpoint', 'ip_address', 'api_key__user__username')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'


try:
    admin.site.register(APIKey, APIKeyAdmin)
    admin.site.register(APIUsage, APIUsageAdmin)
except admin.sites.AlreadyRegistered:
    pass


