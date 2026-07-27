Product Requirement Document (PRD): Response Mode Optimization (response_mode="compact")1. Executive Summary & ObjectiveThis PRD outlines the requirements for implementing Response Mode Optimization using LlamaIndex's built-in ResponseMode.COMPACT (or response_mode="compact") within the chat and query engine workflows (src/apps/chat/views.py and src/postgres_rag.py).The primary goal is to reduce response generation latency by up to 50% and minimize LLM API costs by eliminating unnecessary, iterative LLM synthesis calls. By packing retrieved context nodes tightly into single prompt frames up to the target LLM’s context boundary before invoking the LLM, the system minimizes sequential refine API turns.2. Problem Statement & Operational ContextThe ProblemIn standard RAG setups (or when using default/iterative modes like response_mode="refine"), LlamaIndex evaluates retrieved chunks sequentially. If 5 chunks are retrieved:The engine sends Chunk 1 + Question $\rightarrow$ gets Initial Answer.Sends Initial Answer + Chunk 2 + Question $\rightarrow$ gets Refined Answer.Repeats through Chunks 3, 4, and 5 (resulting in 5 sequential LLM API calls).This causes:High latency (1.5s–4s total execution time).Redundant input/output token costs across multiple API calls.The Solution: Compact Synthesis Mode (compact)response_mode="compact" instructs LlamaIndex to concatenate (stuff) multiple retrieved text chunks into a single consolidated context block before issuing an LLM synthesis request.For models like gemini-2.5-flash-lite, all top $k=5\text{--}10$ retrieved nodes easily fit into a single context prompt.Reduces total synthesis LLM calls from $N$ calls down to 1 call.3. High-Level Architecture & Execution Comparison❌ ITERATIVE REFINE MODE (Slow - N LLM Calls)
[Query] + [Chunk 1] ──► LLM ──► [Draft 1]
[Draft 1] + [Chunk 2] ──► LLM ──► [Draft 2]
[Draft 2] + [Chunk 3] ──► LLM ──► [Final Answer] (Total: 3 LLM Calls)

✅ OPTIMIZED COMPACT MODE (Fast - 1 LLM Call)
[Query] + [Chunk 1 + Chunk 2 + Chunk 3] ──► LLM ──► [Final Answer] (Total: 1 LLM Call)
4. Technical Specifications4.1. Core LlamaIndex IntegrationUpdate as_query_engine() parameters across src/apps/chat/views.py, src/postgres_rag.py, and src/apps/evaluate/eval_services.py:Python# src/apps/chat/views.py or src/postgres_rag.py

from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.response_synthesizers import ResponseMode

def get_optimized_query_engine(vector_store, embed_model, llm, top_k=5):
    """
    Constructs an optimized LlamaIndex query engine utilizing 
    Compact Response Mode for sub-second synthesis.
    """
    index = VectorStoreIndex.from_vector_store(
        vector_store, 
        embed_model=embed_model
    )
    
    query_engine = index.as_query_engine(
        llm=llm,
        similarity_top_k=top_k,
        response_mode="compact",  # <--- Forces context stuffing into single call
    )
    return query_engine
4.2. Database & Project Parameters Integration (src/apps/projects/models.py)Allow per-project response mode overrides while defaulting to compact:Python# src/apps/projects/models.py

class Project(models.Model):
    # ... existing fields ...

    RESPONSE_MODE_CHOICES = [
        ("compact", "Compact (Fastest - Stuffs Context into 1 Call)"),
        ("refine", "Refine (Iterative - Thorough for Multi-Chunk Deep Analysis)"),
        ("tree_summarize", "Tree Summarize (Hierarchical Summary for Broad Queries)"),
    ]

    response_mode = models.CharField(
        max_length=50,
        choices=RESPONSE_MODE_CHOICES,
        default="compact",
        help_text="LlamaIndex response synthesis mode. 'Compact' maximizes speed and cuts LLM API calls."
    )
4.3. Admin Form Integration (src/apps/projects/admin.py)Expose response_mode inside the Unfold Admin Project configuration parameters tab:Python# src/apps/projects/admin.py

@admin.register(Project, site=custom_admin_site)
class ProjectAdmin(ModelAdmin):
    # ...
    fieldsets = (
        (
            "Parameters",
            {
                "classes": ("tab",),
                "fields": (
                    "project_id",
                    "display_name",
                    "storage_type",
                    "response_mode",  # <--- Exposed here
                    "document_parsing",
                    "chunking",
                    "embedding_model",
                    "custom_prompt",
                    "custom_prompt_text",
                    "use_hyde",
                    "use_structural_grading",
                ),
            },
        ),
        # ...
    )
4.4. Runtime Query View Handler (src/apps/chat/views.py)Python# src/apps/chat/views.py

def query_project_rag(project, query_text: str, user_system_prompt: str) -> dict:
    vector_store = get_vector_store(project.project_id)
    embed_model = GeminiEmbedding(model_name="models/gemini-embedding-001")
    llm = GoogleGenAI(model="gemini-2.5-flash-lite")

    index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)
    
    # Use the project's configured response_mode (defaults to 'compact')
    mode = getattr(project, "response_mode", "compact")
    
    query_engine = index.as_query_engine(
        llm=llm,
        similarity_top_k=5,
        response_mode=mode,
    )

    formatted_query = f"System Instructions: {user_system_prompt}\n\nUser Question: {query_text}" if user_system_prompt else query_text
    response = query_engine.query(formatted_query)

    source_documents = []
    if hasattr(response, 'source_nodes'):
        source_documents = _extract_source_documents([node.node.metadata for node in response.source_nodes])

    return {
        "response": str(response),
        "source_documents": source_documents,
    }
5. Performance Metrics & BenchmarksMetricLegacy / Iterative Mode (refine)Optimized Mode (compact)Target ImprovementAPI Calls per Query ($k=5$)5 Sequential Calls1 Consolidated Call80% reduction in API turnsSynthesis Latency~2,500ms – 4,000ms~400ms – 800ms~3x to 5x faster TTFTToken Cost EfficiencyHigh (repeats query/prompt across $N$ iterations)Low (single prompt execution)~40% token cost reduction6. Testing & Rollout PlanUnit Tests (src/apps/chat/tests.py):Verify that initializing index.as_query_engine(response_mode="compact") completes successfully without schema errors.Verify that the returned LlamaIndex Response object contains all expected source metadata nodes.Evaluation Suite Benchmark (src/apps/evaluate/):Execute evaluation runs before and after applying compact mode to verify that Answer Relevancy and Faithfulness scores remain identical or improve while query latency drops significantly.