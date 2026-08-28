"""
Dynamic LiteLLM Router for unified inference across model providers:
- Google Gemini Cloud API (gemini/gemini-2.5-flash-lite, gemini/gemini-3.7-flash)
- OpenAI (openai/gpt-4o, openai/gpt-4o-mini)
- Anthropic Claude (anthropic/claude-3-5-sonnet)
- Local Ollama (ollama/gemma4:12b-mlx, ollama/llama3.3)
- DeepSeek / Groq / Mistral
"""

import os
import json
import logging
from typing import Any, Dict, Generator, Optional
import litellm

logger = logging.getLogger(__name__)

# Configure LiteLLM global settings
litellm.drop_params = True
litellm.set_verbose = False

OLLAMA_ENDPOINT = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434/api/generate")


def normalize_model_id(model_id: str) -> str:
    """
    Normalize model identifiers into LiteLLM canonical provider/model format.
    """
    if not model_id:
        return "gemini/gemini-2.5-flash-lite"
    model_str = model_id.strip()
    if "/" in model_str:
        return model_str
    if model_str.startswith("gemini-") or model_str.startswith("models/"):
        return f"gemini/{model_str}"
    if ":" in model_str or "gemma" in model_str.lower() or "llama" in model_str.lower() or "mlx" in model_str.lower():
        return f"ollama/{model_str}"
    if model_str.startswith("gpt-") or model_str.startswith("o1") or model_str.startswith("o3"):
        return f"openai/{model_str}"
    if model_str.startswith("claude-"):
        return f"anthropic/{model_str}"
    return f"gemini/{model_str}"


def generate_llm_response(
    prompt: str,
    model_id: str = "gemini-2.5-flash-lite",
    system_prompt: str = "",
    temperature: float = 0.2,
    max_tokens: int = 1024,
    disable_thinking: bool = False,
    extra_headers: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Generate synchronous response text using LiteLLM.
    """
    canonical_model = normalize_model_id(model_id)
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    kwargs: Dict[str, Any] = {
        "model": canonical_model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "timeout": 60,
    }

    if disable_thinking and any(k in canonical_model.lower() for k in ["gemma", "deepseek", "mlx"]):
        kwargs["extra_body"] = {"thinking": False}

    if extra_headers:
        kwargs["extra_headers"] = extra_headers

    try:
        response = litellm.completion(**kwargs)
        if response and response.choices:
            return response.choices[0].message.content or ""
        return ""
    except Exception as exc:
        err_str = str(exc)
        if any(k in err_str.lower() for k in ["ollama", "11434", "connection refused", "apiconnectionerror"]):
            logger.error(f"Error invoking local Ollama model '{canonical_model}': {exc}")
            raise RuntimeError(
                f"Local LLM service failure ({canonical_model}): Local Ollama server is not running or accessible. Please start Ollama on your machine (http://localhost:11434)."
            ) from exc
        logger.error(f"Error invoking model '{canonical_model}': {exc}")
        raise exc


def stream_llm_response(
    prompt: str,
    model_id: str = "gemini-2.5-flash-lite",
    system_prompt: str = "",
    temperature: float = 0.2,
    max_tokens: int = 1024,
    disable_thinking: bool = False,
) -> Generator[str, None, None]:
    """
    Generator yielding SSE-formatted token chunks for streaming HTTP responses.
    """
    canonical_model = normalize_model_id(model_id)
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    kwargs: Dict[str, Any] = {
        "model": canonical_model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
        "timeout": 60,
    }

    if disable_thinking and any(k in canonical_model.lower() for k in ["gemma", "deepseek", "mlx"]):
        kwargs["extra_body"] = {"thinking": False}

    try:
        response_stream = litellm.completion(**kwargs)
        for chunk in response_stream:
            if chunk and chunk.choices and hasattr(chunk.choices[0], "delta"):
                delta = getattr(chunk.choices[0].delta, "content", None)
                if delta:
                    payload = json.dumps({"token": delta, "done": False})
                    yield f"data: {payload}\n\n"
    except Exception as exc:
        err_str = str(exc)
        logger.error(f"Streaming error on model '{canonical_model}': {exc}")
        if any(k in err_str.lower() for k in ["ollama", "11434", "connection refused"]):
            err_msg = f"Local LLM service failure ({canonical_model}): Local Ollama server is not running or accessible (http://localhost:11434)."
        else:
            err_msg = str(exc)
        err_payload = json.dumps({"error": err_msg, "done": True})
        yield f"data: {err_payload}\n\n"
