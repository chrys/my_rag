# Task 2: Prompt Isolation & Citation Synthesis represents
Description: Instead of passing user queries directly to an LLM with blind faith, this task separates the system into a protective Prompt Sandbox and forces the engine to meticulously construct explicit, verifiable footnotes back to the exact source documents.
Business benefits:
- Hallucination Containment
- Defensible Accountability (The Audit Trail)
- Mitigating Prompt Injection Risks

High level solution: 
- Leverage LlamaIndex’s structured PromptTemplate and ResponseSynthesizer frameworks to enforce strict behaviors

Step A
- Add to user's prompt the below system prompt to isolate the retrieved database text nodes from the user's chat space, setting strict ground rules.
```corporate_qa_template = """
You are a secure corporate compliance auditor assistant. Your task is to answer the user's question using ONLY the verified context blocks provided below.

=== STRATEGIC CONTEXT BLOCKS ===
{context_str}
================================

CRITICAL INSTRUCTIONS:
1. Base your answer strictly on the context blocks provided above. Do NOT use outside knowledge or extrapolate.
2. If the context does not contain the answer, reply exactly with: "I am sorry, but the approved documentation does not contain the necessary information to answer your request."
3. Every factual assertion you make must be immediately followed by an inline citation format mapping back to its index number, for example: [Doc: 2, Page: 14].

User Query: {query_str}
Answer:
"""

Step B 
- Use LlamaIndex's response synthesizer to synthesize the answer with citation. For example 
synthesizer = CitationResponseSynthesizer.from_defaults(
    text_qa_template=isolated_prompt,
    citation_chunk_size=512,  # Sub-sentence tracking granularity
    llm=local_llm  # Or cloud_llm depending on your router choice
)

Step C: Parse the Rich Payload to the HTMX Frontend
The user should see  a fluid chat bubble, and hovering over the [1] citation footnote dynamically pulls the actual file name and source text block right inside their dashboard.