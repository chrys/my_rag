"""
Chat models for managing conversation history
"""

from django.db import models
from django.contrib.auth.models import User
from apps.projects.models import Project


class ChatMessage(models.Model):
    """
    Represents a message in a chat conversation.
    Tracks both user queries and bot responses along with context.
    """
    
    MESSAGE_TYPES = [
        ('user', 'User Message'),
        ('assistant', 'Assistant Response'),
    ]
    
    # Relationships
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='chat_messages',
        help_text="The project this chat is for"
    )
    
    # Optional user association (if using Django auth)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chat_messages',
        help_text="The user who sent this message"
    )
    
    # Message content
    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPES,
        default='user',
        help_text="Type of message (user or assistant)"
    )
    
    content = models.TextField(
        help_text="The actual message content"
    )
    
    # Response content (for assistant messages)
    response_html = models.TextField(
        blank=True,
        help_text="HTML-formatted response (markdown rendered)"
    )
    
    # Context and metadata
    context_documents = models.JSONField(
        default=list,
        blank=True,
        help_text="List of documents used as context for this response"
    )
    
    system_prompt_used = models.TextField(
        blank=True,
        help_text="The system prompt that was used for this message"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Session tracking (optional)
    session_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Session identifier for grouping conversations"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', '-created_at']),
            models.Index(fields=['session_id', '-created_at']),
            models.Index(fields=['message_type']),
        ]
    
    def __str__(self):
        preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f"{self.get_message_type_display()}: {preview}"
