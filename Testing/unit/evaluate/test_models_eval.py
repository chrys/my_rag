"""
Unit tests for evaluate app models
"""

import pytest
from django.contrib.auth.models import User
from src.apps.evaluate.models import EvaluationDataset, EvaluationResult
from src.apps.projects.models import Project


@pytest.mark.django_db
class TestEvaluationDatasetModel:
    """Tests for EvaluationDataset model"""
    
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
    
    def test_create_evaluation_dataset(self, user, project):
        """Test creating an evaluation dataset"""
        dataset = EvaluationDataset.objects.create(
            project=project,
            user=user,
            name='Test Dataset',
            description='A test evaluation dataset',
            num_questions=20
        )
        
        assert dataset.id is not None
        assert dataset.project == project
        assert dataset.user == user
        assert dataset.name == 'Test Dataset'
        assert dataset.state == 'PENDING'
    
    def test_dataset_default_state_is_pending(self, project):
        """Test that default state is PENDING"""
        dataset = EvaluationDataset.objects.create(
            project=project,
            name='Test Dataset'
        )
        
        assert dataset.state == 'PENDING'
    
    def test_dataset_state_choices(self):
        """Test that state choices are valid"""
        states = [choice[0] for choice in EvaluationDataset.DATASET_STATES]
        
        assert 'PENDING' in states
        assert 'GENERATING' in states
        assert 'GENERATED' in states
        assert 'FAILED' in states
    
    def test_dataset_json_fields(self, project):
        """Test JSON field handling"""
        qa_pairs = [
            {'question': 'Q1', 'answer': 'A1'},
            {'question': 'Q2', 'answer': 'A2'}
        ]
        
        dataset = EvaluationDataset.objects.create(
            project=project,
            name='Test Dataset',
            qa_pairs=qa_pairs,
            question_generation_params={'param1': 'value1'}
        )
        
        assert dataset.qa_pairs == qa_pairs
        assert dataset.question_generation_params == {'param1': 'value1'}
    
    def test_dataset_str_representation(self, project):
        """Test string representation"""
        dataset = EvaluationDataset.objects.create(
            project=project,
            name='Test Dataset'
        )
        
        assert str(dataset) == f"Test Dataset ({project.display_name})"
    
    def test_dataset_timestamp_fields(self, project):
        """Test that timestamps are set correctly"""
        dataset = EvaluationDataset.objects.create(
            project=project,
            name='Test Dataset'
        )
        
        assert dataset.created_at is not None
        assert dataset.generated_at is None
    
    def test_dataset_with_null_user(self, project):
        """Test creating dataset with null user"""
        dataset = EvaluationDataset.objects.create(
            project=project,
            name='Test Dataset',
            user=None
        )
        
        assert dataset.user is None
    
    def test_dataset_with_error_message(self, project):
        """Test storing error message"""
        dataset = EvaluationDataset.objects.create(
            project=project,
            name='Test Dataset',
            state='FAILED',
            error_message='Generation failed: timeout'
        )
        
        assert dataset.state == 'FAILED'
        assert dataset.error_message == 'Generation failed: timeout'
    
    def test_dataset_num_questions_validation(self, project):
        """Test number of questions field"""
        dataset = EvaluationDataset.objects.create(
            project=project,
            name='Test Dataset',
            num_questions=50
        )
        
        assert dataset.num_questions == 50
    
    def test_cascade_delete_on_project(self, user, project):
        """Test cascade delete when project is deleted"""
        dataset = EvaluationDataset.objects.create(
            project=project,
            user=user,
            name='Test Dataset'
        )
        
        dataset_id = dataset.id
        project.delete()
        
        assert not EvaluationDataset.objects.filter(id=dataset_id).exists()
    
    def test_set_null_on_user_delete(self, user, project):
        """Test that user is set to NULL on user deletion"""
        dataset = EvaluationDataset.objects.create(
            project=project,
            user=user,
            name='Test Dataset'
        )
        
        user.delete()
        dataset.refresh_from_db()
        
        assert dataset.user is None
    
    def test_dataset_ordering(self, project):
        """Test that datasets are ordered by created_at descending"""
        dataset1 = EvaluationDataset.objects.create(
            project=project,
            name='Dataset 1'
        )
        dataset2 = EvaluationDataset.objects.create(
            project=project,
            name='Dataset 2'
        )
        
        datasets = list(EvaluationDataset.objects.all())
        assert datasets[0].id == dataset2.id  # Most recent first
        assert datasets[1].id == dataset1.id
    
    def test_filter_by_state(self, project):
        """Test filtering datasets by state"""
        dataset1 = EvaluationDataset.objects.create(
            project=project,
            name='Dataset 1',
            state='PENDING'
        )
        dataset2 = EvaluationDataset.objects.create(
            project=project,
            name='Dataset 2',
            state='GENERATED'
        )
        
        pending = EvaluationDataset.objects.filter(state='PENDING')
        assert len(pending) == 1
        assert pending[0].id == dataset1.id
    
    def test_filter_by_project(self, project):
        """Test filtering datasets by project"""
        other_project = Project.objects.create(
            project_id='other_project',
            display_name='Other Project'
        )
        
        dataset1 = EvaluationDataset.objects.create(
            project=project,
            name='Dataset 1'
        )
        dataset2 = EvaluationDataset.objects.create(
            project=other_project,
            name='Dataset 2'
        )
        
        project_datasets = EvaluationDataset.objects.filter(project=project)
        assert len(project_datasets) == 1
        assert project_datasets[0].id == dataset1.id
    
    def test_update_dataset_state(self, project):
        """Test updating dataset state"""
        dataset = EvaluationDataset.objects.create(
            project=project,
            name='Test Dataset'
        )
        
        dataset.state = 'GENERATING'
        dataset.save()
        
        dataset.refresh_from_db()
        assert dataset.state == 'GENERATING'


@pytest.mark.django_db
class TestEvaluationResultModel:
    """Tests for EvaluationResult model"""
    
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
    
    def test_create_evaluation_result(self, dataset, project):
        """Test creating an evaluation result"""
        result = EvaluationResult.objects.create(
            dataset=dataset,
            project=project,
            evaluator_name='Faithfulness Evaluator',
            metrics={'faithfulness': 0.85, 'relevance': 0.90}
        )
        
        assert result.id is not None
        assert result.dataset == dataset
        assert result.project == project
        assert result.evaluator_name == 'Faithfulness Evaluator'
    
    def test_result_metrics_json_field(self, dataset, project):
        """Test metrics JSON field"""
        metrics = {
            'faithfulness': 0.85,
            'relevance': 0.90,
            'correctness': 0.88
        }
        
        result = EvaluationResult.objects.create(
            dataset=dataset,
            project=project,
            evaluator_name='Test Evaluator',
            metrics=metrics
        )
        
        assert result.metrics == metrics
    
    def test_result_individual_scores(self, dataset, project):
        """Test individual scores JSON field"""
        scores = [
            {'question_id': 1, 'score': 0.9},
            {'question_id': 2, 'score': 0.8}
        ]
        
        result = EvaluationResult.objects.create(
            dataset=dataset,
            project=project,
            evaluator_name='Test Evaluator',
            individual_scores=scores
        )
        
        assert result.individual_scores == scores
    
    def test_result_str_representation(self, dataset, project):
        """Test string representation"""
        result = EvaluationResult.objects.create(
            dataset=dataset,
            project=project,
            evaluator_name='Test Evaluator'
        )
        
        assert str(result) == f"Evaluation: Test Evaluator on {dataset.name}"
    
    def test_result_cascade_delete_on_dataset(self, dataset, project):
        """Test cascade delete when dataset is deleted"""
        result = EvaluationResult.objects.create(
            dataset=dataset,
            project=project,
            evaluator_name='Test Evaluator'
        )
        
        result_id = result.id
        dataset.delete()
        
        assert not EvaluationResult.objects.filter(id=result_id).exists()
    
    def test_result_cascade_delete_on_project(self, dataset, project):
        """Test cascade delete when project is deleted"""
        result = EvaluationResult.objects.create(
            dataset=dataset,
            project=project,
            evaluator_name='Test Evaluator'
        )
        
        result_id = result.id
        project.delete()
        
        assert not EvaluationResult.objects.filter(id=result_id).exists()
    
    def test_result_timestamp(self, dataset, project):
        """Test that created_at is set"""
        result = EvaluationResult.objects.create(
            dataset=dataset,
            project=project,
            evaluator_name='Test Evaluator'
        )
        
        assert result.created_at is not None
    
    def test_result_ordering(self, dataset, project):
        """Test that results are ordered by created_at descending"""
        result1 = EvaluationResult.objects.create(
            dataset=dataset,
            project=project,
            evaluator_name='Evaluator 1'
        )
        result2 = EvaluationResult.objects.create(
            dataset=dataset,
            project=project,
            evaluator_name='Evaluator 2'
        )
        
        results = list(EvaluationResult.objects.all())
        assert results[0].id == result2.id
        assert results[1].id == result1.id
    
    def test_filter_by_dataset(self, dataset, project):
        """Test filtering results by dataset"""
        other_dataset = EvaluationDataset.objects.create(
            project=project,
            name='Other Dataset'
        )
        
        result1 = EvaluationResult.objects.create(
            dataset=dataset,
            project=project,
            evaluator_name='Evaluator'
        )
        result2 = EvaluationResult.objects.create(
            dataset=other_dataset,
            project=project,
            evaluator_name='Evaluator'
        )
        
        dataset_results = EvaluationResult.objects.filter(dataset=dataset)
        assert len(dataset_results) == 1
        assert dataset_results[0].id == result1.id
    
    def test_filter_by_project(self, dataset, project):
        """Test filtering results by project"""
        other_project = Project.objects.create(
            project_id='other_project',
            display_name='Other Project'
        )
        
        result1 = EvaluationResult.objects.create(
            dataset=dataset,
            project=project,
            evaluator_name='Evaluator'
        )
        result2 = EvaluationResult.objects.create(
            dataset=dataset,
            project=other_project,
            evaluator_name='Evaluator'
        )
        
        project_results = EvaluationResult.objects.filter(project=project)
        assert len(project_results) == 1
        assert project_results[0].id == result1.id
    
    def test_multiple_results_per_dataset(self, dataset, project):
        """Test that a dataset can have multiple results"""
        result1 = EvaluationResult.objects.create(
            dataset=dataset,
            project=project,
            evaluator_name='Evaluator 1'
        )
        result2 = EvaluationResult.objects.create(
            dataset=dataset,
            project=project,
            evaluator_name='Evaluator 2'
        )
        
        dataset.refresh_from_db()
        assert dataset.results.count() == 2
