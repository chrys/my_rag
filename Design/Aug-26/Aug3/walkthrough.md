# Sprint Walkthrough: Google File Search Integration, Ingestion Hygiene & Unified Document Pipeline (Aug 3)

## Overview
Successfully implemented full end-to-end Google File Search (GFS) integration, pre-upload ingestion hygiene & format gating, SHA-256 local state registry deduplication, 3-step metadata extraction & user enrichment, parameter constraints locking, and HTMX UI review & duplicate collision modals.

---

## Changes Implemented

### 1. Database Models & State Registry (`src/apps/documents/models.py`, `src/apps/projects/models.py`)
- **Document Model**: Added `content_hash` (SHA-256 indexed), `store_file_id` (GFS resource identifier), and `custom_metadata` (stored key-value dictionary).
- **Project Model**:
  - Re-enabled `storage_type = 'google'` in `clean()`.
  - Added choices for `gemini-3.5-flash-lite` and `gemini-3.7-flash`.
  - Enforced parameter locks when `storage_type == 'google'` (disabling HyDE, Synthesizer, and Response Mode; locking Chunking and Embedding to Default).
- **Django Migrations**: Clean migrations generated and applied (`documents.0007` and `projects.0014`).

### 2. GFS Core Upgrades (`src/google_file_search.py`, `src/apps/projects/views.py`, `src/apps/chat/views.py`)
- **Store Provisioning**: Implemented `create_file_search_store` with immediate creation on project setup and error handling for invalid API keys/permissions.
- **Typed Metadata Ingestion**: Updated `add_document_to_store` to format and upload up to 20 typed metadata items (`string_value` or `numeric_value`).
- **Dynamic Querying & Filtering**: Updated `ask_store_question` to support dynamic LLM model selection and optional `metadata_filters` expressions.

### 3. Pre-Upload Format & Hygiene Gate (`src/apps/documents/services.py`)
- **Hygiene Gate**: Implemented `check_document_hygiene` verifying whitelisted extensions, 0-byte guard, 100MB single-file size ceiling, and PDF/DOCX corruption or DRM encryption checks.
- **SHA-256 Deduplication**: Implemented `compute_file_sha256` for instant local collision detection.
- **Noise Stripping**: Implemented `strip_noisy_artifacts` to clean headers, footers, pagination patterns (`Page X of Y`, `- X -`), and legal boilerplate.

### 4. 3-Step Metadata Extraction Pipeline (`src/apps/documents/services.py`)
- **Step 1 (System/File)**: `extract_system_and_file_metadata` extracts deterministic file stats, date, uploader, and PDF page count & author.
- **Step 2 (AI Content Classification)**: `extract_ai_metadata_with_gemini_flash` extracts `document_type`, `department`, and `language` with graceful fallback on rate limits or offline mode.
- **Step 3 (GFS Typed Formatter)**: `format_and_validate_gfs_metadata` sanitizes keys, enforces type exclusivity, and caps at 20 entries.

### 5. HTMX Views & Interactive Modals (`src/apps/documents/views.py`, `src/apps/documents/urls.py`, `templates/partials/`)
- **Pre-Flight Inspection View**: `inspect_document` endpoint runs hygiene checks, detects SHA-256 hash collisions, extracts initial metadata, and serves the corresponding modal.
- **Duplicate Collision Modal**: `templates/partials/document_duplicate_modal.html` prompts user to "Skip Upload" or "Force Re-upload" (which purges old GFS store index and replaces it).
- **Metadata Review Modal**: `templates/partials/document_upload_modal.html` provides interactive key-value tag editor before final confirmation.
- **Document Badges**: `templates/partials/document_items.html` renders metadata badges directly below document items.
- **Project Form Parameter Locks**: `templates/partials/project_form.html` dynamically locks parameters when `Google File Search` is selected.

---

## Verification Results

### Automated Test Suite
- **GFS Core Tests**: `Testing/unit/projects/test_gfs_core.py` (6 passed)
- **Hygiene Gate Tests**: `Testing/unit/documents/test_gfs_hygiene.py` (6 passed)
- **Metadata Pipeline Tests**: `Testing/unit/documents/test_gfs_metadata.py` (4 passed)
- **Inspection & Upload Views Tests**: `Testing/unit/documents/test_gfs_views.py` (4 passed)
- **Models & Serializer Tests**: `Testing/unit/projects/test_models.py`, `Testing/unit/documents/test_models.py`, `Testing/unit/projects/test_serializers.py` (80 passed)
- **Full Test Suite Regression**: **450 tests passed across all apps with 0 failures**.
