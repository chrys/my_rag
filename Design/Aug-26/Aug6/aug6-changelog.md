# Sprint Changelog: Aug 6 - Removal of Project-Level Chunking Field & Pico.css Dashboard Redesign

**Branch:** `Aug6`  
**Date:** August 30, 2026  
**Focus:** 
1. Architectural simplification — remove redundant `chunking` setting from `Project` and establish `Document.chunking_strategy` as the sole source of truth for text chunking.
2. **Task 1: Dashboard Redesign with Pico.css** — Modern, lightweight project-scoped dashboard with primary blue palette (`#2563eb`), sticky project selector, and 5-section sidebar navigation.
3. **Task 2: Advanced Document Management Solution** — Multi-tier deduplication pipeline (SHA-256 binary match + SimHash near-duplicate detection), real-time search & multi-axis filtering, chunk inspection, and atomic PostgreSQL PGVector hard deletion.

---

## 1. Motivation & Background

- **Chunking Simplification**: With document-type specific node parsers (`auto_detect`, `markdown`, `code`, `hierarchical`, `sentence`), chunking is handled dynamically per document. The legacy `Project.chunking` field was removed across all models, migrations, forms, and templates.
- **Pico.css Dashboard (Task 1)**: The dashboard was redesigned using Pico.css v2 with a custom blue theme, instant HTMX partial swapping, and persistent project scoping.
- **Document Management (Task 2)**: Added multi-tier deduplication, real-time debounced search, multi-axis filtering (Name, Date, File Type, Status), chunk node inspection, and atomic PGVector synchronization on single/bulk document deletions.

---

## 2. Changes Made

### A. Task 1: Pico.css Dashboard & Navigation Layout
- **`static/css/pico.custom.css`**: Configured custom Pico.css build with primary blue palette (`#2563eb`), slate dark-mode tokens, compact tables, and status pills.
- **`static/js/theme_toggle.js`**: Created client-side theme switcher supporting light/dark modes with local storage persistence.
- **`templates/dashboard/base.html`**: Built main shell with sticky top-bar (Logo, Project dropdown, Theme toggle, User badge) and 5-section left sidebar targeting `#dashboard-workspace` via HTMX.
- **`templates/dashboard/workspace.html` & Partial Views**:
  - `parameters.html`: 1.1 Parameters editor (model, response mode, HyDE, active toggle).
  - `prompt.html`: 1.2 System Prompt & Persona editor with preset buttons.
  - `api_keys.html`: 1.3 Project-scoped API keys with generator modal and revocation.
  - `sources.html`: 2.1 Sources upload, deduplication, search/filters, and connector accordions.
  - `chat.html`: 3. Chat with LiteLLM SSE token streaming and source citations.
  - `evaluate.html`: 4. Evaluation suite with Synthetic QA generation and metric scorecards.
  - `monitor.html`: 5. Operations and telemetry placeholder card.
- **`src/apps/projects/views.py` & `src/apps/projects/urls.py`**: Added `dashboard_view`, `project_parameters_view`, `project_prompt_view`, `project_api_keys_view`, `project_sources_view`, `project_chat_view`, `project_evaluate_view`, and `project_monitor_view`.
- **`src/apps/my_rag_project/urls.py`**: Mounted `/rag/` and `/rag/dashboard/` to the Pico.css dashboard for authenticated users.

### B. Task 2: Advanced Document Management & Ingestion Pipeline
- **`src/apps/documents/services.py`**:
  - Implemented `compute_text_simhash(text)` for 64-bit fingerprinting with unigrams and bigrams.
  - Implemented `simhash_similarity(h1, h2)` for Hamming distance normalized similarity.
  - Implemented `check_near_duplicate(project, extracted_text, threshold=0.85)` to flag document revisions.
- **Interactive Modals**:
  - `templates/partials/document_duplicate_modal.html`: Exact binary duplicate resolution (Skip vs Force Replace).
  - `templates/partials/document_revision_modal.html`: Near-duplicate revision resolution (Replace Old Version vs Index as Separate Document vs Cancel).
  - `templates/dashboard/partials/inspect_document_modal.html`: Extracted chunk nodes, token counts, and SHA-256 inspection.
- **Search & Multi-Axis Filtering**:
  - `filter_sources_view`: Asynchronous HTMX filtering by debounced document name, date range (Today, 7 days, 30 days, All time), file type (.md, code, .pdf, .txt), and state (INDEXED, PENDING, FAILED).
- **Atomic Deletion & PGVector Purging**:
  - `delete_source_view` & `bulk_delete_sources_view`: Atomically drops Django document records, removes physical files, and purges all embedding chunks from PostgreSQL `rag_project_<store_id>` PGVector tables.

### C. User Testing Refinements & Dashboard Polish
- **Menu Numbering Removal**: Removed legacy section numbering across `templates/dashboard/base.html` and workspace tab headers (`parameters.html`, `prompt.html`, `api_keys.html`, `sources.html`, `chat.html`, `evaluate.html`, `monitor.html`).
- **Parameters Tab**:
  - Added direct link to `https://models.litellm.ai/` for supported LiteLLM model strings.
  - Bound "Disable Reasoning/Thinking Mode" dynamically via Alpine.js to only activate when a local Gemma model is selected.
- **API Keys Tab**:
  - Fixed toggle and revoke actions to return the Pico partial with proper CSRF headers.
  - Added one-time raw token generation banner with copy action, and sliced displayed keys to `{{ key.key|slice:":12" }}...`.
- **Chat Workflow**:
  - Resized input bar layout (`flex: 1 1 auto; width: 100%;` for input, compact button `flex-shrink: 0; width: auto;`).
  - Updated client-side stream parser in `chat.html` to handle both application/json payloads and SSE streaming responses, properly rendering bot response HTML, source cards, and response latency badges.
- **Sources & Ingestion Reliability**:
  - Fixed `upload_document` to render `dashboard/partials/sources.html` or `dashboard/partials/document_rows.html` instead of legacy unstyled Tailwind cards (`partials/document_items.html`).
  - Added global SVG constraints and Tailwind utility polyfills in `static/css/pico.custom.css` preventing SVGs from expanding to 100% viewport width.
  - Integrated duplicate and revision modals directly over the full Sources workspace, preventing screen blanking when clicking "Skip Upload".
  - Fixed safe document path lookup in `check_near_duplicate()` (resolving `AttributeError` on `file_path`) and corrected 2-element tuple return unpacking.
  - **Upload Progress Indication**: Added `hx-indicator="#upload-loading-banner"`, `hx-disabled-elt`, button state transitions (`⏳ Ingesting & Indexing...` with `aria-busy="true"`), and an animated progress banner during ingestion.

### D. Task 3: Secure Connectivity & Health Check API Endpoints
- **`src/apps/api/api_views.py`**:
  - **`GET /api/ping/` & `GET /rag/api/ping/`**: Ultra-low-latency in-memory response (`<1ms`) with zero database queries, preventing thread starvation.
  - **`GET /api/health/` & `GET /rag/api/health/`**: Verifies PostgreSQL database connectivity (`SELECT 1`), cached for 15 seconds to prevent connection pool exhaustion.
- **Abuse Prevention & Authentication**:
  - Multi-channel shared secret verification supporting `X-Health-Key` header, `Authorization: Bearer <key>`, URL query parameter `?key=`, or active API key, returning `403 Forbidden` on unauthorized requests.
- **`src/apps/my_rag_project/settings/base.py`**: Configured `HEALTH_CHECK_KEY` (defaults to `rag-health-secret-key` or environment override).
- **`src/apps/api/api_urls.py`**: Registered `ping/` and `health/` endpoints under `/api/` and `/rag/api/`.

### E. Task 4: API Documentation & AI Governance Sync
- **`Documentation/API/external_swagger.yaml` & `Documentation/API/swgger.yaml`**:
  - Documented `/ping/` and `/health/` endpoints under the `Health` tag.
  - Added `healthKeyAuth` security scheme and response schemas (`PingResponse`, `HealthResponse`, `ForbiddenErrorResponse`).
- **`project-context.md`**:
  - Added **API Documentation Governance** directive mandating that all API changes across `apps/api/`, `apps/chat/`, `apps/documents/`, and `apps/projects/` must be synchronized with `Documentation/API/` specs in the same task.

### F. Data Models & Migrations
- `src/apps/projects/migrations/0018_remove_project_chunking.py`: Dropped legacy `chunking` field from `Project`.
- `src/apps/documents/migrations/0008_alter_document_chunking_strategy.py`: Standardized `Document.chunking_strategy` choices.

### G. Task 5: Role-Based Separation of Django Admin & Pico.css Dashboard
- **Admin Access Enforcement (`is_staff` / `is_superuser`)**:
  - Directs admin users to the **Django admin UI** (`/rag/admin/`) upon login, visiting `/rag/`, or navigating to `/rag/dashboard/` (unless previewing via `?preview=1`).
  - Added an "⚙️ Admin UI" button to the Pico top navbar when an admin is previewing the client interface.
  - Page helpers (`admin_page`, `chat_page`, `evaluate_page`) in `apps/chat/pages.py` automatically route admins to Django admin workflows (`/rag/unfold/chat/`, `/rag/unfold/evaluate/`).
- **Regular User Access Enforcement (`not is_staff and not is_superuser`)**:
  - Directs regular authenticated users to the **Pico.css dashboard** (`/rag/dashboard/`) on login and when visiting `/rag/`.
  - Updated `CustomUnfoldAdminSite.has_permission()` and wrapped both `custom_admin_site.admin_view` and `standard_admin.site.admin_view` to automatically intercept and redirect regular users to `/rag/dashboard/` if they attempt to access `/rag/admin/` or `/rag/unfold/`.

### H. Task 6: Store IDs Availability on API Keys Interface
- **Pico.css Dashboard (`templates/dashboard/partials/api_keys.html`)**:
  - **Active Project Store ID Card**: Prominently displays the target `store_id` (`project.project_id`) with 1-click clipboard copy and an explanatory tooltip on how to pass it in `/rag/api/chat/` requests.
  - **Available Store IDs Section**: Added an interactive accordion card displaying all store IDs available to the specific user, including Project Name, Backend (`postgres`, `google`, `local`), Store ID (`project_id`), External Store ID (if applicable), and 1-click Copy buttons.
  - **Scoped Store ID Table Column**: Added a dedicated "Scoped Store ID" column with quick-copy icons directly in the API keys table.
  - **Key Generation Modal & Alert**: Display scoped Project and Store ID during key generation and in the post-creation confirmation banner.
- **Django Admin (`src/apps/api/admin.py`)**:
  - Added `store_id` display to `list_display`, `readonly_fields`, and `fieldsets` in `APIKeyAdmin`.

---

## 3. Verification & Test Results

- **Unit & Regression Test Suites**:
  - `Testing/unit/test_rag_auth_urls.py`: **13 passed** (Verifies admin login/redirects to `/rag/admin/`, dashboard redirection to `/rag/admin/`, preview param override, regular user login/redirects to `/rag/dashboard/`, and admin route blocking for non-staff).
  - `Testing/unit/api/test_ping_health.py`: **8 passed** (Missing key 403, Invalid key 403, Header key 200, Query param 200, Bearer token 200, /rag/ prefix 200, Active API key 200, Cached DB health 200).
  - `Testing/unit/documents/test_sources_management.py`: **5 passed** (SimHash similarity, Multi-axis filtering, Atomic single & bulk delete, Chunk inspector, Upload duplicate detection).
  - `Testing/unit/projects/test_dashboard_views.py`: **4 passed** (Dashboard routing, Parameters, Prompt, API Keys + Store IDs availability).
  - **Full Suite Across Apps**: `DJANGO_ENV=testing pytest Testing/unit/test_rag_auth_urls.py Testing/unit/projects Testing/unit/documents Testing/unit/chat Testing/unit/api -v`: **430 passed**, 0 failed (100% pass rate).



