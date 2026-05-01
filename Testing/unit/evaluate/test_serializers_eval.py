"""
Unit tests for evaluate app serializers
"""

import pytest
from django.contrib.auth.models import User
from rest_framework import serializers
from src.apps.evaluate.models import EvaluationDataset, EvaluationResult
from src.apps.evaluate.serializers import (
    EvaluationDatasetSerializer,
    EvaluationDatasetCreateSerializer,
    EvaluationDatasetListSerializer,
    EvaluationResultSerializer,
)
from src.apps.projects.models import Project


@pytest.mark.django_db
class TestEvaluationResultSerializer:
    """Tests for EvaluationResultSerializer"""
    
    @pytest.fixture
    def project(self):
        """Create a test project"""
        return Project.objects.create(
            project_id='test_project',
            display_name='Test Project'
        )
    
    @pytest.fixture
    def dataset(self, project):
        """Create a test dataset"""
        return EvaluationDataset.objects.create(
            project=project,
            name='Test Dataset'
        )
    
    @pytest.fixture
    def result(self, dataset, project):
        """Create a test result"""
        return EvaluationResult.objects.create(
            dataset=dataset,
            project=project,
            evaluator_name='Test Evaluator',
            metrics={'faithfulness': 0.85}
        )
    
    def test_result_serializer_serialization(self, result):
        """Test serializing an evaluation result"""
        serializer = EvaluationResultSerializer(result)
        data = serializer.data
        
        assert data['id'] == result.id
        assert data['evaluator_name'] == 'Test Evaluator'
        assert data['metrics'] == {'faithfulness': 0.85}
        assert 'created_at' in data
    
    def test_result_serializer_read_only_fields(self, result):
        """Test that created_at is read-only"""
        serializer = EvaluationResultSerializer(result)
        
        assert 'created_at' in serializer.fields
        assert serializer.fields['created_at'].read_only is True
    
    def test_result_serializer_creation(self, dataset, project):
        """Test creating a result via serializer"""
        data = {
            'dataset': dataset.id,
            'project': project.id,
            'evaluator_name': 'New Evaluator',
            'metrics': {'score': 0.75}
        }
        
        serializer = EvaluationResultSerializer(data=data)
        assert serializer.is_valid()
        result = serializer.save()
        
        assert result.evaluator_name == 'New Evaluator'
        assert result.metrics == {'score': 0.75}


@pytest.mark.django_db
class TestEvaluationDatasetSerializer:
    """Tests for EvaluationDatasetSerializer"""
    
    @pytest.fixture
    def user(self):
        """Create a test user"""
        return User.objects.create_user(username='testuser', password='testpass')
    
    @pytest.fixture
    def project(self):
        """Create a test project"""
        return Project.objects.create(
            project_id='test_project',
            display_name='Test Project'
        )
    
    @pytest.fixture
    def dataset(self, project, user):
        """Create a test dataset"""
        return EvaluationDataset.objects.create(
            project=project,
            user=user,
            name='Test Dataset',
            description='Test description',
            num_questions=10
        )
    
    def test_dataset_serializer_serialization(self, dataset):
        """Test serializing a dataset"""
        serializer = EvaluationDatasetSerializer(dataset)
        data = serializer.data
        
        assert data['id'] == dataset.id
        assert data['name'] == 'Test Dataset'
        assert data['description'] == 'Test description'
        assert data['state'] == 'PENDING'
        assert data['num_questions'] == 10
    
    def test_dataset_serializer_read_only_fields(self, dataset):
        """Test that certain fields are read-only"""
        serializer = EvaluationDatasetSerializer(dataset)
        
        assert serializer.fields['created_at'].read_only is True
        assert serializer.fields['generated_at'].read_only is True
        assert serializer.fields['state'].read_only is True
        assert serializer.fields['error_message'].read_only is True
    
    def test_dataset_serializer_with_results(self, dataset):
        """Test serializer includes results"""
        result = EvaluationResult.objects.create(
            dataset=dataset,
            project=dataset.project,
            evaluator_name='Test Evaluator'
        )
        
        serializer = EvaluationDatasetSerializer(dataset)
        data = serializer.data
        
        assert len(data['results']) == 1
        assert data['results'][0]['evaluator_name'] == 'Test Evaluator'


@pytest.mark.django_db
class TestEvaluationDatasetCreateSerializer:
    """Tests for EvaluationDatasetCreateSerializer"""
    
    @pytest.fixture
    def project(self):
        """Create a test project"""
        return Project.objects.create(
            project_id='test_project',
            display_name='Test Project'
        )
    
    def test_create_serializer_valid_data(self, project):
        """Test creating dataset with valid data"""
        data = {
            'project': project.id,
            'name': 'New Dataset',
            'description': 'Test description',
            'num_questions': 20,
            'question_generation_params': {'param1': 'value1'}
        }
        
        serializer = EvaluationDatasetCreateSerializer(data=data)
        assert serializer.is_valid()
        
        dataset = serializer.save()
        assert dataset.name == 'New Dataset'
        assert dataset.num_questions == 20
    
    def test_create_serializer_num_questions_min_validation(self, project):
        """Test num_questions minimum validation"""
        data = {
            'project': project.id,
            'name': 'New Dataset',
            'num_questions': 0
        }
        
        serializer = EvaluationDatasetCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'num_questions' in serializer.errors
    
    def test_create_serializer_num_questions_max_validation(self, project):
        """Test num_questions maximum validation"""
        data = {
            'project': project.id,
            'name': 'New Dataset',
            'num_questions': 101
        }
        
        serializer = EvaluationDatasetCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'num_questions' in serializer.errors
    
    def test_create_serializer_num_questions_boundary(self, project):
        """Test num_questions at boundaries"""
        # Test minimum valid
        data = {
            'project': project.id,
            'name': 'Dataset',
            'num_questions': 1
        }
        serializer = EvaluationDatasetCreateSerializer(data=data)
        assert serializer.is_valid()
        
        # Test maximum valid
        data['num_questions'] = 100
        serializer = EvaluationDatasetCreateSerializer(data=data)
        assert serializer.is_valid()
    
    def test_create_serializer_excludes_state_field(self, project):
        """Test that create serializer doesn't include state"""
        assert 'state' not in EvaluationDatasetCreateSerializer().fields
        assert 'error_message' not in EvaluationDatasetCreateSerializer().fields
        assert 'generated_at' not in EvaluationDatasetCreateSerializer().fields
    
    def test_create_serializer_requires_project(self):
        """Test that project is required"""
        data = {
            'name': 'New Dataset',
            'num_questions': 10
        }
        
        serializer = EvaluationDatasetCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'project' in serializer.errors
    
    def test_create_serializer_requires_name(self, project):
        """Test that name is required"""
        data = {
            'project': project.id,
            'num_questions': 10
        }
        
        serializer = EvaluationDatasetCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors


@pytest.mark.django_db
class TestEvaluationDatasetListSerializer:
    """Tests for EvaluationDatasetListSerializer"""
    
    @pytest.fixture
    def project(self):
        """Create a test project"""
        return Project.objects.create(
            project_id='test_project',
            display_name='Test Project'
        )
    
    @pytest.fixture
    def dataset(self, project):
        """Create a test dataset"""
        return EvaluationDataset.objects.create(
            project=project,
            name='Test Dataset',
            num_questions=10
        )
    
    def test_list_serializer_fields(self, dataset):
        """Test list serializer includes correct fields"""
        serializer = EvaluationDatasetListSerializer(dataset)
        data = serializer.data
        
        # Should have lightweight fields
        assert 'id' in data
        assert 'project' in data
        assert 'name' in data
        assert 'state' in data
        assert 'num_questions' in data
        assert 'created_at' in data
        
        # Should not have heavy fields
        assert 'qa_pairs' not in data
        assert 'question_generation_params' not in data
    
    def test_list_serializer_result_count(self, dataset, project):
        """Test result_count method field"""
        # Add some results
        EvaluationResult.objects.create(
            dataset=dataset,
            project=project,
            evaluator_name='Evaluator 1'
        )
        EvaluationResult.objects.create(
            dataset=dataset,
            project=project,
            evaluator_name='Evaluator 2'
        )
        
        serializer = EvaluationDatasetListSerializer(dataset)
        data = serializer.data
        
        assert data['result_count'] == 2
    
    def test_list_serializer_result_count_zero(self, dataset):
        """Test result_count when no results"""
        serializer = EvaluationDatasetListSerializer(dataset)
        data = serializer.data
        
        assert data['result_count'] == 0
    
    def test_list_serializer_serializes_multiple(self, dataset, project):
        """Test serializing multiple datasets"""
        dataset2 = EvaluationDataset.objects.create(
            project=project,
            name='Dataset 2',
            num_questions=5
        )
        
        datasets = [dataset, dataset2]
        serializer = EvaluationDatasetListSerializer(datasets, many=True)
        data = serializer.data
        
        assert len(data) == 2
        assert data[0]['name'] in ['Test Dataset', 'Dataset 2']
