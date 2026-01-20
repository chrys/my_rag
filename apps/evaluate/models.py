"""
Evaluation models for managing dataset generation and testing
"""

from django.db import models
from django.contrib.auth.models import User
from apps.projects.models import Project


class EvaluationDataset(models.Model):
    """
    Represents a dataset generated for evaluation purposes.
    Uses llama-index to generate synthetic question-answer pairs.
    """
    
    DATASET_STATES = [
        ('PENDING', 'Pending Generation'),
        ('GENERATING', 'Currently Generating'),
        ('GENERATED', 'Successfully Generated'),
        ('FAILED', 'Generation Failed'),
    ]
    
    # Relationships
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='evaluation_datasets',
        help_text="The project this dataset is for"
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The user who created this dataset"
    )
    
    # Dataset info
    name = models.CharField(
        max_length=255,
        help_text="Name of the evaluation dataset"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Description of what this dataset tests"
    )
    
    # Status
    state = models.CharField(
        max_length=20,
        choices=DATASET_STATES,
        default='PENDING',
        help_text="Current generation status"
    )
    
    # Configuration
    num_questions = models.IntegerField(
        default=10,
        help_text="Number of questions to generate"
    )
    
    question_generation_params = models.JSONField(
        default=dict,
        blank=True,
        help_text="Parameters used for question generation"
    )
    
    # Dataset content
    qa_pairs = models.JSONField(
        default=list,
        blank=True,
        help_text="Generated question-answer pairs"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    generated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the dataset was generated"
    )
    
    # Error tracking
    error_message = models.TextField(
        blank=True,
        help_text="Error message if generation failed"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'state']),
            models.Index(fields=['state']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.project.display_name})"


class EvaluationResult(models.Model):
    """
    Represents results from running evaluations against a dataset.
    Stores metrics like faithfulness, relevance, and correctness.
    """
    
    # Relationships
    dataset = models.ForeignKey(
        EvaluationDataset,
        on_delete=models.CASCADE,
        related_name='results',
        help_text="The dataset this evaluation is for"
    )
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='evaluation_results',
        help_text="The project being evaluated"
    )
    
    # Evaluation metadata
    evaluator_name = models.CharField(
        max_length=255,
        help_text="Name of the evaluator used"
    )
    
    # Results
    metrics = models.JSONField(
        default=dict,
        help_text="Evaluation metrics (faithfulness, relevance, etc.)"
    )
    
    individual_scores = models.JSONField(
        default=list,
        blank=True,
        help_text="Per-question evaluation scores"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['dataset', 'evaluator_name']),
            models.Index(fields=['project']),
        ]
    
    def __str__(self):
        return f"Evaluation: {self.evaluator_name} on {self.dataset.name}"
