"""
DRF API Views for projects app
"""

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
    """
    queryset = Project.objects.all()
    permission_classes = [AllowAny]
    
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
            serializer = SystemPromptSerializer(prompt)
            return Response(serializer.data)
        
        # POST - set prompt
        content = request.data.get('content', '')
        prompt, created = SystemPrompt.objects.get_or_create(
            project=project,
            defaults={'content': content}
        )
        if not created:
            prompt.content = content
            prompt.save()
        
        serializer = SystemPromptSerializer(prompt)
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
