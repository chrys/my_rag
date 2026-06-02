from rest_framework import serializers
from .models import EvaluationDataset, EvaluationRun, EvaluationResultMetrics


class EvaluationDatasetSerializer(serializers.ModelSerializer):
    """Serializer for EvaluationDataset QA items"""
    class Meta:
        model = EvaluationDataset
        fields = [
            "id", "project", "document", "question",
            "ground_truth", "source", "created_at"
        ]
        read_only_fields = ["created_at"]


class EvaluationRunSerializer(serializers.ModelSerializer):
    """Serializer for EvaluationRun instances"""
    class Meta:
        model = EvaluationRun
        fields = [
            "id", "project", "started_at", "completed_at",
            "status", "error_message"
        ]
        read_only_fields = ["started_at", "completed_at"]


class EvaluationResultMetricsSerializer(serializers.ModelSerializer):
    """Serializer for EvaluationResultMetrics"""
    class Meta:
        model = EvaluationResultMetrics
        fields = [
            "id", "run", "dataset_item", "context_recall",
            "context_precision", "faithfulness", "answer_relevancy"
        ]
