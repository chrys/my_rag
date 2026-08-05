"""
Serializers for documents app
"""

from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for Document model"""
    
    class Meta:
        model = Document
        fields = [
            'id', 'project', 'document_name', 'display_name',
            'external_document_id', 'mime_type', 'file_size',
            'state', 'indexed_at', 'error_message', 'created_at'
        ]
        read_only_fields = ['created_at', 'indexed_at']


class DocumentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/uploading documents"""
    
    class Meta:
        model = Document
        fields = ['project', 'document_name', 'display_name', 'mime_type', 'file_size']
    

    def validate_document_name(self, value):
        """Sanitize document name"""
        import re
        if value:
            value = re.sub(r'[^a-zA-Z0-9_.-]', '_', value)
        return value

    def validate_state(self, value):
        """Document starts in PENDING state"""
        return 'PENDING'


class DocumentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating document metadata"""
    
    class Meta:
        model = Document
        fields = ['display_name', 'state', 'error_message']


class DocumentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing documents"""
    
    class Meta:
        model = Document
        fields = ['id', 'document_name', 'display_name', 'state', 'created_at']
