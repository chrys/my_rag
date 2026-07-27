# CodeBundle: src
Generated: 2026-07-26T08:09:19.957Z
Root: /Users/chrys/Projects/my_rag/src
Files: 90

## How to apply changes
- Return changes as **unified diffs** per file whenever possible.
- Files are delimited with `<!-- FILE: ... -->` markers.

## Project tree
```
├─ __init__.py
├─ apps
│  ├─ __init__.py
│  ├─ api
│  │  ├─ __init__.py
│  │  ├─ admin.py
│  │  ├─ api_urls.py
│  │  ├─ api_views.py
│  │  ├─ apps.py
│  │  ├─ migrations
│  │  │  ├─ __init__.py
│  │  │  └─ 0001_initial.py
│  │  ├─ models.py
│  │  ├─ serializers.py
│  │  ├─ tests.py
│  │  └─ views.py
│  ├─ chat
│  │  ├─ __init__.py
│  │  ├─ admin_views.py
│  │  ├─ admin.py
│  │  ├─ api_views.py
│  │  ├─ apps.py
│  │  ├─ migrations
│  │  │  ├─ __init__.py
│  │  │  └─ 0001_initial.py
│  │  ├─ models.py
│  │  ├─ pages.py
│  │  ├─ serializers.py
│  │  ├─ tests.py
│  │  ├─ urls.py
│  │  └─ views.py
│  ├─ documents
│  │  ├─ __init__.py
│  │  ├─ admin.py
│  │  ├─ api_views.py
│  │  ├─ apps.py
│  │  ├─ migrations
│  │  │  ├─ __init__.py
│  │  │  ├─ 0001_initial.py
│  │  │  └─ 0002_document_expiration_date_document_is_expired_checked.py
│  │  ├─ models.py
│  │  ├─ serializers.py
│  │  ├─ services.py
│  │  ├─ tests.py
│  │  ├─ urls.py
│  │  └─ views.py
│  ├─ evaluate
│  │  ├─ __init__.py
│  │  ├─ admin_views.py
│  │  ├─ admin.py
│  │  ├─ api_views.py
│  │  ├─ apps.py
│  │  ├─ eval_services.py
│  │  ├─ migrations
│  │  │  ├─ __init__.py
│  │  │  ├─ 0001_initial.py
│  │  │  └─ 0002_manualevaluationrun_manualevaluationitem.py
│  │  ├─ models.py
│  │  ├─ serializers.py
│  │  ├─ tests.py
│  │  ├─ urls.py
│  │  └─ views.py
│  ├─ my_rag_project
│  │  ├─ __init__.py
│  │  ├─ admin.py
│  │  ├─ asgi.py
│  │  ├─ settings
│  │  │  ├─ __init__.py
│  │  │  ├─ base.py
│  │  │  ├─ settings_dev.py
│  │  │  ├─ settings_prod.py
│  │  │  └─ settings_test.py
│  │  ├─ urls.py
│  │  └─ wsgi.py
│  └─ projects
│     ├─ __init__.py
│     ├─ admin.py
│     ├─ api_views.py
│     ├─ apps.py
│     ├─ db_utils.py
│     ├─ migrations
│     │  ├─ __init__.py
│     │  ├─ 0001_initial.py
│     │  ├─ 0002_alter_project_storage_type.py
│     │  ├─ 0003_project_user.py
│     │  ├─ 0004_alter_project_storage_type.py
│     │  ├─ 0005_project_chunking_project_custom_prompt_and_more.py
│     │  ├─ 0006_project_use_markitdown_and_more.py
│     │  ├─ 0007_alter_project_storage_type.py
│     │  ├─ 0008_alter_project_document_parsing.py
│     │  └─ 0009_alter_project_storage_type_and_more.py
│     ├─ models.py
│     ├─ serializers.py
│     ├─ tests.py
│     ├─ urls.py
│     └─ views.py
├─ google_file_search.py
├─ local_project_storage.py
├─ local_rag.py
├─ optional_dependencies.py
├─ postgres_rag.py
├─ prompt_storage.py
└─ rag-api-gunicorn.conf.py
```

## Files list

- `__init__.py` (53 bytes)
- `apps/__init__.py` (39 bytes)
- `apps/api/__init__.py` (0 bytes)
- `apps/api/admin.py` (941 bytes)
- `apps/api/api_urls.py` (1630 bytes)
- `apps/api/api_views.py` (4538 bytes)
- `apps/api/apps.py` (90 bytes)
- `apps/api/migrations/__init__.py` (0 bytes)
- `apps/api/migrations/0001_initial.py` (2611 bytes)
- `apps/api/models.py` (2487 bytes)
- `apps/api/serializers.py` (1949 bytes)
- `apps/api/tests.py` (60 bytes)
- `apps/api/views.py` (63 bytes)
- `apps/chat/__init__.py` (0 bytes)
- `apps/chat/admin_views.py` (1008 bytes)
- `apps/chat/admin.py` (701 bytes)
- `apps/chat/api_views.py` (3807 bytes)
- `apps/chat/apps.py` (92 bytes)
- `apps/chat/migrations/__init__.py` (0 bytes)
- `apps/chat/migrations/0001_initial.py` (2282 bytes)
- `apps/chat/models.py` (2449 bytes)
- `apps/chat/pages.py` (882 bytes)
- `apps/chat/serializers.py` (1359 bytes)
- `apps/chat/tests.py` (60 bytes)
- `apps/chat/urls.py` (524 bytes)
- `apps/chat/views.py` (12457 bytes)
- `apps/documents/__init__.py` (0 bytes)
- `apps/documents/admin.py` (768 bytes)
- `apps/documents/api_views.py` (5152 bytes)
- `apps/documents/apps.py` (102 bytes)
- `apps/documents/migrations/__init__.py` (0 bytes)
- `apps/documents/migrations/0001_initial.py` (2342 bytes)
- `apps/documents/migrations/0002_document_expiration_date_document_is_expired_checked.py` (673 bytes)
- `apps/documents/models.py` (2799 bytes)
- `apps/documents/serializers.py` (1352 bytes)
- `apps/documents/services.py` (5213 bytes)
- `apps/documents/tests.py` (60 bytes)
- `apps/documents/urls.py` (288 bytes)
- `apps/documents/views.py` (17746 bytes)
- `apps/evaluate/__init__.py` (0 bytes)
- `apps/evaluate/admin_views.py` (15319 bytes)
- `apps/evaluate/admin.py` (990 bytes)
- `apps/evaluate/api_views.py` (1666 bytes)
- `apps/evaluate/apps.py` (100 bytes)
- `apps/evaluate/eval_services.py` (30642 bytes)
- `apps/evaluate/migrations/__init__.py` (0 bytes)
- `apps/evaluate/migrations/0001_initial.py` (3736 bytes)
- `apps/evaluate/migrations/0002_manualevaluationrun_manualevaluationitem.py` (2581 bytes)
- `apps/evaluate/models.py` (6405 bytes)
- `apps/evaluate/serializers.py` (1134 bytes)
- `apps/evaluate/tests.py` (60 bytes)
- `apps/evaluate/urls.py` (708 bytes)
- `apps/evaluate/views.py` (6841 bytes)
- `apps/my_rag_project/__init__.py` (0 bytes)
- `apps/my_rag_project/admin.py` (3888 bytes)
- `apps/my_rag_project/asgi.py` (414 bytes)
- `apps/my_rag_project/settings/__init__.py` (413 bytes)
- `apps/my_rag_project/settings/base.py` (6998 bytes)
- `apps/my_rag_project/settings/settings_dev.py` (1000 bytes)
- `apps/my_rag_project/settings/settings_prod.py` (3330 bytes)
- `apps/my_rag_project/settings/settings_test.py` (1183 bytes)
- `apps/my_rag_project/urls.py` (1020 bytes)
- `apps/my_rag_project/wsgi.py` (414 bytes)
- `apps/projects/__init__.py` (0 bytes)
- `apps/projects/admin.py` (5491 bytes)
- `apps/projects/api_views.py` (6604 bytes)
- `apps/projects/apps.py` (100 bytes)
- `apps/projects/db_utils.py` (1144 bytes)
- `apps/projects/migrations/__init__.py` (0 bytes)
- `apps/projects/migrations/0001_initial.py` (2858 bytes)
- `apps/projects/migrations/0002_alter_project_storage_type.py` (568 bytes)
- `apps/projects/migrations/0003_project_user.py` (677 bytes)
- `apps/projects/migrations/0004_alter_project_storage_type.py` (587 bytes)
- `apps/projects/migrations/0005_project_chunking_project_custom_prompt_and_more.py` (1666 bytes)
- `apps/projects/migrations/0006_project_use_markitdown_and_more.py` (678 bytes)
- `apps/projects/migrations/0007_alter_project_storage_type.py` (591 bytes)
- `apps/projects/migrations/0008_alter_project_document_parsing.py` (530 bytes)
- `apps/projects/migrations/0009_alter_project_storage_type_and_more.py` (800 bytes)
- `apps/projects/models.py` (5959 bytes)
- `apps/projects/serializers.py` (2113 bytes)
- `apps/projects/tests.py` (60 bytes)
- `apps/projects/urls.py` (411 bytes)
- `apps/projects/views.py` (7663 bytes)
- `google_file_search.py` (14448 bytes)
- `local_project_storage.py` (5506 bytes)
- `local_rag.py` (20550 bytes)
- `optional_dependencies.py` (757 bytes)
- `postgres_rag.py` (12886 bytes)
- `prompt_storage.py` (1969 bytes)
- `rag-api-gunicorn.conf.py` (406 bytes)

---
<!-- FILE: __init__.py -->
## __init__.py

```py
# This file makes the src directory a Python package

```
<!-- END_FILE -->

---
<!-- FILE: apps/__init__.py -->
## apps/__init__.py

```py
"""
Django apps for my_rag project
"""

```
<!-- END_FILE -->

---
<!-- FILE: apps/api/__init__.py -->
## apps/api/__init__.py

```py


```
<!-- END_FILE -->

---
<!-- FILE: apps/api/admin.py -->
## apps/api/admin.py

```py
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

```
<!-- END_FILE -->

---
<!-- FILE: apps/api/api_urls.py -->
## apps/api/api_urls.py

```py
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from src.apps.projects.api_views import ProjectViewSet, SystemPromptViewSet
from src.apps.documents.api_views import DocumentViewSet
from src.apps.documents.views import delete_document
from src.apps.chat.api_views import ChatMessageViewSet
from src.apps.evaluate.api_views import EvaluationDatasetViewSet, EvaluationResultMetricsViewSet, EvaluationRunViewSet
from src.apps.api.api_views import APIKeyViewSet, APIUsageViewSet

# Create router and register viewsets
router = DefaultRouter()

# Register ProjectViewSet with custom lookup regex to accept slashes
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'prompts', SystemPromptViewSet, basename='prompt')
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'messages', ChatMessageViewSet, basename='message')
router.register(r'datasets', EvaluationDatasetViewSet, basename='dataset')
router.register(r'results', EvaluationResultMetricsViewSet, basename='result')
router.register(r'runs', EvaluationRunViewSet, basename='run')
router.register(r'keys', APIKeyViewSet, basename='apikey')
router.register(r'usage', APIUsageViewSet, basename='apiusage')

app_name = 'api'

urlpatterns = [
    # Must come BEFORE router.urls — the DRF router splits 'file.txt' into pk + format suffix
    # so filenames with dots never reach get_object(). This explicit route catches them first.
    re_path(r'^documents/(?P<document_id>[^/]+\.[^/]+)$', delete_document, name='document-delete'),
    path('', include(router.urls)),
]

```
<!-- END_FILE -->

---
<!-- FILE: apps/api/api_views.py -->
## apps/api/api_views.py

```py
"""
DRF API Views for API app
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import APIKey, APIUsage
from .serializers import (
    APIKeySerializer,
    APIKeyCreateSerializer,
    APIKeyListSerializer,
    APIUsageSerializer,
    APIUsageListSerializer,
)


class APIKeyViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for APIKey model
    
    Endpoints:
    - GET /api/keys/ - List user's API keys
    - POST /api/keys/ - Create new API key
    - GET /api/keys/{id}/ - Get API key
    - DELETE /api/keys/{id}/ - Delete API key
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only the authenticated user's API keys"""
        return APIKey.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return APIKeyCreateSerializer
        elif self.action == 'list':
            return APIKeyListSerializer
        return APIKeySerializer
    
    def perform_create(self, serializer):
        """Associate API key with authenticated user"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active API keys for user"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class APIUsageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for APIUsage model (Read-only)
    
    Endpoints:
    - GET /api/usage/ - List API usage
    - GET /api/usage/{id}/ - Get usage entry
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return usage logs for user's API keys"""
        user_keys = APIKey.objects.filter(user=self.request.user)
        return APIUsage.objects.filter(api_key__in=user_keys).order_by('-created_at')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return APIUsageListSerializer
        return APIUsageSerializer
    
    @action(detail=False, methods=['get'])
    def by_key(self, request):
        """Get usage for a specific API key"""
        key_id = request.query_params.get('key_id')
        if not key_id:
            return Response({'error': 'key_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify user owns this key
        key = APIKey.objects.filter(id=key_id, user=request.user).first()
        if not key:
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        
        queryset = APIUsage.objects.filter(api_key=key).order_by('-created_at')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_endpoint(self, request):
        """Get usage for a specific endpoint"""
        endpoint = request.query_params.get('endpoint')
        if not endpoint:
            return Response({'error': 'endpoint required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user_keys = APIKey.objects.filter(user=request.user)
        queryset = self.get_queryset().filter(api_key__in=user_keys, endpoint=endpoint)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get usage summary statistics"""
        from django.db.models import Count, Avg, Q
        from datetime import timedelta
        from django.utils import timezone
        
        user_keys = APIKey.objects.filter(user=request.user)
        usage = APIUsage.objects.filter(api_key__in=user_keys)
        
        last_24h = timezone.now() - timedelta(hours=24)
        
        return Response({
            'total_requests': usage.count(),
            'requests_last_24h': usage.filter(created_at__gte=last_24h).count(),
            'avg_response_time_ms': usage.aggregate(Avg('response_time_ms'))['response_time_ms__avg'] or 0,
            'error_count': usage.filter(status_code__gte=400).count(),
            'by_endpoint': list(usage.values('endpoint').annotate(count=Count('id')).order_by('-count')),
        })

```
<!-- END_FILE -->

---
<!-- FILE: apps/api/apps.py -->
## apps/api/apps.py

```py
from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = 'src.apps.api'

```
<!-- END_FILE -->

---
<!-- FILE: apps/api/migrations/__init__.py -->
## apps/api/migrations/__init__.py

```py


```
<!-- END_FILE -->

---
<!-- FILE: apps/api/migrations/0001_initial.py -->
## apps/api/migrations/0001_initial.py

```py
# Generated by Django 6.0.1 on 2026-01-20 10:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='APIKey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(help_text='The API key (keep secret)', max_length=255, unique=True)),
                ('name', models.CharField(help_text='Human-friendly name for this key', max_length=255)),
                ('is_active', models.BooleanField(default=True, help_text='Whether this key is active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_used_at', models.DateTimeField(blank=True, help_text='Last time this key was used', null=True)),
                ('user', models.ForeignKey(help_text='The user this API key belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='api_keys', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='APIUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('endpoint', models.CharField(help_text='The API endpoint that was called', max_length=255)),
                ('method', models.CharField(help_text='HTTP method (GET, POST, etc.)', max_length=10)),
                ('status_code', models.IntegerField(help_text='HTTP response status code')),
                ('response_time_ms', models.IntegerField(help_text='Response time in milliseconds')),
                ('ip_address', models.GenericIPAddressField(help_text='IP address of the request')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('api_key', models.ForeignKey(help_text='The API key that was used', on_delete=django.db.models.deletion.CASCADE, related_name='usage_logs', to='api.apikey')),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['api_key', '-created_at'], name='api_apiusag_api_key_0fd8c4_idx'), models.Index(fields=['-created_at'], name='api_apiusag_created_677328_idx')],
            },
        ),
    ]

```
<!-- END_FILE -->

---
<!-- FILE: apps/api/models.py -->
## apps/api/models.py

```py
"""
API models for managing API authentication and usage
"""

import secrets
from django.db import models
from django.contrib.auth.models import User


class APIKey(models.Model):
    """
    API key for programmatic access to the API.
    Replaces HTTP Basic Auth for better token management.
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='api_keys',
        help_text="The user this API key belongs to"
    )
    
    key = models.CharField(
        max_length=255,
        unique=True,
        help_text="The API key (keep secret)"
    )
    
    name = models.CharField(
        max_length=255,
        help_text="Human-friendly name for this key"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this key is active"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time this key was used"
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"
    
    @staticmethod
    def generate_key():
        """Generate a secure random API key"""
        return secrets.token_urlsafe(32)


class APIUsage(models.Model):
    """
    Tracks API usage for monitoring and billing purposes.
    """
api_key=***REDACTED***
        APIKey,
        on_delete=models.CASCADE,
        related_name='usage_logs',
        help_text="The API key that was used"
    )
    
    endpoint = models.CharField(
        max_length=255,
        help_text="The API endpoint that was called"
    )
    
    method = models.CharField(
        max_length=10,
        help_text="HTTP method (GET, POST, etc.)"
    )
    
    status_code = models.IntegerField(
        help_text="HTTP response status code"
    )
    
    response_time_ms = models.IntegerField(
        help_text="Response time in milliseconds"
    )
    
    ip_address = models.GenericIPAddressField(
        help_text="IP address of the request"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['api_key', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code}"

```
<!-- END_FILE -->

---
<!-- FILE: apps/api/serializers.py -->
## apps/api/serializers.py

```py
"""
Serializers for API app
"""

from rest_framework import serializers
from .models import APIKey, APIUsage


class APIKeySerializer(serializers.ModelSerializer):
    """Serializer for APIKey model"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = APIKey
        fields = [
            'id', 'user', 'user_username', 'key', 'name',
            'is_active', 'created_at', 'last_used_at'
        ]
        read_only_fields = ['key', 'created_at', 'last_used_at']


class APIKeyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating API keys"""
    key = serializers.CharField(read_only=True)
    
    class Meta:
        model = APIKey
        fields = ['name', 'is_active', 'key']
    
    def create(self, validated_data):
        """Create API key with generated token"""
        validated_data['key'] = APIKey.generate_key()
        return super().create(validated_data)


class APIKeyListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing API keys"""
    
    class Meta:
        model = APIKey
        fields = [
            'id', 'name', 'is_active', 'created_at', 'last_used_at'
        ]


class APIUsageSerializer(serializers.ModelSerializer):
    """Serializer for APIUsage model"""
    api_key_name = serializers.CharField(source='api_key.name', read_only=True)
    
    class Meta:
        model = APIUsage
        fields = [
            'id', 'api_key', 'api_key_name', 'endpoint', 'method',
            'status_code', 'response_time_ms', 'ip_address', 'created_at'
        ]
        read_only_fields = ['created_at']


class APIUsageListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing API usage"""
    
    class Meta:
        model = APIUsage
        fields = [
            'id', 'endpoint', 'method', 'status_code',
            'response_time_ms', 'created_at'
        ]

```
<!-- END_FILE -->

---
<!-- FILE: apps/api/tests.py -->
## apps/api/tests.py

```py
from django.test import TestCase

# Create your tests here.

```
<!-- END_FILE -->

---
<!-- FILE: apps/api/views.py -->
## apps/api/views.py

```py
from django.shortcuts import render

# Create your views here.

```
<!-- END_FILE -->

---
<!-- FILE: apps/chat/__init__.py -->
## apps/chat/__init__.py

```py


```
<!-- END_FILE -->

---
<!-- FILE: apps/chat/admin_views.py -->
## apps/chat/admin_views.py

```py
"""
Admin views for the chat application, integrated with django-unfold.
"""

from django.views.generic import TemplateView
from unfold.views import UnfoldModelAdminViewMixin
from src.apps.projects.models import Project


class ChatWorkflowView(UnfoldModelAdminViewMixin, TemplateView):
    """
    Custom administration view representing the Chat Workflow dashboard,
    conforming to the django-unfold style guide.
    """

    title = "Chat Workflow"
    permission_required = ()
    template_name = "admin/chat_workflow.html"

    def get_context_data(self, **kwargs) -> dict:
        """
        Add active projects to the template context.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments.

        Returns
        -------
        dict
            The updated context dict containing active projects.
        """
        context = super().get_context_data(**kwargs)
        context["projects"] = Project.objects.filter(is_active=True)
        return context

```
<!-- END_FILE -->

---
<!-- FILE: apps/chat/admin.py -->
## apps/chat/admin.py

```py
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

```
<!-- END_FILE -->

---
<!-- FILE: apps/chat/api_views.py -->
## apps/chat/api_views.py

```py
"""
DRF API Views for chat app
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import ChatMessage
from src.apps.projects.models import Project
from .serializers import (
    ChatMessageSerializer,
    ChatMessageCreateSerializer,
    ChatMessageListSerializer,
    ChatResponseSerializer,
)


class ChatMessageViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for ChatMessage model
    
    Endpoints:
    - GET /api/messages/ - List messages
    - POST /api/messages/ - Create message
    - GET /api/messages/{id}/ - Get message
    """
    queryset = ChatMessage.objects.all()
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return ChatMessageCreateSerializer
        elif self.action == 'list':
            return ChatMessageListSerializer
        return ChatMessageSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new chat message, handling form field mapping"""
        # Map form fields to serializer fields
        data = request.data.copy()
        
        # Convert store_id to project lookup
        store_id = data.get('store_id')
        if store_id:
            project = get_object_or_404(Project, project_id=store_id)
            data['project'] = project.id
        
        # Convert query to content
        query = data.get('query')
        if query:
            data['content'] = query
        
        # Set message type to user
        data['message_type'] = 'user'
        
        # Remove fields not in serializer
        data.pop('store_id', None)
        data.pop('query', None)
        data.pop('system_prompt', None)  # TODO: handle system_prompt storage
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=False, methods=['get'])
    def by_project(self, request):
        """Get messages for a specific project"""
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response({'error': 'project_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset().filter(project_id=project_id).order_by('-created_at')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_session(self, request):
        """Get messages from a specific session"""
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response({'error': 'session_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset().filter(session_id=session_id).order_by('created_at')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_user(self, request):
        """Get messages from authenticated user"""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        queryset = self.get_queryset().filter(user=request.user).order_by('-created_at')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

```
<!-- END_FILE -->

---
<!-- FILE: apps/chat/apps.py -->
## apps/chat/apps.py

```py
from django.apps import AppConfig


class ChatConfig(AppConfig):
    name = 'src.apps.chat'

```
<!-- END_FILE -->

---
<!-- FILE: apps/chat/migrations/__init__.py -->
## apps/chat/migrations/__init__.py

```py


```
<!-- END_FILE -->

---
<!-- FILE: apps/chat/migrations/0001_initial.py -->
## apps/chat/migrations/0001_initial.py

```py
# Generated by Django 6.0.1 on 2026-01-20 10:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('projects', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_type', models.CharField(choices=[('user', 'User Message'), ('assistant', 'Assistant Response')], default='user', help_text='Type of message (user or assistant)', max_length=20)),
                ('content', models.TextField(help_text='The actual message content')),
                ('response_html', models.TextField(blank=True, help_text='HTML-formatted response (markdown rendered)')),
                ('context_documents', models.JSONField(blank=True, default=list, help_text='List of documents used as context for this response')),
                ('system_prompt_used', models.TextField(blank=True, help_text='The system prompt that was used for this message')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('session_id', models.CharField(blank=True, help_text='Session identifier for grouping conversations', max_length=100)),
                ('project', models.ForeignKey(help_text='The project this chat is for', on_delete=django.db.models.deletion.CASCADE, related_name='chat_messages', to='projects.project')),
                ('user', models.ForeignKey(blank=True, help_text='The user who sent this message', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='chat_messages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['project', '-created_at'], name='chat_chatme_project_b13469_idx'), models.Index(fields=['session_id', '-created_at'], name='chat_chatme_session_ff25f5_idx'), models.Index(fields=['message_type'], name='chat_chatme_message_1f44ae_idx')],
            },
        ),
    ]

```
<!-- END_FILE -->

---
<!-- FILE: apps/chat/models.py -->
## apps/chat/models.py

```py
"""
Chat models for managing conversation history
"""

from django.db import models
from django.contrib.auth.models import User
from src.apps.projects.models import Project


class ChatMessage(models.Model):
    """
    Represents a message in a chat conversation.
    Tracks both user queries and bot responses along with context.
    """
    
    MESSAGE_TYPES = [
        ('user', 'User Message'),
        ('assistant', 'Assistant Response'),
    ]
    
    # Relationships
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='chat_messages',
        help_text="The project this chat is for"
    )
    
    # Optional user association (if using Django auth)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chat_messages',
        help_text="The user who sent this message"
    )
    
    # Message content
    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPES,
        default='user',
        help_text="Type of message (user or assistant)"
    )
    
    content = models.TextField(
        help_text="The actual message content"
    )
    
    # Response content (for assistant messages)
    response_html = models.TextField(
        blank=True,
        help_text="HTML-formatted response (markdown rendered)"
    )
    
    # Context and metadata
    context_documents = models.JSONField(
        default=list,
        blank=True,
        help_text="List of documents used as context for this response"
    )
    
    system_prompt_used = models.TextField(
        blank=True,
        help_text="The system prompt that was used for this message"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Session tracking (optional)
    session_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Session identifier for grouping conversations"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', '-created_at']),
            models.Index(fields=['session_id', '-created_at']),
            models.Index(fields=['message_type']),
        ]
    
    def __str__(self):
        preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f"{self.get_message_type_display()}: {preview}"

```
<!-- END_FILE -->

---
<!-- FILE: apps/chat/pages.py -->
## apps/chat/pages.py

```py
"""
Page views for template rendering
"""

from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required


@login_required
@require_http_methods(["GET"])
def index(request):
    """Home page - redirects to unfold dashboard"""
    return redirect('/rag/dashboard/')


@login_required
@require_http_methods(["GET"])
def admin_page(request):
    """Admin dashboard - redirects to unfold dashboard"""
    return redirect('/rag/dashboard/')


@login_required
@require_http_methods(["GET"])
def chat_page(request):
    """Chat interface - redirects to unfold chat panel"""
    return redirect('/rag/dashboard/chat/')


@login_required
@require_http_methods(["GET"])
def evaluate_page(request):
    """Redirect to evaluation dashboard panel"""
    return redirect('/rag/dashboard/evaluate/')


```
<!-- END_FILE -->

---
<!-- FILE: apps/chat/serializers.py -->
## apps/chat/serializers.py

```py
"""
Serializers for chat app
"""

from rest_framework import serializers
from .models import ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for ChatMessage model"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'project', 'user', 'user_username', 'message_type',
            'content', 'response_html', 'context_documents',
            'system_prompt_used', 'session_id', 'created_at'
        ]
        read_only_fields = ['created_at', 'response_html']


class ChatMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating chat messages"""
    
    class Meta:
        model = ChatMessage
        fields = ['project', 'message_type', 'content', 'session_id']


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat API responses"""
    user_message = serializers.CharField()
    bot_response = serializers.CharField()
    bot_response_html = serializers.CharField()


class ChatMessageListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing chat messages"""
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'message_type', 'content', 'created_at', 'session_id'
        ]

```
<!-- END_FILE -->

---
<!-- FILE: apps/chat/tests.py -->
## apps/chat/tests.py

```py
from django.test import TestCase

# Create your tests here.

```
<!-- END_FILE -->

---
<!-- FILE: apps/chat/urls.py -->
## apps/chat/urls.py

```py
"""
URL routing for chat app (pages only)
"""

from django.urls import path
from . import pages, views

app_name = 'chat'

urlpatterns = [
    path('', pages.index, name='index'),
    path('dashboard/', pages.admin_page, name='admin'),
    path('chat/', pages.chat_page, name='chat_page'),
    path('api/chat/', views.chat, name='chat_api'),
    path('evaluate/', pages.evaluate_page, name='evaluate_page'),
    path('submit/', views.chat_submit, name='submit'),
    # API endpoints are registered in apps/api/api_urls.py
]

```
<!-- END_FILE -->

---
<!-- FILE: apps/chat/views.py -->
## apps/chat/views.py

```py
"""
Chat views for handling conversations
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.utils.html import escape
import markdown
import sys
import os
import json

from src.local_project_storage import get_local_project_storage
from src.optional_dependencies import LazyModuleProxy
from src.prompt_storage import get_prompt_storage

from .models import ChatMessage
from src.apps.projects.models import Project, SystemPrompt


gfs = LazyModuleProxy(
    "src.google_file_search",
    "Google File Search dependencies are not installed in this environment.",
)


def get_rag_engine(*args, **kwargs):
    from src.local_rag import get_rag_engine as local_get_rag_engine

    return local_get_rag_engine(*args, **kwargs)


def _user_can_access_project(project: Project | None, user) -> bool:
    """Return whether the current user can access the given project."""
    if not project or project.user_id is None:
        return True

    return bool(getattr(user, 'is_authenticated', False) and user.id == project.user_id)


def _get_project_system_prompt(project: Project | None, store_id: str) -> str:
    """Return the persisted system prompt for the given project/store."""
    if project and project.storage_type == 'postgres':
        prompt = SystemPrompt.objects.filter(project=project).values_list('content', flat=True).first()
        return prompt or ''

    prompt_storage = get_prompt_storage()
    return prompt_storage.get_prompt(store_id)


def _extract_source_documents(source_nodes) -> list[str]:
    """Return a deduplicated list of document names from engine source metadata."""
    document_names: list[str] = []

    for source in source_nodes or []:
        if isinstance(source, dict):
            document_name = (
                source.get('document') 
                or source.get('name') 
                or source.get('id') 
                or source.get('file_name')
            )
        else:
            document_name = str(source) if source else ''

        if document_name and document_name not in document_names:
            document_names.append(str(document_name))

    return document_names





@require_http_methods(["POST"])
@csrf_exempt
def chat(request):
    """Handle chat messages and generate responses"""
    # Programmatic fallback for Basic Authentication
    if not getattr(request.user, 'is_authenticated', False) and 'HTTP_AUTHORIZATION' in request.META:
        import base64
        from django.contrib.auth import authenticate
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Basic '):
            try:
                encoded_credentials = auth_header.split(' ', 1)[1]
                decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
                username, password = decoded_credentials.split(':', 1)
                user = authenticate(username=username, password=password)
                if user is not None:
                    request.user = user
            except Exception:
                pass

    try:
        data = json.loads(request.body)
        store_id = data.get('store_id')
        query = data.get('query')
        system_prompt = data.get('system_prompt', '')
        
        if not store_id or not query:
            return JsonResponse({'error': 'Missing store_id or query'}, status=400)

        # Look up project for storage type
        project = Project.objects.filter(project_id=store_id).first()

        if not _user_can_access_project(project, request.user):
            return JsonResponse({'error': 'Forbidden'}, status=403)
        
        # Get prompt if not provided
        if not system_prompt:
            system_prompt = _get_project_system_prompt(project, store_id)
        
        # Query the appropriate backend
        if store_id.startswith('local_'):
            rag_engine = get_rag_engine(store_id)
            bot_response = rag_engine.query(query, system_prompt=system_prompt)
            source_documents = _extract_source_documents(bot_response.get('source_nodes', [])) if isinstance(bot_response, dict) else []
            if isinstance(bot_response, dict):
                bot_response = bot_response.get('response', 'Error generating response.')
        elif store_id.startswith('rag_') or store_id.startswith('postgres_'):
            from llama_index.core import VectorStoreIndex, Settings
            from llama_index.embeddings.google import GeminiEmbedding
            from llama_index.llms.google_genai import GoogleGenAI
            from src.apps.documents.services import get_vector_store
            import os
            
            vector_store = get_vector_store(store_id)
            embed_model = GeminiEmbedding(
                model_name="models/gemini-embedding-001",
api_key=***REDACTED***
            )
            llm = GoogleGenAI(
                model="gemini-2.5-flash-lite",
api_key=***REDACTED***
            )
            from llama_index.core.embeddings import BaseEmbedding
            from llama_index.core.llms import LLM
            if isinstance(embed_model, BaseEmbedding):
                Settings.embed_model = embed_model
            if isinstance(llm, LLM):
                Settings.llm = llm
            
            index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)
            query_engine = index.as_query_engine(llm=llm)
            
            prompt = system_prompt or "You are a helpful assistant."
            response = query_engine.query(f"System Context: {prompt}\n\nQuery: {query}")
            bot_response = str(response)
            source_documents = []
            if hasattr(response, 'source_nodes'):
                source_documents = _extract_source_documents([node.node.metadata for node in response.source_nodes])
        else:
            google_store_id = project.external_store_id if project and project.external_store_id else store_id
            bot_response = gfs.ask_store_question(
                google_store_id,
                query,
                system_prompt=system_prompt
            )
            source_documents = []
        
        # Convert markdown to HTML
        bot_response_html = markdown.markdown(bot_response)
        
        # Store in database if user is authenticated
        if request.user.is_authenticated:
            ChatMessage.objects.create(
                project=project,
                user=request.user,
                message_type='user',
                content=query
            )
            ChatMessage.objects.create(
                project=project,
                user=request.user,
                message_type='assistant',
                content=bot_response,
                response_html=bot_response_html
            )
        
        return JsonResponse({
            'user_message': query,
            'bot_response': bot_response,
            'bot_response_html': bot_response_html,
            'source_documents': source_documents,
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def chat_submit(request):
    """
    Handle HTMX/form chat submissions and return rendered HTML partials.
    Supports local, postgres, and google-backed projects.
    """
    # Standard POST or JSON extraction
    if request.content_type == "application/json":
        try:
            data = json.loads(request.body)
        except Exception:
            data = {}
    else:
        data = request.POST

    store_id = data.get("store_id")
    query = data.get("query")
    system_prompt = data.get("system_prompt", "")

    if not store_id or not query:
        from django.http import HttpResponse
        return HttpResponse("Missing store_id or query", status=400)

    # Look up project
    project = Project.objects.filter(project_id=store_id).first()

    if not _user_can_access_project(project, request.user):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Forbidden")

    # Get prompt if not provided
    if not system_prompt:
        system_prompt = _get_project_system_prompt(project, store_id)

    # Query the appropriate backend
    try:
        if store_id.startswith("local_"):
            rag_engine = get_rag_engine(store_id)
            bot_response = rag_engine.query(query, system_prompt=system_prompt)
            source_documents = _extract_source_documents(bot_response.get("source_nodes", [])) if isinstance(bot_response, dict) else []
            if isinstance(bot_response, dict):
                bot_response = bot_response.get("response", "Error generating response.")
        elif store_id.startswith("rag_") or store_id.startswith("postgres_"):
            from llama_index.core import VectorStoreIndex, Settings
            from llama_index.embeddings.google import GeminiEmbedding
            from llama_index.llms.google_genai import GoogleGenAI
            from src.apps.documents.services import get_vector_store
            import os
            
            vector_store = get_vector_store(store_id)
            embed_model = GeminiEmbedding(
                model_name="models/gemini-embedding-001",
api_key=***REDACTED***
            )
            llm = GoogleGenAI(
                model="gemini-2.5-flash-lite",
api_key=***REDACTED***
            )
            from llama_index.core.embeddings import BaseEmbedding
            from llama_index.core.llms import LLM
            if isinstance(embed_model, BaseEmbedding):
                Settings.embed_model = embed_model
            if isinstance(llm, LLM):
                Settings.llm = llm
            
            index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)
            query_engine = index.as_query_engine(llm=llm)
            
            prompt = system_prompt or "You are a helpful assistant."
            response = query_engine.query(f"System Context: {prompt}\n\nQuery: {query}")
            bot_response = str(response)
            source_documents = []
            if hasattr(response, "source_nodes"):
                source_documents = _extract_source_documents([node.node.metadata for node in response.source_nodes])
        else:
            google_store_id = project.external_store_id if project and project.external_store_id else store_id
            bot_response = gfs.ask_store_question(
                google_store_id,
                query,
                system_prompt=system_prompt
            )
            source_documents = []

        # Convert markdown to HTML
        bot_response_html = markdown.markdown(bot_response)

        # Append source attribution if we have sources
        if source_documents:
            sources_html = f'<div class="mt-2 text-xs text-gray-500"><strong>Sources:</strong> {", ".join(source_documents)}</div>'
            bot_response_html += sources_html

        # Store in database if user is authenticated
        if request.user.is_authenticated:
            ChatMessage.objects.create(
                project=project,
                user=request.user,
                message_type="user",
                content=query
            )
            ChatMessage.objects.create(
                project=project,
                user=request.user,
                message_type="assistant",
                content=bot_response,
                response_html=bot_response_html
            )

        from django.http import HttpResponse
        
        user_html = render_to_string("partials/chat_message.html", {
            "sender": "user",
            "message": escape(query),
        })
        
        bot_html = render_to_string("partials/chat_message.html", {
            "sender": "bot",
            "message": bot_response_html,
        })

        return HttpResponse(user_html + bot_html)

    except Exception as e:
        import traceback
        traceback.print_exc()
        from django.http import HttpResponse
        return HttpResponse(f"Error: {str(e)}", status=500)


```
<!-- END_FILE -->

---
<!-- FILE: apps/documents/__init__.py -->
## apps/documents/__init__.py

```py


```
<!-- END_FILE -->

---
<!-- FILE: apps/documents/admin.py -->
## apps/documents/admin.py

```py
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

```
<!-- END_FILE -->

---
<!-- FILE: apps/documents/api_views.py -->
## apps/documents/api_views.py

```py
"""
DRF API Views for documents app
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Document
from .serializers import (
    DocumentSerializer,
    DocumentCreateSerializer,
    DocumentUpdateSerializer,
    DocumentListSerializer,
)
from src.apps.projects.models import Project


class DocumentViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Document model
    
    Endpoints:
    - GET /api/documents/ - List all documents
    - POST /api/documents/ - Create document
    - GET /api/documents/{id}/ - Get document
    - PUT /api/documents/{id}/ - Update document
    - DELETE /api/documents/{id}/ - Delete document
    """
    queryset = Document.objects.all()
    permission_classes = [AllowAny]
    lookup_field = 'pk'
    lookup_value_regex = '.+'  # Allow any character including dots
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return DocumentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return DocumentUpdateSerializer
        elif self.action == 'list':
            return DocumentListSerializer
        return DocumentSerializer
    
    def get_object(self):
        """Override to support lookup by document_name or id.
        DRF router splits 'file.txt' into pk='file' + format='txt', so we reconstruct it.
        """
        pk = self.kwargs.get('pk')
        format_suffix = self.kwargs.get('format')
        
        # Reconstruct the full filename if format suffix was extracted by the router
        if format_suffix:
            lookup_value = f"{pk}.{format_suffix}"
        else:
            lookup_value = pk
        
        queryset = self.filter_queryset(self.get_queryset())
        
        # Try lookup by ID first (if it's numeric)
        if str(lookup_value).isdigit():
            try:
                return queryset.get(id=int(lookup_value))
            except Document.DoesNotExist:
                pass
        
        # Try lookup by exact document_name
        try:
            return queryset.get(document_name=lookup_value)
        except Document.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound(f"Document '{lookup_value}' not found")
    
    def destroy(self, request, *args, **kwargs):
        """Override destroy to also delete from RAG index"""
        document = self.get_object()
        store_id = request.query_params.get('store_id')
        
        # For RAG projects, also delete from index
        if store_id and (store_id.startswith('rag_') or store_id.startswith('postgres_')):
            try:
                from src.postgres_rag import PostgresRAGEngine
                rag_engine = PostgresRAGEngine(store_id)
                # Delete from txtai index if needed
                # Note: txtai doesn't have a built-in delete_by_id, 
                # so we just remove from DB
            except Exception as e:
                print(f"⚠️ Warning: Could not delete from postgres index: {e}")
        
        # Delete from Django DB
        self.perform_destroy(document)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
    @action(detail=False, methods=['get'])
    def by_project(self, request):
        """Get documents for a specific project"""
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response({'error': 'project_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        from django.db.models import Q
        if str(project_id).isdigit():
            queryset = self.get_queryset().filter(Q(project_id=int(project_id)) | Q(project__project_id=project_id))
        else:
            queryset = self.get_queryset().filter(project__project_id=project_id)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_state(self, request):
        """Get documents by indexing state"""
        doc_state = request.query_params.get('state')
        if not doc_state:
            return Response({'error': 'state required'}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset().filter(state=doc_state)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def indexed(self, request):
        """Get all indexed documents"""
        queryset = self.get_queryset().filter(state='INDEXED')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def failed(self, request):
        """Get all failed documents"""
        queryset = self.get_queryset().filter(state='FAILED')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

```
<!-- END_FILE -->

---
<!-- FILE: apps/documents/apps.py -->
## apps/documents/apps.py

```py
from django.apps import AppConfig


class DocumentsConfig(AppConfig):
    name = 'src.apps.documents'

```
<!-- END_FILE -->

---
<!-- FILE: apps/documents/migrations/__init__.py -->
## apps/documents/migrations/__init__.py

```py


```
<!-- END_FILE -->

---
<!-- FILE: apps/documents/migrations/0001_initial.py -->
## apps/documents/migrations/0001_initial.py

```py
# Generated by Django 6.0.1 on 2026-01-20 10:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_name', models.CharField(help_text='Name/path of the document', max_length=500)),
                ('display_name', models.CharField(blank=True, help_text='Human-friendly display name', max_length=500)),
                ('external_document_id', models.CharField(blank=True, help_text='ID from external service (e.g., Google Document ID)', max_length=255, null=True)),
                ('mime_type', models.CharField(blank=True, default='application/octet-stream', help_text='MIME type of the document', max_length=100)),
                ('file_size', models.BigIntegerField(blank=True, help_text='Size of the file in bytes', null=True)),
                ('state', models.CharField(choices=[('PENDING', 'Pending Indexing'), ('INDEXING', 'Currently Indexing'), ('INDEXED', 'Successfully Indexed'), ('FAILED', 'Indexing Failed')], default='PENDING', help_text='Current indexing status', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('indexed_at', models.DateTimeField(blank=True, help_text='When the document was successfully indexed', null=True)),
                ('error_message', models.TextField(blank=True, help_text='Error message if indexing failed')),
                ('project', models.ForeignKey(help_text='The project this document belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='projects.project')),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['project', 'state'], name='documents_d_project_5e312d_idx'), models.Index(fields=['state'], name='documents_d_state_df10a5_idx'), models.Index(fields=['-created_at'], name='documents_d_created_71dced_idx')],
                'unique_together': {('project', 'document_name')},
            },
        ),
    ]

```
<!-- END_FILE -->

---
<!-- FILE: apps/documents/migrations/0002_document_expiration_date_document_is_expired_checked.py -->
## apps/documents/migrations/0002_document_expiration_date_document_is_expired_checked.py

```py
# Generated by Django 6.0.1 on 2026-06-02 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='expiration_date',
            field=models.DateTimeField(blank=True, help_text='When this document expires', null=True),
        ),
        migrations.AddField(
            model_name='document',
            name='is_expired_checked',
            field=models.BooleanField(default=False, help_text='Whether this document has expiration tracking enabled'),
        ),
    ]

```
<!-- END_FILE -->

---
<!-- FILE: apps/documents/models.py -->
## apps/documents/models.py

```py
"""
Document models for managing indexed documents
"""

from django.db import models
from src.apps.projects.models import Project


class Document(models.Model):
    """
    Represents a document indexed within a project.
    Tracks document metadata and indexing status.
    """
    
    INDEX_STATES = [
        ('PENDING', 'Pending Indexing'),
        ('INDEXING', 'Currently Indexing'),
        ('INDEXED', 'Successfully Indexed'),
        ('FAILED', 'Indexing Failed'),
    ]
    
    # Relationships
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='documents',
        help_text="The project this document belongs to"
    )
    
    # Document info
    document_name = models.CharField(
        max_length=500,
        help_text="Name/path of the document"
    )
    
    display_name = models.CharField(
        max_length=500,
        blank=True,
        help_text="Human-friendly display name"
    )
    
    # External reference
    external_document_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="ID from external service (e.g., Google Document ID)"
    )
    
    # File metadata
    mime_type = models.CharField(
        max_length=100,
        blank=True,
        default='application/octet-stream',
        help_text="MIME type of the document"
    )
    
    file_size = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Size of the file in bytes"
    )
    
    # Indexing status
    state = models.CharField(
        max_length=20,
        choices=INDEX_STATES,
        default='PENDING',
        help_text="Current indexing status"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    indexed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the document was successfully indexed"
    )
    
    # Error tracking
    error_message = models.TextField(
        blank=True,
        help_text="Error message if indexing failed"
    )
    
    # Expiration tracking
    is_expired_checked = models.BooleanField(
        default=False,
        help_text="Whether this document has expiration tracking enabled"
    )
    expiration_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this document expires"
    )
    
    class Meta:
        ordering = ['-created_at']
        unique_together = [['project', 'document_name']]
        indexes = [
            models.Index(fields=['project', 'state']),
            models.Index(fields=['state']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.display_name or self.document_name} ({self.project.display_name})"

```
<!-- END_FILE -->

---
<!-- FILE: apps/documents/serializers.py -->
## apps/documents/serializers.py

```py
"""
Serializers for documents app
"""

from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for Document model"""
    
    class Meta:
        model = Document
        fields = [
            'id', 'project', 'document_name', 'display_name',
            'external_document_id', 'mime_type', 'file_size',
            'state', 'indexed_at', 'error_message', 'created_at'
        ]
        read_only_fields = ['created_at', 'indexed_at']


class DocumentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/uploading documents"""
    
    class Meta:
        model = Document
        fields = ['project', 'document_name', 'display_name', 'mime_type', 'file_size']
    
    def validate_state(self, value):
        """Document starts in PENDING state"""
        return 'PENDING'


class DocumentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating document metadata"""
    
    class Meta:
        model = Document
        fields = ['display_name', 'state', 'error_message']


class DocumentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing documents"""
    
    class Meta:
        model = Document
        fields = ['id', 'document_name', 'display_name', 'state', 'created_at']

```
<!-- END_FILE -->

---
<!-- FILE: apps/documents/services.py -->
## apps/documents/services.py

```py
import os
from django.conf import settings
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.google import GeminiEmbedding

import logging
logger = logging.getLogger(__name__)

def get_safe_table_name(project_id: str) -> str:
    """
    Return a postgres-safe table name under 48 characters to keep "data_" + table name
    and automatically generated index names (e.g. {table_name}_idx_1) under 63 bytes.
    Uses MD5 hash to ensure uniqueness while preserving a readable prefix.
    """
    base_name = f"rag_project_{project_id}"
    if len(base_name) > 48:
        import hashlib
        hash_suffix = hashlib.md5(project_id.encode('utf-8')).hexdigest()[:8]
        max_id_len = 48 - 12 - 9  # 48 - len("rag_project_") - len("_hash")
        truncated_id = project_id[:max_id_len]
        return f"rag_project_{truncated_id}_{hash_suffix}"
    return base_name

class LlamaIndexIngestionPipeline:
    def __init__(self, project_id):
        self.project_id = project_id
        # Configure gemini-embedding-001
        self.embed_model = GeminiEmbedding(
            model_name="models/gemini-embedding-001",
api_key=***REDACTED***
        )
        
    def index_document(self, file_path, original_filename: str = None):
        # Read the document
        documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
        
        if original_filename:
            for doc in documents:
                doc.metadata['file_name'] = original_filename
                doc.metadata['file_path'] = original_filename
        
        config = getattr(settings, "REMOTE_POSTGRES_CONFIG", {})
        
        table_name = get_safe_table_name(self.project_id)
        
        # Configure Vector Store
        vector_store = PGVectorStore.from_params(
            database=config.get("NAME", "postgres"),
            host=config.get("HOST", "localhost"),
            port=config.get("PORT", "5432"),
            user=config.get("USER", "postgres"),
password=***REDACTED***
            table_name=table_name,
            embed_dim=3072 # Standard for gemini-embedding-001
        )
        
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # Create Index
        index = VectorStoreIndex.from_documents(
            documents, 
            storage_context=storage_context,
            embed_model=self.embed_model
        )
        return index

def get_vector_store(project_id):
    config = getattr(settings, "REMOTE_POSTGRES_CONFIG", {})
    table_name = get_safe_table_name(project_id)
    return PGVectorStore.from_params(
        database=config.get("NAME", "postgres"),
        host=config.get("HOST", "localhost"),
        port=config.get("PORT", "5432"),
        user=config.get("USER", "postgres"),
password=***REDACTED***
        table_name=table_name,
        embed_dim=3072
    )


def check_structural_quality(filepath: str) -> None:
    """
    Evaluate structural quality of extracted text using gemini-2.5-flash-lite.
    Raises ValueError if score is 7 or lower.
    """
    from llama_index.core import SimpleDirectoryReader
    from google import genai
    from google.genai import types
    import json

    # Extract first 1000 characters from file
    docs = SimpleDirectoryReader(input_files=[filepath]).load_data()
    full_text = "\n".join([d.text for d in docs])
    snippet = full_text[:1000]

    # Call Gemini to score quality
api_key=***REDACTED***
    client = genai.Client(api_key=api_key)

    prompt = f"""You are a Data Quality Inspector. Review the following text snippet extracted from a document. 
Determine if the text structure is intact and readable, or if the layout parser failed.

Look for these failure signs:
- Words mashed together without spaces (e.g., "TheCompanyReport2024")
- Words that do not have any meaning 
- Shattered sentences from misread columns (e.g., "Revenue $5M Introduction to")
- Excessive raw font artifact codes (e.g., "CID:12 CID:44")

Score the text quality from 1 (Complete Garbage) to 10 (Perfectly Readable).
Respond ONLY with a JSON object in this format:
{{"score": int, "reason": "string"}}

Text snippet:
\"\"\"{snippet}\"\"\""""

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1
        ),
    )

    try:
        res_data = json.loads(response.text)
        score = int(res_data.get("score", 10))
        reason = res_data.get("reason", "")
        # Log to the server terminal clearly
        logger.info(f"📊 [QUALITY GATE] Document: {filepath} | Score: {score}/10 | Reason: {reason}")
    except Exception as parse_err:
        # Fallback if JSON parsing fails
        score = 10
        reason = f"Fallback due to parsing error: {str(parse_err)}"

    if score <= 7:
        raise ValueError(f"Extraction quality too low (Score: {score}/10). Reason: {reason}")


```
<!-- END_FILE -->

---
<!-- FILE: apps/documents/tests.py -->
## apps/documents/tests.py

```py
from django.test import TestCase

# Create your tests here.

```
<!-- END_FILE -->

---
<!-- FILE: apps/documents/urls.py -->
## apps/documents/urls.py

```py
"""
URL routing for documents app
"""
from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('documents/<str:store_id>/', views.list_documents, name='list'),
    path('documents/<str:store_id>/upload/', views.upload_document, name='upload'),
]

```
<!-- END_FILE -->

---
<!-- FILE: apps/documents/views.py -->
## apps/documents/views.py

```py
"""
Document views for managing indexed documents
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.utils.text import get_valid_filename
import sys
import os
import tempfile

# Add src to path
from src.local_project_storage import get_local_project_storage
from src.optional_dependencies import LazyModuleProxy
from urllib.parse import unquote

from .models import Document
from src.apps.projects.models import Project
from src.apps.projects.db_utils import test_postgres_connection
from src.postgres_rag import EmbeddingRateLimitError




SUPPORTED_TEXT_FILE_EXTENSIONS = {'.pdf', '.txt', '.md'}

gfs = LazyModuleProxy(
    "src.google_file_search",
    "Google File Search dependencies are not installed in this environment.",
)


def get_rag_engine(*args, **kwargs):
    from src.local_rag import get_rag_engine as local_get_rag_engine

    return local_get_rag_engine(*args, **kwargs)


def _sanitize_uploaded_filename(filename: str) -> str:
    """Return a filesystem-safe upload filename without requiring Werkzeug."""
    normalized_name = filename.replace("\\", "/").split("/")[-1].strip()
    if not normalized_name:
        return "upload"

    sanitized_name = get_valid_filename(normalized_name)
    return sanitized_name or "upload"


def _doc_adapter(doc):
    """Return a dict that matches the interface expected by document templates."""
    from django.utils import timezone
    is_expired = False
    if doc.is_expired_checked and doc.expiration_date:
        is_expired = timezone.now() > doc.expiration_date

    return {
        'name': doc.document_name,
        'display_name': doc.display_name or doc.document_name,
        'mime_type': doc.mime_type,
        'indexed_at': doc.indexed_at,
        'state': type('State', (), {'name': doc.state})(),
        'error_message': getattr(doc, 'error_message', ''),
        'is_expired': is_expired,
    }


@require_http_methods(["GET"])
def list_documents(request, store_id):
    """List documents in a project, returning an HTML partial."""
    doc_type = request.GET.get('type', 'admin')

    # Look up project by project_id in the Django database
    project = Project.objects.filter(project_id=store_id).first()

    if project:
        if project.storage_type == 'google':
            # For Google projects, fetch from the API using external_store_id
            try:
                documents = gfs.list_documents_in_store(project.external_store_id)
            except Exception:
                documents = []
        else:
            # For local projects, use Django ORM
            docs_qs = Document.objects.filter(project=project)
            documents = [_doc_adapter(d) for d in docs_qs]
        
        project_name = project.display_name
        storage_type = project.storage_type
    else:
        # Fallback: project not in DB yet — try legacy local_project_storage
        storage = get_local_project_storage()
        local_projects = storage.list_projects()
        legacy = next((p for p in local_projects if p['id'] == store_id), None)
        if legacy:
            documents = [
                {
                    'name': doc_name,
                    'display_name': doc_name,
                    'mime_type': 'document',
                    'indexed_at': doc_info.get('indexed_at') if isinstance(doc_info, dict) else None,
                    'state': type('State', (), {'name': 'INDEXED'})(),
                }
                for doc_name, doc_info in (
                    ((d, legacy['documents'].get(d)) if isinstance(legacy['documents'], dict) else (d, {}))
                    for d in legacy.get('documents', []) if d
                )
            ]
            project_name = legacy['display_name']
            storage_type = 'local'
        else:
            documents = []
            project_name = store_id
            storage_type = 'unknown'

    if doc_type == 'evaluate':
        return render(request, 'partials/evaluate_document_items.html', {'documents': documents})

    return render(request, 'partials/document_list.html', {
        'documents': documents,
        'store_id': store_id,
        'project_name': project_name,
        'storage_type': storage_type,
        'url_prefix': '/rag',
    })


@require_http_methods(["POST"])
@csrf_exempt
def upload_document(request, store_id):
    """Upload and index a document"""
    storage = get_local_project_storage()
    
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file provided'}, status=400)
    
    file = request.FILES['file']
    if not file or file.name == '':
        return JsonResponse({'error': 'Invalid file'}, status=400)
        
    is_expired_checked = request.POST.get('is_expired') == 'on'
    expiration_date = None
    if is_expired_checked:
        expiration_date_str = request.POST.get('expiration_date')
        if expiration_date_str:
            from django.utils.dateparse import parse_datetime
            from django.utils import timezone
            parsed_dt = parse_datetime(expiration_date_str)
            if parsed_dt:
                if timezone.is_naive(parsed_dt):
                    expiration_date = timezone.make_aware(parsed_dt)
                else:
                    expiration_date = parsed_dt
    
    try:
        filename = _sanitize_uploaded_filename(file.name)
        file_ext = os.path.splitext(filename)[1].lower()

        if (store_id.startswith('rag_') or store_id.startswith('postgres_')) and file_ext not in SUPPORTED_TEXT_FILE_EXTENSIONS:
            return JsonResponse(
                {'error': f'Unsupported file type: {file_ext or "[none]"}. Supported file types are: .pdf, .txt, .md'},
                status=400,
            )
        
        # Save to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            for chunk in file.chunks():
                tmp.write(chunk)
            filepath = tmp.name
        
        try:
            if store_id.startswith('local_'):
                # Local project indexing
                rag_engine = get_rag_engine(store_id)
                success = rag_engine.index_document(filepath, filename)
                
                if success:
                    storage.add_document(store_id, filename)
                else:
                    os.unlink(filepath)
                    return JsonResponse({'error': 'Failed to index document'}, status=500)
            elif store_id.startswith('rag_') or store_id.startswith('postgres_'):
                project = Project.objects.filter(project_id=store_id).first()

                if store_id.startswith('postgres_'):
                    conn_success, conn_error = test_postgres_connection()
                    if not conn_success:
                        error_msg = f"PostgreSQL VPS Connection failed: {conn_error}"
                        if project:
                            Document.objects.update_or_create(
                                project=project,
                                document_name=filename,
                                defaults={
                                    'display_name': filename,
                                    'state': 'FAILED',
                                    'error_message': error_msg,
                                    'indexed_at': None,
                                    'is_expired_checked': is_expired_checked,
                                    'expiration_date': expiration_date,
                                }
                            )
                        docs_qs = Document.objects.filter(project=project)
                        documents = [_doc_adapter(d) for d in docs_qs]
                        return render(request, 'partials/document_items.html', {
                            'documents': documents,
                            'store_id': store_id,
                            'url_prefix': '/rag',
                        })

                # RAG project indexing
                from src.apps.documents.services import LlamaIndexIngestionPipeline
                from django.utils import timezone

                try:
                    # Ingestion Quality Grading Gate
                    if project and project.use_structural_grading:
                        from src.apps.documents.services import check_structural_quality
                        check_structural_quality(filepath)

                    pipeline = LlamaIndexIngestionPipeline(project_id=store_id)
                    index = pipeline.index_document(filepath, original_filename=filename)
                    success = index is not None
                except EmbeddingRateLimitError as exc:
                    if project:
                        Document.objects.update_or_create(
                            project=project,
                            document_name=filename,
                            defaults={
                                'display_name': filename,
                                'state': 'FAILED',
                                'error_message': str(exc),
                                'indexed_at': None,
                                'is_expired_checked': is_expired_checked,
                                'expiration_date': expiration_date,
                            }
                        )
                    return JsonResponse({'error': str(exc)}, status=503)
                except Exception as exc:
                    if project:
                        Document.objects.update_or_create(
                            project=project,
                            document_name=filename,
                            defaults={
                                'display_name': filename,
                                'state': 'FAILED',
                                'error_message': str(exc),
                                'indexed_at': None,
                                'is_expired_checked': is_expired_checked,
                                'expiration_date': expiration_date,
                            }
                        )
                    docs_qs = Document.objects.filter(project=project)
                    documents = [_doc_adapter(d) for d in docs_qs]
                    return render(request, 'partials/document_items.html', {
                        'documents': documents,
                        'store_id': store_id,
                        'url_prefix': '/rag',
                    })
                
                if success:
                    if project:
                        Document.objects.update_or_create(
                            project=project,
                            document_name=filename,
                            defaults={
                                'display_name': filename,
                                'state': 'INDEXED',
                                'error_message': '',
                                'indexed_at': timezone.now(),
                                'is_expired_checked': is_expired_checked,
                                'expiration_date': expiration_date,
                            }
                        )
                else:
                    if project:
                        Document.objects.update_or_create(
                            project=project,
                            document_name=filename,
                            defaults={
                                'display_name': filename,
                                'state': 'FAILED',
                                'error_message': 'Failed to index document in RAG project',
                                'indexed_at': None,
                                'is_expired_checked': is_expired_checked,
                                'expiration_date': expiration_date,
                            }
                        )
                    docs_qs = Document.objects.filter(project=project)
                    documents = [_doc_adapter(d) for d in docs_qs]
                    return render(request, 'partials/document_items.html', {
                        'documents': documents,
                        'store_id': store_id,
                        'url_prefix': '/rag',
                    })
            else:
                # Google store - look up the project to get the external_store_id
                from src.google_file_search import GoogleFileSearchPermissionError

                project = Project.objects.filter(project_id=store_id).first()
                if project and project.external_store_id:
                    # Use the actual Google store ID
                    google_store_id = project.external_store_id
                else:
                    # Fallback to store_id (for backward compatibility)
                    google_store_id = store_id

                try:
                    document_resource_name = gfs.add_document_to_store(google_store_id, filepath)
                except GoogleFileSearchPermissionError as exc:
                    return JsonResponse({'error': str(exc)}, status=403)

                if not document_resource_name:
                    return JsonResponse({'error': 'Failed to upload document to Google File Search store'}, status=502)
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)
        
        # Return updated documents list
        project = Project.objects.filter(project_id=store_id).first()
        if project and project.storage_type == 'google':
            # For Google projects, fetch from API
            documents = gfs.list_documents_in_store(project.external_store_id)
        elif project and project.storage_type == 'postgres':
            # For RAG projects, fetch from Django DB
            docs_qs = Document.objects.filter(project=project)
            documents = [_doc_adapter(d) for d in docs_qs]
        else:
            # For local projects, check local storage first
            local_projects = storage.list_projects()
            proj = next((p for p in local_projects if p['id'] == store_id), None)
            
            if proj:
                documents = [
                    {
                        'name': doc_name,
                        'display_name': doc_name,
                        'mime_type': 'document',
                        'indexed_at': doc_info.get('indexed_at') if isinstance(doc_info, dict) else None,
                        'state': type('State', (), {'name': 'INDEXED'})()
                    }
                    for doc_name, doc_info in (
                        ((d, proj['documents'].get(d)) if isinstance(proj['documents'], dict) else (d, {}))
                        for d in proj.get('documents', []) if d
                    )
                ]
            else:
                documents = []
        
        return render(request, 'partials/document_items.html', {
            'documents': documents,
            'store_id': store_id,
            'url_prefix': '/rag',
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'Upload failed: {str(e)}'}, status=500)


@require_http_methods(["DELETE"])
@csrf_exempt
def delete_document(request, document_id):
    """Delete a document"""
    storage = get_local_project_storage()
    document_id = unquote(document_id)
    # Strip trailing slash if any (from URL matching)
    document_id = document_id.rstrip('/')
    store_id = request.GET.get('store_id')
    
    try:
        if store_id and store_id.startswith('local_'):
            # Local document deletion
            rag_engine = get_rag_engine(store_id)
            success = rag_engine.delete_document(document_id)
            
            if success:
                storage.remove_document(store_id, document_id)
        elif store_id and (store_id.startswith('rag_') or store_id.startswith('postgres_')):
            project = Project.objects.filter(project_id=store_id).first()
            if project:
                from src.postgres_rag import PostgresRAGEngine
                try:
                    rag_engine = PostgresRAGEngine(store_id, require_llm=False)
                    rag_engine.delete_document(document_id)
                except Exception as cleanup_error:
                    print(f"Warning: RAG engine cleanup failed for {document_id}: {cleanup_error}")
                Document.objects.filter(project=project, document_name=document_id).delete()
        else:
            # Google document deletion - look up project to get external_store_id
            project = Project.objects.filter(project_id=store_id).first()
            if project and project.external_store_id:
                google_store_id = project.external_store_id
                gfs.delete_document_from_store(google_store_id, document_id)
            elif '/' in document_id:
                # Fallback: extract store from document_id if it contains the store reference
                parts = document_id.split('/')
                if len(parts) >= 2:
                    store_id_from_doc = parts[1]
                    gfs.delete_document_from_store(store_id_from_doc, document_id)
        
        # Return refreshed document list HTML for HTMX to swap in
        from django.http import HttpResponse
        response = HttpResponse(status=200)
        response['HX-Trigger'] = 'documentListChanged'
        return response
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

```
<!-- END_FILE -->

---
<!-- FILE: apps/evaluate/__init__.py -->
## apps/evaluate/__init__.py

```py


```
<!-- END_FILE -->

---
<!-- FILE: apps/evaluate/admin_views.py -->
## apps/evaluate/admin_views.py

```py
"""
Admin views for the evaluate application, integrated with django-unfold.
"""

import csv
import io
from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from unfold.views import UnfoldModelAdminViewMixin
from src.apps.projects.models import Project
from src.apps.evaluate.models import (
    EvaluationDataset,
    EvaluationRun,
    EvaluationResultMetrics,
    ManualEvaluationRun,
    ManualEvaluationItem,
)
from src.apps.evaluate.eval_services import (
    generate_answer_for_manual_item,
    batch_generate_manual_answers,
)


class EvaluationWorkflowView(UnfoldModelAdminViewMixin, TemplateView):
    """
    Custom administration view representing the Evaluation Workflow dashboard,
    conforming to the django-unfold style guide.
    """

    title = "Evaluation Workflow"
    permission_required = ()
    template_name = "admin/evaluation_workflow.html"

    def get_context_data(self, **kwargs) -> dict:
        """
        Add active projects with their Ragas metrics to the template context.

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments.

        Returns
        -------
        dict
            The updated context dict containing projects_data.
        """
        context = super().get_context_data(**kwargs)
        projects_qs = Project.objects.filter(is_active=True)
        projects_data = []

        for project in projects_qs:
            qa_count = EvaluationDataset.objects.filter(project=project).count()
            latest_run = EvaluationRun.objects.filter(project=project).order_by("-started_at").first()
            
            avg_metrics = {}
            if latest_run and latest_run.status == "SUCCESS":
                metrics = EvaluationResultMetrics.objects.filter(run=latest_run)
                if metrics.exists():
                    avg_metrics = {
                        "recall": sum(m.context_recall or 0 for m in metrics) / metrics.count(),
                        "precision": sum(m.context_precision or 0 for m in metrics) / metrics.count(),
                        "faithfulness": sum(m.faithfulness or 0 for m in metrics) / metrics.count(),
                        "relevancy": sum(m.answer_relevancy or 0 for m in metrics) / metrics.count(),
                    }

            projects_data.append({
                "project": project,
                "qa_count": qa_count,
                "latest_run": latest_run,
                "avg_metrics": avg_metrics
            })

        context["projects"] = projects_qs
        context["projects_data"] = projects_data
        context["url_prefix"] = "/rag"
        return context


@method_decorator(csrf_exempt, name="dispatch")
class QaSetupWorkflowView(UnfoldModelAdminViewMixin, TemplateView):
    """
    Custom administration view representing the Dataset Configuration workspace,
    preserving django-unfold sidebars and main navigation.
    """

    title = "Dataset Configuration"
    permission_required = ()
    template_name = "evaluate/manual_qa.html"

    def get_context_data(self, **kwargs) -> dict:
        """
        Add project and existing dataset items to template context.
        """
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs.get("project_id")
        project = get_object_or_404(Project, project_id=project_id)
        dataset_items = EvaluationDataset.objects.filter(project=project)
        
        context["project"] = project
        context["dataset_items"] = dataset_items
        context["url_prefix"] = "/rag"
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle QA submissions (manual inputs, CSV imports, background generation).
        """
        project_id = self.kwargs.get("project_id")
        project = get_object_or_404(Project, project_id=project_id)
        input_method = request.POST.get("input_method")

        if input_method == "manual":
            # Process manual QAs
            questions = request.POST.getlist("question[]")
            answers = request.POST.getlist("answer[]")

            count = 0
            for q, a in zip(questions, answers):
                if q.strip() and a.strip():
                    EvaluationDataset.objects.create(
                        project=project,
                        document=None,
                        question=q.strip(),
                        ground_truth=a.strip(),
                        source="MANUAL"
                    )
                    count += 1

            if request.headers.get("HX-Request"):
                dataset_items = EvaluationDataset.objects.filter(project=project)
                return render(request, "evaluate/qa_list_partial.html", {
                    "project": project,
                    "dataset_items": dataset_items,
                    "message": f"✓ Successfully saved {count} custom QA items!"
                })
            return redirect(reverse("custom_admin:evaluation-workflow"))

        elif input_method == "csv":
            # Process CSV upload
            csv_file = request.FILES.get("csv_file")
            if not csv_file:
                return HttpResponseBadRequest("No CSV file uploaded.")

            try:
                data_set = csv_file.read().decode("utf-8")
                io_string = io.StringIO(data_set)
                reader = csv.DictReader(io_string)

                # Case-insensitive headers lookup
                headers = {h.lower().strip(): h for h in reader.fieldnames or []}
                q_col = headers.get("question")
                a_col = headers.get("answer")

                if not q_col or not a_col:
                    err_msg = "CSV must contain 'Question' and 'Answer' column headers."
                    if request.headers.get("HX-Request"):
                        return HttpResponse(f'<div class="p-4 bg-red-50 text-red-700 rounded-lg">✗ {err_msg}</div>')
                    return HttpResponseBadRequest(err_msg)

                count = 0
                for row in reader:
                    q_val = row.get(q_col, "").strip()
                    a_val = row.get(a_col, "").strip()
                    if q_val and a_val:
                        EvaluationDataset.objects.create(
                            project=project,
                            document=None,
                            question=q_val,
                            ground_truth=a_val,
                            source="CSV_UPLOAD"
                        )
                        count += 1

                if request.headers.get("HX-Request"):
                    dataset_items = EvaluationDataset.objects.filter(project=project)
                    return render(request, "evaluate/qa_list_partial.html", {
                        "project": project,
                        "dataset_items": dataset_items,
                        "message": f"✓ Imported {count} items from CSV!"
                    })
                return redirect(reverse("custom_admin:evaluation-workflow"))

            except Exception as e:
                err_msg = f"Error parsing CSV: {e}"
                if request.headers.get("HX-Request"):
                    return HttpResponse(f'<div class="p-4 bg-red-50 text-red-700 rounded-lg">✗ {err_msg}</div>')
                return HttpResponseBadRequest(err_msg)

        elif input_method == "generate":
            # Process automatic QA generation
            num_questions = int(request.POST.get("num_questions", 5))
            from src.apps.evaluate.eval_services import start_async_qa_generation
            start_async_qa_generation(project.project_id, num_questions)
            context = {
                "project": project,
                "status": "RUNNING",
                "mode": "qa_generation"
            }
            return render(request, "evaluate/run_progress.html", context)


@method_decorator(csrf_exempt, name="dispatch")
class RunEvaluationView(UnfoldModelAdminViewMixin, View):
    """
    POST endpoint to execute retrieval accuracy evaluations.
    """
    permission_required = ()

    def post(self, request, *args, **kwargs):
        project_id = request.POST.get("project_id")
        document_id = request.POST.get("document_id")
        eval_method = request.POST.get("eval_method")

        if eval_method == "open_rag":
            return HttpResponse('<div class="p-4 bg-yellow-50 text-yellow-700 rounded-md border border-yellow-100">Open RAG Eval is not implemented yet.</div>')

        if not project_id or not document_id:
            return HttpResponse('<div class="p-4 bg-red-50 text-red-700 rounded-md border border-red-100">Error: Missing project or document configuration.</div>')

        project = get_object_or_404(Project, project_id=project_id)

        from src.apps.documents.models import Document
        try:
            document = Document.objects.get(project=project, id=document_id)
        except (Document.DoesNotExist, ValueError):
            document = get_object_or_404(Document, project=project, document_name=document_id)

        from src.apps.evaluate.eval_services import SyntheticQAEvaluator
        evaluator = SyntheticQAEvaluator(project.project_id)
        results = evaluator.evaluate_retrieval_recall(document.document_name)

        context = {
            "results": results,
            "project": project,
            "document": document,
            "url_prefix": "/rag",
        }
        return render(request, "admin/evaluation_scorecard.html", context)


def get_manual_workspace_context(run: ManualEvaluationRun) -> dict:
    """
    Helper function to build summary metrics context for manual evaluation workspace.
    """
    items = run.items.all()
    total_count = items.count()
    green_count = items.filter(rating="GREEN").count()
    orange_count = items.filter(rating="ORANGE").count()
    red_count = items.filter(rating="RED").count()
    unrated_count = items.filter(rating="UNRATED").count()
    pending_gen_count = items.filter(status__in=["PENDING", "FAILED"]).count()

    return {
        "run": run,
        "project": run.project,
        "items": items,
        "total_count": total_count,
        "green_count": green_count,
        "orange_count": orange_count,
        "red_count": red_count,
        "unrated_count": unrated_count,
        "pending_gen_count": pending_gen_count,
        "url_prefix": "/rag",
    }


@method_decorator(csrf_exempt, name="dispatch")
class CreateManualEvaluationRunView(UnfoldModelAdminViewMixin, View):
    """
    POST endpoint to initialize a Manual Evaluation Run from text inputs or CSV file upload.
    """
    permission_required = ()

    def post(self, request, *args, **kwargs):
        project_id = request.POST.get("project_id")
        input_method = request.POST.get("input_method", "manual")

        if not project_id:
            return HttpResponse('<div class="p-4 bg-red-50 text-red-700 rounded-lg">✗ Error: Target project ID is required.</div>', status=400)

        project = get_object_or_404(Project, project_id=project_id)
        questions = []
        source_type = "MANUAL_INPUT"

        if input_method == "manual":
            raw_text = request.POST.get("manual_questions", "")
            questions = [q.strip() for q in raw_text.split("\n") if q.strip()]
        elif input_method == "csv":
            source_type = "CSV_UPLOAD"
            csv_file = request.FILES.get("csv_file")
            if not csv_file:
                return HttpResponse('<div class="p-4 bg-red-50 text-red-700 rounded-lg">✗ No CSV file uploaded.</div>', status=400)

            try:
                data_set = csv_file.read().decode("utf-8")
                io_string = io.StringIO(data_set)
                reader = csv.DictReader(io_string)

                # Look for 'questions' or 'question' header (case-insensitive)
                headers = {h.lower().strip(): h for h in reader.fieldnames or []}
                q_col = headers.get("questions") or headers.get("question")
                if not q_col:
                    return HttpResponse('<div class="p-4 bg-red-50 text-red-700 rounded-lg">✗ CSV must contain a "questions" or "question" column header.</div>', status=400)

                for row in reader:
                    q_val = row.get(q_col, "").strip()
                    if q_val:
                        questions.append(q_val)
            except Exception as exc:
                return HttpResponse(f'<div class="p-4 bg-red-50 text-red-700 rounded-lg">✗ Error parsing CSV: {exc}</div>', status=400)

        if not questions:
            return HttpResponse('<div class="p-4 bg-yellow-50 text-yellow-800 rounded-lg">⚠️ Please provide at least one valid question to evaluate.</div>', status=400)

        run = ManualEvaluationRun.objects.create(
            project=project,
            source_type=source_type
        )
        for q in questions:
            ManualEvaluationItem.objects.create(
                run=run,
                question=q,
                status="PENDING",
                rating="UNRATED"
            )

        context = get_manual_workspace_context(run)
        return render(request, "evaluate/manual_eval_workspace.html", context)


@method_decorator(csrf_exempt, name="dispatch")
class GenerateManualAnswerView(UnfoldModelAdminViewMixin, View):
    """
    POST endpoint to generate RAG answer for a single ManualEvaluationItem.
    """
    permission_required = ()

    def post(self, request, item_id, *args, **kwargs):
        item = get_object_or_404(ManualEvaluationItem, id=item_id)
        generate_answer_for_manual_item(str(item.id))
        context = get_manual_workspace_context(item.run)
        return render(request, "evaluate/manual_eval_workspace.html", context)


@method_decorator(csrf_exempt, name="dispatch")
class BatchGenerateManualAnswersView(UnfoldModelAdminViewMixin, View):
    """
    POST endpoint to generate RAG answers for all pending items in a ManualEvaluationRun.
    """
    permission_required = ()

    def post(self, request, run_id, *args, **kwargs):
        run = get_object_or_404(ManualEvaluationRun, id=run_id)
        batch_generate_manual_answers(str(run.id))
        context = get_manual_workspace_context(run)
        return render(request, "evaluate/manual_eval_workspace.html", context)


@method_decorator(csrf_exempt, name="dispatch")
class RateManualItemView(UnfoldModelAdminViewMixin, View):
    """
    POST endpoint to update the Red/Orange/Green rating of a ManualEvaluationItem.
    """
    permission_required = ()

    def post(self, request, item_id, *args, **kwargs):
        item = get_object_or_404(ManualEvaluationItem, id=item_id)
        rating = request.POST.get("rating", "UNRATED")
        if rating in ["GREEN", "ORANGE", "RED", "UNRATED"]:
            item.rating = rating
            item.save()
        context = get_manual_workspace_context(item.run)
        return render(request, "evaluate/manual_eval_workspace.html", context)




```
<!-- END_FILE -->

---
<!-- FILE: apps/evaluate/admin.py -->
## apps/evaluate/admin.py

```py
from django.contrib import admin
from .models import EvaluationDataset, EvaluationRun, EvaluationResultMetrics


@admin.register(EvaluationDataset)
class EvaluationDatasetAdmin(admin.ModelAdmin):
    list_display = ("question", "project", "document", "source", "created_at")
    list_filter = ("source", "project", "created_at")
    search_fields = ("question", "ground_truth", "project__display_name")
    readonly_fields = ("created_at",)


@admin.register(EvaluationRun)
class EvaluationRunAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "status", "started_at", "completed_at")
    list_filter = ("status", "project", "started_at")
    search_fields = ("id", "project__display_name")
    readonly_fields = ("started_at",)


@admin.register(EvaluationResultMetrics)
class EvaluationResultMetricsAdmin(admin.ModelAdmin):
    list_display = ("run", "dataset_item", "context_recall", "context_precision", "faithfulness", "answer_relevancy")
    list_filter = ("run__project",)

```
<!-- END_FILE -->

---
<!-- FILE: apps/evaluate/api_views.py -->
## apps/evaluate/api_views.py

```py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import EvaluationDataset, EvaluationRun, EvaluationResultMetrics
from .serializers import (
    EvaluationDatasetSerializer,
    EvaluationRunSerializer,
    EvaluationResultMetricsSerializer,
)


class EvaluationDatasetViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for EvaluationDataset model
    """
    queryset = EvaluationDataset.objects.all()
    serializer_class = EvaluationDatasetSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=["get"])
    def by_project(self, request):
        """Get QA items for a specific project"""
        project_id = request.query_params.get("project_id")
        if not project_id:
            return Response({"error": "project_id required"}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset().filter(project_id=project_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class EvaluationRunViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for EvaluationRun model
    """
    queryset = EvaluationRun.objects.all()
    serializer_class = EvaluationRunSerializer
    permission_classes = [AllowAny]


class EvaluationResultMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for EvaluationResultMetrics model (Read-only)
    """
    queryset = EvaluationResultMetrics.objects.all()
    serializer_class = EvaluationResultMetricsSerializer
    permission_classes = [AllowAny]

```
<!-- END_FILE -->

---
<!-- FILE: apps/evaluate/apps.py -->
## apps/evaluate/apps.py

```py
from django.apps import AppConfig


class EvaluateConfig(AppConfig):
    name = 'src.apps.evaluate'

```
<!-- END_FILE -->

---
<!-- FILE: apps/evaluate/eval_services.py -->
## apps/evaluate/eval_services.py

```py
import os
import json
import logging
import threading
import traceback
from django.conf import settings
from django.utils import timezone
from src.apps.evaluate.models import (
    EvaluationDataset,
    EvaluationRun,
    EvaluationResultMetrics,
    ManualEvaluationRun,
    ManualEvaluationItem,
)
from src.apps.projects.models import Project
from src.apps.documents.services import get_vector_store
from llama_index.core import VectorStoreIndex, Settings
from llama_index.embeddings.google import GeminiEmbedding
from llama_index.llms.google_genai import GoogleGenAI

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# Global in-memory dictionary to track async QA generation status
# Mapped: project_id -> {"status": "PENDING"|"RUNNING"|"SUCCESS"|"FAILED", "error": str, "count": int}
QA_GEN_STATUS = {}


class SyntheticQAEvaluator:
    """
    Evaluates RAG retrieval recall percentage using synthetically generated questions.
    """

    def __init__(self, project_id: str):
        self.project_id = project_id
api_key=***REDACTED***
        self.client = genai.Client(api_key=api_key) if api_key else None
        self.embed_model = GeminiEmbedding(
            model_name="models/gemini-embedding-001",
api_key=***REDACTED***
        )
        
        # Configure LlamaIndex globally to use Google GenAI/Gemini instead of OpenAI
        from llama_index.core import Settings
        from llama_index.llms.google_genai import GoogleGenAI
        from llama_index.core.embeddings import BaseEmbedding
        from llama_index.core.llms import LLM
        
        if isinstance(self.embed_model, BaseEmbedding):
            Settings.embed_model = self.embed_model
        
        llm = GoogleGenAI(
            model="gemini-2.5-flash-lite",
api_key=***REDACTED***
        )
        if isinstance(llm, LLM):
            Settings.llm = llm

    def fetch_document_nodes(self, document_name: str) -> list[dict]:
        """
        Fetch up to 5 text nodes associated with the target document from PostgreSQL.

        Parameters
        ----------
        document_name : str
            The name of the target document file.

        Returns
        -------
        list[dict]
            List of nodes containing 'node_id', 'text', and 'metadata'.
        """
        config = getattr(settings, "REMOTE_POSTGRES_CONFIG", {})
        
        from src.apps.documents.services import get_safe_table_name
        safe_table = get_safe_table_name(self.project_id)
        tables_to_try = [
            f"data_{safe_table}",
            safe_table,
            f"data_rag_project_{self.project_id}",
            f"rag_project_{self.project_id}"
        ]

        nodes = []
        conn = None
        try:
            import psycopg2
            conn = psycopg2.connect(
                dbname=config.get("NAME", "postgres"),
                user=config.get("USER", "postgres"),
password=***REDACTED***
                host=config.get("HOST", "localhost"),
                port=int(config.get("PORT", "5432")),
            )
            with conn.cursor() as cur:
                for table in tables_to_try:
                    # Check if table exists
                    cur.execute(f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = '{table}'
                        );
                    """)
                    if cur.fetchone()[0]:
                        # Try metadata_ first, fallback to metadata
                        try:
                            query = f"""
                                SELECT id, text, node_id, metadata_ 
                                FROM {table} 
                                WHERE metadata_->>'file_name' = %s
                                LIMIT 5;
                            """
                            cur.execute(query, (document_name,))
                            rows = cur.fetchall()
                        except Exception:
                            conn.rollback()
                            query = f"""
                                SELECT id, text, node_id, metadata 
                                FROM {table} 
                                WHERE metadata->>'file_name' = %s
                                LIMIT 5;
                            """
                            cur.execute(query, (document_name,))
                            rows = cur.fetchall()

                        for row in rows:
                            nodes.append({
                                "id": row[0],
                                "text": row[1],
                                "node_id": row[2],
                                "metadata": json.loads(row[3]) if isinstance(row[3], str) else row[3],
                            })
                        break
        except Exception as exc:
            logger.warning(f"Error fetching document nodes: {exc}")
        finally:
            if conn:
                conn.close()

        return nodes

    def generate_synthetic_questions(self, node_text: str) -> list[str]:
        """
        Generate 3 synthetic questions that can be answered only using the provided text.

        Parameters
        ----------
        node_text : str
            The text of the document node.

        Returns
        -------
        list[str]
            List of 3 generated questions.
        """
        if not self.client:
            return []

        prompt = f"""Generate 3 questions that can be answered only using this text. Output each question on a new line. Do not add numbering or prefixes.

Text:
{node_text}"""

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.3),
            )
            text_response = response.text or ""
            questions = [q.strip() for q in text_response.split("\n") if q.strip()]
            return questions[:3]
        except Exception as exc:
            logger.warning(f"Error generating questions: {exc}")
            return []

    def evaluate_retrieval_recall(self, document_name: str) -> dict:
        """
        Runs the full Synthetic QA recall evaluation flow for a document.

        Parameters
        ----------
        document_name : str
            The name of the document to evaluate.

        Returns
        -------
        dict
            Evaluation results containing recall score, summary and citation logs.
        """
        nodes = self.fetch_document_nodes(document_name)
        if not nodes:
            return {
                "recall_score": 0.0,
                "total_questions": 0,
                "matches": 0,
                "logs": [],
                "error": "No indexed text nodes found for this document in the PostgreSQL store."
            }

        # Step 2: Generate Questions & Build Ground Truth Map
        ground_truth = []  # list of {"question": str, "expected_node_id": str}
        for node in nodes:
            questions = self.generate_synthetic_questions(node["text"])
            for q in questions:
                ground_truth.append({
                    "question": q,
                    "expected_node_id": node["node_id"]
                })

        if not ground_truth:
            return {
                "recall_score": 0.0,
                "total_questions": 0,
                "matches": 0,
                "logs": [],
                "error": "Failed to generate synthetic questions for the document nodes."
            }

        # Step 3: Configure Vector Store & Load Ingestion Pipeline Index
        vector_store = get_vector_store(self.project_id)
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            embed_model=self.embed_model
        )
        retriever = index.as_retriever(similarity_top_k=5)

        # Step 4: Run Tests & Calculate Recall
        matches = 0
        logs = []

        for item in ground_truth:
            question = item["question"]
            expected_node_id = item["expected_node_id"]

            try:
                retrieved_nodes = retriever.retrieve(question)
                retrieved_ids = [n.node.node_id for n in retrieved_nodes]
                
                success = expected_node_id in retrieved_ids
                if success:
                    matches += 1

                logs.append({
                    "question": question,
                    "expected_node_id": expected_node_id,
                    "success": success,
                    "citations": retrieved_ids,
                })
            except Exception as query_exc:
                logger.warning(f"Error querying question '{question}': {query_exc}")
                logs.append({
                    "question": question,
                    "expected_node_id": expected_node_id,
                    "success": False,
                    "citations": [],
                    "error": str(query_exc),
                })

        total_questions = len(ground_truth)
        recall_score = (matches / total_questions) * 100 if total_questions > 0 else 0.0

        return {
            "recall_score": round(recall_score, 2),
            "total_questions": total_questions,
            "matches": matches,
            "logs": logs,
        }



def _get_postgres_chunks(project_id: str) -> list[dict]:
    """
    Robust function to query the PostgreSQL tables for a project's indexed text chunks.
    Tries both 'data_rag_project_{project_id}' and 'rag_project_{project_id}' tables.

    Only returns chunks whose ``file_name`` metadata matches a Django ``Document``
    record in the ``INDEXED`` state for the given project.  This prevents orphaned
    chunks (e.g. from documents that failed quality checks after partial ingestion)
    from polluting QA generation or evaluation results.
    """
    import psycopg2
    config = getattr(settings, "REMOTE_POSTGRES_CONFIG", {})
    
    db_name = config.get("NAME")
    db_user = config.get("USER")
    db_pass = config.get("PASSWORD")
    db_host = config.get("HOST")
    db_port = config.get("PORT", "5432")
    
    if not all([db_name, db_user, db_pass, db_host]):
        logger.warning("PostgreSQL credentials missing in settings.")
        return []

    # Build an allowlist of document_name values for this project that are INDEXED.
    from src.apps.documents.models import Document
    indexed_names: set[str] = set(
        Document.objects.filter(project__project_id=project_id, state="INDEXED")
        .values_list("document_name", flat=True)
    )
    logger.info(
        "QA chunk filter: project=%s has %d INDEXED document(s): %s",
        project_id,
        len(indexed_names),
        indexed_names,
    )

    from src.apps.documents.services import get_safe_table_name
    safe_table = get_safe_table_name(project_id)
    tables_to_try = [
        f"data_{safe_table}",
        safe_table,
        f"data_rag_project_{project_id}",
        f"rag_project_{project_id}"
    ]
    chunks = []

    for table in tables_to_try:
        conn = None
        try:
            conn = psycopg2.connect(
                host=db_host,
                port=int(db_port),
                database=db_name,
                user=db_user,
password=***REDACTED***
                connect_timeout=3
            )
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute(f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = '{table}'
                );
            """)
            exists = cursor.fetchone()[0]
            if not exists:
                cursor.close()
                conn.close()
                continue
                
            # LlamaIndex's PGVectorStore typically uses 'metadata_' column, but legacy schemas might use 'metadata'
            try:
                cursor.execute(f"SELECT text, metadata_ FROM {table} LIMIT 500;")
            except Exception:
                try:
                    conn.rollback()
                    cursor.execute(f"SELECT text, metadata FROM {table} LIMIT 500;")
                except Exception as inner_exc:
                    logger.warning(f"Failed querying columns from table {table}: {inner_exc}")
                    cursor.close()
                    conn.close()
                    continue

            rows = cursor.fetchall()
            skipped = 0
            for row in rows:
                text_content = row[0]
                metadata_val = row[1]
                if isinstance(metadata_val, str):
                    try:
                        metadata_val = json.loads(metadata_val)
                    except ValueError:
                        metadata_val = {}
                metadata_val = metadata_val or {}

                # Determine file name from metadata (LlamaIndex stores it under
                # 'file_name' or falls back to 'file_path').
                chunk_file = (
                    metadata_val.get("file_name")
                    or metadata_val.get("file_path")
                    or ""
                )

                # Skip chunks whose source document is not in the INDEXED allowlist.
                # If indexed_names is empty (project has no indexed docs yet) we also
                # skip every chunk so that QA generation fails gracefully.
                if indexed_names and chunk_file not in indexed_names:
                    skipped += 1
                    logger.debug(
                        "Skipping orphaned chunk from '%s' (not in INDEXED docs)", chunk_file
                    )
                    continue

                chunks.append({"text": text_content, "metadata": metadata_val})

            if skipped:
                logger.info(
                    "Filtered out %d orphaned chunk(s) from non-INDEXED documents for project %s.",
                    skipped,
                    project_id,
                )

            cursor.close()
            conn.close()
            # Successfully fetched from this table
            break
        except Exception as exc:
            logger.warning(f"Failed fetching chunks from table {table}: {exc}")
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
            continue
            
    return chunks


def generate_synthetic_qas(project_id: str, num_questions: int) -> None:
    """
    Automatically generates questions and ground truth answers from ingested chunks.
    Designed to be run in a background worker thread.
    """
    global QA_GEN_STATUS
    QA_GEN_STATUS[project_id] = {"status": "RUNNING", "error": "", "count": 0}

    try:
        project = Project.objects.filter(project_id=project_id).first()
        if not project:
            raise ValueError(f"Project with ID '{project_id}' not found.")

        # Fetch all document text chunks
        chunks = _get_postgres_chunks(project_id)
        if not chunks:
            raise ValueError("No text chunks found in the project vector database. Please ingest documents first.")

        # Set up Gemini model
api_key=***REDACTED***
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set.")

        llm = GoogleGenAI(
            model="gemini-2.5-flash-lite",
api_key=***REDACTED***
        )

        # Distribute question count across chunks
        qas_generated = 0
        chunks_to_use = chunks[:min(len(chunks), max(1, num_questions // 2 + 1))]

        for chunk in chunks_to_use:
            if qas_generated >= num_questions:
                break

            chunk_text = chunk["text"]
            file_name = chunk["metadata"].get("file_name") or chunk["metadata"].get("file_path") or ""

            # Attempt to link to Django Document model if file_name is available
            document_obj = None
            if file_name:
                from src.apps.documents.models import Document
                document_obj = Document.objects.filter(project=project, document_name=file_name).first()

            prompt = f"""You are an advanced QA Engine. Inspect the following text chunk taken from an isolated corporate document:
\"\"\"
{chunk_text}
\"\"\"

Generate two realistic user search questions and two corresponding ideal, factual answers based STRICTLY on the text provided. Do not extrapolate.
Respond ONLY with a valid JSON array matching this schema:
[
  {{"question": "string", "ground_truth": "string"}},
  {{"question": "string", "ground_truth": "string"}}
]"""

            try:
                response = llm.complete(prompt)
                resp_text = (response.text or "").strip()
                
                # Clean up markdown JSON wrappers if present
                if resp_text.startswith("```json"):
                    resp_text = resp_text[7:]
                if resp_text.endswith("```"):
                    resp_text = resp_text[:-3]
                resp_text = resp_text.strip()

                qa_list = json.loads(resp_text)
                for item in qa_list:
                    if qas_generated >= num_questions:
                        break
                    
                    EvaluationDataset.objects.create(
                        project=project,
                        document=document_obj,
                        question=item["question"],
                        ground_truth=item["ground_truth"],
                        source="GENERATED"
                    )
                    qas_generated += 1
            except Exception as e:
                logger.warning(f"Error parsing Gemini response for chunk: {e}")
                continue

        if qas_generated == 0:
            raise ValueError("Failed to synthesize QA pairs. Check model prompts or API credentials.")

        QA_GEN_STATUS[project_id] = {"status": "SUCCESS", "error": "", "count": qas_generated}

    except Exception as exc:
        logger.error(f"Error generating QA pairs: {exc}")
        QA_GEN_STATUS[project_id] = {"status": "FAILED", "error": str(exc), "count": 0}


def _evaluate_metric_via_llm(llm, metric_name: str, question: str, contexts: list[str], answer: str, ground_truth: str) -> float:
    """
    Fallback LLM evaluation routine to compute metrics in case Ragas is not installed/loaded.
    """
    contexts_joined = "\n---\n".join(contexts)
    
    prompts = {
        "faithfulness": f"""You are an evaluation expert. Evaluate if the generated answer is completely derived from the retrieved contexts (no hallucinations or extra extrapolations).
Contexts:
{contexts_joined}

Generated Answer:
{answer}

Respond ONLY with a single float score between 0.0 (completely hallucinated/unsupported) and 1.0 (completely supported by contexts).""",
        
        "answer_relevancy": f"""You are an evaluation expert. Evaluate if the generated answer is highly relevant and directly addresses the user question.
User Question:
{question}

Generated Answer:
{answer}

Respond ONLY with a single float score between 0.0 (completely irrelevant) and 1.0 (completely relevant and addresses query).""",
        
        "context_recall": f"""You are an evaluation expert. Compare the ground truth answer with the retrieved contexts, and evaluate the fraction of the ground truth that can be recalled from the contexts.
Ground Truth Answer:
{ground_truth}

Retrieved Contexts:
{contexts_joined}

Respond ONLY with a single float score between 0.0 (none of the ground truth is present in the contexts) and 1.0 (all ground truth details can be recalled from contexts).""",
        
        "context_precision": f"""You are an evaluation expert. Given the user question and the retrieved contexts, evaluate how precise and relevant the contexts are for answering the question.
User Question:
{question}

Retrieved Contexts:
{contexts_joined}

Respond ONLY with a single float score between 0.0 (completely irrelevant contexts) and 1.0 (contexts are perfectly precise and relevant)."""
    }

    try:
        response = llm.complete(prompts[metric_name])
        resp_val = (response.text or "").strip()
        return min(max(float(resp_val), 0.0), 1.0)
    except Exception:
        # Graceful fallback default
        return 0.8


def execute_evaluation_run(run_id: str) -> None:
    """
    Asynchronously executes a full RAG tracing pipeline and computes metrics.
    Runs inside a background worker thread.
    """
    try:
        run = EvaluationRun.objects.filter(id=run_id).first()
        if not run:
            logger.error(f"EvaluationRun {run_id} not found.")
            return

        run.status = "RUNNING"
        run.save()

        project = run.project
        dataset_items = EvaluationDataset.objects.filter(project=project)
        
        if not dataset_items.exists():
            raise ValueError("No QA items found in dataset. Please add manual QAs, upload CSV, or generate QAs first.")

        # Initialize LLM and Embedding Model
api_key=***REDACTED***
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set.")

        embed_model = GeminiEmbedding(
            model_name="models/gemini-embedding-001",
api_key=***REDACTED***
        )
        llm = GoogleGenAI(
            model="gemini-2.5-flash-lite",
api_key=***REDACTED***
        )

        from llama_index.core.embeddings import BaseEmbedding
        from llama_index.core.llms import LLM
        if isinstance(embed_model, BaseEmbedding):
            Settings.embed_model = embed_model
        if isinstance(llm, LLM):
            Settings.llm = llm

        # Set up LlamaIndex PostgreSQL Retriever
        vector_store = get_vector_store(project.project_id)
        index = VectorStoreIndex.from_vector_store(vector_store)
        retriever = index.as_retriever(similarity_top_k=3)

        # Ragas dynamic import check
        ragas_available = False
        try:
            import ragas
            from ragas.metrics import faithfulness, answer_relevancy, context_recall, context_precision
            ragas_available = True
        except ImportError:
            logger.info("Ragas not installed. Using fallback LLM-based metric scoring.")

        traces = []

        # Step 1: Trace Retrieval & Synthesis
        for item in dataset_items:
            try:
                # Similarity search
                nodes = retriever.retrieve(item.question)
                contexts = [n.text for n in nodes]
                
                # If no contexts found, default
                if not contexts:
                    contexts = ["No matching contexts retrieved from database."]

                # RAG synthesis
                base_prompt = "Based on the following documents, answer this question:"
                prompt = f"{base_prompt}\n\nQuestion: {item.question}\n\nDocuments:\n"
                for ctx in contexts:
                    prompt += f"\n---\n{ctx}\n"

                response = llm.complete(prompt)
                answer = (response.text or "").strip()

                traces.append({
                    "item": item,
                    "question": item.question,
                    "contexts": contexts,
                    "answer": answer,
                    "ground_truth": item.ground_truth
                })
            except Exception as e:
                logger.warning(f"Error executing RAG tracing for dataset item {item.id}: {e}")
                continue

        if not traces:
            raise ValueError("All dataset items failed to execute through the RAG pipeline.")

        # Step 2: Metric Computation
        if ragas_available:
            try:
                import pandas as pd
                from datasets import Dataset
                from ragas import evaluate as ragas_evaluate

                # Package traces into Hugging Face / Pandas format
                data_dict = {
                    "question": [t["question"] for t in traces],
                    "contexts": [t["contexts"] for t in traces],
                    "answer": [t["answer"] for t in traces],
                    "ground_truth": [t["ground_truth"] for t in traces]
                }
                
                df = pd.DataFrame(data_dict)
                dataset_hf = Dataset.from_pandas(df)

                # Execute Ragas
                results = ragas_evaluate(
                    dataset_hf,
                    metrics=[faithfulness, answer_relevancy, context_recall, context_precision]
                )

                # Record results
                for i, trace in enumerate(traces):
                    EvaluationResultMetrics.objects.create(
                        run=run,
                        dataset_item=trace["item"],
                        context_recall=results["context_recall"][i],
                        context_precision=results["context_precision"][i],
                        faithfulness=results["faithfulness"][i],
                        answer_relevancy=results["answer_relevancy"][i]
                    )
            except Exception as r_err:
                logger.warning(f"Ragas evaluation crashed, falling back to LLM scoring: {r_err}")
                ragas_available = False

        # Fallback LLM scoring (runs if ragas not available or crashed)
        if not ragas_available:
            for trace in traces:
                c_recall = _evaluate_metric_via_llm(llm, "context_recall", trace["question"], trace["contexts"], trace["answer"], trace["ground_truth"])
                c_precision = _evaluate_metric_via_llm(llm, "context_precision", trace["question"], trace["contexts"], trace["answer"], trace["ground_truth"])
                faith = _evaluate_metric_via_llm(llm, "faithfulness", trace["question"], trace["contexts"], trace["answer"], trace["ground_truth"])
                rel = _evaluate_metric_via_llm(llm, "answer_relevancy", trace["question"], trace["contexts"], trace["answer"], trace["ground_truth"])

                EvaluationResultMetrics.objects.create(
                    run=run,
                    dataset_item=trace["item"],
                    context_recall=c_recall,
                    context_precision=c_precision,
                    faithfulness=faith,
                    answer_relevancy=rel
                )

        run.status = "SUCCESS"
        run.completed_at = timezone.now()
        run.save()

    except Exception as exc:
        logger.error(f"Error running evaluation: {exc}")
        run.status = "FAILED"
        run.error_message = str(exc)
        run.completed_at = timezone.now()
        run.save()


def start_async_qa_generation(project_id: str, num_questions: int) -> None:
    """
    Triggers QA generation in a lightweight background thread.
    """
    thread = threading.Thread(target=generate_synthetic_qas, args=(project_id, num_questions))
    thread.daemon = True
    thread.start()


def start_async_evaluation_run(run_id: str) -> None:
    """
    Triggers Ragas/RAG evaluation in a lightweight background thread.
    """
    thread = threading.Thread(target=execute_evaluation_run, args=(run_id,))
    thread.daemon = True
    thread.start()


def generate_answer_for_manual_item(item_id: str) -> ManualEvaluationItem:
    """
    Queries the project's RAG pipeline (LlamaIndex retriever + Gemini LLM) to generate
    an answer and store context citations for a single ManualEvaluationItem.
    """
    item = ManualEvaluationItem.objects.filter(id=item_id).first()
    if not item:
        raise ValueError(f"ManualEvaluationItem with ID {item_id} not found.")

    item.status = "GENERATING"
    item.error_message = ""
    item.save()

    try:
        project = item.run.project
api_key=***REDACTED***

        # Set up LlamaIndex models if API key exists
        llm = GoogleGenAI(
            model="gemini-2.5-flash-lite",
api_key=***REDACTED***
        ) if api_key else None

        embed_model = GeminiEmbedding(
            model_name="models/gemini-embedding-001",
api_key=***REDACTED***
        ) if api_key else None

        if embed_model:
            Settings.embed_model = embed_model
        if llm:
            Settings.llm = llm

        contexts = []
        answer_text = ""

        try:
            vector_store = get_vector_store(project.project_id)
            index = VectorStoreIndex.from_vector_store(vector_store)
            retriever = index.as_retriever(similarity_top_k=3)
            nodes = retriever.retrieve(item.question)
            contexts = [n.text for n in nodes if hasattr(n, 'text') and n.text]
        except Exception as ret_err:
            logger.warning(f"Retriever exception for project {project.project_id}: {ret_err}")

        if not contexts:
            contexts = ["No specific context chunks retrieved from vector store."]

        if llm:
            base_prompt = "Based on the following document context, answer the user's question accurately and concisely:\n"
            context_block = "\n---\n".join(contexts)
            prompt = f"{base_prompt}\nContexts:\n{context_block}\n\nQuestion: {item.question}\nAnswer:"
            response = llm.complete(prompt)
            answer_text = (response.text or "").strip()
        else:
            answer_text = f"Simulated RAG Answer for '{item.question}' (GOOGLE_API_KEY not configured)."

        item.answer = answer_text
        item.citations = contexts
        item.status = "GENERATED"
        item.save()
        return item

    except Exception as exc:
        logger.error(f"Error generating manual answer for item {item_id}: {exc}")
        item.status = "FAILED"
        item.error_message = str(exc)
        item.save()
        return item


def batch_generate_manual_answers(run_id: str) -> None:
    """
    Generates answers for all pending or failed ManualEvaluationItems in a run.
    """
    run = ManualEvaluationRun.objects.filter(id=run_id).first()
    if not run:
        logger.error(f"ManualEvaluationRun {run_id} not found for batch generation.")
        return

    items = run.items.filter(status__in=["PENDING", "FAILED"])
    for item in items:
        generate_answer_for_manual_item(str(item.id))


```
<!-- END_FILE -->

---
<!-- FILE: apps/evaluate/migrations/__init__.py -->
## apps/evaluate/migrations/__init__.py

```py


```
<!-- END_FILE -->

---
<!-- FILE: apps/evaluate/migrations/0001_initial.py -->
## apps/evaluate/migrations/0001_initial.py

```py
# Generated by Django 6.0.1 on 2026-06-02 12:45

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('projects', '0001_initial'),
        ('documents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EvaluationDataset',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('question', models.TextField(help_text='The reference question to search and evaluate')),
                ('ground_truth', models.TextField(help_text='The gold-standard ground-truth reference answer')),
                ('source', models.CharField(choices=[('GENERATED', 'Generated'), ('MANUAL', 'Manual'), ('CSV_UPLOAD', 'CSV Upload')], default='MANUAL', help_text='Source of the dataset pair acquisition', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('document', models.ForeignKey(blank=True, help_text='The document this QA pair was generated from (null for manual/CSV-uploaded QAs)', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dataset_items', to='documents.document')),
                ('project', models.ForeignKey(help_text='The project this validation item belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='dataset_items', to='projects.project')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='EvaluationRun',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('RUNNING', 'Running'), ('SUCCESS', 'Success'), ('FAILED', 'Failed')], default='PENDING', help_text='Current state of the evaluation run', max_length=20)),
                ('error_message', models.TextField(blank=True, help_text='Error details if status is FAILED')),
                ('project', models.ForeignKey(help_text='The project being evaluated', on_delete=django.db.models.deletion.CASCADE, related_name='evaluation_runs', to='projects.project')),
            ],
            options={
                'ordering': ['-started_at'],
            },
        ),
        migrations.CreateModel(
            name='EvaluationResultMetrics',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('context_recall', models.FloatField(blank=True, help_text='Context Recall score', null=True)),
                ('context_precision', models.FloatField(blank=True, help_text='Context Precision score', null=True)),
                ('faithfulness', models.FloatField(blank=True, help_text='Faithfulness score', null=True)),
                ('answer_relevancy', models.FloatField(blank=True, help_text='Answer Relevancy score', null=True)),
                ('dataset_item', models.ForeignKey(help_text='The reference QA dataset item evaluated', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='result_metrics', to='evaluate.evaluationdataset')),
                ('run', models.ForeignKey(help_text='The evaluation run this result belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='result_metrics', to='evaluate.evaluationrun')),
            ],
        ),
    ]

```
<!-- END_FILE -->

---
<!-- FILE: apps/evaluate/migrations/0002_manualevaluationrun_manualevaluationitem.py -->
## apps/evaluate/migrations/0002_manualevaluationrun_manualevaluationitem.py

```py
# Generated by Django 6.0.1 on 2026-07-24 08:16

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('evaluate', '0001_initial'),
        ('projects', '0009_alter_project_storage_type_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManualEvaluationRun',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('source_type', models.CharField(choices=[('MANUAL_INPUT', 'Manual Input'), ('CSV_UPLOAD', 'CSV Upload')], default='MANUAL_INPUT', help_text='Origin of the question set', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(help_text='The project being evaluated manually', on_delete=django.db.models.deletion.CASCADE, related_name='manual_evaluation_runs', to='projects.project')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ManualEvaluationItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('question', models.TextField(help_text='The question to evaluate')),
                ('answer', models.TextField(blank=True, default='', help_text='Generated response from the project RAG API')),
                ('citations', models.JSONField(blank=True, default=list, help_text='List of context texts/sources retrieved for answer')),
                ('rating', models.CharField(choices=[('UNRATED', 'Unrated'), ('GREEN', 'Good'), ('ORANGE', 'Needs Improvement'), ('RED', 'Bad')], default='UNRATED', help_text='Human evaluator score rating', max_length=20)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('GENERATING', 'Generating'), ('GENERATED', 'Generated'), ('FAILED', 'Failed')], default='PENDING', help_text='Answer generation state', max_length=20)),
                ('error_message', models.TextField(blank=True, default='', help_text='Error details if answer generation failed')),
                ('run', models.ForeignKey(help_text='The manual evaluation run this item belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='items', to='evaluate.manualevaluationrun')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]

```
<!-- END_FILE -->

---
<!-- FILE: apps/evaluate/models.py -->
## apps/evaluate/models.py

```py
import uuid
from django.db import models
from src.apps.projects.models import Project
from src.apps.documents.models import Document


class EvaluationDataset(models.Model):
    """
    Stores individual question and answer reference pairs.
    Can be generated from document chunks, or written/uploaded manually by users.
    """
    SOURCE_CHOICES = [
        ("GENERATED", "Generated"),
        ("MANUAL", "Manual"),
        ("CSV_UPLOAD", "CSV Upload"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="dataset_items",
        help_text="The project this validation item belongs to"
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="dataset_items",
        help_text="The document this QA pair was generated from (null for manual/CSV-uploaded QAs)"
    )
    question = models.TextField(help_text="The reference question to search and evaluate")
    ground_truth = models.TextField(help_text="The gold-standard ground-truth reference answer")
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default="MANUAL",
        help_text="Source of the dataset pair acquisition"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.question[:40]}... -> {self.ground_truth[:40]}..."


class EvaluationRun(models.Model):
    """
    Represents an execution event of a dataset against the project configuration.
    """
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("RUNNING", "Running"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="evaluation_runs",
        help_text="The project being evaluated"
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
        help_text="Current state of the evaluation run"
    )
    error_message = models.TextField(blank=True, help_text="Error details if status is FAILED")

    class Meta:
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"Run {self.id} ({self.status}) at {self.started_at}"


class EvaluationResultMetrics(models.Model):
    """
    Stores Ragas scores for individual questions and their aggregated metrics during a run.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    run = models.ForeignKey(
        EvaluationRun,
        on_delete=models.CASCADE,
        related_name="result_metrics",
        help_text="The evaluation run this result belongs to"
    )
    dataset_item = models.ForeignKey(
        EvaluationDataset,
        on_delete=models.SET_NULL,
        null=True,
        related_name="result_metrics",
        help_text="The reference QA dataset item evaluated"
    )
    context_recall = models.FloatField(null=True, blank=True, help_text="Context Recall score")
    context_precision = models.FloatField(null=True, blank=True, help_text="Context Precision score")
    faithfulness = models.FloatField(null=True, blank=True, help_text="Faithfulness score")
    answer_relevancy = models.FloatField(null=True, blank=True, help_text="Answer Relevancy score")

    def __str__(self) -> str:
        return f"Metrics for item {self.dataset_item_id} inside run {self.run_id}"


class ManualEvaluationRun(models.Model):
    """
    Represents a manual evaluation session for a project.
    """
    SOURCE_CHOICES = [
        ("MANUAL_INPUT", "Manual Input"),
        ("CSV_UPLOAD", "CSV Upload"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="manual_evaluation_runs",
        help_text="The project being evaluated manually"
    )
    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default="MANUAL_INPUT",
        help_text="Origin of the question set"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Manual Run {self.id} for {self.project.display_name} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class ManualEvaluationItem(models.Model):
    """
    Individual question-answer pair evaluated manually with Red/Orange/Green ratings.
    """
    RATING_CHOICES = [
        ("UNRATED", "Unrated"),
        ("GREEN", "Good"),
        ("ORANGE", "Needs Improvement"),
        ("RED", "Bad"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("GENERATING", "Generating"),
        ("GENERATED", "Generated"),
        ("FAILED", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    run = models.ForeignKey(
        ManualEvaluationRun,
        on_delete=models.CASCADE,
        related_name="items",
        help_text="The manual evaluation run this item belongs to"
    )
    question = models.TextField(help_text="The question to evaluate")
    answer = models.TextField(blank=True, default="", help_text="Generated response from the project RAG API")
    citations = models.JSONField(default=list, blank=True, help_text="List of context texts/sources retrieved for answer")
    rating = models.CharField(
        max_length=20,
        choices=RATING_CHOICES,
        default="UNRATED",
        help_text="Human evaluator score rating"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
        help_text="Answer generation state"
    )
    error_message = models.TextField(blank=True, default="", help_text="Error details if answer generation failed")

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return f"Manual Item: {self.question[:30]}... ({self.rating})"


```
<!-- END_FILE -->

---
<!-- FILE: apps/evaluate/serializers.py -->
## apps/evaluate/serializers.py

```py
from rest_framework import serializers
from .models import EvaluationDataset, EvaluationRun, EvaluationResultMetrics


class EvaluationDatasetSerializer(serializers.ModelSerializer):
    """Serializer for EvaluationDataset QA items"""
    class Meta:
        model = EvaluationDataset
        fields = [
            "id", "project", "document", "question",
            "ground_truth", "source", "created_at"
        ]
        read_only_fields = ["created_at"]


class EvaluationRunSerializer(serializers.ModelSerializer):
    """Serializer for EvaluationRun instances"""
    class Meta:
        model = EvaluationRun
        fields = [
            "id", "project", "started_at", "completed_at",
            "status", "error_message"
        ]
        read_only_fields = ["started_at", "completed_at"]


class EvaluationResultMetricsSerializer(serializers.ModelSerializer):
    """Serializer for EvaluationResultMetrics"""
    class Meta:
        model = EvaluationResultMetrics
        fields = [
            "id", "run", "dataset_item", "context_recall",
            "context_precision", "faithfulness", "answer_relevancy"
        ]

```
<!-- END_FILE -->

---
<!-- FILE: apps/evaluate/tests.py -->
## apps/evaluate/tests.py

```py
from django.test import TestCase

# Create your tests here.

```
<!-- END_FILE -->

---
<!-- FILE: apps/evaluate/urls.py -->
## apps/evaluate/urls.py

```py
from django.urls import path
from . import views

app_name = "evaluate"

urlpatterns = [
    path("evaluate/", views.evaluation_dashboard, name="dashboard"),
    path("evaluate/qa-setup/<str:project_id>/", views.qa_setup, name="qa_setup"),
    path("evaluate/qa-status/<str:project_id>/", views.qa_generation_status, name="qa_status"),
    path("evaluate/run/<str:project_id>/", views.run_evaluation, name="run_evaluation"),
    path("evaluate/run-status/<uuid:run_id>/", views.evaluation_run_status, name="run_status"),
    path("evaluate/results/<uuid:run_id>/", views.evaluation_results, name="results"),
    path("evaluate/qa-item/<uuid:item_id>/delete/", views.delete_qa_item, name="delete_qa_item"),
]

```
<!-- END_FILE -->

---
<!-- FILE: apps/evaluate/views.py -->
## apps/evaluate/views.py

```py
import csv
import io
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from src.apps.projects.models import Project
from src.apps.documents.models import Document
from .models import EvaluationDataset, EvaluationRun, EvaluationResultMetrics
from .eval_services import (
    start_async_qa_generation,
    start_async_evaluation_run,
    QA_GEN_STATUS,
)

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["GET"])
def evaluation_dashboard(request):
    """
    Redirects to the central modern Unfold evaluation dashboard.
    """
    return redirect("/rag/dashboard/evaluate/")


@login_required
def qa_setup(request, project_id):
    """
    Redirects standard QA Setup view to the Unfold Admin QaSetupWorkflowView.
    """
    return redirect(reverse("custom_admin:qa-setup-workflow", kwargs={"project_id": project_id}))


@login_required
@require_http_methods(["GET"])
def qa_generation_status(request, project_id):
    """
    Polling endpoint for automatic QA generation.
    """
    status_data = QA_GEN_STATUS.get(project_id, {"status": "PENDING", "error": "", "count": 0})
    project = get_object_or_404(Project, project_id=project_id)

    if status_data["status"] == "SUCCESS":
        dataset_items = EvaluationDataset.objects.filter(project=project)
        return render(request, "evaluate/qa_list_partial.html", {
            "project": project,
            "dataset_items": dataset_items,
            "count": status_data.get("count", 0)
        })
    elif status_data["status"] == "FAILED":
        return HttpResponse(f'<div class="p-4 bg-red-50 text-red-700 rounded-lg">✗ Generation failed: {status_data["error"]}</div>')
    else:
        # Still running
        context = {
            "project": project,
            "status": "RUNNING",
            "mode": "qa_generation"
        }
        return render(request, "evaluate/run_progress.html", context)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def run_evaluation(request, project_id):
    """
    Creates an EvaluationRun and triggers background RAG Ragas evaluation.
    """
    project = get_object_or_404(Project, project_id=project_id)
    run = EvaluationRun.objects.create(
        project=project,
        status="PENDING"
    )

    # Start async thread
    start_async_evaluation_run(run.id)

    context = {
        "project": project,
        "run": run,
        "status": "RUNNING",
        "mode": "evaluation"
    }
    return render(request, "evaluate/run_progress.html", context)


@login_required
@require_http_methods(["GET"])
def evaluation_run_status(request, run_id):
    """
    Polling endpoint for evaluation runs.
    """
    run = get_object_or_404(EvaluationRun, id=run_id)

    if run.status == "SUCCESS":
        # Redirect to results grid view
        return HttpResponse(f'<div hx-get="{reverse("evaluate:results", args=[run.id])}" hx-trigger="load" hx-target="#evaluation-content-pane"></div>')
    elif run.status == "FAILED":
        return HttpResponse(f'<div class="p-4 bg-red-50 text-red-700 rounded-lg">✗ Evaluation failed: {run.error_message}</div>')
    else:
        # Still running / pending
        context = {
            "project": run.project,
            "run": run,
            "status": "RUNNING",
            "mode": "evaluation"
        }
        return render(request, "evaluate/run_progress.html", context)


@login_required
@require_http_methods(["GET"])
def evaluation_results(request, run_id):
    """
    Fetches evaluation metrics and renders the grid results table.
    """
    run = get_object_or_404(EvaluationRun, id=run_id)
    metrics = EvaluationResultMetrics.objects.filter(run=run).select_related("dataset_item")

    if not metrics.exists():
        return HttpResponse('<div class="p-4 text-gray-500">No evaluation metrics recorded for this run.</div>')

    avg_recall = sum(m.context_recall or 0 for m in metrics) / metrics.count()
    avg_precision = sum(m.context_precision or 0 for m in metrics) / metrics.count()
    avg_faithfulness = sum(m.faithfulness or 0 for m in metrics) / metrics.count()
    avg_relevancy = sum(m.answer_relevancy or 0 for m in metrics) / metrics.count()
    avg_total = (avg_recall + avg_precision + avg_faithfulness + avg_relevancy) / 4

    def get_color(score):
        if score >= 0.85:
            return "green"
        elif score >= 0.70:
            return "yellow"
        return "red"

    # Traces data for detailed drill-down
    traces = []
    # Use LlamaIndex to query top matching contexts for debugging display
    for item in metrics:
        # RAG Tracing Context display
        traces.append({
            "metric": item,
            "question": item.dataset_item.question if item.dataset_item else "N/A",
            "ground_truth": item.dataset_item.ground_truth if item.dataset_item else "N/A",
            "recall_color": get_color(item.context_recall or 0),
            "precision_color": get_color(item.context_precision or 0),
            "faithfulness_color": get_color(item.faithfulness or 0),
            "relevancy_color": get_color(item.answer_relevancy or 0)
        })

    context = {
        "run": run,
        "avg_recall": avg_recall,
        "avg_precision": avg_precision,
        "avg_faithfulness": avg_faithfulness,
        "avg_relevancy": avg_relevancy,
        "avg_total": avg_total,
        "recall_color": get_color(avg_recall),
        "precision_color": get_color(avg_precision),
        "faithfulness_color": get_color(avg_faithfulness),
        "relevancy_color": get_color(avg_relevancy),
        "total_color": get_color(avg_total),
        "traces": traces,
        "url_prefix": "/rag"
    }
    return render(request, "evaluate/metrics_grid.html", context)



@login_required
@require_http_methods(["POST", "DELETE"])
@csrf_exempt
def delete_qa_item(request, item_id):
    """
    Deletes a specific QA dataset item from the database.
    If HTMX request, returns the updated QA list partial.
    """
    item = get_object_or_404(EvaluationDataset, id=item_id)
    project = item.project
    item.delete()

    if request.headers.get("HX-Request"):
        dataset_items = EvaluationDataset.objects.filter(project=project)
        return render(request, "evaluate/qa_list_partial.html", {
            "project": project,
            "dataset_items": dataset_items,
            "message": "✓ QA item deleted successfully."
        })

    return redirect(reverse("custom_admin:qa-setup-workflow", kwargs={"project_id": project.project_id}))


```
<!-- END_FILE -->

---
<!-- FILE: apps/my_rag_project/__init__.py -->
## apps/my_rag_project/__init__.py

```py


```
<!-- END_FILE -->

---
<!-- FILE: apps/my_rag_project/admin.py -->
## apps/my_rag_project/admin.py

```py
"""
Custom Admin Site configuration for the my_rag_project.
Integrates django-unfold and overrides permission rules to allow regular authenticated users.
"""

from django.http import HttpRequest
from django.urls import path
from unfold.sites import UnfoldAdminSite


class CustomUnfoldAdminSite(UnfoldAdminSite):
    """
    Custom administration site utilizing django-unfold theme.
    Overrides standard permissions to allow regular authenticated users access to the dashboard.
    """

    def has_permission(self, request: HttpRequest) -> bool:
        """
        Check if the user has permission to access this admin site.
        Allows any active authenticated user.

        Parameters
        ----------
        request : HttpRequest
            The incoming HTTP request object.

        Returns
        -------
        bool
            True if the user is authenticated and active, False otherwise.
        """
        return bool(request.user and request.user.is_authenticated and request.user.is_active)

    def get_urls(self) -> list:
        """
        Overridden to inject custom chat and evaluation workflow views
        into the admin site's URL structure.

        Returns
        -------
        list
            The complete list of admin URL patterns.
        """
        urls = super().get_urls()
        from src.apps.chat.admin_views import ChatWorkflowView
        from src.apps.evaluate.admin_views import (
            EvaluationWorkflowView,
            QaSetupWorkflowView,
            RunEvaluationView,
            CreateManualEvaluationRunView,
            GenerateManualAnswerView,
            BatchGenerateManualAnswersView,
            RateManualItemView,
        )
        from src.apps.projects.models import Project

        # Fetch the registered Project ModelAdmin instance from the registry
        project_admin = self._registry.get(Project)
        if not project_admin:
            from src.apps.projects.admin import ProjectAdmin
            project_admin = ProjectAdmin(Project, self)

        custom_urls = [
            path(
                "chat/",
                self.admin_view(ChatWorkflowView.as_view(model_admin=project_admin)),
                name="chat-workflow",
            ),
            path(
                "evaluate/",
                self.admin_view(EvaluationWorkflowView.as_view(model_admin=project_admin)),
                name="evaluation-workflow",
            ),
            path(
                "evaluate/qa-setup/<str:project_id>/",
                self.admin_view(QaSetupWorkflowView.as_view(model_admin=project_admin)),
                name="qa-setup-workflow",
            ),
            path(
                "evaluate/run/",
                self.admin_view(RunEvaluationView.as_view(model_admin=project_admin)),
                name="run-evaluation",
            ),
            path(
                "evaluate/manual/create/",
                self.admin_view(CreateManualEvaluationRunView.as_view(model_admin=project_admin)),
                name="manual-eval-create",
            ),
            path(
                "evaluate/manual/generate-answer/<uuid:item_id>/",
                self.admin_view(GenerateManualAnswerView.as_view(model_admin=project_admin)),
                name="manual-eval-generate-answer",
            ),
            path(
                "evaluate/manual/generate-all/<uuid:run_id>/",
                self.admin_view(BatchGenerateManualAnswersView.as_view(model_admin=project_admin)),
                name="manual-eval-generate-all",
            ),
            path(
                "evaluate/manual/rate/<uuid:item_id>/",
                self.admin_view(RateManualItemView.as_view(model_admin=project_admin)),
                name="manual-eval-rate",
            ),
        ]
        return custom_urls + urls


custom_admin_site = CustomUnfoldAdminSite(name="custom_admin")

```
<!-- END_FILE -->

---
<!-- FILE: apps/my_rag_project/asgi.py -->
## apps/my_rag_project/asgi.py

```py
"""
ASGI config for my_rag_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.apps.my_rag_project.settings')

application = get_asgi_application()

```
<!-- END_FILE -->

---
<!-- FILE: apps/my_rag_project/settings/__init__.py -->
## apps/my_rag_project/settings/__init__.py

```py
"""
Settings package for my_rag project.
Dynamically loads appropriate settings based on DJANGO_SETTINGS_MODULE environment variable.
"""

import os

# Determine which settings module to use
ENV = os.getenv('DJANGO_ENV', 'development')

if ENV == 'production':
    from .settings_prod import *
elif ENV == 'testing':
    from .settings_test import *
else:  # development (default)
    from .settings_dev import *

```
<!-- END_FILE -->

---
<!-- FILE: apps/my_rag_project/settings/base.py -->
## apps/my_rag_project/settings/base.py

```py
"""
Base Django settings for my_rag project.
Common settings shared across all environments.
"""

import os
import sys

# Force pure-Python implementation of Protobuf to bypass Python 3.14 C-extension incompatibility
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
sys.modules["google._upb._message"] = None
sys.modules["google._upb"] = None

from pathlib import Path
from django.urls import reverse_lazy
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Sentry/Bugsink
try:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    if os.getenv("DJANGO_ENV") != "testing":
        sentry_sdk.init(
            dsn="https://650bb7f2a68c4a1a90577694622e4545@www.fasolaki.com/bugsink/1",
            integrations=[DjangoIntegration()],
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
        )
except ImportError:
    pass

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# Robustly find the project root by locating manage.py
current_dir = Path(__file__).resolve().parent
while not (current_dir / 'manage.py').exists() and current_dir.parent != current_dir:
    current_dir = current_dir.parent

if (current_dir / 'manage.py').exists():
    BASE_DIR = current_dir
else:
    # Fallback to the original logic
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent

# Add apps directory to Python path for imports
APPS_DIR = BASE_DIR / 'src' / 'apps'
sys.path.insert(0, str(APPS_DIR))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-key-change-in-production')

# Application definition
INSTALLED_APPS = [
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party
    'rest_framework',
    'corsheaders',
    
    # Local apps
    'src.apps.chat.apps.ChatConfig',
    'src.apps.projects.apps.ProjectsConfig',
    'src.apps.documents.apps.DocumentsConfig',
    'src.apps.evaluate.apps.EvaluateConfig',
    'src.apps.api.apps.ApiConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS middleware - must be before common
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'src.apps.my_rag_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'src.apps.my_rag_project.wsgi.application'

# Database - default to SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

# Media files (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'uploads'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# File upload settings - matching Flask's 20MB max
DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024  # 20MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024  # 20MB

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Application settings from Flask config
ALLOW_FILE_UPLOADS = True
JSON_SORT_KEYS = False

# Auth routes for the dashboard live under /rag/.
LOGIN_URL = '/rag/accounts/login/'
LOGIN_REDIRECT_URL = '/rag/'

# Remote PostgreSQL configuration for local RAG projects (VPS)
REMOTE_POSTGRES_CONFIG = {
    'NAME': os.getenv('postgres_name', 'rag_dashboard'),
    'USER': os.getenv('postgres_user', 'rag_user2'),
    'PASSWORD': os.getenv('postgres_password', 'ThinkRAG2026!'),
    'HOST': os.getenv('postgres_host', 'localhost'),
    'PORT': os.getenv('postgres_port', '5432'),
}

# django-unfold administration configuration
UNFOLD = {
    "SITE_TITLE": "RAG Dashboard",
    "SITE_HEADER": "RAG Administration",
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Navigation",
                "items": [
                    {
                        "title": "Projects",
                        "icon": "folder",
                        "link": reverse_lazy("custom_admin:projects_project_changelist"),
                    },
                    {
                        "title": "Chat Workflow",
                        "icon": "chat",
                        "link": reverse_lazy("custom_admin:chat-workflow"),
                    },
                    {
                        "title": "Evaluation Workflow",
                        "icon": "star",
                        "link": reverse_lazy("custom_admin:evaluation-workflow"),
                    },
                ],
            },
        ],
    },
}



```
<!-- END_FILE -->

---
<!-- FILE: apps/my_rag_project/settings/settings_dev.py -->
## apps/my_rag_project/settings/settings_dev.py

```py
"""
Django settings for development environment.
Extends base settings with development-specific overrides.
"""

from .base import *

# Override development-specific settings
DEBUG = True

ALLOWED_HOSTS = ['*']

# CORS settings - allow all origins in development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

CORS_ALLOW_ALL_ORIGINS = True

# For development, show all settings
DEBUG_PROPAGATE_EXCEPTIONS = True

# Development database (can override with environment variable if needed)
# DATABASES['default'] inherited from base.py (SQLite)

# Email backend for development (console output)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Enable Django Debug Toolbar if available
try:
    import debug_toolbar
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']
except ImportError:
    pass

```
<!-- END_FILE -->

---
<!-- FILE: apps/my_rag_project/settings/settings_prod.py -->
## apps/my_rag_project/settings/settings_prod.py

```py
"""
Django settings for production environment.
Extends base settings with production-specific security settings.
"""

import os
from .base import *

# Override production-specific settings
DEBUG = False

# Strict ALLOWED_HOSTS for production
ALLOWED_HOSTS = [
    'fasolaki.com',
    'www.fasolaki.com',
]

# Static files URL for /rag/ prefix
STATIC_URL = '/rag/static/'

# Login URL with /rag/ prefix
LOGIN_URL = '/rag/accounts/login/'
LOGIN_REDIRECT_URL = '/rag/'

# CORS settings - restrict to specific domains in production
CORS_ALLOWED_ORIGINS = [
    'https://www.fasolaki.com',
    'https://fasolaki.com',
]

CSRF_TRUSTED_ORIGINS = [
    'https://www.fasolaki.com',
    'https://fasolaki.com',
]

# Security settings for production
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
    'script-src': ("'self'", "'unsafe-inline'"),
    'style-src': ("'self'", "'unsafe-inline'"),
}

# HSTS settings (optional, but recommended)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True


# Production database (configure via environment variables or secrets)
# For PostgreSQL in production:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# SECRET_KEY must be set in environment for production
if not os.getenv('SECRET_KEY') or os.getenv('SECRET_KEY') == 'django-insecure-dev-key-change-in-production':
    raise ValueError("SECRET_KEY environment variable must be set and changed in production")

# Static files - use whitenoise for serving static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Logging configuration for production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
}

# Ensure logs directory exists
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

# Email configuration (configure for your mail provider)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = os.getenv('EMAIL_HOST')
# EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

```
<!-- END_FILE -->

---
<!-- FILE: apps/my_rag_project/settings/settings_test.py -->
## apps/my_rag_project/settings/settings_test.py

```py
"""
Django settings for testing environment.
Extends base settings with testing-specific overrides.
"""

from .base import *

# Override testing-specific settings
DEBUG = True

ALLOWED_HOSTS = ['*']

# Use in-memory database for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# CORS settings - allow all origins in testing
CORS_ALLOW_ALL_ORIGINS = True

# Disable migrations for faster tests (optional)
# Uncomment if you want to skip migrations during testing
# class DisableMigrations:
#     def __contains__(self, item):
#         return True
#     def __getitem__(self, item):
#         return None
# MIGRATION_MODULES = DisableMigrations()

# Email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Password hasher for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

```
<!-- END_FILE -->

---
<!-- FILE: apps/my_rag_project/urls.py -->
## apps/my_rag_project/urls.py

```py
"""
URL configuration for my_rag_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from src.apps.my_rag_project.admin import custom_admin_site
from src.apps.chat.views import chat as chat_api_view

urlpatterns = [
    # Custom Unfold Admin Site under /rag/
    path('rag/dashboard/', custom_admin_site.urls),
    # Admin at root level under /rag/
    path('rag/admin/', admin.site.urls),
    # Auth routes under /rag/
    path('rag/accounts/', include('django.contrib.auth.urls')),
    # Preserved DRF API routes
    path('rag/api/chat/', chat_api_view, name='chat_api'),
    path('rag/api/', include('src.apps.api.api_urls')),
    path('rag/', include('src.apps.documents.urls')),
    path('rag/', include('src.apps.projects.urls')),
    path('rag/', include('src.apps.chat.urls')),
    path('rag/', include('src.apps.evaluate.urls')),
]

```
<!-- END_FILE -->

---
<!-- FILE: apps/my_rag_project/wsgi.py -->
## apps/my_rag_project/wsgi.py

```py
"""
WSGI config for my_rag_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.apps.my_rag_project.settings')

application = get_wsgi_application()

```
<!-- END_FILE -->

---
<!-- FILE: apps/projects/__init__.py -->
## apps/projects/__init__.py

```py


```
<!-- END_FILE -->

---
<!-- FILE: apps/projects/admin.py -->
## apps/projects/admin.py

```py
from django import forms
from django.contrib import admin
from unfold.admin import ModelAdmin
from src.apps.my_rag_project.admin import custom_admin_site
from .models import Project, SystemPrompt


class ProjectAdminForm(forms.ModelForm):
    custom_prompt_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
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
                locked_fields = ['embedding_model', 'document_parsing', 'use_markitdown']
                for field_name in locked_fields:
                    if field_name in self.fields:
                        self.fields[field_name].disabled = True
                        self.fields[field_name].help_text = (
                            "🔒 Locked: Cannot be changed after the first source has been indexed."
                        )

    def clean(self):
        cleaned_data = super().clean()
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
    readonly_fields = ("project_id", "created_at", "updated_at", "document_uploader_and_list")
    fieldsets = (
        (
            "Parameters",
            {
                "classes": ("tab",),
                "fields": (
                    "project_id",
                    "display_name",
                    "storage_type",
                    "description",
                    "is_active",
                    "synthesizer",
                    "document_parsing",
                    "chunking",
                    "embedding_model",
                    "custom_prompt",
                    "custom_prompt_text",
                    "use_markitdown",
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
                    "use_structural_grading",
                    "created_at",
                    "updated_at",
                    "document_uploader_and_list",
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


@admin.register(SystemPrompt, site=custom_admin_site)
class SystemPromptAdmin(ModelAdmin):
    list_display = ("project", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("project__display_name",)
    readonly_fields = ("created_at", "updated_at")

```
<!-- END_FILE -->

---
<!-- FILE: apps/projects/api_views.py -->
## apps/projects/api_views.py

```py
"""
DRF API Views for projects app
"""

from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Project, SystemPrompt
from .serializers import (
    ProjectSerializer,
    ProjectCreateSerializer,
    ProjectUpdateSerializer,
    ProjectListSerializer,
    SystemPromptSerializer,
)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Project model
    
    Endpoints:
    - GET /api/projects/ - List all projects
    - POST /api/projects/ - Create project
    - GET /api/projects/{id}/ - Get project details
    - PUT /api/projects/{id}/ - Update project
    - DELETE /api/projects/{id}/ - Delete project
    
    Supports multiple lookup methods:
    - By primary key (id)
    - By project_id
    - By external_store_id (may contain slashes)
    """
    queryset = Project.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'  # Default lookup field
    lookup_value_regex = '[^/]+'  # Allow anything except forward slash in URL segment
    
    def get_queryset(self):
        """Filter projects by authenticated user"""
        if getattr(self, 'swagger_fake_view', False):
            return Project.objects.none()
        return Project.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Set the user to the authenticated user on create"""
        serializer.save(user=self.request.user)
    
    def get_object(self):
        """
        Override to support lookup by pk, project_id, or external_store_id
        """
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        
        # Try to find by primary key first (if it's a digit)
        lookup_value = self.kwargs[lookup_url_kwarg]
        if isinstance(lookup_value, int) or (isinstance(lookup_value, str) and lookup_value.isdigit()):
            try:
                obj = queryset.get(pk=lookup_value)
                self.check_object_permissions(self.request, obj)
                return obj
            except Project.DoesNotExist:
                pass
        
        # Try to find by project_id
        try:
            obj = queryset.get(project_id=lookup_value)
            self.check_object_permissions(self.request, obj)
            return obj
        except Project.DoesNotExist:
            pass
        
        # Try to find by external_store_id
        try:
            obj = queryset.get(external_store_id=lookup_value)
            self.check_object_permissions(self.request, obj)
            return obj
        except Project.DoesNotExist:
            pass
        
        # If not found by any method, raise 404
        from django.http import Http404
        raise Http404("No Project matches the given query.")
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return ProjectCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ProjectUpdateSerializer
        elif self.action == 'list':
            return ProjectListSerializer
        return ProjectSerializer
    
    @action(detail=True, methods=['get', 'post'])
    def prompt(self, request, pk=None):
        """Get or set system prompt for project"""
        project = self.get_object()
        
        if request.method == 'GET':
            prompt = project.system_prompt if hasattr(project, 'system_prompt') else None
            # Return in the format expected by the frontend
            prompt_content = prompt.content if prompt else ''
            return Response({'prompt': prompt_content})
        
        # POST - set prompt
        # Accept both 'content' (API standard) and 'prompt' (legacy frontend key)
        content = request.data.get('content') or request.data.get('prompt', '')
        prompt, created = SystemPrompt.objects.get_or_create(
            project=project,
            defaults={'content': content}
        )
        if not created:
            prompt.content = content
            prompt.save()
        
        # Return in the format expected by the frontend
        return Response({'status': 'success', 'prompt': content})
    
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """Get documents for this project"""
        from src.apps.documents.models import Document
        from src.apps.documents.serializers import DocumentListSerializer
        
        project = self.get_object()
        
        # Get documents for this project (Document has ForeignKey to Project)
        docs = Document.objects.filter(project=project)
        
        serializer = DocumentListSerializer(docs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active projects"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_storage(self, request):
        """Filter projects by storage type"""
        storage_type = request.query_params.get('type')
        if not storage_type:
            return Response({'error': 'storage type required'}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset().filter(storage_type=storage_type)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SystemPromptViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for SystemPrompt model
    
    Endpoints:
    - GET /api/prompts/ - List all prompts
    - POST /api/prompts/ - Create prompt
    - GET /api/prompts/{id}/ - Get prompt
    - PUT /api/prompts/{id}/ - Update prompt
    - DELETE /api/prompts/{id}/ - Delete prompt
    """
    queryset = SystemPrompt.objects.all()
    serializer_class = SystemPromptSerializer
    permission_classes = [AllowAny]
    
    def perform_create(self, serializer):
        """Ensure only one prompt per project"""
        project = serializer.validated_data.get('project')
        # Delete existing prompt for this project if exists
        SystemPrompt.objects.filter(project=project).delete()
        serializer.save()

```
<!-- END_FILE -->

---
<!-- FILE: apps/projects/apps.py -->
## apps/projects/apps.py

```py
from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    name = 'src.apps.projects'

```
<!-- END_FILE -->

---
<!-- FILE: apps/projects/db_utils.py -->
## apps/projects/db_utils.py

```py
import psycopg2
from django.conf import settings
from logging import getLogger

logger = getLogger(__name__)

def test_postgres_connection() -> tuple[bool, str]:
    """
    Test the connection to the remote PostgreSQL database using REMOTE_POSTGRES_CONFIG.

    Returns
    -------
    tuple[bool, str]
        (success, error_message)
    """
    config = getattr(settings, "REMOTE_POSTGRES_CONFIG", {})
    
    db_name = config.get("NAME")
    db_user = config.get("USER")
    db_pass = config.get("PASSWORD")
    db_host = config.get("HOST")
    db_port = config.get("PORT", "5432")
    
    if not all([db_name, db_user, db_pass, db_host]):
        return False, "Missing remote PostgreSQL connection credentials in environment variables."

    try:
        conn = psycopg2.connect(
            host=db_host,
            port=int(db_port),
            database=db_name,
            user=db_user,
password=***REDACTED***
            connect_timeout=5
        )
        conn.close()
        return True, ""
    except Exception as exc:
        logger.error(f"PostgreSQL connection check failed: {exc}")
        return False, str(exc)

```
<!-- END_FILE -->

---
<!-- FILE: apps/projects/migrations/__init__.py -->
## apps/projects/migrations/__init__.py

```py


```
<!-- END_FILE -->

---
<!-- FILE: apps/projects/migrations/0001_initial.py -->
## apps/projects/migrations/0001_initial.py

```py
# Generated by Django 6.0.1 on 2026-01-20 10:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_id', models.CharField(help_text="Unique project identifier (e.g., 'local_20250120_143000_my_project')", max_length=255, unique=True)),
                ('display_name', models.CharField(help_text='Human-friendly name for the project', max_length=255)),
                ('storage_type', models.CharField(choices=[('local', 'Local FAISS Indexing'), ('google', 'Google File Search')], default='local', help_text='Type of storage backend (local FAISS or Google File Search)', max_length=20)),
                ('external_store_id', models.CharField(blank=True, help_text='ID from external service (e.g., Google Store ID)', max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('description', models.TextField(blank=True, help_text='Optional description of the project')),
                ('is_active', models.BooleanField(default=True, help_text='Whether this project is active')),
                ('document_count', models.IntegerField(default=0, help_text='Number of documents in this project')),
                ('last_indexed_at', models.DateTimeField(blank=True, help_text='When documents were last indexed', null=True)),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['storage_type', 'is_active'], name='projects_pr_storage_acbf1b_idx'), models.Index(fields=['-created_at'], name='projects_pr_created_775fe7_idx')],
            },
        ),
        migrations.CreateModel(
            name='SystemPrompt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(blank=True, help_text='The system prompt content for this project')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('project', models.OneToOneField(help_text='The project this prompt is associated with', on_delete=django.db.models.deletion.CASCADE, related_name='system_prompt', to='projects.project')),
            ],
            options={
                'verbose_name': 'System Prompt',
                'verbose_name_plural': 'System Prompts',
            },
        ),
    ]

```
<!-- END_FILE -->

---
<!-- FILE: apps/projects/migrations/0002_alter_project_storage_type.py -->
## apps/projects/migrations/0002_alter_project_storage_type.py

```py
# Generated by Django 6.0.1 on 2026-02-27 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='storage_type',
            field=models.CharField(choices=[('local', 'Local FAISS Indexing'), ('google', 'Google File Search'), ('rag', 'RAG')], default='local', help_text='Type of storage backend (local FAISS or Google File Search)', max_length=20),
        ),
    ]

```
<!-- END_FILE -->

---
<!-- FILE: apps/projects/migrations/0003_project_user.py -->
## apps/projects/migrations/0003_project_user.py

```py
# Generated by Django 6.0.1 on 2026-02-28 07:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_alter_project_storage_type'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='user',
            field=models.ForeignKey(blank=True, help_text='The user who owns this project', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='projects', to=settings.AUTH_USER_MODEL),
        ),
    ]

```
<!-- END_FILE -->

---
<!-- FILE: apps/projects/migrations/0004_alter_project_storage_type.py -->
## apps/projects/migrations/0004_alter_project_storage_type.py

```py
# Generated by Django 6.0.1 on 2026-05-27 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_project_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='storage_type',
            field=models.CharField(choices=[('local', 'Local FAISS Indexing'), ('google', 'Google File Search'), ('postgres', 'Postgres RAG')], default='local', help_text='Type of storage backend (local FAISS or Google File Search)', max_length=20),
        ),
    ]

```
<!-- END_FILE -->

---
<!-- FILE: apps/projects/migrations/0005_project_chunking_project_custom_prompt_and_more.py -->
## apps/projects/migrations/0005_project_chunking_project_custom_prompt_and_more.py

```py
# Generated by Django 6.0.1 on 2026-05-29 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_alter_project_storage_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='chunking',
            field=models.CharField(choices=[('fixed-size', 'Fixed-size'), ('sentence-paragraph', 'Sentence/paragraph'), ('recursive', 'Recursive'), ('document-structure', 'Document-structure'), ('semantic', 'Semantic')], default='fixed-size', help_text='Text chunking strategy', max_length=50),
        ),
        migrations.AddField(
            model_name='project',
            name='custom_prompt',
            field=models.BooleanField(default=False, help_text='Whether to use a custom prompt'),
        ),
        migrations.AddField(
            model_name='project',
            name='document_parsing',
            field=models.CharField(choices=[('pymupdf', 'PyMUPDF'), ('markitdown', 'markitdown')], default='pymupdf', help_text='Document parsing backend', max_length=50),
        ),
        migrations.AddField(
            model_name='project',
            name='embedding_model',
            field=models.CharField(choices=[('gemini-1', 'Gemini embedding 1'), ('google-2', 'Google embedding 2'), ('gemma', 'fkEmbeddingGemma')], default='gemini-1', help_text='Embedding model to use', max_length=50),
        ),
        migrations.AddField(
            model_name='project',
            name='synthesizer',
            field=models.BooleanField(default=False, help_text='Enable or disable the synthesizer'),
        ),
    ]

```
<!-- END_FILE -->

---
<!-- FILE: apps/projects/migrations/0006_project_use_markitdown_and_more.py -->
## apps/projects/migrations/0006_project_use_markitdown_and_more.py

```py
# Generated by Django 6.0.1 on 2026-06-02 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0005_project_chunking_project_custom_prompt_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='use_markitdown',
            field=models.BooleanField(default=False, help_text='Use MarkItDown pipeline'),
        ),
        migrations.AddField(
            model_name='project',
            name='use_structural_grading',
            field=models.BooleanField(default=False, help_text='Use structural quality grading'),
        ),
    ]

```
<!-- END_FILE -->

---
<!-- FILE: apps/projects/migrations/0007_alter_project_storage_type.py -->
## apps/projects/migrations/0007_alter_project_storage_type.py

```py
# Generated by Django 6.0.1 on 2026-06-02 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0006_project_use_markitdown_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='storage_type',
            field=models.CharField(choices=[('local', 'Local'), ('google', 'Google File Search'), ('postgres', 'Postgres RAG')], default='local', help_text='Type of storage backend (local FAISS or Google File Search)', max_length=20),
        ),
    ]

```
<!-- END_FILE -->

---
<!-- FILE: apps/projects/migrations/0008_alter_project_document_parsing.py -->
## apps/projects/migrations/0008_alter_project_document_parsing.py

```py
# Generated by Django 6.0.1 on 2026-06-02 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0007_alter_project_storage_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='document_parsing',
            field=models.CharField(choices=[('pymupdf', 'PyMUPDF'), ('markitdown', 'markitdown')], default='markitdown', help_text='Document parsing backend', max_length=50),
        ),
    ]

```
<!-- END_FILE -->

---
<!-- FILE: apps/projects/migrations/0009_alter_project_storage_type_and_more.py -->
## apps/projects/migrations/0009_alter_project_storage_type_and_more.py

```py
# Generated by Django 6.0.1 on 2026-06-02 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0008_alter_project_document_parsing'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='storage_type',
            field=models.CharField(choices=[('local', 'Local'), ('google', 'Google File Search'), ('postgres', 'Postgres RAG')], default='local', help_text='Type of storage backend (local or Google File Search)', max_length=20),
        ),
        migrations.AlterField(
            model_name='project',
            name='use_structural_grading',
            field=models.BooleanField(default=True, help_text='Use structural quality grading'),
        ),
    ]

```
<!-- END_FILE -->

---
<!-- FILE: apps/projects/models.py -->
## apps/projects/models.py

```py
"""
Project models for managing file search stores and projects
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Project(models.Model):
    """
    Represents a project/store for document indexing and retrieval.
    Can be backed by either Google File Search or local indexing.
    """
    
    STORAGE_TYPES = [
        ('local', 'Local'),
        ('google', 'Google File Search'),
        ('postgres', 'Postgres RAG'),
    ]
    
    # Identifiers
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='projects',
        null=True,
        blank=True,
        help_text="The user who owns this project"
    )
    project_id = models.CharField(
        max_length=255,
        unique=True,
        help_text="Unique project identifier (e.g., 'local_20250120_143000_my_project')"
    )
    display_name = models.CharField(
        max_length=255,
        help_text="Human-friendly name for the project"
    )
    
    # Storage configuration
    storage_type = models.CharField(
        max_length=20,
        choices=STORAGE_TYPES,
        default='local',
        help_text="Type of storage backend (local or Google File Search)"
    )
    external_store_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="ID from external service (e.g., Google Store ID)"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(
        blank=True,
        help_text="Optional description of the project"
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this project is active"
    )

    # Parameter Placeholders (to be defined later)
    synthesizer = models.BooleanField(
        default=False,
        help_text="Enable or disable the synthesizer"
    )
    document_parsing = models.CharField(
        max_length=50,
        choices=[
            ("markitdown", "markitdown"),
        ],
        default="markitdown",
        help_text="Document parsing backend (cannot be changed after first source is indexed)."
    )
    chunking = models.CharField(
        max_length=50,
        choices=[
            ("fixed-size", "Fixed-size"),
            ("sentence-paragraph", "Sentence/paragraph"),
            ("recursive", "Recursive"),
            ("document-structure", "Document-structure"),
            ("semantic", "Semantic"),
        ],
        default="fixed-size",
        help_text="Text chunking strategy"
    )
    embedding_model = models.CharField(
        max_length=50,
        choices=[
            ("gemini-1", "Gemini embedding 1"),
        ],
        default="gemini-1",
        help_text="Embedding model to use (cannot be changed after first source is indexed)."
    )
    custom_prompt = models.BooleanField(
        default=False,
        help_text="Whether to use a custom prompt"
    )
    use_markitdown = models.BooleanField(
        default=False,
        help_text="Use MarkItDown pipeline (cannot be changed after first source is indexed)."
    )
    use_structural_grading = models.BooleanField(
        default=True,
        help_text="Use structural quality grading"
    )
    
    # Statistics (denormalized for performance)
    document_count = models.IntegerField(
        default=0,
        help_text="Number of documents in this project"
    )
    last_indexed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When documents were last indexed"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['storage_type', 'is_active']),
            models.Index(fields=['-created_at']),
        ]
    
    def clean(self):
        """
        Validate model fields before saving.
        """
        from django.core.exceptions import ValidationError
        super().clean()
        if self.storage_type in ["local", "google"]:
            raise ValidationError({
                "storage_type": "This functionality has not been implemented yet."
            })

    def save(self, *args, **kwargs):
        """
        Overridden to automatically generate a unique, backend-compliant project_id
        if it is left blank or empty (e.g., when created via the Django Admin).
        """
        if not self.project_id:
            from datetime import datetime
            import time
            import uuid
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            microseconds = int(time.time() * 1000000) % 1000000
            safe_name = (self.display_name or "project").lower().replace(' ', '_')[:30]
            rand_suffix = uuid.uuid4().hex[:6]
            
            prefix = self.storage_type or "local"
            self.project_id = f"{prefix}_{timestamp}_{microseconds}_{safe_name}_{rand_suffix}"
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.display_name} ({self.storage_type})"


class SystemPrompt(models.Model):
    """
    Custom system prompt associated with a project.
    Used to guide the AI behavior when chatting with documents in this project.
    """
    
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='system_prompt',
        help_text="The project this prompt is associated with"
    )
    
    content = models.TextField(
        blank=True,
        help_text="The system prompt content for this project"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "System Prompt"
        verbose_name_plural = "System Prompts"
    
    def __str__(self):
        return f"Prompt for {self.project.display_name}"

```
<!-- END_FILE -->

---
<!-- FILE: apps/projects/serializers.py -->
## apps/projects/serializers.py

```py
"""
Serializers for projects app
"""

from rest_framework import serializers
from .models import Project, SystemPrompt


class SystemPromptSerializer(serializers.ModelSerializer):
    """Serializer for SystemPrompt model"""
    
    class Meta:
        model = SystemPrompt
        fields = ['id', 'project', 'content', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project model"""
    system_prompt = SystemPromptSerializer(read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'project_id', 'display_name', 'storage_type',
            'external_store_id', 'description', 'is_active',
            'document_count', 'last_indexed_at', 'created_at',
            'updated_at', 'system_prompt'
        ]
        read_only_fields = ['created_at', 'updated_at', 'document_count', 'last_indexed_at']


class ProjectCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating projects"""
    
    class Meta:
        model = Project
        fields = ['project_id', 'display_name', 'storage_type', 'description']
        
    def validate_storage_type(self, value):
        """Validate storage type"""
        if value in ['local', 'google']:
            raise serializers.ValidationError("This functionality has not been implemented yet.")
        if value not in ['local', 'google', 'postgres']:
            raise serializers.ValidationError("Storage type must be 'local', 'google', or 'postgres'")
        return value


class ProjectUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating projects"""
    
    class Meta:
        model = Project
        fields = ['display_name', 'description', 'is_active']


class ProjectListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing projects"""
    
    class Meta:
        model = Project
        fields = [
            'id', 'project_id', 'display_name', 'storage_type',
            'document_count', 'created_at', 'is_active'
        ]

```
<!-- END_FILE -->

---
<!-- FILE: apps/projects/tests.py -->
## apps/projects/tests.py

```py
from django.test import TestCase

# Create your tests here.

```
<!-- END_FILE -->

---
<!-- FILE: apps/projects/urls.py -->
## apps/projects/urls.py

```py
"""
URL routing for projects app (pages only)
"""

from django.urls import path
from . import views

app_name = 'projects'

# API endpoints are handled by apps/api/api_urls.py
# Page routes for HTML rendering
urlpatterns = [
    path('list/', views.list_projects, name='list'),
    path('create/', views.create_project, name='create'),
    path('delete/<str:store_id>/', views.delete_project, name='delete'),
]

```
<!-- END_FILE -->

---
<!-- FILE: apps/projects/views.py -->
## apps/projects/views.py

```py
"""
Project views for managing file search stores and projects
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import sys
import os

# Add src to path to import Flask modules (temporarily)
from src.local_project_storage import get_local_project_storage
from src.optional_dependencies import LazyModuleProxy
from src.prompt_storage import get_prompt_storage

from .models import Project, SystemPrompt
from .serializers import ProjectSerializer, SystemPromptSerializer
from .db_utils import test_postgres_connection



gfs = LazyModuleProxy(
    "src.google_file_search",
    "Google File Search dependencies are not installed in this environment.",
)


def _user_can_access_project(project, user):
    """Return whether the current user can access the given project."""
    if not project or project.user_id is None:
        return True

    return bool(getattr(user, 'is_authenticated', False) and user.id == project.user_id)


def get_combined_stores(request=None):
    """Get list of projects for the current user from Django database"""
    if request and request.user.is_authenticated:
        projects = Project.objects.filter(user=request.user).order_by('-created_at')
    else:
        # Show projects without an owner for unauthenticated users (legacy behavior)
        projects = Project.objects.filter(user__isnull=True).order_by('-created_at')
    
    # Convert to store-like objects for template compatibility
    stores = [
        type('Store', (), {
            'name': project.project_id,  # Use project_id consistently for both types
            'display_name': project.display_name,
            'create_time': project.created_at,
            'storage_type': project.storage_type
        })()
        for project in projects
    ]
    
    return stores


@login_required
@require_http_methods(["GET"])
def list_projects(request):
    """List all projects/stores"""
    stores = get_combined_stores(request)
    list_type = request.GET.get('type', 'admin')
    
    if list_type == 'chat':
        return render(request, 'partials/chat_project_list.html', {'stores': stores})
    elif list_type == 'evaluate':
        return render(request, 'partials/evaluate_project_list.html', {'stores': stores})
    
    return render(request, 'partials/project_list.html', {'stores': stores})


@require_http_methods(["POST"])
@csrf_exempt
def create_project(request):
    """Create a new project"""
    storage = get_local_project_storage()
    
    display_name = request.POST.get('display_name')
    storage_type = request.POST.get('storage_type', 'google')
    user = request.user if request.user.is_authenticated else None
    
    if display_name:
        if storage_type in ['local', 'google']:
            error_html = (
                f'<div id="project-error-container" hx-swap-oob="true" '
                f'class="mb-4 p-3 bg-red-50 text-red-700 rounded-md border border-red-200 text-sm">'
                f'<strong>Error:</strong> This functionality has not been implemented yet.'
                f'</div>'
            )
            return HttpResponse(error_html)
        elif storage_type == 'postgres':
            success, error_message = test_postgres_connection()
            if not success:
                error_html = (
                    f'<div id="project-error-container" hx-swap-oob="true" '
                    f'class="mb-4 p-3 bg-red-50 text-red-700 rounded-md border border-red-200 text-sm">'
                    f'<strong>Connection failed:</strong> {error_message}'
                    f'</div>'
                )
                return HttpResponse(error_html)

            from datetime import datetime
            import time
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            microseconds = int(time.time() * 1000000) % 1000000
            safe_name = display_name.lower().replace(' ', '_')[:30]
            project_id = f"postgres_{timestamp}_{microseconds}_{safe_name}"
            Project.objects.create(
                project_id=project_id,
                display_name=display_name,
                storage_type='postgres',
                user=user
            )
    
    stores = get_combined_stores(request)
    response_content = (
        '<div id="project-error-container" hx-swap-oob="true"></div>\n'
        + render(request, "partials/project_list.html", {"stores": stores}).content.decode("utf-8")
    )
    response = HttpResponse(response_content)
    response["HX-Trigger"] = "projectCreated"
    return response



@require_http_methods(["DELETE"])
@csrf_exempt
def delete_project(request, store_id):
    """Delete a project"""
    storage = get_local_project_storage()
    
    # Try to find the project in Django database
    try:
        # Find by project_id or external_store_id
        project = Project.objects.filter(
            models.Q(project_id=store_id) | models.Q(external_store_id=store_id)
        ).first()
        
        if project:
            try:
                if project.storage_type == 'local':
                    storage.delete_project(project.project_id)
                elif project.storage_type == 'postgres':
                    from src.postgres_rag import cleanup_project_artifacts

                    document_names = sorted(project.documents.values_list('document_name', flat=True))
                    cleanup_project_artifacts(project.project_id, document_names)
                else:
                    # Delete from Google File Search
                    if project.external_store_id:
                        gfs.delete_file_search_store(project.external_store_id)
            except Exception as cleanup_error:
                print(f"Warning: external cleanup failed for {store_id}: {cleanup_error}")

            # Always delete the Django database record
            project.delete()
    except Exception as e:
        print(f"Error deleting project {store_id}: {e}")
    
    stores = get_combined_stores(request)
    return render(request, 'partials/project_list.html', {'stores': stores})


@require_http_methods(["GET", "POST"])
@csrf_exempt
def manage_prompt(request, store_id):
    """Get or set system prompt for a project"""
    project = Project.objects.filter(project_id=store_id).first()

    if not _user_can_access_project(project, getattr(request, 'user', None)):
        return JsonResponse({'error': 'Forbidden'}, status=403)

    if project and project.storage_type == 'postgres':
        if request.method == 'GET':
            prompt = getattr(project.system_prompt, 'content', '') if hasattr(project, 'system_prompt') else ''
            return JsonResponse({'prompt': prompt})

        content = request.POST.get('content', '')
        SystemPrompt.objects.update_or_create(
            project=project,
            defaults={'content': content}
        )
        return JsonResponse({'status': 'success', 'prompt': content})

    prompt_storage = get_prompt_storage()
    
    if request.method == 'GET':
        prompt = prompt_storage.get_prompt(store_id)
        return JsonResponse({'prompt': prompt})
    
    # POST - set prompt
    content = request.POST.get('content', '')
    prompt_storage.set_prompt(store_id, content)
    
    return JsonResponse({'status': 'success', 'prompt': content})

```
<!-- END_FILE -->

---
<!-- FILE: google_file_search.py -->
## google_file_search.py

```py
import time
from google import genai
from google.genai import errors as genai_errors
from google.genai import types 
import dotenv
import os
import requests


#read GOOGLE_API_KEY from file .env 
dotenv.load_dotenv()
API_KEY=***REDACTED***

if not API_KEY:
    print("WARNING: GOOGLE_API_KEY environment variable not set - API functions will fail at runtime")
else:
    os.environ["GOOGLE_API_KEY"] = API_KEY

os.environ["GEMINI_API_KEY"] = API_KEY

client = genai.Client(api_key=API_KEY) if API_KEY else genai.Client()


class GoogleFileSearchPermissionError(RuntimeError):
    """Raised when the configured Google API credentials cannot access a file search store."""


def _is_permission_error(exc: Exception) -> bool:
    return isinstance(exc, genai_errors.ClientError) and getattr(exc, "code", None) == 403


def create_new_file_search_store(store_display_name: str) -> str:
    """
    Creates a new, empty File Search Store and returns its unique resource name.

    Args:
        store_display_name: The human-readable name for the store (e.g., "Finance_Site_Knowledge").

    Returns:
        The unique store ID (resource name), e.g., 'fileSearchStores/abc-123'.
    """
    
    print(f"Attempting to create store: {store_display_name}...")
    
    try:
        # The .create method is what provisions the new store on Google's backend
        file_search_store = client.file_search_stores.create(
            config={'display_name': store_display_name}
        )
        
        # The .name attribute holds the unique, persistent ID
        store_id = file_search_store.name
        
        print(f"✅ Successfully created store: '{store_display_name}'")
        print(f"   Resource ID: {store_id}\n")
        
        return store_id
        
    except Exception as e:
        print(f"❌ Failed to create store: {e}")
        return ""

def list_all_file_search_stores():
    """Retrieves and prints the list of all File Search Stores."""
    
    print("Fetching list of all File Search Stores...")
    
    try:
        # The list() method returns a PagedList (an iterable object)
        pager = client.file_search_stores.list()
        
        stores = list(pager)
        
        if not stores:
            print("No File Search Stores found for this project.")
            return []

        print(f"\nFound {len(stores)} File Search Store(s):")
        print("=" * 40)

        for store in stores:
            # 🔑 .name is the unique ID you need for API calls
            store_id = store.name
            
            # 🔑 .display_name is the human-readable name you set during creation
            display_name = store.display_name
            
            print(f"Chatbot Name:    {display_name}")
            print(f"Resource ID:     {store_id}")
            print(f"Created On:      {store.create_time.date()}")
            print("-" * 40)
            
        return stores

    except Exception as e:
        print(f"An error occurred while listing stores: {e}")
        return []

def delete_file_search_store(store_id_to_delete: str):
    """
    Deletes a specified File Search Store and all its contents permanently.

    Args:
        store_id_to_delete: The unique resource ID of the store 
                            (e.g., 'fileSearchStores/abc-123').
    """
    
    print(f"⚠️ Attempting to permanently delete store: {store_id_to_delete}...")
    
    try:
        # The .delete method requires the 'name' (the store_id)
        # force=True is required to confirm the removal of all resources
        client.file_search_stores.delete(
            name=store_id_to_delete,
        )
        
        print(f"✅ Successfully deleted store: {store_id_to_delete}")
        
    except Exception as e:
        print(f"❌ Failed to delete store {store_id_to_delete}: {e}")

def add_document_to_store(store_id: str, file_path: str) -> str:
    """
    Uploads a document to a specified File Search Store and waits for indexing to complete.

    Args:
        store_id: The unique resource ID of the target store 
                  (e.g., 'fileSearchStores/abc-123').
        file_path: The local path to the document you want to upload.

    Returns:
        The resource name of the uploaded document if successful, otherwise an empty string.
    """
    
    file_name = os.path.basename(file_path)
    print(f"Uploading and indexing '{file_name}' into store: {store_id}...")
    
    try:
        # The upload_to_file_search_store method initiates the indexing process
        operation = client.file_search_stores.upload_to_file_search_store(
            file=file_path,
            file_search_store_name=store_id,
            config={'display_name': file_name}
        )
        
        print("   ⌛ Waiting for file indexing to complete (This may take a moment)...")

        # --- Wait for Indexing ---
        # Polling the operation ensures the file is fully indexed before you query
        while not operation.done:
            time.sleep(5)
            operation = client.operations.get(operation)

        # Get the result from the completed operation
        # Note: operation.result() is failing with AttributeError in some versions
        
        # Workaround: Fetch the document by name from the store
        print("   Verifying upload...")
        pager = client.file_search_stores.documents.list(parent=store_id)
        all_docs = list(pager)
        
        # Find documents with matching display name
        matching_docs = [d for d in all_docs if d.display_name == file_name]
        
        if matching_docs:
            # Get the most recently created one
            newest_doc = max(matching_docs, key=lambda d: d.create_time)
            document_resource_name = newest_doc.name
            print(f"   ✅ Indexing complete! Document Resource Name: {document_resource_name}\n")
            return document_resource_name
        else:
             raise Exception(f"Document {file_name} not found in store after upload.")
        
    except Exception as e:
        print(f"❌ Failed to add document to store: {e}")
        if _is_permission_error(e):
            raise GoogleFileSearchPermissionError(
                f"Google File Search permission denied for store {store_id}. Check that the configured API key can access this store and that the store still exists."
            ) from e
        return ""

def ask_store_question(store_id: str, query: str, system_prompt: str = None) -> str:
    """
    Asks a question, grounding the answer ONLY in the documents of the specified store.

    Args:
        store_id: The unique resource ID of the target store 
                  (e.g., 'fileSearchStores/abc-123').
        query: The user's question.
        system_prompt: Optional custom system prompt to guide the model's response.

    Returns:
        The model's answer, potentially with citations.
    """
    
    MODEL = "gemini-2.5-flash-lite" # Supports File Search properly
    
    print(f"Querying store '{store_id}' with model {MODEL}...")
    if system_prompt:
        print(f"Using custom system prompt...")
    
    try:
        # --- 1. Configure the FileSearch Tool ---
        from google.genai import types as genai_types
        
        # Create the file search configuration
        file_search_config = genai_types.FileSearch(
            file_search_store_names=[store_id]
        )
        
        # Create tool with file_search
        file_search_tool = genai_types.Tool(
            file_search=file_search_config
        )

        # --- 2. Build GenerateContentConfig with system_instruction ---
        config_kwargs = {
            'tools': [file_search_tool]
        }
        
        if system_prompt:
            config_kwargs['system_instruction'] = system_prompt
            print(f"[DEBUG] System instruction set: {system_prompt[:50]}...")

        # --- 3. Generate Content ---
        response = client.models.generate_content(
            model=MODEL,
            contents=query,
            config=types.GenerateContentConfig(**config_kwargs)
        )

        # --- 4. Format and Return Response ---
        
        if not response.candidates:
             return "No response candidates returned from model."

        answer_text = response.text
        if answer_text is None:
             # Fallback if text is blocked or empty
             if response.candidates[0].finish_reason:
                  return f"Response blocked or finished early: {response.candidates[0].finish_reason}"
             return "No text response generated."
        
        # Optional: Append citations for verification
        citations = []
        if response.candidates and response.candidates[0].grounding_metadata:
            for chunk in response.candidates[0].grounding_metadata.grounding_chunks:
                # The title is the file's display name set during upload
                if chunk.retrieved_context:
                    citations.append(chunk.retrieved_context.title)
        
        if citations:
            answer_text += "\n\n**Sources:** " + ", ".join(set(citations))

        return answer_text

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error processing query: {e}"
    

def list_documents_in_store(store_id: str):
    """
    Retrieves and prints the list of all documents within a specified File Search Store.

    Args:
        store_id: The unique resource ID of the target store 
                  (e.g., 'fileSearchStores/abc-123').
    """
    
    print(f"Fetching documents for store: {store_id}...")
    
    try:
        # The list method is on the 'documents' resource of the store.
        # It requires the 'parent' argument, which is the store's ID.
        pager = client.file_search_stores.documents.list(parent=store_id)
        
        documents = list(pager)
        
        if not documents:
            print(f"No documents found in store: {store_id}")
            return []

        print(f"\nFound {len(documents)} document(s) in the store:")
        print("=" * 60)

        for doc in documents:
            # doc.name is the full Document Resource Name (used for deletion)
            doc_resource_name = doc.name
            
            # doc.display_name is the human-readable name (used for filtering)
            display_name = doc.display_name
            
            print(f"File Name (for filtering): {display_name}")
            print(f"Document ID (for deletion): {doc_resource_name}")
            print(f"State: {doc.state.name}") # State should be 'ACTIVE'
            print("-" * 60)
        
        return documents
        
        
            
    except Exception as e:
        print(f"❌ Failed to list documents for store {store_id}: {e}")
        return []
 
def delete_document_from_store(document_resource_name: str):
    """
    Deletes a specific document and its indexed embeddings from a File Search Store.
    Uses the REST API directly to delete the document.

    Args:
        document_resource_name: The full resource ID of the document to delete 
                                (e.g., 'fileSearchStores/mysecondfilesearchstore-1m3ju15v7hjz/documents/data2txt-dr72i7yy967c').
    """
    
    print(f"⚠️ Attempting to delete document: {document_resource_name}...")
    
    try:
        # Construct the full API endpoint URL with API key as query parameter
        api_url = f"https://generativelanguage.googleapis.com/v1beta/{document_resource_name}?key={API_KEY}&force=true"
        
        # Set up headers
        headers = {
            "Content-Type": "application/json",
        }
        
        # Make DELETE request
        response = requests.delete(api_url, headers=headers)
        
        # Check for successful response
        if response.status_code == 200:
            print(f"✅ Successfully deleted document: {document_resource_name}")
        elif response.status_code == 404:
            print(f"⚠️ Document not found: {document_resource_name}")
        else:
            # Raise exception for other potential errors
            raise Exception(f"API Error {response.status_code}: {response.text}")
        
    except Exception as e:
        print(f"❌ Failed to delete document {document_resource_name}: {e}")
 
def main():
    pass
    # add_document_to_store(store_id = "fileSearchStores/myfirstfilesearchstore-kdvasuq6oqk8", file_path="/Users/chrys/Gemini File Search/data1.txt")
    # add_document_to_store(store_id = "fileSearchStores/mysecondfilesearchstore-1m3ju15v7hjz", file_path="/Users/chrys/Gemini File Search/data2.txt")    

    # USER_QUESTION1 = "What is Happy Payments?"
    # USER_QUESTION2 = "What is Sad Payments?"
    
    # final_answer1 = ask_store_question("fileSearchStores/myfirstfilesearchstore-kdvasuq6oqk8", USER_QUESTION1)
    
    # print("\n--- Answer1 ---")
    # print(final_answer1)
    
    # final_answer2 = ask_store_question("fileSearchStores/mysecondfilesearchstore-1m3ju15v7hjz", USER_QUESTION2)
    
    # print("\n--- Answer2 ---")
    # print(final_answer2)
   
   #get all stores and go through their documents and delete them all 
    # stores = list_all_file_search_stores()
    # if stores:
    #     for store in stores:
    #         store_id = store.name
    #         print(f"Processing store: {store_id}")
    #         #list documents in store
    #         pager = client.file_search_stores.documents.list(parent=store_id)
    #         documents = list(pager)
    #         for doc in documents:
    #             doc_resource_name = doc.name
    #             delete_document_from_store(doc_resource_name)
    
    #get all stores and list ttheir documents
    stores = list_all_file_search_stores()
    if stores:
        for store in stores:
            store_id = store.name
            print(f"Processing store: {store_id}")
            #list documents in store
            list_documents_in_store(store_id)
            
    # delete_document_from_store("fileSearchStores/mysecondfilesearchstore-1m3ju15v7hjz/documents/data2txt-dr72i7yy967c")
    
    # stores = list_all_file_search_stores()
    # if stores:
    #     for store in stores:
    #         store_id = store.name
    #         print(f"Processing store: {store_id}")
    #         #list documents in store
    #         list_documents_in_store(store_id)

if __name__ == "__main__":
    main()

```
<!-- END_FILE -->

---
<!-- FILE: local_project_storage.py -->
## local_project_storage.py

```py
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from copy import deepcopy

class LocalProjectStorage:
    """Handles loading and saving local projects to a JSON file"""
    
    def __init__(self, data_dir: str = None):
        """
        Initialize local project storage
        
        Args:
            data_dir: Directory to store local_projects.json file. Defaults to project root/configuration.
        """
        if data_dir is None:
            # Get the project root (parent of src) then add configuration subdirectory
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(project_root, 'configuration')
        
        self.data_dir = data_dir
        self.projects_file = os.path.join(data_dir, 'local_projects.json')
        self.projects = self._load_projects()
    
    def _load_projects(self) -> dict:
        """Load projects from JSON file or create empty dict if file doesn't exist"""
        # Ensure directory exists first
        os.makedirs(self.data_dir, exist_ok=True)
        
        if os.path.exists(self.projects_file):
            try:
                with open(self.projects_file, 'r') as f:
                    content = f.read().strip()
                    if not content:
                        print(f"📝 Local projects file is empty at {self.projects_file}. Starting with empty projects.")
                        return {}
                    projects = json.loads(content)
                    print(f"✅ Loaded {len(projects)} local projects from {self.projects_file}")
                    return projects
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️ Error reading local projects file: {e}. Starting with empty projects.")
                return {}
        else:
            print(f"📝 No local projects file found at {self.projects_file}. Creating new one on first save.")
            return {}
    
    def _save_projects(self):
        """Save projects to JSON file"""
        try:
            # Ensure directory exists
            os.makedirs(self.data_dir, exist_ok=True)
            
            with open(self.projects_file, 'w') as f:
                json.dump(self.projects, f, indent=2)
            print(f"✅ Saved local projects to {self.projects_file}")
        except IOError as e:
            print(f"❌ Error saving local projects: {e}")
    
    def create_project(self, display_name: str) -> str:
        """
        Create a new local project
        
        Args:
            display_name: The display name for the project
            
        Returns:
            The unique project ID
        """
        try:
            # Generate a unique ID based on timestamp and name
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            project_id = f"local_{timestamp}_{display_name.lower().replace(' ', '_')}"
            
            self.projects[project_id] = {
                "id": project_id,
                "display_name": display_name,
                "created_at": datetime.now().isoformat(),
                "documents": {}  # Store as dict: {document_name: {indexed_at, ...}}
            }
            
            self._save_projects()
            print(f"✅ Created local project: {display_name} (ID: {project_id})")
            return project_id
        except Exception as e:
            print(f"❌ Error creating local project: {e}")
            raise
    
    def get_project(self, project_id: str) -> Optional[dict]:
        """Get a project by ID"""
        return self.projects.get(project_id)
    
    def list_projects(self) -> List[dict]:
        """Get all local projects"""
        return list(self.projects.values())
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project"""
        if project_id in self.projects:
            del self.projects[project_id]
            self._save_projects()
            print(f"✅ Deleted local project: {project_id}")
            return True
        return False
    
    def add_document(self, project_id: str, document_name: str) -> bool:
        """Add a document to a project with metadata"""
        if project_id in self.projects:
            self.projects[project_id]["documents"][document_name] = {
                "indexed_at": datetime.now().isoformat()
            }
            self._save_projects()
            print(f"✅ Added document to project: {document_name}")
            return True
        return False
    
    def remove_document(self, project_id: str, document_name: str) -> bool:
        """Remove a document from a project"""
        if project_id in self.projects:
            if document_name in self.projects[project_id]["documents"]:
                del self.projects[project_id]["documents"][document_name]
                self._save_projects()
                print(f"✅ Removed document from project: {document_name}")
                return True
        return False
    
    def get_all_projects(self) -> dict:
        """Get all projects as a deep copy"""
        return deepcopy(self.projects)


# Global instance
local_project_storage = None

def get_local_project_storage() -> LocalProjectStorage:
    """Get or create the global local project storage instance"""
    global local_project_storage
    if local_project_storage is None:
        local_project_storage = LocalProjectStorage()
    return local_project_storage

```
<!-- END_FILE -->

---
<!-- FILE: local_rag.py -->
## local_rag.py

```py
import os
from typing import List, Optional, Dict
from datetime import datetime
import pypdf
from pathlib import Path
import json
import pickle

try:
    import faiss
    import numpy as np
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    from llama_index.core import Document, VectorStoreIndex
    from llama_index.embeddings.ollama import OllamaEmbedding
    from llama_index.llms.ollama import Ollama
    from llama_index.core.node_parser import SimpleNodeParser
    LLAMAINDEX_AVAILABLE = True
except ImportError:
    LLAMAINDEX_AVAILABLE = False


class LocalRAGEngine:
    """Handles RAG operations for local projects using Ollama and FAISS"""
    
    def __init__(self, project_id: str, data_dir: str = None):
        """
        Initialize RAG engine for a project
        
        Args:
            project_id: The local project ID
            data_dir: Directory for FAISS index storage. Defaults to project root/rag_data
        """
        if not LLAMAINDEX_AVAILABLE or not FAISS_AVAILABLE:
            raise ImportError(
                "LocalRAGEngine requires faiss and llama-index packages. "
                "Install with: pip install faiss-cpu llama-index llama-index-llms-ollama "
                "llama-index-embeddings-ollama"
            )
        
        self.project_id = project_id
        
        if data_dir is None:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(project_root, 'rag_data', project_id)
        
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize embeddings model
        self.embed_model = OllamaEmbedding(
            model_name="embeddinggemma",
            base_url="http://localhost:11434"
        )
        
        # Initialize LLM
        self.llm = Ollama(
            model="gemma3:4b",
            base_url="http://localhost:11434",
            temperature=0.7
        )
        
        # Initialize FAISS index with IndexIDMap for efficient deletion
        self.index_path = os.path.join(self.data_dir, "faiss_index.bin")
        self.metadata_path = os.path.join(self.data_dir, "metadata.json")
        
        self.documents = {}  # Store document content by ID
        self.metadata = {}   # Store metadata
        self.embedding_dim = None  # Will be determined from first embedding
        self.index = None
        self.id_counter = 0  # Counter for assigning document IDs
        
        # Load existing index if it exists
        self._load_index()
        
        print(f"✅ RAG Engine initialized for project: {project_id}")
    
    def _load_index(self):
        """Load FAISS IndexIDMap from disk if it exists"""
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            try:
                print(f"📂 Loading FAISS index from disk...")
                # Load metadata first to get ID counter and data
                with open(self.metadata_path, 'r') as f:
                    data = json.load(f)
                    self.metadata = {int(k): v for k, v in data.get('metadata', {}).items()}
                    self.documents = {int(k): v for k, v in data.get('documents', {}).items()}
                    # Use stored embedding_dim if available, otherwise will be set on first embedding
                    stored_dim = data.get('embedding_dim')
                    if stored_dim:
                        self.embedding_dim = stored_dim
                        print(f"📂 Loaded embedding_dim from metadata: {self.embedding_dim}")
                    self.id_counter = data.get('id_counter', max(self.metadata.keys()) + 1 if self.metadata else 0)
                print(f"📂 Loaded metadata with {len(self.metadata)} documents (IDs: {sorted(self.metadata.keys())})")
                
                # Load the FAISS index
                loaded_index = faiss.read_index(self.index_path)
                print(f"📂 Loaded raw index type: {type(loaded_index).__name__} with {loaded_index.ntotal} vectors")
                
                # If it's already an IndexIDMap, use it directly; otherwise, we have a problem
                if isinstance(loaded_index, faiss.IndexIDMap):
                    self.index = loaded_index
                    print(f"✅ Index is already IndexIDMap with IDs intact")
                else:
                    # This shouldn't happen if we saved correctly, but warn user
                    print(f"⚠️ WARNING: Loaded index is not IndexIDMap! Type: {type(loaded_index).__name__}")
                    print(f"⚠️ This indicates the save didn't preserve the IndexIDMap wrapper!")
                    # Try to rewrap it, but this will lose the original IDs
                    self.index = faiss.IndexIDMap(loaded_index)
                    print(f"⚠️ Rewrapped as IndexIDMap, but IDs may be lost. Document count: {self.index.ntotal}")
                
                print(f"✅ Loaded FAISS IndexIDMap with {self.index.ntotal} documents")
                
                # Sanity check: index vector count should match metadata count
                if self.index.ntotal != len(self.metadata):
                    print(f"⚠️ MISMATCH: Index has {self.index.ntotal} vectors but metadata has {len(self.metadata)} documents!")
                    print(f"⚠️ This could cause inconsistency issues!")
                    
            except Exception as e:
                print(f"⚠️ Error loading index: {e}")
                import traceback
                traceback.print_exc()
                self.index = None
        
        if self.index is None:
            # Create new IndexIDMap with FlatL2
            # Use a temporary dimension; it will be set to actual dimension on first indexing
            temp_dim = self.embedding_dim if self.embedding_dim else 768  # Default to 768 (Ollama embeddinggemma dimension)
            quantizer = faiss.IndexFlatL2(temp_dim)
            self.index = faiss.IndexIDMap(quantizer)
            self.embedding_dim = temp_dim  # Set embedding_dim now
            self.id_counter = 0
            print(f"📊 Created new FAISS IndexIDMap (dimension: {self.embedding_dim})")
    
    def _save_index(self):
        """Save FAISS IndexIDMap and metadata to disk"""
        try:
            if self.index is not None:
                print(f"💾 Saving FAISS index with {self.index.ntotal} documents...")
                # For IndexIDMap, we need to save the wrapper itself, not the base index
                # Make sure we're saving the complete IndexIDMap with IDs intact
                faiss.write_index(self.index, self.index_path)
                print(f"💾 Saved FAISS IndexIDMap to {self.index_path}")
                
                # Verify the save by reading it back
                try:
                    test_index = faiss.read_index(self.index_path)
                    print(f"✅ Verified save: index has {test_index.ntotal} vectors")
                except Exception as ve:
                    print(f"⚠️ Warning: Could not verify index save: {ve}")
                
                # Save metadata with ID counter
                with open(self.metadata_path, 'w') as f:
                    json.dump({
                        'metadata': {str(k): v for k, v in self.metadata.items()},
                        'documents': {str(k): v for k, v in self.documents.items()},
                        'embedding_dim': self.embedding_dim,
                        'id_counter': self.id_counter
                    }, f, indent=2)
                print(f"💾 Saved metadata with {len(self.metadata)} documents to {self.metadata_path}")
        except Exception as e:
            print(f"❌ Error saving index: {e}")
            import traceback
            traceback.print_exc()
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
            print(f"✅ Extracted text from PDF: {len(text)} characters")
            return text
        except Exception as e:
            print(f"❌ Error extracting PDF: {e}")
            raise
    
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from various file formats"""
        file_ext = Path(file_path).suffix.lower()
        
        try:
            if file_ext == '.pdf':
                return self.extract_text_from_pdf(file_path)
            elif file_ext in ['.txt', '.md']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                print(f"✅ Extracted text from {file_ext}: {len(text)} characters")
                return text
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
        except Exception as e:
            print(f"❌ Error extracting text: {e}")
            raise
    
    def index_document(self, file_path: str, document_name: str) -> bool:
        """
        Index a document by extracting text and creating embeddings in FAISS IndexIDMap
        
        Args:
            file_path: Path to the document file
            document_name: Name/ID for the document
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract text from file
            text = self.extract_text_from_file(file_path)
            
            if not text:
                print(f"⚠️ No text extracted from document: {document_name}")
                return False
            
            # Create embedding using Ollama
            embedding = self.embed_model.get_text_embedding(text)
            embedding_array = np.array([embedding], dtype=np.float32)
            
            # Validate embedding dimension
            embedding_dim = len(embedding)
            print(f"📊 Embedding dimension: {embedding_dim}, Index dimension: {self.embedding_dim}")
            
            # Initialize FAISS index if not already done
            if self.index is None:
                self.embedding_dim = embedding_dim
                quantizer = faiss.IndexFlatL2(self.embedding_dim)
                self.index = faiss.IndexIDMap(quantizer)
                print(f"📊 Created FAISS IndexIDMap with dimension {self.embedding_dim}")
            elif embedding_dim != self.embedding_dim:
                # Dimension mismatch - this shouldn't happen but let's handle it
                print(f"⚠️ Embedding dimension mismatch! Expected {self.embedding_dim}, got {embedding_dim}")
                print(f"⚠️ Recreating index with correct dimension...")
                self.embedding_dim = embedding_dim
                quantizer = faiss.IndexFlatL2(self.embedding_dim)
                self.index = faiss.IndexIDMap(quantizer)
                self.id_counter = 0
                self.metadata = {}
                self.documents = {}
            
            # Assign document ID and add to FAISS with ID
            doc_id = self.id_counter
            self.id_counter += 1
            doc_id_array = np.array([doc_id], dtype=np.int64)
            self.index.add_with_ids(embedding_array, doc_id_array)
            
            # Store metadata and document
            self.metadata[doc_id] = {
                "document_name": document_name,
                "file_path": file_path,
                "indexed_at": datetime.now().isoformat(),
                "project_id": self.project_id
            }
            self.documents[doc_id] = text
            
            print(f"✅ Indexed document: {document_name} (ID: {doc_id})")
            print(f"📊 Index size: {self.index.ntotal} documents")
            
            # Save to disk
            self._save_index()
            
            return True
            
        except Exception as e:
            print(f"❌ Error indexing document: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def query(self, query_text: str, top_k: int = 3) -> dict:
        """
        Query the indexed documents
        
        Args:
            query_text: The query string
            top_k: Number of relevant documents to retrieve
            
        Returns:
            Dictionary with query response and source documents
        """
        try:
            # Check if index exists and has documents
            if self.index is None or self.index.ntotal == 0:
                print(f"⚠️ [QUERY] No documents in index")
                return {
                    "response": "I don't have any indexed documents to answer this question. Please upload documents first.",
                    "source_nodes": []
                }
            
            # Embed the query
            query_embedding = self.embed_model.get_text_embedding(query_text)
            query_array = np.array([query_embedding], dtype=np.float32)
            
            # Determine actual k value
            actual_k = min(top_k, self.index.ntotal)
            print(f"📊 [QUERY] Searching {actual_k} results (top_k={top_k}, available={self.index.ntotal})")
            
            # Query FAISS
            distances, indices = self.index.search(query_array, actual_k)
            
            print(f"📊 [QUERY] FAISS returned {len(indices[0])} results")
            
            # Extract documents and create context
            source_docs = []
            context_text = ""
            
            for i, doc_id in enumerate(indices[0]):
                if doc_id >= 0:  # -1 means no result found
                    if doc_id in self.documents:
                        metadata = self.metadata.get(doc_id, {})
                        doc_text = self.documents[doc_id]
                        distance = float(distances[0][i])
                        
                        source_docs.append({
                            "document": metadata.get("document_name", f"Doc {doc_id}"),
                            "score": distance
                        })
                        context_text += f"\n---\nDocument: {metadata.get('document_name')}\n{doc_text[:1000]}\n"  # Limit context
            
            print(f"📊 [QUERY] Found {len(source_docs)} source documents: {[s['document'] for s in source_docs]}")
            
            # Generate response using LLM
            if len(source_docs) == 0:
                response_text = "I don't have any indexed documents to answer this question. Please upload documents first."
            else:
                prompt = f"Based on the following documents, answer this question: {query_text}\n\nDocuments:{context_text}"
                response_text = self.llm.complete(prompt).text if hasattr(self.llm, 'complete') else f"No relevant documents found for: {query_text}"
            
            return {
                "response": response_text,
                "source_nodes": source_docs
            }
        except Exception as e:
            print(f"❌ Error querying documents: {e}")
            raise
    
    def get_collection_info(self) -> dict:
        """Get information about the indexed documents"""
        try:
            return {
                "project_id": self.project_id,
                "index_name": "FAISS",
                "document_count": self.index.ntotal if self.index else 0,
                "data_dir": self.data_dir
            }
        except Exception as e:
            print(f"⚠️ Error getting index info: {e}")
            return {
                "project_id": self.project_id,
                "index_name": "FAISS",
                "document_count": 0,
                "data_dir": self.data_dir
            }
    
    def delete_document(self, document_name: str) -> bool:
        """Delete a document from FAISS IndexIDMap by document name"""
        try:
            print(f"📊 Attempting to delete: '{document_name}'")
            
            # Find the document ID by name
            doc_id_to_delete = None
            for doc_id, meta in self.metadata.items():
                if meta.get("document_name") == document_name:
                    doc_id_to_delete = doc_id
                    break
            
            if doc_id_to_delete is not None:
                # Remove from metadata and documents first
                del self.metadata[doc_id_to_delete]
                del self.documents[doc_id_to_delete]
                
                print(f"✅ Deleted document: {document_name}")
                print(f"📊 Remaining documents: {len(self.metadata)}")
                
                # Rebuild the FAISS index with remaining documents
                # This ensures embeddings are actually removed (remove_ids can leave orphaned vectors)
                if len(self.metadata) > 0:
                    print(f"🔄 Rebuilding FAISS index with remaining documents...")
                    embeddings_list = []
                    id_list = []
                    
                    # Get embeddings for all remaining documents
                    for doc_id in sorted(self.metadata.keys()):
                        text = self.documents[doc_id]
                        embedding = self.embed_model.get_text_embedding(text)
                        embeddings_list.append(embedding)
                        id_list.append(doc_id)
                    
                    # Create new index with remaining documents
                    embeddings_array = np.array(embeddings_list, dtype=np.float32)
                    id_array = np.array(id_list, dtype=np.int64)
                    
                    quantizer = faiss.IndexFlatL2(self.embedding_dim)
                    self.index = faiss.IndexIDMap(quantizer)
                    self.index.add_with_ids(embeddings_array, id_array)
                    
                    print(f"✅ Rebuilt FAISS index with {len(self.metadata)} documents")
                else:
                    # No documents left - create empty index
                    print(f"🔄 Clearing FAISS index (no documents left)...")
                    quantizer = faiss.IndexFlatL2(self.embedding_dim)
                    self.index = faiss.IndexIDMap(quantizer)
                    print(f"✅ FAISS index cleared")
                
                self._save_index()
                return True
            else:
                print(f"⚠️ Document not found: {document_name}")
                return False
        except Exception as e:
            print(f"❌ Error deleting document: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def clear_collection(self) -> bool:
        """Clear all embeddings from the index"""
        try:
            self.index = None
            self.metadata = {}
            self.documents = {}
            
            # Delete index files
            if os.path.exists(self.index_path):
                os.remove(self.index_path)
            if os.path.exists(self.metadata_path):
                os.remove(self.metadata_path)
            
            print(f"✅ Cleared FAISS index for project: {self.project_id}")
            return True
        except Exception as e:
            print(f"❌ Error clearing index: {e}")
            return False


# Global RAG engines cache - DISABLED for now due to stale data issues
# Each request will create a fresh instance to load current data from disk
_rag_engines = {}


def get_rag_engine(project_id: str) -> LocalRAGEngine:
    """Get or create a RAG engine for a project
    
    NOTE: We create a fresh instance each time instead of caching
    to ensure we always load the latest data from disk.
    The underlying ChromaDB with duckdb+parquet handles persistence.
    """
    # For now, don't use caching - create fresh instance each time
    # This ensures we always load the latest data from disk
    engine = LocalRAGEngine(project_id)
    print(f"🔄 Created fresh RAG engine for {project_id} (caching disabled)")
    return engine

def get_rag_engine_cached(project_id: str) -> LocalRAGEngine:
    """Get or reuse a cached RAG engine for a project"""
    if project_id not in _rag_engines:
        _rag_engines[project_id] = LocalRAGEngine(project_id)
    return _rag_engines[project_id]

```
<!-- END_FILE -->

---
<!-- FILE: optional_dependencies.py -->
## optional_dependencies.py

```py
"""Helpers for optional runtime-only dependencies."""

from __future__ import annotations

import importlib
from typing import Any


class LazyModuleProxy:
    """Load an optional module only when one of its attributes is accessed."""

    def __init__(self, module_name: str, missing_dependency_message: str):
        self._module_name = module_name
        self._missing_dependency_message = missing_dependency_message

    def _load_module(self):
        try:
            return importlib.import_module(self._module_name)
        except ModuleNotFoundError as exc:
            raise RuntimeError(self._missing_dependency_message) from exc

    def __getattr__(self, attribute_name: str) -> Any:
        return getattr(self._load_module(), attribute_name)

```
<!-- END_FILE -->

---
<!-- FILE: postgres_rag.py -->
## postgres_rag.py

```py
import os
import json
import shutil
import numpy as np
import pypdf
from pathlib import Path
import dotenv
import time

dotenv.load_dotenv()

try:
    from google import genai
    from google.genai import errors as genai_errors
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    genai_errors = None
    types = None
    GENAI_AVAILABLE = False

# Kept for any code that checks this flag — now satisfied by google-genai alone.
POSTGRES_RAG_DEPENDENCIES_AVAILABLE = GENAI_AVAILABLE
TXTAI_AVAILABLE = GENAI_AVAILABLE  # legacy alias

# Per-project index directory: rag_data/indices/<project_id>/
INDICES_DIR = Path(__file__).parent.parent / "rag_data" / "indices"

# gemini-embedding-001 default output dimension
EMBEDDING_DIM = 768
EMBEDDING_MODEL = "gemini-embedding-001"


class EmbeddingRateLimitError(RuntimeError):
    """Raised when the embedding API remains rate limited after retries."""


def _is_rate_limit_error(exc: Exception) -> bool:
    return bool(
        genai_errors
        and isinstance(exc, genai_errors.ClientError)
        and getattr(exc, "code", None) == 429
    )


def _embed_texts(client, texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> np.ndarray:
    """
    Call Gemini embedding API and return a float32 array of shape (N, EMBEDDING_DIM).

    Parameters
    ----------
    client : genai.Client
    texts : list[str]
    task_type : str
        "RETRIEVAL_DOCUMENT" for indexing, "RETRIEVAL_QUERY" for queries.
    """
    attempts = 3
    for attempt in range(attempts):
        try:
            result = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=texts,
                config=types.EmbedContentConfig(
                    task_type=task_type,
                    output_dimensionality=EMBEDDING_DIM,
                ),
            )
            return np.array([e.values for e in result.embeddings], dtype=np.float32)
        except Exception as exc:
            if not _is_rate_limit_error(exc) or attempt == attempts - 1:
                raise
            time.sleep(min(2 ** attempt, 8))


def _cosine_scores(query_vec: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """
    Return cosine similarity between a single query vector and a document matrix.

    Parameters
    ----------
    query_vec : np.ndarray, shape (D,)
    matrix : np.ndarray, shape (N, D)

    Returns
    -------
    np.ndarray, shape (N,)
    """
    q = query_vec / (np.linalg.norm(query_vec) + 1e-10)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-10
    return (matrix / norms) @ q


def cleanup_project_artifacts(project_id: str, document_names: list[str]) -> bool:
    """
    Best-effort removal of all persisted index files for a project.

    No API calls are made — purely filesystem cleanup.
    """
    index_path = INDICES_DIR / project_id
    if index_path.is_dir():
        shutil.rmtree(index_path)
    elif index_path.exists():
        index_path.unlink()
    return True


class PostgresRAGEngine:
    def __init__(self, project_id: str, require_llm: bool = True):
        if not GENAI_AVAILABLE:
            raise ImportError(
                "PostgresRAGEngine requires google-genai. "
                "Install it with: pip install google-genai"
            )
api_key=***REDACTED***
        if require_llm and not api_key:
            raise ValueError("PostgresRAGEngine requires GOOGLE_API_KEY to be set")

        self.project_id = project_id
        self.index_dir = INDICES_DIR / project_id
        self.embeddings_path = self.index_dir / "embeddings.npy"
        self.content_path = self.index_dir / "content.json"

        # Client is None when no API key — deletion operations don't need it.
        self.client = genai.Client(api_key=api_key) if api_key else None

        # Load existing index from disk, or start with empty arrays.
        if self.embeddings_path.exists() and self.content_path.exists():
            self._embeddings = np.load(str(self.embeddings_path))
            with open(self.content_path) as f:
                self._content = json.load(f)  # list of {"id": str, "text": str}
            print(f"[INIT] Loaded index for project {project_id}: {len(self._content)} docs")
        else:
            self._embeddings = np.empty((0, EMBEDDING_DIM), dtype=np.float32)
            self._content = []
            print(f"[INIT] New index for project {project_id}")

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _save(self) -> None:
        self.index_dir.mkdir(parents=True, exist_ok=True)
        np.save(str(self.embeddings_path), self._embeddings)
        with open(self.content_path, "w") as f:
            json.dump(self._content, f)

    def _remove_entries(self, document_id: str) -> None:
        """Remove all entries matching document_id from the in-memory index."""
        keep = [i for i, c in enumerate(self._content) if c["id"] != document_id]
        if len(keep) == len(self._content):
            return
        self._embeddings = self._embeddings[keep] if keep else np.empty((0, EMBEDDING_DIM), dtype=np.float32)
        self._content = [self._content[i] for i in keep]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract_text_from_file(self, file_path: str) -> str:
        file_ext = Path(file_path).suffix.lower()
        try:
            if file_ext == ".pdf":
                text = ""
                with open(file_path, "rb") as f:
                    for page in pypdf.PdfReader(f).pages:
                        text += page.extract_text()
                return text
            elif file_ext in (".txt", ".md"):
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
        except Exception as exc:
            print(f"❌ Error extracting text: {exc}")
            raise

    def index_document(self, file_path: str, document_name: str) -> bool:
        if not self.client:
            raise ValueError("GOOGLE_API_KEY is required for indexing")

        text = self.extract_text_from_file(file_path)
        if not text:
            return False

        # Replace any existing entry for this document before adding the new one.
        self._remove_entries(document_name)

        try:
            vec = _embed_texts(self.client, [text], task_type="RETRIEVAL_DOCUMENT")
        except Exception as exc:
            if _is_rate_limit_error(exc):
                raise EmbeddingRateLimitError(
                    "Gemini embedding API is temporarily rate limited. Please try again in a minute."
                ) from exc
            raise
        self._embeddings = (
            np.vstack([self._embeddings, vec]) if self._embeddings.shape[0] else vec
        )
        self._content.append({"id": document_name, "text": text})
        self._save()
        print(f"[INDEX] Indexed '{document_name}' into project {self.project_id}")
        return True

    def delete_document(self, document_name: str) -> bool:
        self._remove_entries(document_name)
        self._save()

        # Delete matching chunks from PGVectorStore database tables
        try:
            import psycopg2
            from django.conf import settings
            from src.apps.documents.services import get_safe_table_name

            config = getattr(settings, "REMOTE_POSTGRES_CONFIG", {})
            db_name = config.get("NAME")
            db_user = config.get("USER")
            db_pass = config.get("PASSWORD")
            db_host = config.get("HOST")
            db_port = config.get("PORT", "5432")

            if all([db_name, db_user, db_pass, db_host]):
                safe_table = get_safe_table_name(self.project_id)
                tables_to_try = [
                    f"data_{safe_table}",
                    safe_table,
                    f"data_rag_project_{self.project_id}",
                    f"rag_project_{self.project_id}"
                ]

                for table in tables_to_try:
                    conn = None
                    try:
                        conn = psycopg2.connect(
                            host=db_host,
                            port=int(db_port),
                            database=db_name,
                            user=db_user,
password=***REDACTED***
                            connect_timeout=3
                        )
                        cursor = conn.cursor()

                        # Check if table exists
                        cursor.execute(f"""
                            SELECT EXISTS (
                                SELECT FROM information_schema.tables 
                                WHERE table_name = '{table}'
                            );
                        """)
                        exists = cursor.fetchone()[0]
                        if not exists:
                            cursor.close()
                            conn.close()
                            continue

                        # Delete all matching chunks by checking file_name in metadata_ or metadata JSON column
                        try:
                            cursor.execute(
                                f"DELETE FROM {table} WHERE metadata_->>'file_name' = %s OR metadata_->>'file_path' = %s;",
                                (document_name, document_name)
                            )
                            conn.commit()
                        except Exception:
                            try:
                                conn.rollback()
                                cursor.execute(
                                    f"DELETE FROM {table} WHERE metadata->>'file_name' = %s OR metadata->>'file_path' = %s;",
                                    (document_name, document_name)
                                )
                                conn.commit()
                            except Exception as inner_exc:
                                print(f"Warning: Failed deleting from columns for {table}: {inner_exc}")

                        cursor.close()
                        conn.close()
                    except Exception as table_exc:
                        print(f"Warning: Failed connecting/deleting for table {table}: {table_exc}")
                        if conn:
                            try:
                                conn.close()
                            except Exception:
                                pass
        except Exception as e:
            print(f"Warning: Failed deleting database chunks: {e}")

        return True

    def delete_project_artifacts(self, document_names: list[str]) -> bool:
        if self.index_dir.is_dir():
            shutil.rmtree(self.index_dir)
        elif self.index_dir.exists():
            self.index_dir.unlink()
        self._embeddings = np.empty((0, EMBEDDING_DIM), dtype=np.float32)
        self._content = []
        return True

    def query(self, query_text: str, top_k: int = 3, system_prompt: str = "") -> dict:
        if not self.client:
            raise ValueError("GOOGLE_API_KEY is required for querying")

        print(f"[QUERY] '{query_text}' in project {self.project_id}")

        source_docs: list[dict] = []
        context_text = ""

        if self._content:
            q_vec = _embed_texts(self.client, [query_text], task_type="RETRIEVAL_QUERY")[0]
            scores = _cosine_scores(q_vec, self._embeddings)
            top_indices = np.argsort(scores)[::-1][:top_k]
            for i in top_indices:
                entry = self._content[int(i)]
                source_docs.append({"document": entry["id"]})
                context_text += f"\n---\n{entry['text'][:1000]}\n"

        print(f"[QUERY] Found {len(source_docs)} matching docs")

        if not source_docs:
            response_text = (
                "I don't have any indexed documents to answer this question. "
                "Please upload documents first."
            )
        else:
            base_prompt = system_prompt or "Based on the following documents, answer this question:"
            prompt = f"{base_prompt}\n\nQuestion: {query_text}\n\nDocuments:{context_text}"
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.7),
            )
            response_text = response.text or ""

        return {"response": response_text, "source_nodes": source_docs}

```
<!-- END_FILE -->

---
<!-- FILE: prompt_storage.py -->
## prompt_storage.py

```py
"""
Prompt storage module for managing system prompts.
This is a stub implementation for the Django migration.
In the final Django version, prompts should be stored in the SystemPrompt model.
"""

import json
import os


class PromptStorage:
    """Simple in-memory prompt storage with JSON file backup"""
    
    def __init__(self):
        """Initialize prompt storage"""
        self.prompts = {}
        self.config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'configuration',
            'prompts.json'
        )
        self._load_prompts()
    
    def _load_prompts(self):
        """Load prompts from configuration file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    self.prompts = json.load(f)
        except Exception:
            self.prompts = {}
    
    def _save_prompts(self):
        """Save prompts to configuration file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.prompts, f, indent=2)
        except Exception:
            pass
    
    def get_prompt(self, store_id):
        """Get system prompt for a store"""
        return self.prompts.get(store_id, '')
    
    def set_prompt(self, store_id, content):
        """Set system prompt for a store"""
        self.prompts[store_id] = content
        self._save_prompts()
    
    def delete_prompt(self, store_id):
        """Delete system prompt for a store"""
        if store_id in self.prompts:
            del self.prompts[store_id]
            self._save_prompts()


# Global instance
_prompt_storage = None


def get_prompt_storage():
    """Get or create the global prompt storage instance"""
    global _prompt_storage
    if _prompt_storage is None:
        _prompt_storage = PromptStorage()
    return _prompt_storage

```
<!-- END_FILE -->

---
<!-- FILE: rag-api-gunicorn.conf.py -->
## rag-api-gunicorn.conf.py

```py
import os

# Gunicorn configuration for FastAPI app (running uvicorn workers)
bind = "127.0.0.1:8001"  # Local binding for development
workers = 2
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Environment
env = {
    "PYTHONUNBUFFERED": "1",
}

```
<!-- END_FILE -->


---
## Bundle notes
- Redaction: enabled (mask: `***REDACTED***`).
- No truncations.

