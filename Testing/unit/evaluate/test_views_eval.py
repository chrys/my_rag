"""
Unit tests for the evaluate app standard and HTMX views.
"""

import csv
import io
import pytest
import uuid
from unittest.mock import patch, MagicMock
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory
from django.http import Http404, HttpResponse
from django.urls import reverse
from src.apps.evaluate.models import EvaluationDataset, EvaluationRun, EvaluationResultMetrics
from src.apps.evaluate.views import (
    evaluation_dashboard,
    qa_setup,
    qa_generation_status,
    run_evaluation,
    evaluation_run_status,
    evaluation_results,
    delete_qa_item,
)
from src.apps.evaluate.admin_views import QaSetupWorkflowView
from src.apps.projects.models import Project


@pytest.mark.django_db
class TestEvaluationViews:
    """Tests for Django evaluation views"""

    @pytest.fixture
    def factory(self):
        """Request factory fixture"""
        return RequestFactory()

    @pytest.fixture
    def user(self):
        """Test user fixture"""
        return User.objects.create_user(username="test_eval_user", password="password123")

    @pytest.fixture
    def project(self):
        """Test project fixture"""
        return Project.objects.create(
            project_id="test_proj_views",
            display_name="Views Project",
            storage_type="postgres"
        )

    def test_evaluation_dashboard_authenticated(self, factory, user, project):
        """Test rendering the central evaluation dashboard redirects to Unfold"""
        request = factory.get("/rag/evaluate/")
        request.user = user

        response = evaluation_dashboard(request)
        assert response.status_code == 302
        assert response.url == "/rag/dashboard/evaluate/"

    def test_qa_setup_redirect(self, factory, user, project):
        """Test standard qa_setup view redirects to custom admin workflow"""
        request = factory.get(f"/rag/evaluate/qa-setup/{project.project_id}/")
        request.user = user

        response = qa_setup(request, project_id=project.project_id)
        assert response.status_code == 302
        assert reverse("custom_admin:qa-setup-workflow", kwargs={"project_id": project.project_id}) in response.url

    @patch("src.apps.evaluate.admin_views.QaSetupWorkflowView.render_to_response")
    def test_qa_setup_get(self, mock_render, factory, user, project):
        """Test GET request to QaSetupWorkflowView"""
        mock_render.return_value = HttpResponse(b"Mock Dataset Configuration for Views Project")
        request = factory.get(f"/rag/dashboard/evaluate/qa-setup/{project.project_id}/")
        request.user = user

        view = QaSetupWorkflowView.as_view(model_admin=MagicMock())
        response = view(request, project_id=project.project_id)
        assert response.status_code == 200
        assert b"Dataset Configuration" in response.content
        assert b"Views Project" in response.content

    def test_qa_setup_post_manual(self, factory, user, project):
        """Test POST request to QaSetupWorkflowView with manual QA inputs"""
        data = {
            "input_method": "manual",
            "question[]": ["Q1?", "Q2?"],
            "answer[]": ["A1.", "A2."],
        }
        request = factory.post(f"/rag/dashboard/evaluate/qa-setup/{project.project_id}/", data)
        request.user = user
        request.META["HTTP_HX_REQUEST"] = "true"

        view = QaSetupWorkflowView.as_view(model_admin=MagicMock())
        response = view(request, project_id=project.project_id)
        assert response.status_code == 200
        assert b"Successfully saved 2 custom QA items" in response.content

        # Verify items saved in database
        datasets = EvaluationDataset.objects.filter(project=project).order_by("question")
        assert datasets.count() == 2
        assert datasets[0].question == "Q1?"
        assert datasets[0].ground_truth == "A1."
        assert datasets[0].source == "MANUAL"

    def test_qa_setup_post_csv_success(self, factory, user, project):
        """Test POST request to QaSetupWorkflowView with a valid CSV file upload"""
        csv_content = "Question,Answer\nWhere is pgvector?,PostgreSQL pgvector database.\nHow does RAG work?,Retrieval-Augmented Generation."
        csv_file = SimpleUploadedFile(
            "test_qas.csv",
            csv_content.encode("utf-8"),
            content_type="text/csv"
        )
        data = {
            "input_method": "csv",
            "csv_file": csv_file,
        }
        request = factory.post(f"/rag/dashboard/evaluate/qa-setup/{project.project_id}/", data)
        request.user = user
        request.META["HTTP_HX_REQUEST"] = "true"

        view = QaSetupWorkflowView.as_view(model_admin=MagicMock())
        response = view(request, project_id=project.project_id)
        assert response.status_code == 200
        assert b"Imported 2 items from CSV" in response.content

        # Verify DB contents
        datasets = EvaluationDataset.objects.filter(project=project, source="CSV_UPLOAD").order_by("question")
        assert datasets.count() == 2
        assert datasets[0].question == "How does RAG work?"
        assert datasets[1].ground_truth == "PostgreSQL pgvector database."

    def test_qa_setup_post_csv_missing_headers(self, factory, user, project):
        """Test POST request to QaSetupWorkflowView with invalid CSV file missing headers"""
        csv_content = "Query,Response\nWhere is pgvector?,PostgreSQL.\n"
        csv_file = SimpleUploadedFile("invalid.csv", csv_content.encode("utf-8"), content_type="text/csv")
        data = {
            "input_method": "csv",
            "csv_file": csv_file,
        }
        request = factory.post(f"/rag/dashboard/evaluate/qa-setup/{project.project_id}/", data)
        request.user = user
        request.META["HTTP_HX_REQUEST"] = "true"

        view = QaSetupWorkflowView.as_view(model_admin=MagicMock())
        response = view(request, project_id=project.project_id)
        assert response.status_code == 200
        assert b"CSV must contain 'Question' and 'Answer' column headers" in response.content

    @patch("src.apps.evaluate.eval_services.start_async_qa_generation")
    def test_qa_setup_post_generate(self, mock_start_gen, factory, user, project):
        """Test POST request to QaSetupWorkflowView to trigger automatic QA generation"""
        data = {
            "input_method": "generate",
            "num_questions": "7"
        }
        request = factory.post(f"/rag/dashboard/evaluate/qa-setup/{project.project_id}/", data)
        request.user = user

        view = QaSetupWorkflowView.as_view(model_admin=MagicMock())
        response = view(request, project_id=project.project_id)
        assert response.status_code == 200
        assert b"Synthesizing Dataset Questions..." in response.content
        mock_start_gen.assert_called_once_with(project.project_id, 7)

    def test_qa_generation_status_running(self, factory, user, project):
        """Test polling QA generation status while running"""
        from src.apps.evaluate.views import QA_GEN_STATUS
        QA_GEN_STATUS[project.project_id] = {"status": "RUNNING", "error": "", "count": 0}

        request = factory.get(f"/rag/evaluate/qa-status/{project.project_id}/")
        request.user = user

        response = qa_generation_status(request, project_id=project.project_id)
        assert response.status_code == 200
        assert b"Synthesizing Dataset Questions..." in response.content

    def test_qa_generation_status_success(self, factory, user, project):
        """Test polling QA generation status upon successful completion"""
        from src.apps.evaluate.views import QA_GEN_STATUS
        QA_GEN_STATUS[project.project_id] = {"status": "SUCCESS", "error": "", "count": 5}

        # Seed some dataset items in DB
        EvaluationDataset.objects.create(
            project=project,
            question="Generated Q1?",
            ground_truth="Answer 1.",
            source="GENERATED"
        )

        request = factory.get(f"/rag/evaluate/qa-status/{project.project_id}/")
        request.user = user

        response = qa_generation_status(request, project_id=project.project_id)
        assert response.status_code == 200
        assert b"Successfully synthesized 5 QA pairs" in response.content
        assert b"Generated Q1?" in response.content

    def test_qa_generation_status_failed(self, factory, user, project):
        """Test polling QA generation status upon failure"""
        from src.apps.evaluate.views import QA_GEN_STATUS
        QA_GEN_STATUS[project.project_id] = {"status": "FAILED", "error": "API rate limit reached", "count": 0}

        request = factory.get(f"/rag/evaluate/qa-status/{project.project_id}/")
        request.user = user

        response = qa_generation_status(request, project_id=project.project_id)
        assert response.status_code == 200
        assert b"Generation failed: API rate limit reached" in response.content

    @patch("src.apps.evaluate.views.start_async_evaluation_run")
    def test_run_evaluation_trigger(self, mock_start_eval, factory, user, project):
        """Test triggering an evaluation benchmark run"""
        request = factory.post(f"/rag/evaluate/run/{project.project_id}/")
        request.user = user

        response = run_evaluation(request, project_id=project.project_id)
        assert response.status_code == 200
        assert b"Running Evaluation Benchmarks..." in response.content

        # Verify EvaluationRun created in DB
        runs = EvaluationRun.objects.filter(project=project)
        assert runs.count() == 1
        mock_start_eval.assert_called_once_with(runs[0].id)

    def test_evaluation_run_status_running(self, factory, user, project):
        """Test polling evaluation run status when running"""
        run = EvaluationRun.objects.create(project=project, status="RUNNING")

        request = factory.get(f"/rag/evaluate/run-status/{run.id}/")
        request.user = user

        response = evaluation_run_status(request, run_id=run.id)
        assert response.status_code == 200
        assert b"Running Evaluation Benchmarks..." in response.content

    def test_evaluation_run_status_success(self, factory, user, project):
        """Test polling evaluation run status upon success returns HTMX redirect payload"""
        run = EvaluationRun.objects.create(project=project, status="SUCCESS")

        request = factory.get(f"/rag/evaluate/run-status/{run.id}/")
        request.user = user

        response = evaluation_run_status(request, run_id=run.id)
        assert response.status_code == 200
        assert b"hx-get" in response.content
        assert f"/rag/evaluate/results/{run.id}/".encode() in response.content

    def test_evaluation_run_status_failed(self, factory, user, project):
        """Test polling evaluation run status upon failure returns error alert"""
        run = EvaluationRun.objects.create(project=project, status="FAILED", error_message="Database lock timeout")

        request = factory.get(f"/rag/evaluate/run-status/{run.id}/")
        request.user = user

        response = evaluation_run_status(request, run_id=run.id)
        assert response.status_code == 200
        assert b"Evaluation failed: Database lock timeout" in response.content

    def test_evaluation_results_render(self, factory, user, project):
        """Test rendering the detailed evaluation metrics grid results page"""
        dataset = EvaluationDataset.objects.create(
            project=project,
            question="Metric Question?",
            ground_truth="Ideal Answer.",
            source="MANUAL"
        )
        run = EvaluationRun.objects.create(project=project, status="SUCCESS")
        metrics = EvaluationResultMetrics.objects.create(
            run=run,
            dataset_item=dataset,
            context_recall=0.9,
            context_precision=0.72,
            faithfulness=0.55,
            answer_relevancy=0.95
        )

        request = factory.get(f"/rag/evaluate/results/{run.id}/")
        request.user = user

        response = evaluation_results(request, run_id=run.id)
        assert response.status_code == 200
        assert b"Ragas Benchmark Results" in response.content
        assert b"Metric Question?" in response.content
        # Check overall stats average rendering
        assert b"0.90" in response.content
        assert b"0.72" in response.content
        assert b"0.55" in response.content
        assert b"0.95" in response.content

    def test_delete_qa_item_non_htmx(self, factory, user, project):
        """Test deleting a QA dataset item via standard POST/DELETE request redirects"""
        dataset = EvaluationDataset.objects.create(
            project=project,
            question="To be deleted?",
            ground_truth="Answer.",
            source="MANUAL"
        )
        assert EvaluationDataset.objects.filter(id=dataset.id).exists()

        request = factory.post(f"/rag/evaluate/qa-item/{dataset.id}/delete/")
        request.user = user

        response = delete_qa_item(request, item_id=dataset.id)
        assert response.status_code == 302
        assert not EvaluationDataset.objects.filter(id=dataset.id).exists()

    def test_delete_qa_item_htmx(self, factory, user, project):
        """Test deleting a QA dataset item via HTMX request returns list partial and success message"""
        dataset = EvaluationDataset.objects.create(
            project=project,
            question="HTMX to delete?",
            ground_truth="Answer.",
            source="MANUAL"
        )
        assert EvaluationDataset.objects.filter(id=dataset.id).exists()

        request = factory.delete(f"/rag/evaluate/qa-item/{dataset.id}/delete/")
        request.user = user
        request.META["HTTP_HX_REQUEST"] = "true"

        response = delete_qa_item(request, item_id=dataset.id)
        assert response.status_code == 200
        assert b"QA item deleted successfully" in response.content
        assert not EvaluationDataset.objects.filter(id=dataset.id).exists()
