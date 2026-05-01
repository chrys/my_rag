"""
Serializers for evaluate app
"""

from rest_framework import serializers
from .models import EvaluationDataset, EvaluationResult


class EvaluationResultSerializer(serializers.ModelSerializer):
    """Serializer for EvaluationResult model"""
    
    class Meta:
        model = EvaluationResult
        fields = [
            'id', 'dataset', 'project', 'evaluator_name',
            'metrics', 'individual_scores', 'created_at'
        ]
        read_only_fields = ['created_at']


class EvaluationDatasetSerializer(serializers.ModelSerializer):
    """Serializer for EvaluationDataset model"""
    results = EvaluationResultSerializer(many=True, read_only=True)
    
    class Meta:
        model = EvaluationDataset
        fields = [
            'id', 'project', 'user', 'name', 'description',
            'state', 'num_questions', 'question_generation_params',
            'qa_pairs', 'error_message', 'created_at', 'generated_at',
            'results'
        ]
        read_only_fields = ['created_at', 'generated_at', 'state', 'error_message']


class EvaluationDatasetCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating evaluation datasets"""
    
    class Meta:
        model = EvaluationDataset
        fields = ['project', 'name', 'description', 'num_questions', 'question_generation_params']
    
    def validate_num_questions(self, value):
        """Validate number of questions"""
        if value < 1:
            raise serializers.ValidationError("Number of questions must be at least 1")
        if value > 100:
            raise serializers.ValidationError("Number of questions cannot exceed 100")
        return value


class EvaluationDatasetListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing evaluation datasets"""
    result_count = serializers.SerializerMethodField()
    
    class Meta:
        model = EvaluationDataset
        fields = [
            'id', 'project', 'name', 'state', 'num_questions',
            'created_at', 'generated_at', 'result_count'
        ]
    
    def get_result_count(self, obj):
        """Get count of results"""
        return obj.results.count()
