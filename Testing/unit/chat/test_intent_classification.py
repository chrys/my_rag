"""
Unit tests for Pre-Retrieval Intent Classification and Disambiguation (Task 3)
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from src.apps.chat.intent_service import (
    IntentType,
    evaluate_fast_heuristics,
    classify_query_intent,
)


def test_fast_heuristics_greetings():
    greetings = ["Hello", "hi", "Hey!", "Good morning", "howdy", "what's up?"]
    for q in greetings:
        intent, reply = evaluate_fast_heuristics(q)
        assert intent == IntentType.GREETING_OR_CHITCHAT
        assert reply is not None
        assert "assist" in reply.lower() or "help" in reply.lower() or "project" in reply.lower()


def test_fast_heuristics_thanks_and_farewell():
    intent, reply = evaluate_fast_heuristics("Thank you very much!")
    # Substring "thank" or exact regex
    intent_thanks, reply_thanks = evaluate_fast_heuristics("Thank you")
    assert intent_thanks == IntentType.GREETING_OR_CHITCHAT
    assert "welcome" in reply_thanks.lower()

    intent_bye, reply_bye = evaluate_fast_heuristics("Goodbye")
    assert intent_bye == IntentType.GREETING_OR_CHITCHAT
    assert "goodbye" in reply_bye.lower()


def test_fast_heuristics_too_brief_query():
    intent, reply = evaluate_fast_heuristics("?")
    assert intent == IntentType.CLARIFICATION_NEEDED
    assert "brief" in reply.lower() or "question" in reply.lower()


def test_fast_heuristics_informational_query_bypasses_heuristics():
    intent, reply = evaluate_fast_heuristics("What is our Q3 financial revenue?")
    assert intent is None
    assert reply is None


@patch("src.apps.chat.intent_service.genai.Client")
def test_classify_query_intent_llm_vector_search(mock_genai_client):
    mock_resp = MagicMock()
    mock_resp.text = json.dumps({
        "intent": "VECTOR_SEARCH",
        "clarification_message": None,
        "direct_response": None,
        "confidence": 0.95
    })
    mock_inst = MagicMock()
    mock_inst.models.generate_content.return_value = mock_resp
    mock_genai_client.return_value = mock_inst

    with patch.dict("os.environ", {"GOOGLE_API_KEY": "fake_key"}):
        result = classify_query_intent("Summarize chapter 4 of the architectural handbook.")
        assert result["intent"] == "VECTOR_SEARCH"
        assert result["requires_retrieval"] is True
        assert result["response"] is None


@patch("src.apps.chat.intent_service.genai.Client")
def test_classify_query_intent_llm_clarification(mock_genai_client):
    mock_resp = MagicMock()
    mock_resp.text = json.dumps({
        "intent": "CLARIFICATION_NEEDED",
        "clarification_message": "Could you specify which project or document you are referring to?",
        "direct_response": None,
        "confidence": 0.9
    })
    mock_inst = MagicMock()
    mock_inst.models.generate_content.return_value = mock_resp
    mock_genai_client.return_value = mock_inst

    with patch.dict("os.environ", {"GOOGLE_API_KEY": "fake_key"}):
        result = classify_query_intent("Tell me more about it.")
        assert result["intent"] == "CLARIFICATION_NEEDED"
        assert result["requires_retrieval"] is False
        assert "specify" in result["response"].lower() or "clarify" in result["response"].lower()


@patch("src.apps.chat.intent_service.genai.Client")
def test_classify_query_intent_llm_error_fallback(mock_genai_client):
    mock_inst = MagicMock()
    mock_inst.models.generate_content.side_effect = Exception("API rate limit")
    mock_genai_client.return_value = mock_inst

    with patch.dict("os.environ", {"GOOGLE_API_KEY": "fake_key"}):
        result = classify_query_intent("Complex retrieval query that failed classification")
        # Should gracefully fall back to VECTOR_SEARCH
        assert result["intent"] == "VECTOR_SEARCH"
        assert result["requires_retrieval"] is True
