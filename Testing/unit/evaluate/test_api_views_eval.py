"""
Unit tests for the new evaluate app DRF API views
"""

import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory
from src.apps.evaluate.api_views import EvaluationDatasetViewSet, EvaluationRunViewSet
from src.apps.evaluate.models import EvaluationDataset, EvaluationRun
from src.apps.projects.models import Project


@pytest.mark.django_db
class TestEvaluationApiViews:
    """Tests for EvaluationDatasetViewSet and EvaluationRunViewSet"""

    @pytest.fixture
    def api_factory(self):
        """Create API request factory"""
        return APIRequestFactory()

    @pytest.fixture
    def project(self):
        """Create a test project"""
        return Project.objects.create(
            project_id="test_project_api",
            display_name="Test Project"
        )

    def test_list_datasets(self, api_factory, project) -> None:
        """Test listing datasets"""
        EvaluationDataset.objects.create(
            project=project,
            question="What is pgvector?",
            ground_truth="PostgreSQL pgvector.",
            source="MANUAL"
        )

        request = api_factory.get("/api/datasets/")
        view = EvaluationDatasetViewSet.as_view({"get": "list"})
        response = view(request)

        assert response.status_code == status.HTTP_200_OK
        results = response.data.get("results", []) if isinstance(response.data, dict) else response.data
        assert len(results) >= 1

    def test_create_run(self, api_factory, project) -> None:
        """Test creating an evaluation run"""
        data = {
            "project": project.id,
            "status": "PENDING"
        }

        request = api_factory.post("/api/runs/", data, format="json")
        view = EvaluationRunViewSet.as_view({"post": "create"})
        response = view(request)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == "PENDING"
        assert response.data["project"] == project.id

    def test_by_project_action(self, api_factory, project) -> None:
        """Test fetching datasets by project ID"""
        EvaluationDataset.objects.create(
            project=project,
            question="What is pgvector?",
            ground_truth="PostgreSQL pgvector.",
            source="MANUAL"
        )

        request = api_factory.get(f"/api/datasets/by_project/?project_id={project.id}")
        view = EvaluationDatasetViewSet.as_view({"get": "by_project"})
        response = view(request)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_by_project_action_missing_id(self, api_factory, project) -> None:
        """Test fetching datasets by project ID without providing ID"""
        request = api_factory.get("/api/datasets/by_project/")
        view = EvaluationDatasetViewSet.as_view({"get": "by_project"})
        response = view(request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
