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
  - **`src/apps/projects/models.py`**: Added `llm_model` CharField (`gemini-2.5-flash-lite` vs `gemma4:12b-mlx`) and updated `embedding_model` choices (`models/gemini-embedding-001`).
  - Implemented immutability validation in `Project.clean()` that raises a `ValidationError` when attempting to modify `embedding_model` on projects that already have indexed documents (`document_count > 0`).
  - **`src/apps/projects/serializers.py` & `src/apps/projects/admin.py`**: Updated REST API serializers and Django Admin interfaces to expose and validate `llm_model` and `embedding_model`.

- **Dynamic LLM Request Router**
  - **`src/apps/chat/llm_router.py`**: Created dynamic router function `generate_llm_response(prompt, model_id, system_prompt)`.
  - Routes requests for `gemini-2.5-flash-lite` to Google Gemini Cloud API using `google.genai` Client.
  - Routes requests for `gemma4:12b-mlx` to local Ollama API server (`http://localhost:11434/api/generate`).
  - **`src/apps/chat/views.py` & `src/apps/chat/services.py`**: Integrated router into RAG chat synthesis pipeline.

---

### 2. Native Obsidian Vault Integration

- **Obsidian Data Models**
  - **`src/apps/documents/models.py`**: Added `ObsidianSource` (OneToOne with `Project`, storing `vault_path`, `source_type`, `last_synced_at`) and `ObsidianFile` (ForeignKey to `ObsidianSource`, tracking `relative_path`, `folder_name`, `status` [`PENDING`, `INDEXED`, `FAILED`], `file_mtime`, and `last_indexed_at`).
  - **`src/apps/documents/admin.py`**: Registered `ObsidianSourceAdmin` and `ObsidianFileAdmin`.

- **Obsidian Ingestion & Traversal Engine**
  - **`src/apps/documents/services.py`**:
    - `scan_obsidian_vault(vault_path)`: Scans local vault directories with strict exclusion rules:
      - Ignores folders: `_resources/`, `Templates/`, `.obsidian/`, `.git/`
      - Ignores non-markdown/binary/canvas files: `.png`, `.jpg`, `.pdf`, `.canvas`, `.base`
      - Ignores draft notes matching `Untitled *.md`
    - `sanitize_obsidian_markdown(text)`: Strips Obsidian double-bracket link syntax (converts `[[Note|Alias]]` -> `Alias` and `[[Note]]` -> `Note`).
    - `enrich_chunk_metadata(chunk, folder, file_name, project_id)`: Attaches immediate parent `folder`, relative `file_name`, and `project_id` to ingested vector chunks.
    - **3-Stage Sync & Indexing Lifecycle Engine**:
      - `index_obsidian_vault(project_id)`: Performs a full re-index of all valid notes in the vault.
      - `index_new_obsidian_files(project_id)`: Incremental indexing restricted to pending/unindexed notes.
      - `sync_obsidian_vault(project_id)`: Compares file modified timestamps (`mtime`) to re-index modified notes and purge deleted notes.

- **Obsidian UI & HTMX Frontend Integration**
  - **`templates/partials/document_list.html` & `templates/partials/obsidian_section.html`**: Redesigned the project "Sources" tab with a `Type` selector (`Document` vs `Obsidian`).
  - Added dedicated path input, action buttons (`Index Obsidian Files`, `Sync`, `Index New Files`), and a live status table showing note path, parent folder, status badge, and last indexed time.
  - **`src/apps/documents/views.py` & `src/apps/documents/urls.py`**: Created HTMX partial endpoints for mode switching, vault indexing, and note status table updates (`/rag/projects/<id>/obsidian/...`).

---

## 🗄️ Database Migrations

- `src/apps/projects/migrations/0011_project_llm_model_alter_project_embedding_model.py`: Adds `llm_model` field to `Project` model.
- `src/apps/documents/migrations/0004_obsidiansource_obsidianfile.py`: Creates `ObsidianSource` and `ObsidianFile` models.

---

## 🧪 Testing & Verification

All capabilities were verified with dedicated unit tests in `Testing/unit/`:

- **`Testing/unit/projects/test_models.py`**: Tests model fields, choices, and immutability guardrails on `Project.clean()`.
- **`Testing/unit/chat/test_llm_router.py`**: Tests LLM routing behavior between cloud Gemini API and local Ollama API.
- **`Testing/unit/documents/test_obsidian_models.py`**: Tests `ObsidianSource` and `ObsidianFile` relationships and constraints.
- **`Testing/unit/documents/test_obsidian_services.py`**: Tests vault traversal exclusion rules, link sanitization, and metadata enrichment.
- **`Testing/unit/documents/test_obsidian_lifecycle.py`**: Tests full re-indexing, incremental indexing, and timestamp-based sync lifecycle.
- **`Testing/unit/documents/test_obsidian_views.py`**: Tests HTMX view responses and Obsidian endpoints.

**Test Run Result:** `135 passed` across entire unit test suite.
