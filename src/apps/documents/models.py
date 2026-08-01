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
    
    CHUNKING_CHOICES = [
        ("project_default", "Use Project Default"),
        ("auto_detect", "Auto-Detect by File Extension"),
        ("markdown", "Markdown Header Splitter"),
        ("code", "Code / AST Splitter"),
        ("hierarchical", "Hierarchical / Parent-Child"),
        ("sentence", "Sentence / Paragraph Splitter"),
    ]

    chunking_strategy = models.CharField(
        max_length=50,
        choices=CHUNKING_CHOICES,
        default="auto_detect",
        help_text="Document-specific chunking strategy."
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


class ObsidianSource(models.Model):
    """
    Represents an Obsidian vault source configuration for a project.
    """
    SOURCE_TYPES = [
        ('document', 'Document'),
        ('obsidian', 'Obsidian'),
    ]

    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='obsidian_source',
        help_text="The project this Obsidian source is attached to"
    )
    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_TYPES,
        default='document',
        help_text="Selected source type for this project (Document or Obsidian)"
    )
    vault_path = models.CharField(
        max_length=1024,
        blank=True,
        help_text="Absolute local file directory path to the Obsidian vault"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_synced_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the vault was last synced"
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Obsidian Source for {self.project.display_name} ({self.vault_path})"


class ObsidianFile(models.Model):
    """
    Tracks individual notes within an Obsidian vault and their indexing state.
    """
    FILE_STATES = [
        ('PENDING', 'Pending Indexing'),
        ('INDEXED', 'Successfully Indexed'),
        ('FAILED', 'Indexing Failed'),
    ]

    obsidian_source = models.ForeignKey(
        ObsidianSource,
        on_delete=models.CASCADE,
        related_name='files',
        help_text="The Obsidian source this note belongs to"
    )
    relative_path = models.CharField(
        max_length=1024,
        help_text="Relative file path from vault root (e.g. Certifications/AWS_Guide.md)"
    )
    folder_name = models.CharField(
        max_length=255,
        help_text="Immediate parent folder name (e.g. AWS)"
    )
    status = models.CharField(
        max_length=20,
        choices=FILE_STATES,
        default='PENDING',
        help_text="Indexing status of this note"
    )
    file_mtime = models.FloatField(
        default=0.0,
        help_text="Last modified timestamp (mtime) of the note file"
    )
    last_indexed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this note was last indexed"
    )
    error_message = models.TextField(
        blank=True,
        help_text="Error message if note indexing failed"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['relative_path']
        unique_together = [['obsidian_source', 'relative_path']]

    def __str__(self):
        return f"{self.relative_path} [{self.status}]"
