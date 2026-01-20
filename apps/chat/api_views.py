"""
DRF API Views for chat app
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import ChatMessage
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
