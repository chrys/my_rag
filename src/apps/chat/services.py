import os
import re
import logging
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


def generate_adaptive_hyde_passage(query: str) -> str:
    """
    Single-turn Adaptive HyDE query routing and hypothetical document generation.
    Uses raw text completion and regex parsing as specified in jul2-specs.md.
    
    If query is classified as DIRECT_LOOKUP (error codes, SKUs, exact names), returns original query text.
    If query is CONCEPTUAL, generates a hypothetical passage to improve vector retrieval recall.
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
        api_key = os.getenv("GOOGLE_API_KEY", "")
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=300
            ),
        )

        response_text = response.text if hasattr(response, 'text') else str(response)

        # Regex extraction
        category_match = re.search(r"CATEGORY:\s*(DIRECT_LOOKUP|CONCEPTUAL)", response_text, re.IGNORECASE)
        category = category_match.group(1).upper() if category_match else "CONCEPTUAL"

        if category == "DIRECT_LOOKUP":
            logger.info(f"🔍 [HyDE Router] Query: '{query}' -> Category: DIRECT_LOOKUP (Bypassing HyDE)")
            return query

        passage_match = re.search(r"HYPOTHETICAL_DOCUMENT:\s*(.*)", response_text, re.DOTALL | re.IGNORECASE)
        if passage_match:
            hypothetical_doc = passage_match.group(1).strip()
            logger.info(f"💡 [HyDE Router] Query: '{query}' -> Category: CONCEPTUAL | HyDE Passage generated ({len(hypothetical_doc)} chars)")
            return hypothetical_doc

        return query

    except Exception as exc:
        logger.warning(f"Failed to generate HyDE passage for query '{query}': {exc}. Using raw query.")
        return query
