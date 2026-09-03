# Task Checklist: Sprint Aug 6 - Dashboard Redesign & Document Management Solution

**Sprint:** August 2026 (Aug 6)  
**Spec Document:** `Design/Aug-26/Aug6/aug6-specs.md`  
**Plan Document:** `Design/Aug-26/Aug6/plan.md`  
**Todo Path:** `Design/Aug-26/Aug6/todo.md`  

---

## Phase 1: Pico.css Layout Foundation & Navigation Routing

- [x] **Task 1.1: Pico.css Setup & Custom Blue Palette Theme Tokens**
  - **Description:** Install Pico.css v2 stylesheet and configure custom blue theme tokens (`--pico-primary: #2563eb`, `--pico-primary-hover: #1d4ed8`) and slate dark-mode variables in `static/css/pico.custom.css`.
  - **Acceptance:** Pico.css loads cleanly; dark/light theme switcher toggles `data-theme="dark"` / `data-theme="light"` on `<html>` with smooth transition.
  - **Verify:** Open dashboard in browser, verify primary blue button styles and dark mode toggle.
  - **Files:** `static/css/pico.custom.css`, `static/js/theme_toggle.js`

- [x] **Task 1.2: Dashboard Shell Template (Top Bar + 5-Section Sidebar)**
  - **Description:** Build `templates/dashboard/base.html` containing the persistent Top Bar (Brand logo, Project Selector dropdown, theme toggle, user info) and Left Navigation Sidebar (5 numbered sections: Configuration, Index, Chat, Evaluate, Monitor) targeting `#dashboard-workspace` via HTMX.
  - **Acceptance:** Top bar renders active project; sidebar links trigger partial HTMX swaps into `#dashboard-workspace` without full-page reloads.
  - **Verify:** Load `/rag/dashboard/`, confirm sidebar click changes active link styling and swaps content.
  - **Files:** `templates/dashboard/base.html`, `templates/dashboard/workspace.html`

- [x] **Task 1.3: Core Dashboard Views & Multi-Project Routing**
  - **Description:** Implement `DashboardView` in `src/apps/projects/views.py` and mount routes `/rag/` and `/rag/dashboard/` to resolve the active project (from query param `?project_id=`, session, or most recent project) and render the dashboard shell.
  - **Acceptance:** Navigating to `/rag/dashboard/` auto-selects user's active project; switching dropdown updates workspace and session.
  - **Verify:** `DJANGO_ENV=testing pytest Testing/unit/projects/test_views.py -v`
  - **Files:** `src/apps/projects/views.py`, `src/apps/projects/urls.py`, `src/apps/my_rag_project/urls.py`

### Checkpoint 1: Foundation
- [x] Dashboard shell renders with Pico.css blue styling.
- [x] Project dropdown lists all owned projects; switching preserves context.

---

## Phase 2: Configuration Workspace Tabs (1.1, 1.2, 1.3)

- [x] **Task 2.1: 1.1 Parameters Workspace View & Partial**
  - **Description:** Create `templates/dashboard/partials/parameters.html` and `ProjectParametersView` allowing users to view and update project display name, LiteLLM model identifier, response mode, use_hyde, synthesizer, document parsing, disable_thinking, and active status.
  - **Acceptance:** Parameters load for selected project; POST updates model and returns inline success alert.
  - **Verify:** `DJANGO_ENV=testing pytest Testing/unit/projects/test_parameters_view.py -v`
  - **Files:** `src/apps/projects/views.py`, `templates/dashboard/partials/parameters.html`

- [x] **Task 2.2: 1.2 Prompt Workspace View & Partial**
  - **Description:** Create `templates/dashboard/partials/prompt.html` and `ProjectPromptView` for editing system instructions with monospace textarea, character counter, custom prompt toggle, and preset templates.
  - **Acceptance:** SystemPrompt saves via HTMX without full-page reload; presets populate prompt textarea instantly.
  - **Verify:** `DJANGO_ENV=testing pytest Testing/unit/projects/test_prompt_view.py -v`
  - **Files:** `src/apps/projects/views.py`, `templates/dashboard/partials/prompt.html`

- [x] **Task 2.3: 1.3 API Keys Workspace View & Partial**
  - **Description:** Create `templates/dashboard/partials/api_keys.html` and `ProjectApiKeysView` for generating, listing, copying, and revoking project-scoped API keys.
  - **Acceptance:** Generating a key shows one-time secret key modal with copy button; revoking/deleting key updates table via HTMX.
  - **Verify:** `DJANGO_ENV=testing pytest Testing/unit/api/test_project_scoped_apikey.py -v`
  - **Files:** `src/apps/projects/views.py`, `templates/dashboard/partials/api_keys.html`

### Checkpoint 2: Configuration Suite
- [x] Parameters, Prompt, and API Key tabs fully operational with Pico.css styling.

---

## Phase 3: Sources & Advanced Document Management (2.1 Sources)

- [x] **Task 3.1: Multi-Tier Deduplication Pipeline (SHA-256 & SimHash)**
  - **Description:** Implement Tier 1 SHA-256 exact binary matching and Tier 2 SimHash text near-duplicate checker in `src/apps/documents/services.py`.
  - **Acceptance:** Exact duplicates trigger SHA-256 match; near-duplicates ($\ge 85\%$ textual similarity) are flagged for revision handling.
  - **Verify:** `DJANGO_ENV=testing pytest Testing/unit/documents/test_deduplication.py -v`
  - **Files:** `src/apps/documents/services.py`, `src/apps/documents/views.py`

- [x] **Task 3.2: Interactive Duplicate & Revision Modals**
  - **Description:** Build `templates/partials/document_duplicate_modal.html` and `templates/partials/document_revision_modal.html` providing Skip, Force Replace, and Stack Revision workflows.
  - **Acceptance:** Duplicate modal allows skipping or atomic force-replace; revision modal allows version stacking.
  - **Verify:** Test uploading exact duplicate file and slightly modified revision in upload form.
  - **Files:** `templates/partials/document_duplicate_modal.html`, `templates/partials/document_revision_modal.html`, `src/apps/documents/views.py`

- [x] **Task 3.3: Sources View with Search & Multi-Axis Filtering**
  - **Description:** Implement `ProjectSourcesView` and `/rag/projects/<project_id>/sources/filter/` with debounced text search (Name/Display Name), Date Range dropdown (Today, 7 days, 30 days, Custom), File Type filter (.md, code, .pdf, .txt), and Status filter.
  - **Acceptance:** Filter inputs asynchronously update document table rows without page reload.
  - **Verify:** `DJANGO_ENV=testing pytest Testing/unit/documents/test_source_filters.py -v`
  - **Files:** `src/apps/documents/views.py`, `src/apps/documents/urls.py`, `templates/dashboard/partials/sources.html`

- [x] **Task 3.4: Granular & Batch Document Actions with PGVector Sync**
  - **Description:** Implement Inspect Chunks modal (`[👁]`), single atomic delete with PostgreSQL PGVector vector purging (`[🗑]`), multi-select bulk delete, and re-indexing parser override (`[🔄]`).
  - **Acceptance:** Deleting a document drops Django record and purges all matching rows from `rag_project_<store_id>` PGVector table; inspect modal displays parsed node snippets and token counts.
  - **Verify:** `DJANGO_ENV=testing pytest Testing/unit/documents/test_document_deletion.py -v`
  - **Files:** `src/apps/documents/views.py`, `src/apps/documents/services.py`, `templates/dashboard/partials/inspect_document_modal.html`

- [x] **Task 3.5: Third-Party Connectors Accordion (Obsidian & Google Calendar)**
  - **Description:** Integrate Obsidian Vault sync and Google Calendar sync controls as collapsible accordion cards under the Sources view.
  - **Acceptance:** Sync buttons trigger indexing; sync progress and status badges update dynamically.
  - **Verify:** `DJANGO_ENV=testing pytest Testing/unit/documents/test_obsidian_views.py -v`
  - **Files:** `templates/dashboard/partials/sources.html`, `src/apps/documents/views.py`

### Checkpoint 3: Sources & Document Management
- [x] Multi-tier deduplication blocks duplicates and handles revisions.
- [x] Search, filtering, chunk inspection, and atomic single/bulk deletion fully functional.

---

## Phase 4: Native Chat, Evaluate & Monitor Workspace (3, 4, 5)

- [x] **Task 4.1: 3. Chat Workspace Integration**
  - **Description:** Integrate the LiteLLM SSE token streaming chat interface into `templates/dashboard/partials/chat.html` with auto-resizing query bar, model indicator badge, source citations accordion, and thumbs-up/down feedback.
  - **Acceptance:** Queries stream token-by-token; source citations expand with document passsages; feedback persists to database.
  - **Verify:** `DJANGO_ENV=testing pytest Testing/unit/chat/test_chat_views.py -v`
  - **Files:** `templates/dashboard/partials/chat.html`, `src/apps/chat/views.py`

- [x] **Task 4.2: 4. Evaluate Workspace Integration**
  - **Description:** Integrate Synthetic QA generation, Evaluation run dashboard, Scorecards, Manual evaluation judge mode, and Local LLM benchmark runner into `templates/dashboard/partials/evaluate.html`.
  - **Acceptance:** Evaluation runs display metric scorecards (Precision, Recall, Faithfulness); QA generator builds golden pairs from PGVector chunks.
  - **Verify:** `DJANGO_ENV=testing pytest Testing/unit/evaluate/test_synthetic_qa_eval.py -v`
  - **Files:** `templates/dashboard/partials/evaluate.html`, `src/apps/evaluate/views.py`

- [x] **Task 4.3: 5. Monitor Placeholder & Theme Polish**
  - **Description:** Create `templates/dashboard/partials/monitor.html` with a clean Pico.css telemetry card and perform full responsive layout polish.
  - **Acceptance:** Monitor tab loads cleanly; mobile and desktop layouts render without visual bugs in both dark and light modes.
  - **Verify:** Manual check on desktop and mobile viewports; verify contrast ratios.
  - **Files:** `templates/dashboard/partials/monitor.html`, `static/css/pico.custom.css`

---

## Phase 5: Verification & Full Regression Testing

- [x] **Task 5.1: Unit & Regression Test Verification**
  - **Description:** Execute full test suites and ensure 0 failures.
  - **Acceptance:** 100% pass rate across `Testing/unit/` and `Testing/regression/`.
  - **Verify:** `DJANGO_ENV=testing pytest Testing/unit -v && DJANGO_ENV=testing pytest Testing/regression -v`
  - **Files:** `Testing/unit/`, `Testing/regression/`

- [x] **Task 5.2: Documentation & Changelog Update**
  - **Description:** Update `Design/Aug-26/Aug6/aug6-changelog.md` and user documentation.
  - **Acceptance:** Changelog accurately describes Task 1 & Task 2 implementations.
  - **Files:** `Design/Aug-26/Aug6/aug6-changelog.md`

### Checkpoint 5: Complete & Ready for Review
- [x] All acceptance criteria met across all 5 phases.
