# Spec: Sprint Aug 6 - Dashboard Redesign with Pico.css & Document Management Solution

**Sprint:** August 2026 (Aug 6)  
**Document Path:** `Design/Aug-26/Aug6/aug6-specs.md`  
**Status:** Aligned & Final Approved Specification (Post-Interview Alignment)  
**Design System:** Pico.css (Semantic HTML, Ultra-Lightweight, Zero-Build, Primary Color: Blue `#2563eb`)

---

## 1. Objective & Design Philosophy

Deliver a unified, high-performance, lightweight, and cohesive web dashboard experience for managing, indexing, querying, and evaluating RAG projects by executing two core initiatives:
1. **Task 1: Dashboard Redesign with Pico.css**:
   - Establish a **project-centric navigation model** where the user selects an active project from a sticky top bar, automatically scoping all left-sidebar tabs to that project.
   - Serve `/rag/` and `/rag/dashboard/` directly with the new Pico.css dashboard for all authenticated users, keeping `/rag/admin/` for the Django Unfold backend.
   - Replace complex styling with **Pico.css** using a modern primary blue accent (`#2563eb`) and native dark/light mode switching.
   - Structure the left navigation menu into 5 numbered categories: **1. Configuration** (1.1 Parameters, 1.2 Prompt, 1.3 API Keys), **2. Index** (2.1 Sources), **3. Chat**, **4. Evaluate**, and **5. Monitor** (Placeholder).
2. **Task 2: Advanced Document Management Solution (Under Sources)**:
   - Implement a **multi-tier deduplication pipeline** (Tier 1: SHA-256 binary hash, Tier 2: SimHash text near-duplicate detection, Tier 3: PGVector embedding indexing) ensuring no identical or conflicting draft documents contaminate the vector index.
   - Provide real-time **search and multi-axis filtering** (by document name, upload/indexed date range, file extension, and ingestion status).
   - Implement **granular and batch document actions** (inspect chunk nodes, single delete with atomic PGVector cleanup, multi-select bulk delete, and re-indexing parser overrides).

---

## 2. Tech Stack

- **Backend Framework**: Django 6.0 (Python 3.14)
- **CSS / UI System**: Pico.css v2 (Semantic HTML, CSS Variables, Theme switching)
- **Frontend Interactivity**: HTMX (Server-driven partial swapping) + Alpine.js (Micro-interactions & modal state)
- **RAG & Vector Storage**: LlamaIndex + PostgreSQL (`pgvector` / `PGVectorStore`) + Google File Search
- **LLM Gateway**: LiteLLM Router (`gemini/gemini-2.5-flash-lite`, Claude, GPT, Ollama)
- **Testing**: `pytest`, `pytest-django`, `pytest-asyncio`

---

## 3. Commands

```bash
# Environment Activation
source .venv/bin/activate

# Development Server
python manage.py runserver

# Database Migrations
DJANGO_ENV=development python manage.py makemigrations
DJANGO_ENV=development python manage.py migrate

# Unit Testing
DJANGO_ENV=testing pytest Testing/unit -v
DJANGO_ENV=testing pytest Testing/unit/projects -v
DJANGO_ENV=testing pytest Testing/unit/documents -v

# Regression Testing
DJANGO_ENV=testing pytest Testing/regression -v
```

---

## 4. Project Structure

```
my_rag/
├── src/
│   ├── apps/
│   │   ├── projects/         → Project model, project settings, API key management
│   │   ├── documents/        → Document model, ingestion pipeline, deduplication, sources views
│   │   ├── chat/             → Chat interface, LiteLLM router, SSE streaming
│   │   ├── evaluate/         → Evaluation runs, synthetic QA generator, scorecards
│   │   ├── api/              → DRF API endpoints and serializers
│   │   └── my_rag_project/   → Django settings, URLs, admin configuration
├── templates/
│   ├── dashboard/            → Pico.css base dashboard layout & workspace
│   │   ├── base.html         → Main dashboard shell (Top Nav + Sidebar + Workspace target)
│   │   └── partials/         → HTMX section views (parameters, prompt, api_keys, sources, chat, evaluate, monitor)
│   └── partials/             → Shared components (document_duplicate_modal, chunk_inspector, etc.)
├── static/
│   ├── css/
│   │   └── pico.custom.css   → Custom Pico.css build with primary blue tokens & dark mode overrides
│   └── js/
├── Testing/
│   ├── unit/                 → Pytest unit tests for all apps
│   └── regression/           → Bug regression test suites
└── Design/Aug-26/Aug6/       → Aug 6 sprint specs, plan, todo, and changelog
```

---

## 5. Code Style & Conventions

```python
# Code Style: Use f-strings, double quotes, type annotations, and docstrings
from django.http import HttpRequest, HttpResponse
from src.apps.projects.models import Project

def get_project_sources_context(request: HttpRequest, project_id: str) -> dict:
    """
    Retrieve project sources along with metadata and deduplication statistics.
    """
    project = Project.objects.filter(project_id=project_id).first()
    if not project:
        raise ValueError(f"Project '{project_id}' was not found.")
    
    return {
        "project": project,
        "documents": project.documents.all().order_by("-created_at"),
    }
```

* **Naming Conventions**: `snake_case` for Python functions/variables, `PascalCase` for classes/models, `kebab-case` for URLs and HTML IDs.
* **String Formatting**: Double quotes (`"..."`), f-strings for string interpolation.
* **Architecture**: Keep business logic in `services.py` or model methods; keep views focused on request routing and template partial rendering.

---

## 6. Testing Strategy

* **Framework**: `pytest` with `pytest-django`.
* **Test Database**: In-memory SQLite for unit tests with `DJANGO_ENV=testing`.
* **Coverage Requirements**:
  * Unit test coverage for all new view endpoints (`Testing/unit/documents/`, `Testing/unit/projects/`).
  * Deduplication verification tests (SHA-256 hash match, force-replace, SimHash revision flagging).
  * Filter tests (name search, date range filtering, file type filtering, status filtering).
  * Atomic deletion synchronization tests ensuring PGVector table records are dropped when a document is deleted.
  * Regression test suite verification (`Testing/regression/`).

---

## 7. Boundaries

### Always:
- Use `Project.project_id` (stable slug/hash) for all URL routes, frontend IDs, and API lookups.
- Scope document, chat, prompt, and API key queries to the authenticated user and active `project_id`.
- Synchronize PostgreSQL PGVector table records when documents are deleted or force-replaced (Hard deletion).
- Run tests with `DJANGO_ENV=testing pytest Testing/unit -v` before finalizing tasks.

### Ask First:
- Modifying core database schema fields on `Project` or `Document`.
- Introducing new external JavaScript frameworks or heavy CSS dependencies.
- Changing permissions or multi-tenant user ownership rules.

### Never:
- Run modifying git commands (e.g. `git push`, `git commit`, `git reset`, `git checkout`).
- Leave orphaned vector embedding rows in PostgreSQL when deleting documents.
- Use raw primary keys (`id`) in URL paths when `project_id` is available.

---

## 8. Detailed Functional Specifications

### 8.1 Task 1: Dashboard Navigation & Pico.css Theme

```
┌────────────────────────────────────────────────────────────────────────────────────────────────┐
│  TOP BAR:  [Logo: My RAG]  │  ⚡ Project Selector: [ Project Dropdown ▼ ]  │  [🌙 Theme] [User] │
├────────────────────────────┬───────────────────────────────────────────────────────────────────┤
│  LEFT MAIN MENU            │  MAIN WORKSPACE CONTENT (#dashboard-workspace)                   │
│                            │                                                                   │
│  📁 1. Configuration       │  ┌─────────────────────────────────────────────────────────────┐  │
│    ├─ 1.1 Parameters       │  │ Active Section Header                                       │  │
│    ├─ 1.2 Prompt           │  ├─────────────────────────────────────────────────────────────┤  │
│    └─ 1.3 API Keys         │  │                                                             │  │
│                            │  │  [Dynamic Section Content loaded via HTMX / Django View]    │  │
│  📑 2. Index               │  │                                                             │  │
│    └─ 2.1 Sources          │  │                                                             │  │
│                            │  │                                                             │  │
│  💬 3. Chat                │  │                                                             │  │
│                            │  │                                                             │  │
│  📊 4. Evaluate            │  └─────────────────────────────────────────────────────────────┘  │
│                            │                                                                   │
│  📈 5. Monitor             │                                                                   │
│    (Placeholder)           │                                                                   │
└────────────────────────────┴───────────────────────────────────────────────────────────────────┘
```

#### Menu Hierarchy:
1. **1. Configuration**
   - **1.1 Parameters** (`/rag/projects/<project_id>/parameters/`): `display_name`, `storage_type`, `llm_model`, `embedding_model`, `response_mode`, `use_hyde`, `synthesizer`, `document_parsing`, `disable_thinking`, `is_active`.
   - **1.2 Prompt** (`/rag/projects/<project_id>/prompt/`): Monospace system prompt textarea, `custom_prompt` toggle, preset prompt templates.
   - **1.3 API Keys** (`/rag/projects/<project_id>/api-keys/`): Key generation, active/revoked listing, copy-to-clipboard, delete key.
2. **2. Index**
   - **2.1 Sources** (`/rag/projects/<project_id>/sources/`): Document ingestion, multi-tier deduplication, search/filter, chunk inspection, third-party connectors (Obsidian, Google Calendar).
3. **3. Chat** (`/rag/projects/<project_id>/chat/`): Multi-model chat workspace with LiteLLM SSE token streaming, source citations, and thumbs-up/down feedback.
4. **4. Evaluate** (`/rag/projects/<project_id>/evaluate/`): Synthetic QA pair generator, automated evaluation runs, scorecards, manual evaluation judge mode, and local LLM benchmarks.
5. **5. Monitor** (`/rag/projects/<project_id>/monitor/`): Clean placeholder card for telemetry, token usage, and latency monitoring.

---

### 8.2 Task 2: Advanced Document Management & Ingestion Pipeline

#### Multi-Tier Deduplication Pipeline:
1. **Tier 1 (Exact Binary Match via SHA-256)**:
   - Computes SHA-256 hash on upload.
   - If `Document.objects.filter(project=project, content_hash=hash)` exists:
     - Triggers `document_duplicate_modal.html`.
     - **Skip**: Aborts upload, saving storage and API embedding quotas.
     - **Force Re-upload / Replace**: Atomically drops old PGVector embeddings and updates the document record.
2. **Tier 2 (Near-Duplicate Text Detection via SimHash / MinHash)**:
   - Computes 64-bit SimHash on extracted document text shingles.
   - If similarity $\ge 85\%$ against an existing document:
     - Prompts user with **"Revision Detected"** modal with similarity score ($92\%$).
     - Choices: **Replace Old Version** (deactivates old PGVector chunks), **Index as Separate Document**, or **Cancel**.
3. **Tier 3 (Vector Embedding & Storage)**:
   - Executes selected document-level node parser (`auto_detect`, `markdown`, `code`, `hierarchical`, `sentence`).
   - Computes embeddings via `models/gemini-embedding-001` (3072 dims) and persists to PostgreSQL `PGVectorStore`.

#### Search & Multi-Axis Filtering Controls (`/rag/projects/<project_id>/sources/filter/`):
- **Search by Name**: Debounced real-time input matching `document_name` and `display_name`.
- **Date Range Filter**: Dropdown presets (*All Time*, *Today*, *Last 7 Days*, *Last 30 Days*, *Custom Date Range*).
- **File Type Filter**: Multi-choice filter for `.md`, `.py`/`.js`/`.ts`/`.html`, `.pdf`, and `.txt`.
- **Ingestion Status**: Filter pills for `INDEXED`, `PENDING`, and `FAILED`.
- **Sorting**: Sortable columns by Name, Size, Date Uploaded, and Ingestion State.

#### Document Actions:
- **Inspect Chunks (`[👁]`)**: Modal displaying extracted text nodes, chunk line counts, token estimates, and PGVector metadata.
- **Delete Document (`[🗑]`)**: Hard deletion atomically removing Django DB record and all corresponding PGVector rows from PostgreSQL.
- **Batch Delete (`[ 🗑 Delete Selected ]`)**: Multi-select row checkboxes with bulk atomic deletion.
- **Re-Index / Parser Override (`[🔄]`)**: Re-parses an existing document with a chosen chunking parser without re-uploading the file.
- **Download Source**: Direct link to download the original raw file.

---

## 9. Success Criteria

- [ ] Top navigation bar renders active project selector; switching projects dynamically scopes all left-menu tabs.
- [ ] Pico.css styling applied with primary blue (`#2563eb`) palette and functional Dark/Light theme toggle.
- [ ] Left sidebar strictly renders the 5 numbered categories and sub-items.
- [ ] Multi-tier deduplication successfully catches exact SHA-256 duplicates and near-duplicate revisions ($\ge 85\%$).
- [ ] Real-time search and multi-axis filters (Name, Date, Type, Status) function asynchronously via HTMX.
- [ ] Single and batch document deletions atomically purge associated PGVector embeddings from PostgreSQL.
- [ ] 100% test pass rate across `Testing/unit` and `Testing/regression`.
