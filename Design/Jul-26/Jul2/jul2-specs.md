# Project Specification: Response Mode, Document Parsers & Adaptive HyDE

## 1. Objective & Scope
This document specifies the design, architecture, and implementation details for three core performance and retrieval enhancements in the Django RAG application (`src/apps/`):
- **TASK 1**: Response Mode Optimization (`response_mode="compact"`).
- **TASK 2**: Document-Type Specific Node Parsers (`MarkdownNodeParser`, `CodeSplitter`, `HierarchicalNodeParser`, `SentenceSplitter`).
- **TASK 3**: Adaptive HyDE & Query Transformation Engine (`use_hyde`, routing matrix).

## 2. Common & Required Commands
- **Environment / Server Setup**:
  ```bash
  python manage.py runserver
  ```
- **Database Migrations**:
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```
- **Test Execution**:
  ```bash
  pytest
  python manage.py test
  ```

## 3. Project Structure
- `src/apps/projects/models.py` — Project configurations (`response_mode`, `use_hyde`)
- `src/apps/projects/admin.py` — Unfold Django Admin interface fields
- `src/apps/documents/models.py` — Document upload metadata (`chunking_strategy`)
- `src/apps/documents/services.py` — Dynamic node parser factory (`select_node_parser`) & LlamaIndex ingestion pipeline
- `src/apps/chat/views.py` & `src/postgres_rag.py` — RAG Query engine initialization & HyDE adaptive query routing
- `templates/partials/document_upload.html` & `document_items.html` — HTMX frontend components

## 4. Code Style & Guidelines
- **PEP 8 Guidelines**: Follow Python standard conventions, snake_case for functions/variables, PascalCase for classes.
- **Django Batteried Included**: Use Django `Model`, `ModelAdmin`, and forms without adding redundant abstractions.
- **Thin Views**: Keep view logic focused on HTTP handling and delegate complex parser/HyDE routing to services (`services.py`).
- **Type Hints**: Include standard Python type annotations for function parameters and return types.

## 5. Testing Strategy
- Place test suites in `Testing/unit/` or app-specific `tests.py`.
- Write unit tests for schema changes (`Project.response_mode`, `Project.use_hyde`, `Document.chunking_strategy`).
- Test dynamic parser selection and verify graceful fallback to `SentenceSplitter` when optional dependencies (e.g. `tree-sitter`) are missing.
- Test HyDE classification regex routing for `DIRECT_LOOKUP` vs `CONCEPTUAL` queries.

## 6. Guardrails & Boundaries
- **Dos**: Always run `makemigrations` and `pytest` after model modifications.
- **Ask Before**: Modifying default system prompts or global vector store schemas.
- **Don'ts**: Never hardcode URLs, bypass CSRF protection, or drop failing tests.

---

# TASK 1 Product Requirement Document (PRD): Response Mode Optimization (`response_mode="compact"`)

## 1. Executive Summary & Objective

This PRD outlines the requirements for implementing Response Mode Optimization using LlamaIndex's built-in `ResponseMode.COMPACT` (or `response_mode="compact"`) within the chat and query engine workflows (`src/apps/chat/views.py` and `src/postgres_rag.py`).

The primary goal is to reduce response generation latency by up to 50% and minimize LLM API costs by eliminating unnecessary, iterative LLM synthesis calls. By packing retrieved context nodes tightly into single prompt frames up to the target LLM’s context boundary before invoking the LLM, the system minimizes sequential refine API turns.

## 2. Problem Statement & Operational Context

### The Problem

In standard RAG setups (or when using default/iterative modes like `response_mode="refine"`), LlamaIndex evaluates retrieved chunks sequentially. If 5 chunks are retrieved:
1. The engine sends Chunk 1 + Question -> gets Initial Answer.
2. Sends Initial Answer + Chunk 2 + Question -> gets Refined Answer.
3. Repeats through Chunks 3, 4, and 5 (resulting in 5 sequential LLM API calls).

This causes:
- High latency (1.5s–4s total execution time).
- Redundant input/output token costs across multiple API calls.

### The Solution: Compact Synthesis Mode (`compact`)

`response_mode="compact"` instructs LlamaIndex to concatenate (stuff) multiple retrieved text chunks into a single consolidated context block before issuing an LLM synthesis request.

- For models like `gemini-2.5-flash-lite`, all top K = 5 - 10 retrieved nodes easily fit into a single context prompt.
- Reduces total synthesis LLM calls from $N$ calls down to 1 call.

## 3. High-Level Architecture & Execution Comparison

```
❌ ITERATIVE REFINE MODE (Slow - N LLM Calls)
[Query] + [Chunk 1] ──► LLM ──► [Draft 1]
[Draft 1] + [Chunk 2] ──► LLM ──► [Draft 2]
[Draft 2] + [Chunk 3] ──► LLM ──► [Final Answer] (Total: 3 LLM Calls)

✅ OPTIMIZED COMPACT MODE (Fast - 1 LLM Call)
[Query] + [Chunk 1 + Chunk 2 + Chunk 3] ──► LLM ──► [Final Answer] (Total: 1 LLM Call)
```

## 4. Technical Specifications

### 4.1. Core LlamaIndex Integration

Update `as_query_engine()` parameters across `src/apps/chat/views.py`, `src/postgres_rag.py`, and `src/apps/evaluate/eval_services.py`:

```python
# src/apps/chat/views.py or src/postgres_rag.py

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
```

### 4.2. Database & Project Parameters Integration (`src/apps/projects/models.py`)

Allow per-project response mode overrides while defaulting to compact:

```python
# src/apps/projects/models.py

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
```

### 4.3. Admin Form Integration (`src/apps/projects/admin.py`)

Expose `response_mode` inside the Unfold Admin Project configuration parameters tab:

```python
# src/apps/projects/admin.py

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
```

### 4.4. Runtime Query View Handler (`src/apps/chat/views.py`)

```python
# src/apps/chat/views.py

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
```

## 5. Performance Metrics & Benchmarks

| Metric | Legacy / Iterative Mode (`refine`) | Optimized Mode (`compact`) | Target Improvement |
| :--- | :--- | :--- | :--- |
| **API Calls per Query** ($k=5$) | 5 Sequential Calls | 1 Consolidated Call | 80% reduction in API turns |
| **Synthesis Latency** | ~2,500ms – 4,000ms | ~400ms – 800ms | ~3x to 5x faster TTFT |
| **Token Cost Efficiency** | High (repeats query/prompt across $N$ iterations) | Low (single prompt execution) | ~40% token cost reduction |

## 6. Testing & Rollout Plan

### Unit Tests (`src/apps/chat/tests.py`)
- Verify that initializing `index.as_query_engine(response_mode="compact")` completes successfully without schema errors.
- Verify that the returned LlamaIndex `Response` object contains all expected source metadata nodes.

### Evaluation Suite Benchmark (`src/apps/evaluate/`)
- Execute evaluation runs before and after applying compact mode to verify that Answer Relevancy and Faithfulness scores remain identical or improve while query latency drops significantly.


---

# TASK 2: Product Requirement Document (PRD): Document-Type Specific Node Parsers

## 1. Executive Summary & Objective

This PRD defines the specifications for introducing Document-Type Specific Node Parsers into the ingestion pipeline (`src/apps/documents/services.py`).

Currently, the system applies a uniform chunking strategy across all uploaded documents within a project. The objective of this enhancement is to allow the ingestion pipeline to select specialized LlamaIndex NodeParser implementations based on the file type (`.pdf`, `.md`, `.py`, `.js`, `.txt`) or user-defined preferences. This ensures that document structure (such as Markdown headers or code AST nodes) is preserved, significantly improving vector retrieval recall and context precision.

## 2. Functional & Technical Overview

### 2.1. Supported Node Parsers & Rules

The ingestion engine will support five primary chunking strategies mapped to LlamaIndex transformations:

| Strategy / File Extension | LlamaIndex Class | Chunking Logic / Behavior | Target Use Case |
| :--- | :--- | :--- | :--- |
| **Markdown** (`.md`) | `MarkdownNodeParser` | Splits documents by structural Markdown headers (`#`, `##`, `###`) while preserving header metadata hierarchy. | Documentation, API guides, structured notes. |
| **Code / AST** (`.py`, `.js`, `.ts`, `.html`) | `CodeSplitter` | AST-aware splitting using tree-sitter. Prevents mid-function or mid-class breaks. | Source code files, technical scripts, API specs. |
| **Hierarchical** (`.pdf`, long text) | `HierarchicalNodeParser` | Generates a 2-tier tree of small child nodes (256 tokens) mapped to parent context blocks (1024 tokens). | Legal documents, multi-page PDFs, research papers. |
| **Sentence Boundary** (`.txt`, FAQs) | `SentenceSplitter` | Default text chunking respecting natural sentence and paragraph boundaries (512 tokens, 50 overlap). | Unstructured text notes, raw transcriptions, FAQs. |
| **Project Default** | Fallback | Inherits the strategy configured on the Project model (`apps/projects/models.py`). | General uploaded files without explicit overrides. |

## 3. High-Level Ingestion Flow

```
                     ┌──────────────────────────────┐
                     │   Uploaded File Ingestion    │
                     └──────────────┬───────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────────┐
                     │ Check Strategy / Extension:  │
                     │  - Document.chunking_strategy│
                     │  - File extension (.md, .py) │
                     └──────────────┬───────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            │ Markdown              │ Code / AST            │ Hierarchical / Default
            ▼                       ▼                       ▼
┌──────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐
│ MarkdownNodeParser   │ │ CodeSplitter         │ │ Hierarchical /       │
│ (Header-based)       │ │ (AST-aware)          │ │ SentenceSplitter     │
└───────────┬──────────┘ └──────────┬───────────┘ └───────────┬──────────┘
            │                       │                         │
            └───────────────────────┼─────────────────────────┘
                                    │ Extracted Nodes
                                    ▼
                     ┌──────────────────────────────┐
                     │   Parallel IngestionPipeline │
                     │   Embeddings & PGVectorStore │
                     └──────────────────────────────┘
```

## 4. Data Model Changes

### 4.1. Document Model (`src/apps/documents/models.py`)

Update the `Document` model to include a `chunking_strategy` field:

```python
# src/apps/documents/models.py

class Document(models.Model):
    # ... existing fields ...

    CHUNKING_CHOICES = [
        ("project_default", "Use Project Default"),
        ("auto_detect", "Auto-Detect by File Extension"),
        ("markdown", "Markdown Header Splitter"),
        ("code", "Code / AST Splitter"),
        ("hierarchical", "Hierarchical / Parent-Child"),
        ("sentence", "Sentence / Paragraph Splitter"),
    ]

    chunking_strategy = models.CharField(
        max_length=50,
        choices=CHUNKING_CHOICES,
        default="auto_detect",
        help_text="Document-specific chunking strategy."
    )
```

## 5. Technical Implementation Details

### 5.1. Dynamic Node Parser Factory (`src/apps/documents/services.py`)

```python
# src/apps/documents/services.py

import os
import logging
from llama_index.core.node_parser import (
    CodeSplitter,
    HierarchicalNodeParser,
    MarkdownNodeParser,
    SentenceSplitter,
)

logger = logging.getLogger(__name__)

def select_node_parser(file_path: str, strategy: str = "auto_detect"):
    """
    Factory function returning the appropriate LlamaIndex NodeParser instance.
    Gracefully falls back to SentenceSplitter if specialized dependencies are missing.
    """
    ext = os.path.splitext(file_path)[1].lower()

    try:
        if strategy == "markdown" or (strategy == "auto_detect" and ext == ".md"):
            return MarkdownNodeParser.from_defaults()

        elif strategy == "code" or (strategy == "auto_detect" and ext in [".py", ".js", ".ts", ".html"]):
            language_map = {
                ".py": "python",
                ".js": "javascript",
                ".ts": "typescript",
                ".html": "html"
            }
            target_lang = language_map.get(ext, "python")
            return CodeSplitter(
                language=target_lang,
                chunk_lines=40,
                chunk_lines_overlap=5,
                max_chars=1500
            )

        elif strategy == "hierarchical":
            return HierarchicalNodeParser.from_defaults(chunk_sizes=[1024, 256])

        else:
            return SentenceSplitter(chunk_size=512, chunk_overlap=50)

    except Exception as exc:
        logger.warning(f"Failed to initialize parser for {file_path} (strategy: {strategy}): {exc}. Falling back to SentenceSplitter.")
        return SentenceSplitter(chunk_size=512, chunk_overlap=50)
```

### 5.2. Pipeline Execution Integration (`src/apps/documents/services.py`)

Modify `LlamaIndexIngestionPipeline` to run parallel ingestion with the dynamic parser:

```python
# src/apps/documents/services.py

from llama_index.core.ingestion import IngestionPipeline
from llama_index.core import SimpleDirectoryReader

class LlamaIndexIngestionPipeline:
    def __init__(self, project_id):
        self.project_id = project_id
        self.embed_model = GeminiEmbedding(
            model_name="models/gemini-embedding-001",
            api_key=settings.GOOGLE_API_KEY
        )

    def index_document(self, file_path: str, original_filename: str = None, strategy: str = "auto_detect"):
        documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
        
        if original_filename:
            for doc in documents:
                doc.metadata['file_name'] = original_filename
                doc.metadata['file_path'] = original_filename

        vector_store = get_vector_store(self.project_id)
        node_parser = select_node_parser(file_path, strategy=strategy)

        # Build parallel LlamaIndex IngestionPipeline
        pipeline = IngestionPipeline(
            transformations=[
                node_parser,
                self.embed_model,
            ],
            vector_store=vector_store,
        )

        # Run multi-threaded ingestion
        nodes = pipeline.run(documents=documents, num_workers=2)
        return len(nodes) > 0
```

## 6. User Interface & Django Admin Integration

### 6.1. Upload Partial (`templates/partials/document_upload.html`)

Update the document upload HTMX modal/form to allow users to optionally select a strategy or leave it on Auto-Detect.

```html
<label for="chunking_strategy" class="block text-sm font-medium text-gray-700">Chunking Strategy</label>
<select name="chunking_strategy" id="chunking_strategy" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm">
    <option value="auto_detect" selected>Auto-Detect (Recommended)</option>
    <option value="markdown">Markdown Header Splitter</option>
    <option value="code">Code / AST Splitter</option>
    <option value="hierarchical">Hierarchical (Parent-Child)</option>
    <option value="sentence">Sentence Boundary</option>
</select>
```

### 6.2. Document List Partial (`templates/partials/document_items.html`)

Display an indicator tag showing which parser strategy was used during indexing (e.g., `[Auto: Code/AST]`, `[Markdown]`).

## 7. Quality & Testing Plan

### Unit Tests (`apps/documents/tests.py`)
- Verify that `.md` files parsed via `MarkdownNodeParser` extract header titles into node metadata.
- Verify that `.py` files parsed via `CodeSplitter` produce valid code snippets without syntax truncation.

### Benchmark Comparison (`apps/evaluate/`)
- Run evaluation benchmarks comparing a repository of `.py` and `.md` files ingested with `SentenceSplitter` vs. Document-Type Specific Parsers.
- Measure expected gains in `context_precision` and `faithfulness`.


---

# TASK 3: Product Requirement Document (PRD): Adaptive HyDE & Query Transformation Engine

## 1. Overview & Objective

This PRD outlines the architecture, data models, and implementation strategy for integrating an Adaptive HyDE (Hypothetical Document Embeddings) & Query Transformation Engine into the Django-based RAG application (`src/apps/`).

The primary objective is to solve the vocabulary/format mismatch between brief or informal user questions and formal, long-form document chunks stored in PostgreSQL vector tables. By transforming short or abstract queries into hypothetical target passages prior to vector search, the system improves semantic recall while controlling latency through adaptive routing.

## 2. Problem Statement & Functional Approach

### The Core Problem

When users submit short, conversational queries (e.g., *"Why is my app running slow?"*), embedding the raw query directly into vector space yields a query vector that aligns poorly with formal, technical documentation chunks (e.g., *"System performance degradation occurs when memory allocation limits are exceeded..."*).

### The Solution: 2-Step Execution Flow

1. **Pre-Retrieval Query Transformation (HyDE)**: Before searching the database, an LLM drafts a hypothetical technical answer passage based on the raw question.
2. **Post-Retrieval Answer Synthesis (Project Prompt)**: The real retrieved chunks are then passed back to the LLM alongside the user's Project Custom System Prompt (stored in `SystemPrompt` / `apps/projects/models.py`) to generate the final response.

## 3. High-Level System Flow

```
                               ┌──────────────────────────┐
                               │       User Query         │
                               └────────────┬─────────────┘
                                            │
                                            ▼
                    ┌────────────────────────────────────────────────┐
                    │  Project Check: Is HyDE Enabled (use_hyde)?    │
                    └───────┬────────────────────────────────┬───────┘
                            │ NO                             │ YES
                            │                                ▼
                            │             ┌────────────────────────────────────┐
                            │             │ Single-Turn Adaptive Router Call:  │
                            │             │ Classify Query & Generate HyDE Doc │
                            │             └─────────────────┬──────────────────┘
                            │                               │
                            ▼                               ▼
                     Raw User Query               Search Text (HyDE / Raw)
                            │                               │
                            └───────────────┬───────────────┘
                                            │
                                            ▼
                            ┌────────────────────────────────┐
                            │     Vector Search Engine       │
                            │  (PGVector / Postgres Store)   │
                            └───────────────┬────────────────┘
                                            │ Retrieved Chunks
                                            ▼
                            ┌────────────────────────────────┐
                            │      Final LLM Synthesis       │
                            │ Context + Project System Prompt│
                            └────────────────────────────────┘
```

## 4. Feature Specifications

### 4.1. Adaptive Query Routing (Combined Classification & Generation)

To prevent unnecessary LLM calls and latency spikes on direct lookups (e.g., error codes, product SKUs, or single-word terms), the system utilizes a Single-Turn Structured Prompt using raw text completion with regex parsing to extract the intent category and hypothetical passage.

#### Routing Logic Matrix

| Query Intent Category | Trigger Criteria / Example | Execution Path | LLM Overhead |
| :--- | :--- | :--- | :--- |
| **`DIRECT_LOOKUP`** | Contains exact IDs, error codes, SKUs, or direct definitions (e.g., *"Error 0x80070005"* or *"CEO email"*) | Bypass HyDE; search PostgreSQL using raw query text | 1 Call (Synthesis) |
| **`CONCEPTUAL`** | Broad, abstract, or informal questions regarding workflows, policies, or troubleshooting | Generate hypothetical passage; embed passage to search vector DB | 2 Calls (HyDE + Synthesis) |
