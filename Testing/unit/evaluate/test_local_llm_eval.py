import pytest
from unittest.mock import patch, MagicMock
from django.contrib.auth.models import User
from src.apps.projects.models import Project
from src.apps.evaluate.models import LocalLLMEvaluationRun, LocalLLMResultMetric
from src.apps.evaluate.eval_services import (
    fetch_available_ollama_models,
    parse_benchmark_csv,
    query_local_ollama_model,
    score_tokens_per_second,
    score_reply_time,
    score_markdown_compatibility,
    score_qualitative_metrics_with_judge,
    calculate_overall_score,
    run_local_llm_benchmark_pipeline,
)


def test_ollama_discovery_success():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "models": [
            {"name": "llama3.1:8b", "size": 4661224676},
            {"name": "mistral:latest", "size": 4109865159},
        ]
    }

    with patch("requests.get", return_value=mock_response):
        models = fetch_available_ollama_models()
        assert len(models) == 2
        assert models[0]["name"] == "llama3.1:8b"
        assert models[1]["name"] == "mistral:latest"


def test_ollama_discovery_unreachable():
    with patch("requests.get", side_effect=Exception("Connection refused")):
        models = fetch_available_ollama_models()
        assert models == []


def test_csv_parser_standard_and_case_insensitive():
    csv_text = """Question,Answer,ExtraColumn1,Notes
What is the return window?,14 days,ExtraInfo,Ignored
How to contact support?,support@example.com,Department,Ignored
"""
    rows = parse_benchmark_csv(csv_text)
    assert len(rows) == 2
    assert rows[0]["question"] == "What is the return window?"
    assert rows[0]["ground_truth"] == "14 days"
    assert rows[1]["question"] == "How to contact support?"
    assert rows[1]["ground_truth"] == "support@example.com"


def test_csv_parser_alternate_headers_and_bom():
    csv_bytes = b"\xef\xbb\xbfquery,ground_truth,metadata\nWhere is the office?,London,HQ\n"
    rows = parse_benchmark_csv(csv_bytes)
    assert len(rows) == 1
    assert rows[0]["question"] == "Where is the office?"
    assert rows[0]["ground_truth"] == "London"


def test_csv_parser_invalid_missing_columns():
    csv_text = "some_col,another_col\nvalue1,value2\n"
    with pytest.raises(ValueError, match="CSV must contain"):
        parse_benchmark_csv(csv_text)


def test_csv_parser_empty_content():
    with pytest.raises(ValueError, match="CSV contains no valid"):
        parse_benchmark_csv("question,answer\n")


def test_score_tokens_per_second():
    assert score_tokens_per_second(0.0) == 0.0
    assert score_tokens_per_second(10.0) == 3.3
    assert score_tokens_per_second(20.0) == 6.5
    assert score_tokens_per_second(35.0) == 10.0
    assert score_tokens_per_second(50.0) == 10.0


def test_score_reply_time():
    assert score_reply_time(0.0) == 0.0
    assert score_reply_time(1.2) == 10.0
    assert score_reply_time(2.5) == 8.7
    assert score_reply_time(5.0) == 6.0
    assert score_reply_time(15.0) == 1.7


def test_score_markdown_compatibility():
    valid_md = "# Title\n- Item 1\n- Item 2\n```python\nprint('hello')\n```\n[[Note Link]]"
    assert score_markdown_compatibility(valid_md) == 10.0

    broken_md = "Unclosed code fence\n```python\nprint('broken')"
    assert score_markdown_compatibility(broken_md) < 10.0


def test_calculate_overall_score():
    metrics = {
        "faithfulness": 9.0,
        "context_utilization": 8.0,
        "citation_accuracy": 9.0,
        "tokens_per_second": 7.0,
        "reply_time": 8.0,
        "instruction_following": 9.0,
        "markdown_compatibility": 10.0,
    }
    overall = calculate_overall_score(metrics)
    assert overall == 8.6  # 60 / 7 = 8.57 -> 8.6


def test_query_local_ollama_model():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "response": "The return window is 14 days.",
        "total_duration": 1800000000,
        "load_duration": 200000000,
        "prompt_eval_duration": 300000000,
        "eval_duration": 1300000000,
        "eval_count": 26,
    }

    with patch("requests.post", return_value=mock_resp):
        res = query_local_ollama_model("llama3.1:8b", "What is the return window?", warmup=False)
        assert res["answer"] == "The return window is 14 days."
        assert round(res["tps"], 1) == 20.0  # 26 / 1.3s = 20.0 tok/s
        assert round(res["reply_time"], 2) == 1.6  # (0.3 + 1.3) = 1.6s


@pytest.mark.django_db
def test_run_local_llm_benchmark_pipeline():
    user = User.objects.create_user(username="pipuser", password="password")
    project = Project.objects.create(
        user=user,
        display_name="Pipeline Project",
        description="Testing pipeline execution"
    )

    dataset = [
        {"question": "What is the return policy?", "ground_truth": "14 days return policy."},
        {"question": "How to contact support?", "ground_truth": "Email support@example.com."}
    ]

    run = LocalLLMEvaluationRun.objects.create(
        project=project,
        models_evaluated=["llama3.1:8b"],
        dataset_name="test_dataset.csv",
        total_questions=2,
        status="PENDING"
    )

    mock_ollama_resp = {
        "answer": "The return policy is 14 days.",
        "tps": 22.5,
        "reply_time": 1.7,
        "eval_count": 30,
        "eval_duration": 1330000000,
        "prompt_eval_duration": 370000000
    }

    mock_judge_scores = {
        "faithfulness": 9.0,
        "context_utilization": 8.5,
        "citation_accuracy": 9.0,
        "instruction_following": 9.5
    }

    with patch("src.apps.evaluate.eval_services.query_local_ollama_model", return_value=mock_ollama_resp), \
         patch("src.apps.evaluate.eval_services.score_qualitative_metrics_with_judge", return_value=mock_judge_scores), \
         patch("src.apps.evaluate.eval_services.retrieve_project_context_chunks", return_value=["Policy document content."]):
        
        finished_run = run_local_llm_benchmark_pipeline(project, ["llama3.1:8b"], dataset, run)

        assert finished_run.status == "SUCCESS"
        assert finished_run.best_model == "llama3.1:8b"
        assert finished_run.best_overall_score > 0
        assert "llama3.1:8b" in finished_run.summary_scores
        assert finished_run.item_metrics.count() == 2
