# Implementation Task Checklist: Multi-Model AI & Obsidian Integration

- [X] Task 1: Model Schema Updates & Immutability Guardrail
  - Acceptance: `Project` model updated with `llm_model` and `embedding_model` choices; `clean()` enforces immutability when `document_count > 0`. Django migrations created and applied cleanly.
  - Verify: `.venv/bin/pytest Testing/unit/projects/test_models.py`
  - Files: `src/apps/projects/models.py`, `src/apps/projects/serializers.py`, `src/apps/projects/migrations/`

- [X] Task 2: Obsidian Source & File Data Models
  - Acceptance: `ObsidianSource` and `ObsidianFile` models created with correct FKs, vault_path, status choices, and timestamps. Migrations applied.
  - Verify: `.venv/bin/python manage.py check` && `.venv/bin/pytest Testing/unit/documents/`
  - Files: `src/apps/documents/models.py`, `src/apps/documents/migrations/`

- [X] Task 3: Multi-Model LLM Dynamic Router
  - Acceptance: `llm_router.py` created to route requests to cloud Gemini 2.5 Flash Lite or local Ollama `http://localhost:11434/api/generate` for `gemma4:12b-mlx`.
  - Verify: `.venv/bin/pytest Testing/unit/chat/test_llm_router.py`
  - Files: `src/apps/chat/llm_router.py`, `src/apps/chat/views.py`, `Testing/unit/chat/test_llm_router.py`

- [X] Task 4: Obsidian Vault Scanner, Markdown Sanitizer & Metadata Enricher
  - Acceptance: Service functions to scan vault paths with exclusion rules, sanitize Markdown double-bracket links (`[[Note|Alias]]` -> `Alias`), and enrich chunks with `folder`, `file_name`, and `project_id`.
  - Verify: `.venv/bin/pytest Testing/unit/documents/test_obsidian_services.py`
  - Files: `src/apps/documents/services.py`, `Testing/unit/documents/test_obsidian_services.py`

- [X] Task 5: 3-Stage Obsidian Sync & Indexing Lifecycle Engine
  - Acceptance: Functions for `index_obsidian_vault`, `index_new_obsidian_files`, and `sync_obsidian_vault` (comparing timestamps and purging deleted notes).
  - Verify: `.venv/bin/pytest Testing/unit/documents/test_obsidian_lifecycle.py`
  - Files: `src/apps/documents/services.py`, `Testing/unit/documents/test_obsidian_lifecycle.py`

- [X] Task 6: Obsidian Views, Endpoints & HTMX Partial Templates
  - Acceptance: Sources tab UI extended with `Type` selector (`Document` vs `Obsidian`), dedicated Obsidian path input, action buttons (`Index Obsidian Files`, `Sync`, `Index New Files`), and status table.
  - Verify: Manual check via server `/rag/dashboard/` and `.venv/bin/pytest Testing/unit/documents/test_obsidian_views.py`
  - Files: `src/apps/documents/views.py`, `src/apps/documents/urls.py`, `templates/projects/partials/sources_tab.html`, `templates/projects/partials/obsidian_section.html`
