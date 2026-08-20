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
    store_file_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="Google Document Resource Name (e.g., fileSearchStores/.../documents/...)"
    )
    
    # File metadata & State Registry
    content_hash = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        help_text="SHA-256 cryptographic hash of binary for deduplication"
    )
    custom_metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Stored key-value metadata tags"
    )
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
        ('google_calendar', 'Google Calendar'),
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
        help_text="Selected source type for this project (Document, Obsidian, or Google Calendar)"
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
        ('MODIFIED', 'Modified on Disk'),
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


class GoogleCalendarSource(models.Model):
    """
    Represents a Google Calendar integration configuration for a project.
    """
    SYNC_STATUSES = [
        ('IDLE', 'Idle'),
        ('SYNCING', 'Syncing Events'),
        ('INDEXING', 'Indexing Vectors'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='google_calendar_source',
        help_text="The project this Google Calendar source is attached to"
    )
    access_token = models.TextField(
        blank=True,
        help_text="OAuth access token"
    )
    refresh_token = models.TextField(
        blank=True,
        help_text="OAuth refresh token"
    )
    token_expiry = models.DateTimeField(
        null=True,
        blank=True,
        help_text="OAuth access token expiration timestamp"
    )
    selected_calendars = models.JSONField(
        default=list,
        blank=True,
        help_text="List of calendar IDs to sync (e.g. ['primary', 'work_cal_id'])"
    )
    lookback_days = models.IntegerField(
        default=30,
        help_text="Lookback window in days (past events)"
    )
    lookahead_days = models.IntegerField(
        default=365,
        help_text="Lookahead window in days (future events)"
    )
    sync_token = models.CharField(
        max_length=512,
        blank=True,
        help_text="Google Calendar API syncToken for incremental delta sync"
    )
    sync_status = models.CharField(
        max_length=20,
        choices=SYNC_STATUSES,
        default='IDLE',
        help_text="Current background synchronization status"
    )
    total_events_count = models.IntegerField(default=0)
    indexed_events_count = models.IntegerField(default=0)
    pending_events_count = models.IntegerField(default=0)
    failed_events_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Google Calendar Source for {self.project.display_name}"


class GoogleCalendarEvent(models.Model):
    """
    Tracks individual Google Calendar events and their vector indexing status.
    """
    EVENT_STATES = [
        ('PENDING', 'Pending Indexing'),
        ('INDEXED', 'Successfully Indexed'),
        ('FAILED', 'Indexing Failed'),
    ]

    calendar_source = models.ForeignKey(
        GoogleCalendarSource,
        on_delete=models.CASCADE,
        related_name='events',
        help_text="The Google Calendar source this event belongs to"
    )
    event_id = models.CharField(
        max_length=255,
        help_text="Unique Google Calendar Event ID"
    )
    summary = models.CharField(
        max_length=500,
        help_text="Event summary / title"
    )
    relative_path = models.CharField(
        max_length=1024,
        help_text="Relative file path of generated Markdown note (e.g. Calendar/2026-08-05_Sync.md)"
    )
    status = models.CharField(
        max_length=20,
        choices=EVENT_STATES,
        default='PENDING',
        help_text="Indexing status of this calendar event"
    )
    event_start = models.DateTimeField(null=True, blank=True)
    event_end = models.DateTimeField(null=True, blank=True)
    last_synced_at = models.DateTimeField(auto_now=True)
    last_indexed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ['-event_start']
        unique_together = [['calendar_source', 'event_id']]

    def __str__(self):
        return f"{self.summary} [{self.status}]"

