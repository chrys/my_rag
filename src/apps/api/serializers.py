"""
Serializers for API app
"""

from rest_framework import serializers
from .models import APIKey, APIUsage


class APIKeySerializer(serializers.ModelSerializer):
    """Serializer for APIKey model"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    project_display_name = serializers.CharField(source='project.display_name', read_only=True, default=None)
    
    class Meta:
        model = APIKey
        fields = [
            'id', 'user', 'user_username', 'project', 'project_display_name',
            'key', 'name', 'is_active', 'created_at', 'last_used_at'
        ]
        read_only_fields = ['key', 'created_at', 'last_used_at']


class APIKeyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating API keys"""
    key = serializers.CharField(read_only=True)
    
    class Meta:
        model = APIKey
        fields = ['name', 'project', 'is_active', 'key']
    
    def create(self, validated_data):
        """Create API key with generated token"""
        validated_data['key'] = APIKey.generate_key()
        return super().create(validated_data)


class APIKeyListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing API keys"""
    project_display_name = serializers.CharField(source='project.display_name', read_only=True, default=None)
    
    class Meta:
        model = APIKey
        fields = [
            'id', 'name', 'project', 'project_display_name', 'is_active', 'created_at', 'last_used_at'
        ]


class APIUsageSerializer(serializers.ModelSerializer):
    """Serializer for APIUsage model"""
    api_key_name = serializers.CharField(source='api_key.name', read_only=True)
    
    class Meta:
        model = APIUsage
        fields = [
            'id', 'api_key', 'api_key_name', 'endpoint', 'method',
            'status_code', 'response_time_ms', 'ip_address', 'created_at'
        ]
        read_only_fields = ['created_at']


class APIUsageListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing API usage"""
    
    class Meta:
        model = APIUsage
        fields = [
            'id', 'endpoint', 'method', 'status_code',
            'response_time_ms', 'created_at'
        ]
