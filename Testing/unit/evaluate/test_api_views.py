"""
Unit tests for evaluate app API views
"""

import pytest
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIRequestFactory
from apps.evaluate.api_views import EvaluationDatasetViewSet, EvaluationResultViewSet
from apps.evaluate.models import EvaluationDataset, EvaluationResult
from apps.projects.models import Project


@pytest.mark.django_db
class TestEvaluationDatasetViewSet:
    """Tests for EvaluationDataset ViewSet"""
    
    @pytest.fixture
    def api_factory(self):
        """Create API request factory"""
        return APIRequestFactory()
    
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
            state='PENDING',
            num_questions=10
        )
    
    def test_list_datasets(self, api_factory, dataset):
        """Test listing datasets"""
        request = api_factory.get('/api/datasets/')
        view = EvaluationDatasetViewSet.as_view({'get': 'list'})
        response = view(request)
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, dict)
        results = response.data.get('results', [])
        assert len(results) >= 1
    
    def test_retrieve_dataset(self, api_factory, dataset):
        """Test retrieving a single dataset"""
        request = api_factory.get(f'/api/datasets/{dataset.id}/')
        view = EvaluationDatasetViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk=dataset.id)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == dataset.id
        assert response.data['name'] == 'Test Dataset'
    
    def test_create_dataset(self, api_factory, project):
        """Test creating a dataset"""
        data = {
            'project': project.id,
            'name': 'New Dataset',
            'description': 'Test dataset',
            'num_questions': 15,
            'question_generation_params': {'key': 'value'}
        }
        
        request = api_factory.post('/api/datasets/', data, format='json')
        view = EvaluationDatasetViewSet.as_view({'post': 'create'})
        response = view(request)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Dataset'
        
        # Verify in database
        dataset = EvaluationDataset.objects.get(name='New Dataset')
        assert dataset.project_id == project.id
    
    def test_create_dataset_with_invalid_num_questions(self, api_factory, project):
        """Test creating dataset with invalid num_questions"""
        data = {
            'project': project.id,
            'name': 'Invalid Dataset',
            'num_questions': 101  # Exceeds max
        }
        
        request = api_factory.post('/api/datasets/', data, format='json')
        view = EvaluationDatasetViewSet.as_view({'post': 'create'})
        response = view(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_update_dataset(self, api_factory, dataset):
        """Test updating a dataset"""
        data = {
            'project': dataset.project.id,
            'name': 'Updated Dataset',
            'description': 'Updated description',
            'num_questions': 20,
            'question_generation_params': {}
        }
        
        request = api_factory.put(f'/api/datasets/{dataset.id}/', data, format='json')
        view = EvaluationDatasetViewSet.as_view({'put': 'update'})
        response = view(request, pk=dataset.id)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated Dataset'
    
    def test_partial_update_dataset(self, api_factory, dataset):
        """Test partial update of dataset"""
        data = {'name': 'Partially Updated'}
        
        request = api_factory.patch(f'/api/datasets/{dataset.id}/', data, format='json')
        view = EvaluationDatasetViewSet.as_view({'patch': 'partial_update'})
        response = view(request, pk=dataset.id)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Partially Updated'
    
    def test_delete_dataset(self, api_factory, dataset):
        """Test deleting a dataset"""
        dataset_id = dataset.id
        
        request = api_factory.delete(f'/api/datasets/{dataset_id}/')
        view = EvaluationDatasetViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=dataset_id)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not EvaluationDataset.objects.filter(id=dataset_id).exists()
    
    def test_dataset_by_project_action(self, api_factory, project):
        """Test by_project custom action"""
        dataset1 = EvaluationDataset.objects.create(
            project=project,
            name='Dataset 1'
        )
        
        other_project = Project.objects.create(
            project_id='other_project',
            display_name='Other Project'
        )
        dataset2 = EvaluationDataset.objects.create(
            project=other_project,
            name='Dataset 2'
        )
        
        request = api_factory.get(f'/api/datasets/by_project/?project_id={project.id}')
        view = EvaluationDatasetViewSet.as_view({'get': 'by_project'})
        response = view(request)
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data if isinstance(response.data, list) else response.data.get('results', [])
        assert len(results) >= 1
        assert all(dataset['project'] == project.id for dataset in results)
    
    def test_dataset_by_project_missing_param(self, api_factory):
        """Test by_project without project_id parameter"""
        request = api_factory.get('/api/datasets/by_project/')
        view = EvaluationDatasetViewSet.as_view({'get': 'by_project'})
        response = view(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
    
    def test_dataset_by_state_action(self, api_factory, project):
        """Test by_state custom action"""
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
        
        request = api_factory.get('/api/datasets/by_state/?state=PENDING')
        view = EvaluationDatasetViewSet.as_view({'get': 'by_state'})
        response = view(request)
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data if isinstance(response.data, list) else response.data.get('results', [])
        assert len(results) >= 1
        assert all(dataset['state'] == 'PENDING' for dataset in results)
    
    def test_dataset_by_state_missing_param(self, api_factory):
        """Test by_state without state parameter"""
        request = api_factory.get('/api/datasets/by_state/')
        view = EvaluationDatasetViewSet.as_view({'get': 'by_state'})
        response = view(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_dataset_results_action(self, api_factory, dataset, project):
        """Test results custom action"""
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
        
        request = api_factory.get(f'/api/datasets/{dataset.id}/results/')
        view = EvaluationDatasetViewSet.as_view({'get': 'results'})
        response = view(request, pk=dataset.id)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
    
    def test_get_serializer_class_for_create(self, api_factory, project):
        """Test that create action uses CreateSerializer"""
        data = {
            'project': project.id,
            'name': 'Test',
            'num_questions': 10
        }
        
        request = api_factory.post('/api/datasets/', data, format='json')
        view = EvaluationDatasetViewSet.as_view({'post': 'create'})
        
        # The view should use CreateSerializer
        # which validates num_questions
        response = view(request)
        
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_get_serializer_class_for_list(self, api_factory, dataset):
        """Test that list action uses ListSerializer"""
        request = api_factory.get('/api/datasets/')
        view = EvaluationDatasetViewSet.as_view({'get': 'list'})
        response = view(request)
        
        # ListSerializer should not include heavy fields
        results = response.data.get('results', [])
        if results:
            assert 'qa_pairs' not in results[0]
            assert 'result_count' in results[0]


@pytest.mark.django_db
class TestEvaluationResultViewSet:
    """Tests for EvaluationResult ViewSet"""
    
    @pytest.fixture
    def api_factory(self):
        """Create API request factory"""
        return APIRequestFactory()
    
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
            metrics={'score': 0.85}
        )
    
    def test_list_results(self, api_factory, result):
        """Test listing results"""
        request = api_factory.get('/api/results/')
        view = EvaluationResultViewSet.as_view({'get': 'list'})
        response = view(request)
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', [])
        assert len(results) >= 1
    
    def test_retrieve_result(self, api_factory, result):
        """Test retrieving a single result"""
        request = api_factory.get(f'/api/results/{result.id}/')
        view = EvaluationResultViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk=result.id)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == result.id
        assert response.data['evaluator_name'] == 'Test Evaluator'
    
    def test_result_viewset_is_read_only(self, api_factory, result):
        """Test that result viewset doesn't allow create/update/delete"""
        data = {
            'dataset': result.dataset.id,
            'project': result.project.id,
            'evaluator_name': 'New Name'
        }
        
        # Should not have create action
        request = api_factory.post('/api/results/', data, format='json')
        view = EvaluationResultViewSet.as_view({'post': 'create'})
        
        try:
            response = view(request)
            # If it gets here, the action should be rejected
            assert response.status_code in [status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_403_FORBIDDEN]
        except AttributeError:
            # Expected: ReadOnlyModelViewSet doesn't have create
            pass
    
    def test_result_by_dataset_action(self, api_factory, dataset, project):
        """Test by_dataset custom action"""
        result1 = EvaluationResult.objects.create(
            dataset=dataset,
            project=project,
            evaluator_name='Evaluator 1'
        )
        
        other_dataset = EvaluationDataset.objects.create(
            project=project,
            name='Other Dataset'
        )
        result2 = EvaluationResult.objects.create(
            dataset=other_dataset,
            project=project,
            evaluator_name='Evaluator 2'
        )
        
        request = api_factory.get(f'/api/results/by_dataset/?dataset_id={dataset.id}')
        view = EvaluationResultViewSet.as_view({'get': 'by_dataset'})
        response = view(request)
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data if isinstance(response.data, list) else response.data.get('results', [])
        assert len(results) >= 1
        assert all(result['dataset'] == dataset.id for result in results)
    
    def test_result_by_dataset_missing_param(self, api_factory):
        """Test by_dataset without dataset_id parameter"""
        request = api_factory.get('/api/results/by_dataset/')
        view = EvaluationResultViewSet.as_view({'get': 'by_dataset'})
        response = view(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_result_by_project_action(self, api_factory, dataset, project):
        """Test by_project custom action"""
        result1 = EvaluationResult.objects.create(
            dataset=dataset,
            project=project,
            evaluator_name='Evaluator 1'
        )
        
        other_project = Project.objects.create(
            project_id='other_project',
            display_name='Other Project'
        )
        result2 = EvaluationResult.objects.create(
            dataset=dataset,
            project=other_project,
            evaluator_name='Evaluator 2'
        )
        
        request = api_factory.get(f'/api/results/by_project/?project_id={project.id}')
        view = EvaluationResultViewSet.as_view({'get': 'by_project'})
        response = view(request)
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data if isinstance(response.data, list) else response.data.get('results', [])
        assert len(results) >= 1
        assert all(result['project'] == project.id for result in results)
    
    def test_result_by_project_missing_param(self, api_factory):
        """Test by_project without project_id parameter"""
        request = api_factory.get('/api/results/by_project/')
        view = EvaluationResultViewSet.as_view({'get': 'by_project'})
        response = view(request)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
