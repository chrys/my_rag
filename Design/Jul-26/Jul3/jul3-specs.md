# Technical Specification: Multi-Model AI Management & Obsidian Vault Integration

---

## 1. Objective & Scope

This specification defines the functional, data, architectural, UI/UX, and testing requirements for two key platform capabilities:

1. **Task 1: Multi-Model AI Management**
   - Project-level configurable embedding model selection (supporting `models/gemini-embedding-001` as default, strictly enforcing a 768-dimensional output).
   - Embedding model immutability guardrail strictly locking the field (read-only in UI, enforcing `ValidationError` on API update attempts once documents/notes are indexed).
   - Project-level LLM model selection for synthesis, chat, and evaluation (`gemini-2.5-flash-lite` cloud API vs `gemma4:12b-mlx`, `gemma4:e2b-mlx`, `gemma4:e4b-mlx` local MLX / Ollama engine).
   - `Disable Thinking` configuration: Conditionally visible checkbox in Parameters when a local Gemma model is selected. Disables Gemma reasoning mode for fast generation by passing `thinking=False` in Ollama API calls.
   - Response Time Display: Measures backend execution time for each query and displays `Response Time: X.XXs` in the chat UI directly under the Source Nodes section.
   - Dynamic runtime routing to cloud API or local engine (connecting strictly to the local Ollama server API at `http://localhost:11434/api/generate` for local Gemma models).
   - Graceful local LLM failure handling: Intercepts Ollama connection errors (`http://localhost:11434`) and informs the user that Ollama is not running and needs to be started.

2. **Task 2: Native Obsidian Vault Integration**
   - Project management "Sources" tab UI update with a `Type` selector (`Document` vs `Obsidian`).
   - Dynamic section display: Standard Document Uploader for `Document` mode vs path input, action buttons (`Index ALL Obsidian files`, `Find Updates`, `Index New Files`), count summary cards, and pending/modified/failed notes table for `Obsidian` mode.
   - Page load context population: Automatically computes and passes Obsidian vault statistics (`get_obsidian_context`) on initial project page load (`list_documents` view).
   - Distinct action button & UI behaviors:
     - `Index ALL Obsidian files`: Performs a full re-index of all valid notes in the vault. Prompts with a confirmation dialog (`hx-confirm`) if notes are already indexed.
     - `Find Updates`: Scans the vault directory to detect new files (`PENDING`) and modified files (`MODIFIED` status when disk `mtime` is newer than stored `file_mtime`) without automatically indexing them.
     - `Index New Files`: Ingests all pending, modified, and failed notes (`PENDING`, `MODIFIED`, `FAILED`), purging old vector embeddings for modified notes prior to re-indexing.
     - **Hidden Indexed Files List**: Hides the list of indexed files, rendering count cards at the top and listing pending, modified, or failed notes in the issues table.
   - Automated vault directory traversal with strict exclusion rules (skipping reserved folders `_resources/`, `Templates/`, `.obsidian/`, `.git/`, binary media, `.canvas`/`.base`, and `Untitled` drafts).
   - Markdown syntax sanitization (`[[Target Note|Custom Alias]]` -> `Custom Alias`, `[[Target Note]]` -> `Target Note`).
   - Metadata enrichment tagging on each chunk (`folder` storing immediate parent folder name, `file_name` storing relative file path, and `project_id`).
   - Three-stage sync and indexing lifecycle (Discovery -> Pre-Processing & Metadata -> Vector Ingestion).

---

## 2. Common & Required Commands

```bash
# Activate virtual environment
source .venv/bin/activate

# Check Django configuration
.venv/bin/python manage.py check

# Generate database migrations
.venv/bin/python manage.py makemigrations

# Apply database migrations
.venv/bin/python manage.py migrate

# Run local development server (with SSH tunnel to Postgres)
./run.sh

# Execute test suite
.venv/bin/pytest

# Execute specific app tests
.venv/bin/pytest Testing/unit/projects/
.venv/bin/pytest Testing/unit/documents/
.venv/bin/pytest Testing/unit/chat/
```

---

## 3. Project Structure

The feature implementation spans the following components across the Django codebase:

```
src/
├── apps/
│   ├── projects/
│   │   ├── models.py             # Project schema updates (embedding_model, llm_model choices & immutability validation)
│   │   ├── views.py              # Project UI views & store helper updates
│   │   ├── api_views.py          # DRF ProjectViewSet serialization & filtering
│   │   ├── serializers.py        # Serializers for embedding_model and llm_model
│   │   └── admin.py              # Django Admin interface overrides
│   ├── documents/
│   │   ├── models.py             # ObsidianSource & ObsidianFile status tracking models
│   │   ├── views.py              # Sources tab partials, Obsidian indexing & sync views
│   │   ├── services.py           # Vault traversal scanner, Markdown sanitizer, & chunk enricher
│   │   └── urls.py               # Obsidian action endpoints (/rag/projects/<id>/obsidian/...)
│   └── chat/
│       ├── views.py              # LLM routing handler
│       └── llm_router.py         # Dynamic routing logic (Gemini cloud vs http://localhost:11434/api/generate)
├── postgres_rag.py               # Vector ingestion & 768-dim embedding enforcement
templates/
└── projects/
    └── partials/
        ├── sources_tab.html      # Sources tab container with Type selector
        ├── document_section.html # Document manager section
        └── obsidian_section.html # Obsidian configuration, action controls & status table
Testing/
└── unit/
    ├── projects/                 # Tests for Project models, serializers, and model immutability
    ├── documents/                # Tests for vault traversal, link sanitization, metadata & sync
    └── chat/                     # Tests for LLM routing (Gemini cloud vs Ollama local API)
```

---

## 4. Code Style & Guidelines

- **PEP 8 Compliance:** Adhere to standard Python styling (snake_case functions/variables, PascalCase models/classes, 120-character line length limit).
- **Separation of Concerns:** Keep Django views thin; isolate vault scanning, Markdown sanitization, and LLM routing inside dedicated service modules (`services.py`, `llm_router.py`).
- **ORM & Database Best Practices:** Use `select_related()` and `prefetch_related()` to prevent N+1 queries. Wrap multi-table state updates in `django.db.transaction.atomic`.
- **Dynamic Frontend Updates:** Utilize HTMX partials (`django-htmx`) for switching between `Document` and `Obsidian` source modes and updating the file status table asynchronously.
- **Type Annotations:** Maintain clear type hints across all service methods (e.g., `def sanitize_markdown(text: str) -> str:`).

---

## 5. Testing Strategy

All new capabilities must be backed by unit and integration tests under `Testing/unit/`:

1. **AI Model Management Tests (`Testing/unit/projects/`):**
   - Verify `Project` model accepts `embedding_model` (`models/gemini-embedding-001`) and `llm_model` (`gemini-2.5-flash-lite`, `gemma4:12b-mlx`).
   - Test immutability guardrail: attempting to change `embedding_model` after `document_count > 0` raises a `ValidationError` and field is disabled in UI.
   - Test LLM router returns cloud provider client for `gemini-2.5-flash-lite` and calls `http://localhost:11434/api/generate` for `gemma4:12b-mlx`.

2. **Obsidian Vault Traversal & Sanitization Tests (`Testing/unit/documents/`):**
   - Test directory scanner correctly ignores reserved folders (`_resources/`, `.obsidian/`, `.git/`, `Templates/`), binary files (`.png`, `.pdf`), proprietary files (`.canvas`, `.base`), and draft notes (`Untitled *.md`).
   - Test Markdown sanitizer converts `[[Target Note|Custom Alias]]` to `Custom Alias` and `[[Target Note]]` to `Target Note`.
   - Test metadata tagger attaches immediate parent `folder`, relative `file_name`, and `project_id` to text chunks.

3. **Lifecycle Sync & Discovery Tests (`Testing/unit/documents/`):**
   - Test `Index ALL Obsidian files` full re-indexing execution and confirmation prompt.
   - Test `Discover new Files` execution populates `PENDING` records without indexing.
   - Test `Index New Files` incremental indexing execution for unindexed notes.

---

## 6. Guardrails & Boundaries

### 6.1. Dos 👍
- **Do enforce 768-dim embeddings:** Ensure all vector embeddings generated by `models/gemini-embedding-001` match 768 dimensions before writing to vector storage.
- **Do sanitize user paths:** Validate local vault path input to ensure directory existence and prevent directory traversal security risks.
- **Do use named URL patterns:** Reference all Obsidian sync and indexing endpoints via named URLs (e.g., `{% url 'documents:obsidian_sync' project_id %}`).
- **Do test changes:** Run `.venv/bin/pytest` after every code update.

### 6.2. Ask Before ❓
- **Ask before modifying shared DB schemas:** Confirm with team before altering existing PostgreSQL vector table structures or indexing column definitions.
- **Ask before changing default models:** Require user approval before changing default fallback model selections.

### 6.3. Don'ts 👎
- **Don't allow embedding model mutation after indexing:** Never allow changing `embedding_model` on a project that already has indexed documents.
- **Don't hardcode absolute paths:** Never hardcode local file paths in repository code; always pull from project configuration or user input.
- **Don't bypass Markdown sanitization:** Never ingest raw Obsidian double-bracket link syntax into vector storage without pre-processing.