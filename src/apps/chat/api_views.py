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
