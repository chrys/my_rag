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
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return DocumentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return DocumentUpdateSerializer
        elif self.action == 'list':
            return DocumentListSerializer
        return DocumentSerializer
    
    @action(detail=False, methods=['get'])
    def by_project(self, request):
        """Get documents for a specific project"""
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response({'error': 'project_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset().filter(project_id=project_id)
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
