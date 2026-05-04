from django.contrib import admin
from .models import APIKey, APIUsage


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_active', 'created_at', 'last_used_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'user__username', 'key')
    readonly_fields = ('key', 'created_at', 'last_used_at')
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Key Info', {'fields': ('name', 'key', 'is_active')}),
        ('Activity', {'fields': ('created_at', 'last_used_at')}),
    )


@admin.register(APIUsage)
class APIUsageAdmin(admin.ModelAdmin):
    list_display = ('endpoint', 'method', 'status_code', 'response_time_ms', 'created_at')
    list_filter = ('method', 'status_code', 'endpoint', 'created_at')
    search_fields = ('endpoint', 'ip_address', 'api_key__user__username')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
