"""
DRF API Views for evaluate app
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import EvaluationDataset, EvaluationResult
from .serializers import (
    EvaluationDatasetSerializer,
    EvaluationDatasetCreateSerializer,
    EvaluationDatasetListSerializer,
    EvaluationResultSerializer,
)


class EvaluationDatasetViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for EvaluationDataset model
    
    Endpoints:
    - GET /api/datasets/ - List datasets
    - POST /api/datasets/ - Create dataset
    - GET /api/datasets/{id}/ - Get dataset
    - DELETE /api/datasets/{id}/ - Delete dataset
    """
    queryset = EvaluationDataset.objects.all()
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return EvaluationDatasetCreateSerializer
        elif self.action == 'list':
            return EvaluationDatasetListSerializer
        return EvaluationDatasetSerializer
    
    @action(detail=False, methods=['get'])
    def by_project(self, request):
        """Get datasets for a specific project"""
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response({'error': 'project_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset().filter(project_id=project_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_state(self, request):
        """Get datasets by state"""
        dataset_state = request.query_params.get('state')
        if not dataset_state:
            return Response({'error': 'state required'}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset().filter(state=dataset_state)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """Get results for a dataset"""
        dataset = self.get_object()
        results = dataset.results.all()
        serializer = EvaluationResultSerializer(results, many=True)
        return Response(serializer.data)


class EvaluationResultViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for EvaluationResult model (Read-only)
    
    Endpoints:
    - GET /api/results/ - List results
    - GET /api/results/{id}/ - Get result
    """
    queryset = EvaluationResult.objects.all()
    serializer_class = EvaluationResultSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def by_dataset(self, request):
        """Get results for a specific dataset"""
        dataset_id = request.query_params.get('dataset_id')
        if not dataset_id:
            return Response({'error': 'dataset_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset().filter(dataset_id=dataset_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_project(self, request):
        """Get all results for a project"""
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response({'error': 'project_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.get_queryset().filter(project_id=project_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
