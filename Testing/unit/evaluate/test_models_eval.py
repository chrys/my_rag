"""
Unit tests for the new evaluate app models: EvaluationDataset, EvaluationRun, and EvaluationResultMetrics.
"""

import pytest
import uuid
from django.contrib.auth.models import User
from src.apps.evaluate.models import EvaluationDataset, EvaluationRun, EvaluationResultMetrics
from src.apps.projects.models import Project
from src.apps.documents.models import Document


@pytest.mark.django_db
class TestEvaluationModels:
    """Tests for the new Evaluation models schema"""

    @pytest.fixture
    def project(self):
        """Create a test project"""
        return Project.objects.create(
            project_id="test_project_eval",
            display_name="Test Project"
        )

    @pytest.fixture
    def document(self, project):
        """Create a test document"""
        return Document.objects.create(
            project=project,
            document_name="test_doc.pdf"
        )

    def test_create_evaluation_dataset_general(self, project):
        """Test creating a general project-level EvaluationDataset QA pair"""
        dataset = EvaluationDataset.objects.create(
            project=project,
            document=None,
            question="What is the RAG architecture?",
            ground_truth="Retrieval-Augmented Generation.",
            source="MANUAL"
        )

        assert isinstance(dataset.id, uuid.UUID)
        assert dataset.project == project
        assert dataset.document is None
        assert dataset.question == "What is the RAG architecture?"
        assert dataset.ground_truth == "Retrieval-Augmented Generation."
        assert dataset.source == "MANUAL"
        assert dataset.created_at is not None

    def test_create_evaluation_dataset_with_document(self, project, document):
        """Test creating a document-linked EvaluationDataset QA pair"""
        dataset = EvaluationDataset.objects.create(
            project=project,
            document=document,
            question="How is chunking done?",
            ground_truth="Chunks are generated using a character splitter.",
            source="GENERATED"
        )

        assert dataset.document == document
        assert dataset.source == "GENERATED"

    def test_create_evaluation_run(self, project):
        """Test creating an EvaluationRun instance"""
        run = EvaluationRun.objects.create(
            project=project,
            status="PENDING"
        )

        assert isinstance(run.id, uuid.UUID)
        assert run.project == project
        assert run.status == "PENDING"
        assert run.started_at is not None
        assert run.completed_at is None

    def test_create_evaluation_result_metrics(self, project):
        """Test creating EvaluationResultMetrics"""
        dataset = EvaluationDataset.objects.create(
            project=project,
            question="Q?",
            ground_truth="A.",
            source="CSV_UPLOAD"
        )
        
        run = EvaluationRun.objects.create(
            project=project,
            status="SUCCESS"
        )

        metrics = EvaluationResultMetrics.objects.create(
            run=run,
            dataset_item=dataset,
            context_recall=0.9,
            context_precision=0.85,
            faithfulness=0.95,
            answer_relevancy=0.88
        )

        assert isinstance(metrics.id, uuid.UUID)
        assert metrics.run == run
        assert metrics.dataset_item == dataset
        assert metrics.context_recall == 0.9
        assert metrics.context_precision == 0.85
        assert metrics.faithfulness == 0.95
        assert metrics.answer_relevancy == 0.88
