"""
Serializers for chat app
"""

from rest_framework import serializers
from .models import ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for ChatMessage model"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'project', 'user', 'user_username', 'message_type',
            'content', 'response_html', 'context_documents',
            'system_prompt_used', 'session_id', 'created_at'
        ]
        read_only_fields = ['created_at', 'response_html']


class ChatMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating chat messages"""
    
    class Meta:
        model = ChatMessage
        fields = ['project', 'message_type', 'content', 'session_id']


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat API responses"""
    user_message = serializers.CharField()
    bot_response = serializers.CharField()
    bot_response_html = serializers.CharField()


class ChatMessageListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing chat messages"""
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'message_type', 'content', 'created_at', 'session_id'
        ]
