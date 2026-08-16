"""
Chat models for managing conversation history
"""

from django.db import models
from django.contrib.auth.models import User
from src.apps.projects.models import Project


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


class ChatFeedback(models.Model):
    """
    Stores user feedback (thumbs up / down) for chat messages.
    Segregated per project.
    """
    VALUE_CHOICES = [
        ('up', 'Thumbs Up'),
        ('down', 'Thumbs Down'),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='feedbacks',
        help_text="The project this feedback belongs to"
    )
    message_id = models.CharField(
        max_length=255,
        db_index=True,
        help_text="The ID of the message being evaluated"
    )
    conversation_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        help_text="Conversation or session identifier"
    )
    customer_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="External customer identifier"
    )
    value = models.CharField(
        max_length=20,
        choices=VALUE_CHOICES,
        help_text="Feedback value ('up' or 'down')"
    )
    timestamp = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp sent from client"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Server creation timestamp"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', '-created_at']),
            models.Index(fields=['project', 'value']),
            models.Index(fields=['message_id']),
        ]

    def __str__(self):
        return f"{self.project.display_name} - {self.value} (Message: {self.message_id[:16]})"

