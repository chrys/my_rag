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
        from django.db.models import Count, Avg
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
