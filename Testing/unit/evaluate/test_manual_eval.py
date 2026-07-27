"""
Unit tests for Manual Evaluation models, services, and view endpoints.
"""

import io
import pytest
import uuid
from unittest.mock import patch, MagicMock
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from src.apps.projects.models import Project
from src.apps.evaluate.models import ManualEvaluationRun, ManualEvaluationItem
from src.apps.evaluate.eval_services import (
    generate_answer_for_manual_item,
    batch_generate_manual_answers,
)


@pytest.mark.django_db
class TestManualEvaluationModels:
    """Tests for ManualEvaluationRun and ManualEvaluationItem models"""

    @pytest.fixture
    def project(self):
        return Project.objects.create(
            project_id="test_manual_project",
            display_name="Manual Eval Test Project"
        )

    def test_manual_run_creation(self, project):
        run = ManualEvaluationRun.objects.create(
            project=project,
            source_type="MANUAL_INPUT"
        )
        assert isinstance(run.id, uuid.UUID)
        assert run.project == project
        assert run.source_type == "MANUAL_INPUT"
        assert run.created_at is not None

    def test_manual_item_creation(self, project):
        run = ManualEvaluationRun.objects.create(
            project=project,
            source_type="CSV_UPLOAD"
        )
        item = ManualEvaluationItem.objects.create(
            run=run,
            question="What is the support email?",
            status="PENDING",
            rating="UNRATED"
        )
        assert isinstance(item.id, uuid.UUID)
        assert item.run == run
        assert item.question == "What is the support email?"
        assert item.rating == "UNRATED"
        assert item.status == "PENDING"
        assert item.answer == ""
        assert item.citations == []


@pytest.mark.django_db
class TestManualEvaluationServices:
    """Tests for manual evaluation answer generation services"""

    @pytest.fixture
    def project(self):
        return Project.objects.create(
            project_id="test_service_project",
            display_name="Service Test Project"
        )

    @pytest.fixture
    def manual_run(self, project):
        run = ManualEvaluationRun.objects.create(
            project=project,
            source_type="MANUAL_INPUT"
        )
        ManualEvaluationItem.objects.create(run=run, question="Q1?")
        ManualEvaluationItem.objects.create(run=run, question="Q2?")
        return run

    @patch("os.getenv", return_value="")
    @patch("src.apps.evaluate.eval_services.get_vector_store")
    def test_generate_answer_for_single_item(self, mock_get_store, mock_getenv, manual_run):
        mock_get_store.side_effect = Exception("Mocked vector store connection skip")
        item = manual_run.items.first()
        updated_item = generate_answer_for_manual_item(str(item.id))
        
        assert updated_item.status == "GENERATED"
        assert updated_item.answer != ""
        assert isinstance(updated_item.citations, list)

    @patch("os.getenv", return_value="")
    @patch("src.apps.evaluate.eval_services.get_vector_store")
    def test_batch_generate_manual_answers(self, mock_get_store, mock_getenv, manual_run):
        mock_get_store.side_effect = Exception("Mocked vector store connection skip")
        batch_generate_manual_answers(str(manual_run.id))
        
        for item in manual_run.items.all():
            assert item.status == "GENERATED"
            assert item.answer != ""


@pytest.mark.django_db
class TestManualEvaluationViews:
    """Tests for manual evaluation HTTP view endpoints"""

    @pytest.fixture
    def user(self):
        return User.objects.create_user(username="admin_user", password="password")

    @pytest.fixture
    def project(self):
        return Project.objects.create(
            project_id="test_views_project",
            display_name="Views Test Project"
        )

    def test_create_manual_run_from_text(self, client, user, project):
        client.force_login(user)
        url = reverse("custom_admin:manual-eval-create")
        
        response = client.post(url, {
            "project_id": project.project_id,
            "input_method": "manual",
            "manual_questions": "What is company policy?\nHow to submit expenses?"
        })
        
        assert response.status_code == 200
        run = ManualEvaluationRun.objects.filter(project=project).first()
        assert run is not None
        assert run.items.count() == 2
        assert run.items.filter(question="What is company policy?").exists()

    def test_create_manual_run_from_csv(self, client, user, project):
        client.force_login(user)
        url = reverse("custom_admin:manual-eval-create")
        
        csv_content = b"questions\nWhere is head office?\nWhat are working hours?\n"
        csv_file = SimpleUploadedFile("test_questions.csv", csv_content, content_type="text/csv")
        
        response = client.post(url, {
            "project_id": project.project_id,
            "input_method": "csv",
            "csv_file": csv_file
        })
        
        assert response.status_code == 200
        run = ManualEvaluationRun.objects.filter(project=project).first()
        assert run is not None
        assert run.items.count() == 2

    def test_rate_manual_item(self, client, user, project):
        client.force_login(user)
        run = ManualEvaluationRun.objects.create(project=project)
        item = ManualEvaluationItem.objects.create(run=run, question="Sample Q")
        
        url = reverse("custom_admin:manual-eval-rate", kwargs={"item_id": item.id})
        
        # Test GREEN rating
        resp = client.post(url, {"rating": "GREEN"})
        assert resp.status_code == 200
        item.refresh_from_db()
        assert item.rating == "GREEN"
        
        # Test ORANGE rating
        resp = client.post(url, {"rating": "ORANGE"})
        assert resp.status_code == 200
        item.refresh_from_db()
        assert item.rating == "ORANGE"

        # Test RED rating
        resp = client.post(url, {"rating": "RED"})
        assert resp.status_code == 200
        item.refresh_from_db()
        assert item.rating == "RED"

    @patch("os.getenv", return_value="")
    @patch("src.apps.evaluate.eval_services.get_vector_store")
    def test_generate_answer_view(self, mock_get_store, mock_getenv, client, user, project):
        mock_get_store.side_effect = Exception("Mocked vector store connection skip")
        client.force_login(user)
        run = ManualEvaluationRun.objects.create(project=project)
        item = ManualEvaluationItem.objects.create(run=run, question="Tell me about pricing.")
        
        url = reverse("custom_admin:manual-eval-generate-answer", kwargs={"item_id": item.id})
        response = client.post(url)
        assert response.status_code == 200
        item.refresh_from_db()
        assert item.status == "GENERATED"
        assert item.answer != ""

    @patch("os.getenv", return_value="")
    @patch("src.apps.evaluate.eval_services.get_vector_store")
    def test_batch_generate_answers_view(self, mock_get_store, mock_getenv, client, user, project):
        mock_get_store.side_effect = Exception("Mocked vector store connection skip")
        client.force_login(user)
        run = ManualEvaluationRun.objects.create(project=project)
        ManualEvaluationItem.objects.create(run=run, question="Q1")
        ManualEvaluationItem.objects.create(run=run, question="Q2")
        
        url = reverse("custom_admin:manual-eval-generate-all", kwargs={"run_id": run.id})
        response = client.post(url)
        assert response.status_code == 200
        
        for item in run.items.all():
            assert item.status == "GENERATED"
