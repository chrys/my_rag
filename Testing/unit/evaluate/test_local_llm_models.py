import pytest
from django.contrib.auth.models import User
from src.apps.projects.models import Project
from src.apps.evaluate.models import LocalLLMEvaluationRun, LocalLLMResultMetric


@pytest.mark.django_db
def test_create_local_llm_evaluation_run():
    user = User.objects.create_user(username="testevaluser", password="password")
    project = Project.objects.create(
        user=user,
        display_name="Local LLM Eval Project",
        description="Testing local LLM evaluation models"
    )

    run = LocalLLMEvaluationRun.objects.create(
        project=project,
        models_evaluated=["llama3.1:8b", "mistral:latest"],
        dataset_name="qa_benchmark.csv",
        total_questions=5,
        status="RUNNING"
    )

    assert run.id is not None
    assert run.models_evaluated == ["llama3.1:8b", "mistral:latest"]
    assert run.status == "RUNNING"
    assert run.total_questions == 5
    assert str(run).startswith(f"Local LLM Benchmark Run {run.id}")


@pytest.mark.django_db
def test_create_local_llm_result_metric():
    user = User.objects.create_user(username="testevaluser2", password="password")
    project = Project.objects.create(
        user=user,
        display_name="Local LLM Project 2",
        description="Testing metrics"
    )

    run = LocalLLMEvaluationRun.objects.create(
        project=project,
        models_evaluated=["llama3.1:8b"],
        total_questions=1,
        status="SUCCESS",
        best_model="llama3.1:8b",
        best_overall_score=8.5,
        summary_scores={"llama3.1:8b": {"overall_score": 8.5}}
    )

    metric = LocalLLMResultMetric.objects.create(
        run=run,
        model_name="llama3.1:8b",
        question="What is the refund policy?",
        ground_truth="Refunds are processed within 14 days.",
        retrieved_context="Policy: Refunds take up to 14 days to complete.",
        model_answer="Refunds take up to 14 days.",
        faithfulness=9.5,
        context_utilization=9.0,
        citation_accuracy=8.5,
        tokens_per_second=28.4,
        reply_time=1.8,
        instruction_following=9.0,
        markdown_compatibility=10.0,
        overall_score=8.5
    )

    assert metric.id is not None
    assert metric.run == run
    assert metric.model_name == "llama3.1:8b"
    assert metric.faithfulness == 9.5
    assert metric.overall_score == 8.5
    assert str(metric) == "Metric [llama3.1:8b]: What is the refund policy? (Score: 8.5/10)"
