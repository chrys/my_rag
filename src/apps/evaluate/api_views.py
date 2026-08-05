from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import EvaluationDataset, EvaluationRun, EvaluationResultMetrics
from .serializers import (
    EvaluationDatasetSerializer,
    EvaluationRunSerializer,
    EvaluationResultMetricsSerializer,
)


class EvaluationDatasetViewSet(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        project = serializer.validated_data.get('project')
        if project and project.user and project.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You do not have permission to add to this project.")
        serializer.save()

    """
    API ViewSet for EvaluationDataset model
    """
    queryset = EvaluationDataset.objects.all()
    serializer_class = EvaluationDatasetSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        """Filter by authenticated user"""
        if getattr(self, 'swagger_fake_view', False):
            return EvaluationDataset.objects.none()
        return EvaluationDataset.objects.filter(project__user=self.request.user)

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
    permission_classes = [IsAuthenticated]



    def get_queryset(self):
        """Filter by authenticated user"""
        if getattr(self, 'swagger_fake_view', False):
            return EvaluationRun.objects.none()
        return EvaluationRun.objects.filter(project__user=self.request.user)

class EvaluationResultMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for EvaluationResultMetrics model (Read-only)
    """
    queryset = EvaluationResultMetrics.objects.all()
    serializer_class = EvaluationResultMetricsSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        """Filter by authenticated user"""
        if getattr(self, 'swagger_fake_view', False):
            return EvaluationResultMetrics.objects.none()
        return EvaluationResultMetrics.objects.filter(evaluation_run__project__user=self.request.user)
