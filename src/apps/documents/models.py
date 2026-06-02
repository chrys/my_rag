"""
Document models for managing indexed documents
"""

from django.db import models
from src.apps.projects.models import Project


class Document(models.Model):
    """
    Represents a document indexed within a project.
    Tracks document metadata and indexing status.
    """
    
    INDEX_STATES = [
        ('PENDING', 'Pending Indexing'),
        ('INDEXING', 'Currently Indexing'),
        ('INDEXED', 'Successfully Indexed'),
        ('FAILED', 'Indexing Failed'),
    ]
    
    # Relationships
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='documents',
        help_text="The project this document belongs to"
    )
    
    # Document info
    document_name = models.CharField(
        max_length=500,
        help_text="Name/path of the document"
    )
    
    display_name = models.CharField(
        max_length=500,
        blank=True,
        help_text="Human-friendly display name"
    )
    
    # External reference
    external_document_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="ID from external service (e.g., Google Document ID)"
    )
    
    # File metadata
    mime_type = models.CharField(
        max_length=100,
        blank=True,
        default='application/octet-stream',
        help_text="MIME type of the document"
    )
    
    file_size = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Size of the file in bytes"
    )
    
    # Indexing status
    state = models.CharField(
        max_length=20,
        choices=INDEX_STATES,
        default='PENDING',
        help_text="Current indexing status"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    indexed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the document was successfully indexed"
    )
    
    # Error tracking
    error_message = models.TextField(
        blank=True,
        help_text="Error message if indexing failed"
    )
    
    # Expiration tracking
    is_expired_checked = models.BooleanField(
        default=False,
        help_text="Whether this document has expiration tracking enabled"
    )
    expiration_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this document expires"
    )
    
    class Meta:
        ordering = ['-created_at']
        unique_together = [['project', 'document_name']]
        indexes = [
            models.Index(fields=['project', 'state']),
            models.Index(fields=['state']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.display_name or self.document_name} ({self.project.display_name})"
