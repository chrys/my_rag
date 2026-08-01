"""
Unit tests for src/apps/chat/llm_router.py
"""

import pytest
from unittest.mock import patch, MagicMock
from src.apps.chat.llm_router import generate_llm_response


def test_llm_router_gemini_cloud():
    with patch("src.apps.chat.llm_router.genai.Client") as MockGenaiClient:
        mock_client = MagicMock()
        MockGenaiClient.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = "Cloud Gemini Answer"
        mock_client.models.generate_content.return_value = mock_response

        result = generate_llm_response(
            prompt="Hello world",
            model_id="gemini-2.5-flash-lite",
            system_prompt="You are a helpful assistant"
        )

        assert result == "Cloud Gemini Answer"
        mock_client.models.generate_content.assert_called_once()


def test_llm_router_gemma_local_ollama():
    with patch("src.apps.chat.llm_router.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Local Gemma Answer"}
        mock_post.return_value = mock_response

        result = generate_llm_response(
            prompt="Hello local model",
            model_id="gemma4:12b-mlx",
            system_prompt="You are local"
        )

        assert result == "Local Gemma Answer"
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["json"]["model"] == "gemma4:12b-mlx"
        assert "Hello local model" in kwargs["json"]["prompt"]


def test_llm_router_gemma_local_failure():
    with patch("src.apps.chat.llm_router.requests.post") as mock_post:
        mock_post.side_effect = Exception("Connection refused")

        with pytest.raises(RuntimeError) as excinfo:
            generate_llm_response(
                prompt="Hello local model",
                model_id="gemma4:12b-mlx"
            )

        assert "Local LLM service failure" in str(excinfo.value)
