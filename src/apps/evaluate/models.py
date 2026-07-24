import uuid
from django.db import models
from src.apps.projects.models import Project
from src.apps.documents.models import Document


class EvaluationDataset(models.Model):
    """
    Stores individual question and answer reference pairs.
    Can be generated from document chunks, or written/uploaded manually by users.
    """
    SOURCE_CHOICES = [
        ("GENERATED", "Generated"),
        ("MANUAL", "Manual"),
        ("CSV_UPLOAD", "CSV Upload"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="dataset_items",
        help_text="The project this validation item belongs to"
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="dataset_items",
        help_text="The document this QA pair was generated from (null for manual/CSV-uploaded QAs)"
    )
    question = models.TextField(help_text="The reference question to search and evaluate")
    ground_truth = models.TextField(help_text="The gold-standard ground-truth reference answer")
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default="MANUAL",
        help_text="Source of the dataset pair acquisition"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.question[:40]}... -> {self.ground_truth[:40]}..."


class EvaluationRun(models.Model):
    """
    Represents an execution event of a dataset against the project configuration.
    """
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("RUNNING", "Running"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="evaluation_runs",
        help_text="The project being evaluated"
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
        help_text="Current state of the evaluation run"
    )
    error_message = models.TextField(blank=True, help_text="Error details if status is FAILED")

    class Meta:
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"Run {self.id} ({self.status}) at {self.started_at}"


class EvaluationResultMetrics(models.Model):
    """
    Stores Ragas scores for individual questions and their aggregated metrics during a run.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    run = models.ForeignKey(
        EvaluationRun,
        on_delete=models.CASCADE,
        related_name="result_metrics",
        help_text="The evaluation run this result belongs to"
    )
    dataset_item = models.ForeignKey(
        EvaluationDataset,
        on_delete=models.SET_NULL,
        null=True,
        related_name="result_metrics",
        help_text="The reference QA dataset item evaluated"
    )
    context_recall = models.FloatField(null=True, blank=True, help_text="Context Recall score")
    context_precision = models.FloatField(null=True, blank=True, help_text="Context Precision score")
    faithfulness = models.FloatField(null=True, blank=True, help_text="Faithfulness score")
    answer_relevancy = models.FloatField(null=True, blank=True, help_text="Answer Relevancy score")

    def __str__(self) -> str:
        return f"Metrics for item {self.dataset_item_id} inside run {self.run_id}"


class ManualEvaluationRun(models.Model):
    """
    Represents a manual evaluation session for a project.
    """
    SOURCE_CHOICES = [
        ("MANUAL_INPUT", "Manual Input"),
        ("CSV_UPLOAD", "CSV Upload"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="manual_evaluation_runs",
        help_text="The project being evaluated manually"
    )
    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default="MANUAL_INPUT",
        help_text="Origin of the question set"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Manual Run {self.id} for {self.project.display_name} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class ManualEvaluationItem(models.Model):
    """
    Individual question-answer pair evaluated manually with Red/Orange/Green ratings.
    """
    RATING_CHOICES = [
        ("UNRATED", "Unrated"),
        ("GREEN", "Good"),
        ("ORANGE", "Needs Improvement"),
        ("RED", "Bad"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("GENERATING", "Generating"),
        ("GENERATED", "Generated"),
        ("FAILED", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    run = models.ForeignKey(
        ManualEvaluationRun,
        on_delete=models.CASCADE,
        related_name="items",
        help_text="The manual evaluation run this item belongs to"
    )
    question = models.TextField(help_text="The question to evaluate")
    answer = models.TextField(blank=True, default="", help_text="Generated response from the project RAG API")
    citations = models.JSONField(default=list, blank=True, help_text="List of context texts/sources retrieved for answer")
    rating = models.CharField(
        max_length=20,
        choices=RATING_CHOICES,
        default="UNRATED",
        help_text="Human evaluator score rating"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
        help_text="Answer generation state"
    )
    error_message = models.TextField(blank=True, default="", help_text="Error details if answer generation failed")

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return f"Manual Item: {self.question[:30]}... ({self.rating})"

