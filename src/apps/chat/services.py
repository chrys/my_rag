import re
import logging

logger = logging.getLogger(__name__)


def generate_adaptive_hyde_passage(query: str, model_id: str = "gemini-2.5-flash-lite", disable_thinking: bool = False) -> str:
    """
    Single-turn Adaptive HyDE query routing and hypothetical document generation.
    Supports dynamic model selection based on project llm_model (e.g. gemma4:12b-mlx vs gemini-2.5-flash-lite).
    """
    if not query or not query.strip():
        return query

    prompt = f"""You are an Adaptive Query Transformation Router for a RAG system.
Analyze the user query below and classify its intent into one of two categories:

CATEGORY 1: DIRECT_LOOKUP
- Queries containing specific error codes (e.g. 0x80070005), exact SKUs, product IDs, emails, or short verbatim definitions.

CATEGORY 2: CONCEPTUAL
- Broad, abstract, or informal questions asking for explanations, troubleshooting procedures, summaries, or how-to guides.

If category is DIRECT_LOOKUP:
Respond with:
CATEGORY: DIRECT_LOOKUP

If category is CONCEPTUAL:
Respond with:
CATEGORY: CONCEPTUAL
HYPOTHETICAL_DOCUMENT: <Write a single paragraph, 3-5 sentence hypothetical technical passage that directly answers the question as if it were extracted from authoritative documentation>

User Query:
"{query}"
"""

    try:
        from .llm_router import generate_llm_response
        response_text = generate_llm_response(prompt=prompt, model_id=model_id, disable_thinking=disable_thinking)

        # Regex extraction
        category_match = re.search(r"CATEGORY:\s*(DIRECT_LOOKUP|CONCEPTUAL)", response_text, re.IGNORECASE)
        category = category_match.group(1).upper() if category_match else "CONCEPTUAL"

        if category == "DIRECT_LOOKUP":
            logger.info(f"🔍 [HyDE Router] Model: {model_id} | Query: '{query}' -> Category: DIRECT_LOOKUP (Bypassing HyDE)")
            return query

        passage_match = re.search(r"HYPOTHETICAL_DOCUMENT:\s*(.*)", response_text, re.DOTALL | re.IGNORECASE)
        if passage_match:
            hypothetical_doc = passage_match.group(1).strip()
            logger.info(f"💡 [HyDE Router] Model: {model_id} | Query: '{query}' -> Category: CONCEPTUAL | HyDE Passage generated ({len(hypothetical_doc)} chars)")
            return hypothetical_doc

        return query

    except Exception as exc:
        logger.warning(f"Failed to generate HyDE passage for query '{query}': {exc}. Using raw query.")
        return query
