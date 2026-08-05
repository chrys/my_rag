# Changelog & Implementation Record: Jul3 Branch

---

## 📋 Overview

The `Jul3` branch delivers two core capabilities for the platform:
1. **Multi-Model AI Management**: Enables project-level configuration of Embedding models (`models/gemini-embedding-001` with strict 768-dim output and immutability guardrails) and dynamic LLM synthesis routing between Cloud API (`gemini-2.5-flash-lite`) and Local MLX Engine (`gemma4:12b-mlx` via Ollama API at `http://localhost:11434/api/generate`).
2. **Native Obsidian Vault Integration**: Adds support for indexing and synchronizing local Obsidian markdown vaults with automated directory scanning, double-bracket link sanitization, chunk metadata enrichment, dynamic HTMX UI tabs, and a 3-stage sync lifecycle engine.

---

## 🚀 Key Features & Changes Delivered

### 1. Multi-Model AI Management

- **Project Schema & Immutability Guardrail**
  - **`src/apps/projects/models.py`**: Added `llm_model` CharField (`gemini-2.5-flash-lite`, `gemma4:12b-mlx`, `gemma4:e2b-mlx`, `gemma4:e4b-mlx`) and `disable_thinking` BooleanField (`default=False`). Updated `embedding_model` choices (`models/gemini-embedding-001`).
  - Implemented immutability validation in `Project.clean()` that raises a `ValidationError` when attempting to modify `embedding_model` on projects that already have indexed documents (`document_count > 0`).
  - **`src/apps/projects/serializers.py` & `src/apps/projects/admin.py`**: Updated REST API serializers and Django Admin interface to expose `disable_thinking` and `llm_model`.
  - **`static/admin/js/custom_prompt_toggle.js`**: Added dynamic toggle logic to display the `Disable Thinking` field row in Parameters only when a local Gemma model is selected.

- **Dynamic LLM Request Router & Performance Tuning**
  - **`src/apps/chat/llm_router.py`**: Created dynamic router function `generate_llm_response(prompt, model_id, system_prompt, disable_thinking)`.
  - Routes requests for `gemini-2.5-flash-lite` to Google Gemini Cloud API using `google.genai` Client.
  - Routes requests for `gemma4:*` models to local Ollama API server (`http://localhost:11434/api/generate`). When `disable_thinking` is enabled, passes `thinking=False` and `options={"thinking": False}` to disable reasoning overhead.
  - **`src/apps/chat/views.py` & `src/apps/chat/services.py`**: Integrated router and `Ollama(thinking=False)` into RAG chat synthesis and HyDE passage generation pipeline.
  - **Response Time UI Metrics**: Measured backend query execution time and rendered `⏱️ Response Time: X.XXs` directly under the Source Nodes section in [chat_workflow.html](file:///Users/chrys/Projects/my_rag/templates/admin/chat_workflow.html).

---

### 2. Native Obsidian Vault Integration

- **Obsidian Data Models**
  - **`src/apps/documents/models.py`**: Added `ObsidianSource` (OneToOne with `Project`, storing `vault_path`, `source_type`, `last_synced_at`) and `ObsidianFile` (ForeignKey to `ObsidianSource`, tracking `relative_path`, `folder_name`, `status` [`PENDING`, `MODIFIED`, `INDEXED`, `FAILED`], `file_mtime`, and `last_indexed_at`).
  - **`src/apps/documents/admin.py`**: Registered `ObsidianSourceAdmin` and `ObsidianFileAdmin`.

- **Obsidian Ingestion & Traversal Engine**
  - **`src/apps/documents/services.py`**:
    - `scan_obsidian_vault(vault_path)`: Scans local vault directories with strict exclusion rules (skipping `_resources/`, `Templates/`, `.obsidian/`, `.git/`, binary media, `.canvas`, and `Untitled` drafts).
    - `discover_obsidian_vault_files(source)`: Detects new notes (`PENDING`) and modified notes on disk (`MODIFIED` status when disk `mtime` exceeds stored `file_mtime`).
    - `sanitize_obsidian_markdown(text)`: Strips Obsidian double-bracket link syntax (converts `[[Note|Alias]]` -> `Alias` and `[[Note]]` -> `Note`).
    - `enrich_chunk_metadata(chunk, folder, file_name, project_id)`: Attaches immediate parent `folder`, relative `file_name`, and `project_id` to ingested vector chunks.
    - `process_obsidian_file_indexing`: Purges old vector embeddings for notes (`engine.delete_document`) prior to re-indexing modified notes.
    - **3-Stage Sync & Indexing Lifecycle Engine**:
      - `index_obsidian_vault(project_id)`: Performs a full re-index of all valid notes in the vault.
      - `index_new_obsidian_files(project_id)`: Incremental indexing targeting `PENDING`, `MODIFIED`, and `FAILED` notes.
      - `sync_obsidian_vault(project_id)`: Compares file modified timestamps (`mtime`) to re-index modified notes and purge deleted notes.

- **Obsidian UI & HTMX Frontend Integration**
  - **`templates/partials/document_list.html` & `templates/partials/obsidian_section.html`**: Redesigned the project "Sources" tab with a `Type` selector (`Document` vs `Obsidian`).
  - Updated action buttons (`Index ALL Obsidian files`, `Find Updates`, `Index New Files`) and added blue `MODIFIED` badge rendering in the pending/modified notes table.
  - **`src/apps/documents/views.py` & `src/apps/documents/urls.py`**: Created HTMX partial endpoints for mode switching, vault discovery, and note status table updates (`/rag/projects/<id>/obsidian/...`).

---

## 🗄️ Database Migrations

- `src/apps/projects/migrations/0011_project_llm_model_alter_project_embedding_model.py`: Adds `llm_model` field to `Project` model.
- `src/apps/projects/migrations/0012_alter_project_llm_model.py`: Adds `gemma4:e2b-mlx` and `gemma4:e4b-mlx` choices to `Project.llm_model`.
- `src/apps/projects/migrations/0013_project_disable_thinking.py`: Adds `disable_thinking` BooleanField to `Project` model.
- `src/apps/documents/migrations/0004_obsidiansource_obsidianfile.py`: Creates `ObsidianSource` and `ObsidianFile` models.
- `src/apps/documents/migrations/0005_alter_obsidianfile_status.py`: Adds `MODIFIED` status choice to `ObsidianFile.status`.

---

## 🧪 Testing & Verification

All capabilities were verified with dedicated unit tests in `Testing/unit/`:

- **`Testing/unit/projects/test_models.py`**: Tests model fields (`disable_thinking`, `llm_model`), choices, and immutability guardrails on `Project.clean()`.
- **`Testing/unit/chat/test_llm_router.py`**: Tests LLM routing behavior between cloud Gemini API and local Ollama API.
- **`Testing/unit/documents/test_obsidian_models.py`**: Tests `ObsidianSource` and `ObsidianFile` relationships and constraints.
- **`Testing/unit/documents/test_obsidian_services.py`**: Tests vault traversal exclusion rules, link sanitization, and metadata enrichment.
- **`Testing/unit/documents/test_obsidian_lifecycle.py`**: Tests full re-indexing, incremental indexing, and timestamp-based sync lifecycle.
- **`Testing/unit/documents/test_obsidian_views.py`**: Tests HTMX view responses and Obsidian endpoints.

**Test Run Result:** `369 passed` across entire unit test suite.
