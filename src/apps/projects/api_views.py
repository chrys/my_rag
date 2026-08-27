"""
DRF API Views for projects app
"""

from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from src.apps.api.permissions import IsAdminOrProjectReadOnly
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
    permission_classes = [IsAdminOrProjectReadOnly]
    lookup_field = 'pk'  # Default lookup field
    lookup_value_regex = '[^/]+'  # Allow anything except forward slash in URL segment

    def get_permissions(self):
        """Allow authenticated project owners to access prompt action"""
        if self.action == 'prompt':
            return [IsAuthenticated()]
        return [permission() for permission in self.permission_classes]
    
    def get_queryset(self):
        """Filter projects by authenticated user or staff/superuser status"""
        if getattr(self, 'swagger_fake_view', False):
            return Project.objects.none()
        user = self.request.user
        if getattr(user, 'is_superuser', False) or getattr(user, 'is_staff', False):
            return Project.objects.all()
        return Project.objects.filter(models.Q(user=user) | models.Q(user__isnull=True))

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
    permission_classes = [IsAuthenticated]
    

    def get_queryset(self):
        """Filter by authenticated user"""
        if getattr(self, 'swagger_fake_view', False):
            return SystemPrompt.objects.none()
        return SystemPrompt.objects.filter(project__user=self.request.user)

    def perform_create(self, serializer):
        """Ensure only one prompt per project"""
        project = serializer.validated_data.get('project')
        # Delete existing prompt for this project if exists
        SystemPrompt.objects.filter(project=project).delete()
        serializer.save()
