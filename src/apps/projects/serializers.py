"""
Serializers for projects app
"""

from rest_framework import serializers
from .models import Project, SystemPrompt


class SystemPromptSerializer(serializers.ModelSerializer):
    """Serializer for SystemPrompt model"""
    
    def validate_content(self, value):
        """Sanitize prompt content"""
        if value and len(value) > 10000:
            raise serializers.ValidationError("System prompt is too long. Max 10000 characters.")
        return value

    class Meta:
        model = SystemPrompt
        fields = ['id', 'project', 'content', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project model"""
    system_prompt = SystemPromptSerializer(read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'project_id', 'display_name', 'storage_type',
            'external_store_id', 'description', 'is_active',
            'embedding_model', 'llm_model', 'disable_thinking',
            'document_count', 'last_indexed_at', 'created_at',
            'updated_at', 'system_prompt'
        ]
        read_only_fields = ['created_at', 'updated_at', 'document_count', 'last_indexed_at']


class ProjectCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating projects"""
    
    class Meta:
        model = Project
        fields = ['project_id', 'display_name', 'storage_type', 'description', 'embedding_model', 'llm_model', 'disable_thinking']
        
    def validate_storage_type(self, value):
        """Validate storage type"""
        if value == 'local':
            raise serializers.ValidationError("This functionality has not been implemented yet.")
        if value not in ['local', 'google', 'postgres']:
            raise serializers.ValidationError("Storage type must be 'local', 'google', or 'postgres'")
        return value


class ProjectUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating projects"""
    
    class Meta:
        model = Project
        fields = ['display_name', 'description', 'is_active', 'embedding_model', 'llm_model', 'disable_thinking']

    def validate(self, attrs):
        if self.instance:
            new_embedding = attrs.get('embedding_model', self.instance.embedding_model)
            if self.instance.embedding_model != new_embedding and (self.instance.document_count > 0 or getattr(self.instance, 'documents', None) and self.instance.documents.exists()):
                raise serializers.ValidationError({"embedding_model": "Embedding model cannot be changed once documents are indexed."})
        return super().validate(attrs)


class ProjectListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing projects"""
    
    class Meta:
        model = Project
        fields = ['id', 'project_id', 'display_name', 'storage_type', 'is_active', 'document_count', 'created_at']
