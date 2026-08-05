"""
Unit tests for the new evaluate app serializers
"""

import pytest
from src.apps.evaluate.models import EvaluationDataset, EvaluationRun, EvaluationResultMetrics
from src.apps.evaluate.serializers import (
    EvaluationDatasetSerializer,
    EvaluationRunSerializer,
    EvaluationResultMetricsSerializer,
)
from src.apps.projects.models import Project


@pytest.mark.django_db
class TestEvaluationSerializers:
    """Tests for EvaluationDataset, EvaluationRun, and EvaluationResultMetrics Serializers"""

    @pytest.fixture
    def project(self):
        """Create a test project"""
        return Project.objects.create(
            project_id="test_project_serial",
            display_name="Test Project"
        )

    def test_dataset_serializer(self, project) -> None:
        """Test serializing EvaluationDataset"""
        dataset = EvaluationDataset.objects.create(
            project=project,
            question="What is RAG?",
            ground_truth="Retrieval-Augmented Generation.",
            source="MANUAL"
        )

        serializer = EvaluationDatasetSerializer(dataset)
        data = serializer.data

        assert data["id"] == str(dataset.id)
        assert data["project"] == project.id
        assert data["question"] == "What is RAG?"
        assert data["ground_truth"] == "Retrieval-Augmented Generation."
        assert data["source"] == "MANUAL"
        assert "created_at" in data

    def test_run_serializer(self, project) -> None:
        """Test serializing EvaluationRun"""
        run = EvaluationRun.objects.create(
            project=project,
            status="RUNNING"
        )

        serializer = EvaluationRunSerializer(run)
        data = serializer.data

        assert data["id"] == str(run.id)
        assert data["project"] == project.id
        assert data["status"] == "RUNNING"
        assert "started_at" in data
        assert data["completed_at"] is None

    def test_result_metrics_serializer(self, project) -> None:
        """Test serializing EvaluationResultMetrics"""
        dataset = EvaluationDataset.objects.create(
            project=project,
            question="What is pgvector?",
            ground_truth="PostgreSQL extension for vector database storage.",
            source="GENERATED"
        )

        run = EvaluationRun.objects.create(
            project=project,
            status="SUCCESS"
        )

        metrics = EvaluationResultMetrics.objects.create(
            run=run,
            dataset_item=dataset,
            context_recall=0.88,
            context_precision=0.92,
            faithfulness=0.85,
            answer_relevancy=0.9
        )

        serializer = EvaluationResultMetricsSerializer(metrics)
        data = serializer.data

        assert str(data["id"]) == str(metrics.id)
        assert str(data["run"]) == str(run.id)
        assert str(data["dataset_item"]) == str(dataset.id)
        assert data["context_recall"] == 0.88
        assert data["context_precision"] == 0.92
        assert data["faithfulness"] == 0.85
        assert data["answer_relevancy"] == 0.9
