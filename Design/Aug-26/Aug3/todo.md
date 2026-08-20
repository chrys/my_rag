# Task Checklist: Google File Search Integration, Ingestion Hygiene & Unified Document Pipeline (Aug 3)

---

- [X] Task 1: Update Django Models & Migrations (Document State Registry & Project GFS Parameters)
  - Acceptance: Add `content_hash`, `store_file_id`, and `custom_metadata` to `Document` model. Update `Project` model validation: re-enable `storage_type='google'`, lock chunking/embedding to Default, add `gemini-3.5-flash-lite` and `gemini-3.7-flash` choices, and disable HyDE/Synthesizer/Response Mode for GFS. Clean migrations generated and applied.
  - Verify: `DJANGO_ENV=testing .venv/bin/pytest Testing/unit/projects/test_models.py Testing/unit/documents/test_models.py --tb=short`
  - Files: `src/apps/documents/models.py`, `src/apps/projects/models.py`, `src/apps/projects/serializers.py`, `Testing/unit/documents/test_models.py`, `Testing/unit/projects/test_models.py`

- [X] Task 2: Implement GFS Core Services (Store Provisioning, Dynamic Models, Typed Metadata & Filter Builder)
  - Acceptance: Implement `create_file_search_store` in `src/google_file_search.py`. Update `add_document_to_store` to pass typed `custom_metadata` (max 20 items, mutually exclusive `string_value`/`numeric_value`). Update `ask_store_question` to support dynamic LLM model selection and optional `metadata_filter` expression. Update project creation view to immediately provision remote GFS stores.
  - Verify: `DJANGO_ENV=testing .venv/bin/pytest Testing/unit/projects/test_gfs_core.py --tb=short`
  - Files: `src/google_file_search.py`, `src/apps/projects/views.py`, `Testing/unit/projects/test_gfs_core.py`

- [X] Task 3: Implement Pre-Upload Format, Hygiene & Deduplication Gate
  - Acceptance: Implement `compute_file_sha256`, `check_document_hygiene` (whitelist verification, 0-byte check, 100MB sanity check, PDF/DOCX corruption & DRM lock check), and `strip_noisy_artifacts` (headers, footers, pagination `Page X of Y`, boilerplate disclaimers, HTML cleanup). Integrate MarkItDown normalization when enabled.
  - Verify: `DJANGO_ENV=testing .venv/bin/pytest Testing/unit/documents/test_gfs_hygiene.py --tb=short`
  - Files: `src/apps/documents/services.py`, `Testing/unit/documents/test_gfs_hygiene.py`

- [X] Task 4: Implement 3-Step Metadata Extraction Pipeline & Typed GFS Formatter
  - Acceptance: Implement `extract_system_and_file_metadata` (Python file stats, date, user, PDF page count & author via `pypdf`), `extract_ai_metadata_with_gemini_flash` (first 3 pages to `gemini-2.5-flash-lite` with structured JSON schema and graceful fallback), and `format_and_validate_gfs_metadata` (strictly typed `string_value` or `numeric_value`, max 20 items).
  - Verify: `DJANGO_ENV=testing .venv/bin/pytest Testing/unit/documents/test_gfs_metadata.py --tb=short`
  - Files: `src/apps/documents/services.py`, `Testing/unit/documents/test_gfs_metadata.py`

- [X] Task 5: Implement Inspection & Upload HTMX Views with Duplicate Handling
  - Acceptance: Implement pre-upload inspection view (`inspect_document`) that checks SHA-256 collision (returns duplicate modal), performs hygiene checks, runs Step 1 + Step 2 metadata extraction, and returns the review modal. Implement upload finalization (`upload_document`) supporting confirmed custom metadata, Force Re-upload (deleting old GFS index), and persisting to Local State Registry.
  - Verify: `DJANGO_ENV=testing .venv/bin/pytest Testing/unit/documents/test_gfs_views.py --tb=short`
  - Files: `src/apps/documents/views.py`, `src/apps/documents/urls.py`, `Testing/unit/documents/test_gfs_views.py`

- [X] Task 6: Implement Frontend Templates (Project Form Parameter Locks, Upload & Duplicate Modals, Document Badges)
  - Acceptance: Update `project_form.html` to dynamically adjust fields when `Google File Search` is selected (disable Response Mode/HyDE/Synthesizer, lock Chunking/Embedding, restrict LLM models). Create `document_upload_modal.html` with interactive metadata editor table. Create `document_duplicate_modal.html` with Skip and Force Re-upload actions. Update `document_list.html` to display GFS metadata badges.
  - Verify: Load `/rag/projects/` and `/rag/documents/` in browser, verify dynamic form behavior, upload modal interaction, duplicate collision prompt, and run `DJANGO_ENV=testing .venv/bin/pytest Testing/unit/documents/ --tb=short`.
  - Files: `templates/partials/project_form.html`, `templates/partials/document_upload_modal.html`, `templates/partials/document_duplicate_modal.html`, `templates/partials/document_list.html`

- [X] Task 7: Full Regression Verification & Walkthrough Documentation
  - Acceptance: Run complete pytest test suite across all apps, verify 0 regressions across `local`, `postgres`, and `google` storage types, and produce final walkthrough documentation.
  - Verify: `DJANGO_ENV=testing .venv/bin/pytest Testing/unit/ Testing/regression/ --tb=short`
  - Files: `Design/Aug-26/Aug3/walkthrough.md`
