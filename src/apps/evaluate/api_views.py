from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from src.apps.api.permissions import IsAdminUserOnly
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
    permission_classes = [IsAdminUserOnly]

    def perform_create(self, serializer):
        project = serializer.validated_data.get('project')
        if project and project.user and project.user != self.request.user and not (self.request.user.is_staff or self.request.user.is_superuser):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You do not have permission to add to this project.")
        serializer.save()

    def get_queryset(self):
        """Filter by authenticated admin or user"""
        if getattr(self, 'swagger_fake_view', False):
            return EvaluationDataset.objects.none()
        if self.request.user.is_staff or self.request.user.is_superuser:
            return EvaluationDataset.objects.all()
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
    permission_classes = [IsAdminUserOnly]

    def get_queryset(self):
        """Filter by authenticated admin or user"""
        if getattr(self, 'swagger_fake_view', False):
            return EvaluationRun.objects.none()
        if self.request.user.is_staff or self.request.user.is_superuser:
            return EvaluationRun.objects.all()
        return EvaluationRun.objects.filter(project__user=self.request.user)


class EvaluationResultMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for EvaluationResultMetrics model (Read-only)
    """
    queryset = EvaluationResultMetrics.objects.all()
    serializer_class = EvaluationResultMetricsSerializer
    permission_classes = [IsAdminUserOnly]

    def get_queryset(self):
        """Filter by authenticated admin or user"""
        if getattr(self, 'swagger_fake_view', False):
            return EvaluationResultMetrics.objects.none()
        if self.request.user.is_staff or self.request.user.is_superuser:
            return EvaluationResultMetrics.objects.all()
        return EvaluationResultMetrics.objects.filter(run__project__user=self.request.user)
