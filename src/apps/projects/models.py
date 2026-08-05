"""
Project models for managing file search stores and projects
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Project(models.Model):
    """
    Represents a project/store for document indexing and retrieval.
    Can be backed by either Google File Search or local indexing.
    """
    
    STORAGE_TYPES = [
        ('local', 'Local'),
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
        help_text="Type of storage backend (local or Google File Search)"
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

    # Parameter Placeholders (to be defined later)
    synthesizer = models.BooleanField(
        default=False,
        help_text="Enable or disable the synthesizer"
    )
    document_parsing = models.CharField(
        max_length=50,
        choices=[
            ("markitdown", "markitdown"),
        ],
        default="markitdown",
        help_text="Document parsing backend (cannot be changed after first source is indexed)."
    )
    chunking = models.CharField(
        max_length=50,
        choices=[
            ("fixed-size", "Fixed-size"),
            ("sentence-paragraph", "Sentence/paragraph"),
            ("recursive", "Recursive"),
            ("document-structure", "Document-structure"),
            ("semantic", "Semantic"),
        ],
        default="fixed-size",
        help_text="Text chunking strategy"
    )
    embedding_model = models.CharField(
        max_length=100,
        choices=[
            ("models/gemini-embedding-001", "Gemini Embedding 001 (768-dim)"),
            ("gemini-1", "Gemini embedding 1"),
        ],
        default="models/gemini-embedding-001",
        help_text="Embedding model to use (cannot be changed after first source is indexed)."
    )
    llm_model = models.CharField(
        max_length=100,
        choices=[
            ("gemini-2.5-flash-lite", "Gemini 2.5 Flash Lite (Cloud)"),
            ("gemma4:12b-mlx", "Gemma 4 12B MLX (Local Ollama)"),
            ("gemma4:e2b-mlx", "Gemma 4 E2B MLX (Local Ollama - Ultra Fast)"),
            ("gemma4:e4b-mlx", "Gemma 4 E4B MLX (Local Ollama - Balanced)"),
        ],
        default="gemini-2.5-flash-lite",
        help_text="LLM model used for synthesis, chat, and evaluation queries."
    )
    disable_thinking = models.BooleanField(
        default=False,
        help_text="Disable reasoning/thinking mode for local Gemma models to accelerate response time."
    )
    custom_prompt = models.BooleanField(
        default=False,
        help_text="Whether to use a custom prompt"
    )
    use_markitdown = models.BooleanField(
        default=False,
        help_text="Use MarkItDown pipeline (cannot be changed after first source is indexed)."
    )
    RESPONSE_MODE_CHOICES = [
        ("compact", "Compact (Fastest - Stuffs Context into 1 Call)"),
        ("refine", "Refine (Iterative - Thorough for Multi-Chunk Deep Analysis)"),
        ("tree_summarize", "Tree Summarize (Hierarchical Summary for Broad Queries)"),
    ]

    response_mode = models.CharField(
        max_length=50,
        choices=RESPONSE_MODE_CHOICES,
        default="compact",
        help_text="LlamaIndex response synthesis mode. 'Compact' maximizes speed and cuts LLM API calls."
    )
    use_hyde = models.BooleanField(
        default=False,
        help_text="Enable Adaptive HyDE (Hypothetical Document Embeddings)"
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
    
    def clean(self):
        """
        Validate model fields before saving.
        """
        from django.core.exceptions import ValidationError
        super().clean()
        if self.storage_type in ["local", "google"]:
            raise ValidationError({
                "storage_type": "This functionality has not been implemented yet."
            })
        if self.pk:
            original = Project.objects.filter(pk=self.pk).values("embedding_model", "document_count").first()
            if original and (original["document_count"] > 0 or self.document_count > 0):
                if original["embedding_model"] != self.embedding_model:
                    raise ValidationError({
                        "embedding_model": "Embedding model cannot be changed once documents are indexed."
                    })

    def save(self, *args, **kwargs):
        """
        Overridden to automatically generate a unique, backend-compliant project_id
        if it is left blank or empty (e.g., when created via the Django Admin).
        """
        if not self.project_id:
            from datetime import datetime
            import time
            import uuid
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            microseconds = int(time.time() * 1000000) % 1000000
            safe_name = (self.display_name or "project").lower().replace(' ', '_')[:30]
            rand_suffix = uuid.uuid4().hex[:6]
            
            prefix = self.storage_type or "local"
            self.project_id = f"{prefix}_{timestamp}_{microseconds}_{safe_name}_{rand_suffix}"
            
        super().save(*args, **kwargs)

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
