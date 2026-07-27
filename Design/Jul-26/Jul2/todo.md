# Task Checklist

- [x] Task 1.1: Add `response_mode` field to Project model & run migrations
  - Acceptance: `Project` model in `src/apps/projects/models.py` has `response_mode` field with choices `compact`, `refine`, `tree_summarize` (default `"compact"`). Database migrations generated and applied.
  - Verify: `python manage.py makemigrations && python manage.py test Testing/unit/projects/`
  - Files: `src/apps/projects/models.py`

- [x] Task 1.2: Expose `response_mode` in Project Admin interface
  - Acceptance: `response_mode` field is added to `fieldsets` in `src/apps/projects/admin.py`.
  - Verify: Admin page renders `response_mode` parameter field.
  - Files: `src/apps/projects/admin.py`

- [x] Task 1.3: Update Query Engine to use `response_mode`
  - Acceptance: `as_query_engine` calls in `src/apps/chat/views.py` and `src/postgres_rag.py` pass dynamic `response_mode` from project configuration.
  - Verify: Unit test verifying `response_mode="compact"` parameter in query engine initialization.
  - Files: `src/apps/chat/views.py`, `src/postgres_rag.py`

- [x] Task 2.1: Add `chunking_strategy` field to Document model
  - Acceptance: `Document` model in `src/apps/documents/models.py` includes `chunking_strategy` choice field (default `"auto_detect"`).
  - Verify: `python manage.py makemigrations` succeeds.
  - Files: `src/apps/documents/models.py`

- [x] Task 2.2: Implement `select_node_parser` factory with dependency fallbacks
  - Acceptance: Factory function returns `MarkdownNodeParser` for `.md`, `CodeSplitter` for `.py`/`.js`/`.ts`/`.html`, `HierarchicalNodeParser` for `.pdf`, and `SentenceSplitter` for `.txt`. Fall back to `SentenceSplitter` if dependencies fail.
  - Verify: Unit tests verifying parser selection and fallback behavior.
  - Files: `src/apps/documents/services.py`

- [x] Task 2.3: Integrate dynamic parser into `LlamaIndexIngestionPipeline`
  - Acceptance: Document indexing pipeline applies `select_node_parser` based on document file extension and `chunking_strategy`.
  - Verify: Test document ingestion with `.md` and `.py` files.
  - Files: `src/apps/documents/services.py`

- [x] Task 2.4: Update Document Upload UI & List Partial
  - Acceptance: Upload form dropdown permits selecting strategy. Document list item renders strategy badge.
  - Verify: Rendered HTML includes strategy select menu and badge tags.
  - Files: `templates/partials/document_upload.html`, `templates/partials/document_items.html`

- [x] Task 3.1: Add `use_hyde` field to Project model & admin
  - Acceptance: `Project` model includes `use_hyde` boolean field (`default=False`), exposed in admin fieldsets.
  - Verify: `python manage.py makemigrations` succeeds.
  - Files: `src/apps/projects/models.py`, `src/apps/projects/admin.py`

- [x] Task 3.2: Implement Adaptive HyDE Router & Passage Generator
  - Acceptance: Single-turn router classifies query into `DIRECT_LOOKUP` or `CONCEPTUAL` using raw text completion + regex extraction.
  - Verify: Unit tests for direct lookup bypass vs conceptual HyDE document generation.
  - Files: `src/apps/chat/services.py`, `src/apps/chat/views.py`

- [x] Task 3.3: Integration & End-to-End Verification
  - Acceptance: Full test suite passes without regressions.
  - Verify: `pytest` / `python manage.py test`
  - Files: `Testing/unit/`
