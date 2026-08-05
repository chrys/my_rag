"""
Dynamic LLM Router for handling generation queries across different LLM backends:
- Google Gemini Cloud API (gemini-2.5-flash-lite)
- Local Ollama API server at http://localhost:11434/api/generate (gemma4:12b-mlx)
"""

import os
import logging
import requests
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

OLLAMA_ENDPOINT = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434/api/generate")


def generate_llm_response(prompt: str, model_id: str = "gemini-2.5-flash-lite", system_prompt: str = "", disable_thinking: bool = False) -> str:
    """
    Generate response text based on the selected project LLM model.
    - 'gemma4:12b-mlx': Routes to local Ollama API server.
    - Otherwise: Routes to Google Gemini Cloud API.
    """
    if "gemma" in model_id.lower() or "mlx" in model_id.lower() or ":" in model_id:
        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            payload = {
                "model": model_id,
                "prompt": full_prompt,
                "stream": False
            }
            if disable_thinking:
                payload["thinking"] = False
                payload["options"] = {"thinking": False}
            response = requests.post(OLLAMA_ENDPOINT, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except Exception as e:
            logger.error(f"Error invoking local Ollama model '{model_id}': {e}")
            raise RuntimeError(f"Local LLM service failure ({model_id}): Local Ollama server is not running or accessible. Please start Ollama on your machine (http://localhost:11434).") from e
    else:
        # Default: Gemini Cloud API
        try:
            api_key = os.getenv("GOOGLE_API_KEY", "")
            client = genai.Client(api_key=api_key)
            config = types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=1024
            )
            if system_prompt:
                config.system_instruction = system_prompt

            response = client.models.generate_content(
                model=model_id if model_id else "gemini-2.5-flash-lite",
                contents=prompt,
                config=config,
            )
            return response.text if hasattr(response, 'text') else str(response)
        except Exception as e:
            logger.error(f"Error invoking Gemini cloud model '{model_id}': {e}")
            raise e
