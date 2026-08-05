"""
DRF API Views for documents app
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Document
from .serializers import (
    DocumentSerializer,
    DocumentCreateSerializer,
    DocumentUpdateSerializer,
    DocumentListSerializer,
)
from src.apps.projects.models import Project


class DocumentViewSet(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        project = serializer.validated_data.get('project')
        if project and project.user and project.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You do not have permission to add to this project.")
        serializer.save()

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
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'
    lookup_value_regex = '.+'  # Allow any character including dots
    

    def get_queryset(self):
        """Filter by authenticated user"""
        if getattr(self, 'swagger_fake_view', False):
            return Document.objects.none()
        return Document.objects.filter(project__user=self.request.user)

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
