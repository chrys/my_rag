"""
Unit tests for src/apps/chat/llm_router.py
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from src.apps.chat.llm_router import (
    generate_llm_response,
    stream_llm_response,
    normalize_model_id,
)


def test_normalize_model_id():
    assert normalize_model_id("gemini-2.5-flash-lite") == "gemini/gemini-2.5-flash-lite"
    assert normalize_model_id("gemini/gemini-3.7-flash") == "gemini/gemini-3.7-flash"
    assert normalize_model_id("gemma4:12b-mlx") == "ollama/gemma4:12b-mlx"
    assert normalize_model_id("ollama/llama3.3") == "ollama/llama3.3"
    assert normalize_model_id("openai/gpt-4o") == "openai/gpt-4o"
    assert normalize_model_id("anthropic/claude-3-5-sonnet") == "anthropic/claude-3-5-sonnet"
    assert normalize_model_id("") == "gemini/gemini-2.5-flash-lite"


def test_llm_router_sync_completion():
    with patch("src.apps.chat.llm_router.litellm.completion") as mock_completion:
        mock_resp = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "Unified LiteLLM Answer"
        mock_resp.choices = [mock_choice]
        mock_completion.return_value = mock_resp

        result = generate_llm_response(
            prompt="Hello world",
            model_id="gemini/gemini-2.5-flash-lite",
            system_prompt="You are a helpful assistant"
        )

        assert result == "Unified LiteLLM Answer"
        mock_completion.assert_called_once()
        args, kwargs = mock_completion.call_args
        assert kwargs["model"] == "gemini/gemini-2.5-flash-lite"
        assert kwargs["messages"] == [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello world"}
        ]


def test_llm_router_stream_completion():
    with patch("src.apps.chat.llm_router.litellm.completion") as mock_completion:
        # Mock streaming chunks
        chunk1 = MagicMock()
        chunk1.choices = [MagicMock(delta=MagicMock(content="Hello"))]
        chunk2 = MagicMock()
        chunk2.choices = [MagicMock(delta=MagicMock(content=" world"))]
        chunk3 = MagicMock()
        chunk3.choices = [MagicMock(delta=MagicMock(content=None))]

        mock_completion.return_value = iter([chunk1, chunk2, chunk3])

        stream_gen = stream_llm_response(
            prompt="Stream test",
            model_id="anthropic/claude-3-5-sonnet",
            system_prompt="System prompt"
        )

        events = list(stream_gen)
        assert len(events) == 2
        assert "Hello" in events[0]
        assert "world" in events[1]
        data0 = json.loads(events[0].replace("data: ", "").strip())
        assert data0["token"] == "Hello"
        assert data0["done"] is False


def test_llm_router_disable_thinking_flag():
    with patch("src.apps.chat.llm_router.litellm.completion") as mock_completion:
        mock_resp = MagicMock()
        mock_resp.choices = [MagicMock(message=MagicMock(content="Fast response"))]
        mock_completion.return_value = mock_resp

        generate_llm_response(
            prompt="Compute fast",
            model_id="ollama/gemma4:12b-mlx",
            disable_thinking=True
        )

        args, kwargs = mock_completion.call_args
        assert kwargs.get("extra_body") == {"thinking": False}


def test_llm_router_ollama_offline_error():
    import litellm.exceptions
    with patch("src.apps.chat.llm_router.litellm.completion") as mock_completion:
        mock_completion.side_effect = litellm.exceptions.APIConnectionError(
            message="Connection refused to 11434",
            llm_provider="ollama",
            model="ollama/gemma4:12b-mlx"
        )

        with pytest.raises(RuntimeError) as excinfo:
            generate_llm_response(
                prompt="Hello local",
                model_id="ollama/gemma4:12b-mlx"
            )

        assert "Local LLM service failure" in str(excinfo.value)
        assert "11434" in str(excinfo.value)
