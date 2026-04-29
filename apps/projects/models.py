"""
Project models for managing file search stores and projects
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Project(models.Model):
    """
    Represents a project/store for document indexing and retrieval.
    Can be backed by either Google File Search or local FAISS indexing.
    """
    
    STORAGE_TYPES = [
        ('local', 'Local FAISS Indexing'),
        ('google', 'Google File Search'),
        ('postgres', 'Postgres RAG'),
    ]
    
    # Identifiers
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='projects',
        null=True,
        blank=True,
        help_text="The user who owns this project"
    )
    project_id = models.CharField(
        max_length=255,
        unique=True,
        help_text="Unique project identifier (e.g., 'local_20250120_143000_my_project')"
    )
    display_name = models.CharField(
        max_length=255,
        help_text="Human-friendly name for the project"
    )
    
    # Storage configuration
    storage_type = models.CharField(
        max_length=20,
        choices=STORAGE_TYPES,
        default='local',
        help_text="Type of storage backend (local FAISS or Google File Search)"
    )
    external_store_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="ID from external service (e.g., Google Store ID)"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(
        blank=True,
        help_text="Optional description of the project"
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this project is active"
    )
    
    # Statistics (denormalized for performance)
    document_count = models.IntegerField(
        default=0,
        help_text="Number of documents in this project"
    )
    last_indexed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When documents were last indexed"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['storage_type', 'is_active']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.display_name} ({self.storage_type})"


class SystemPrompt(models.Model):
    """
    Custom system prompt associated with a project.
    Used to guide the AI behavior when chatting with documents in this project.
    """
    
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='system_prompt',
        help_text="The project this prompt is associated with"
    )
    
    content = models.TextField(
        blank=True,
        help_text="The system prompt content for this project"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "System Prompt"
        verbose_name_plural = "System Prompts"
    
    def __str__(self):
        return f"Prompt for {self.project.display_name}"
