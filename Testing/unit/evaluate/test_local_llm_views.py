import pytest
from unittest.mock import patch
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from src.apps.projects.models import Project
from src.apps.evaluate.models import LocalLLMEvaluationRun, LocalLLMResultMetric


@pytest.mark.django_db
def test_local_llm_model_list_view(client):
    user = User.objects.create_superuser(username="adminuser", password="password")
    client.force_login(user)

    mock_models = [
        {"name": "llama3.1:8b", "size": 4000000000},
        {"name": "mistral:latest", "size": 4000000000}
    ]

    with patch("src.apps.evaluate.admin_views.fetch_available_ollama_models", return_value=mock_models):
        url = reverse("custom_admin:local-llm-models")
        response = client.get(url)
        assert response.status_code == 200
        content = response.content.decode()
        assert "llama3.1:8b" in content
        assert "mistral:latest" in content


@pytest.mark.django_db
def test_local_llm_model_list_view_offline(client):
    user = User.objects.create_superuser(username="adminuser2", password="password")
    client.force_login(user)

    with patch("src.apps.evaluate.admin_views.fetch_available_ollama_models", return_value=[]):
        url = reverse("custom_admin:local-llm-models")
        response = client.get(url)
        assert response.status_code == 200
        content = response.content.decode()
        assert "No local models found" in content or "Ollama Offline" in content


@pytest.mark.django_db
def test_run_local_llm_benchmark_view_success(client):
    user = User.objects.create_superuser(username="adminuser3", password="password")
    client.force_login(user)
    project = Project.objects.create(
        user=user,
        display_name="Benchmark Project",
        description="Testing views"
    )

    csv_content = b"question,answer\nWhat is your policy?,14 day return policy\n"
    csv_file = SimpleUploadedFile("test_benchmark.csv", csv_content, content_type="text/csv")

    mock_ollama_resp = {
        "answer": "14 day return policy.",
        "tps": 25.0,
        "reply_time": 1.5,
        "eval_count": 25,
        "eval_duration": 1000000000,
        "prompt_eval_duration": 500000000
    }
    mock_judge_scores = {
        "faithfulness": 9.0,
        "context_utilization": 9.0,
        "citation_accuracy": 9.0,
        "instruction_following": 9.0
    }

    with patch("threading.Thread") as mock_thread, \
         patch("src.apps.evaluate.eval_services.query_local_ollama_model", return_value=mock_ollama_resp), \
         patch("src.apps.evaluate.eval_services.score_qualitative_metrics_with_judge", return_value=mock_judge_scores), \
         patch("src.apps.evaluate.eval_services.retrieve_project_context_chunks", return_value=["Policy text"]):

        url = reverse("custom_admin:local-llm-run")
        response = client.post(url, {
            "project_id": str(project.project_id),
            "selected_models": ["llama3.1:8b"],
            "csv_file": csv_file
        })

        assert response.status_code == 200
        assert mock_thread.called
        content = response.content.decode()
        assert "Running Local LLM Benchmark" in content or "Benchmarking" in content
        run = LocalLLMEvaluationRun.objects.filter(project=project).first()
        assert run is not None

        # Test polling status view when SUCCESS
        run.status = "SUCCESS"
        run.best_model = "llama3.1:8b"
        run.best_overall_score = 9.0
        run.summary_scores = {"llama3.1:8b": {"overall_score": 9.0}}
        run.save()

        status_url = reverse("custom_admin:local-llm-status", kwargs={"run_id": run.id})
        status_resp = client.get(status_url)
        assert status_resp.status_code == 200
        status_content = status_resp.content.decode()
        assert "Benchmark Scorecard" in status_content


@pytest.mark.django_db
def test_run_compare_llm_benchmark_view_with_gemini(client):
    user = User.objects.create_superuser(username="adminuser_gemini", password="password")
    client.force_login(user)
    project = Project.objects.create(
        user=user,
        display_name="Gemini Benchmark Project",
        description="Testing Gemini model views"
    )

    csv_content = b"question,answer\nWhat is your warranty?,1 year warranty\n"
    csv_file = SimpleUploadedFile("gemini_benchmark.csv", csv_content, content_type="text/csv")

    with patch("threading.Thread") as mock_thread:
        url = reverse("custom_admin:local-llm-run")
        response = client.post(url, {
            "project_id": str(project.project_id),
            "enable_gemini": "1",
            "gemini_model_name": "gemini-2.5-flash-lite",
            "selected_models": ["llama3.1:8b"],
            "csv_file": csv_file
        })

        assert response.status_code == 200
        assert mock_thread.called
        run = LocalLLMEvaluationRun.objects.filter(project=project).first()
        assert run is not None
        assert "gemini-2.5-flash-lite" in run.models_evaluated
        assert "llama3.1:8b" in run.models_evaluated



@pytest.mark.django_db
def test_export_local_llm_csv_view(client):
    user = User.objects.create_superuser(username="adminuser4", password="password")
    client.force_login(user)
    project = Project.objects.create(
        user=user,
        display_name="Export Project",
        description="Testing CSV export"
    )

    run = LocalLLMEvaluationRun.objects.create(
        project=project,
        models_evaluated=["llama3.1:8b"],
        status="SUCCESS",
        total_questions=1,
        best_model="llama3.1:8b",
        best_overall_score=8.8
    )

    LocalLLMResultMetric.objects.create(
        run=run,
        model_name="llama3.1:8b",
        question="What is the shipping cost?",
        ground_truth="Free shipping over $50.",
        retrieved_context="Shipping is free for orders over $50.",
        model_answer="Free shipping over $50.",
        faithfulness=9.5,
        context_utilization=9.0,
        citation_accuracy=9.0,
        tokens_per_second=24.0,
        reply_time=1.4,
        instruction_following=9.5,
        markdown_compatibility=10.0,
        overall_score=8.8
    )

    url = reverse("custom_admin:local-llm-export-csv", kwargs={"run_id": run.id})
    response = client.get(url)

    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"
    assert f'filename="local_llm_benchmark_{run.id}.csv"' in response["Content-Disposition"]

    csv_lines = response.content.decode().strip().split("\r\n")
    if len(csv_lines) == 1:
        csv_lines = response.content.decode().strip().split("\n")

    header = csv_lines[0]
    expected_header = "model_name,question,answer,model_answer,faithfulness,context_utilization,citation_accuracy,tokens_per_second,reply_time,instruction_following,markdown_compatibility,overall_score"
    assert header == expected_header

    data_row = csv_lines[1]
    assert data_row.startswith("llama3.1:8b,What is the shipping cost?,Free shipping over $50.,Free shipping over $50.")
