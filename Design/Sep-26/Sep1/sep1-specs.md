# Spec: Native In-Process Website Scraping & Incremental Indexing Engine (Sep 1)

---

## 1. Objective

### Problem Statement & Background Context
The platform currently supports indexing local files, Obsidian vaults ([ObsidianSource](file:///Users/chrys/Projects/my_rag/src/apps/documents/models.py#L141-L182)), and Google Calendar events ([GoogleCalendarSource](file:///Users/chrys/Projects/my_rag/src/apps/documents/models.py#L238-L306)) into PostgreSQL PGVector and Google File Search. Users frequently need to ground AI assistants against live documentation portals, company websites, and blogs.

This specification establishes **Option 1: Native In-Process Sitemap & HTTP Spider Web Scraping with Incremental Re-Indexing**. It enables users to create a project by entering a root URL, automatically crawls and indexes pages in a background thread, provides live HTMX progress tracking, and allows users to incrementally discover and index new or updated pages on demand.

### Target Users & Use Cases
- **Knowledge Worker / Researcher:** Wants to ground an AI assistant on an external documentation portal or public wiki by entering a single URL.
- **Project Administrator:** Periodically checks a company documentation site or blog to ingest newly published articles with a single click.

### High-Level Goals
1. **Dedicated "Website Project" UI Preset:** Streamlined project creation wizard where the user inputs a website URL, with the system provisioning a project and attaching a `WebSource` under the hood.
2. **Sitemap-First Discovery with Spider Fallback:** Automatically discover site pages via `sitemap.xml` (or `robots.txt` discovery), falling back to a bounded, recursive HTML link spider (BFS).
3. **Optimized Lightweight Content Extraction:** Strip boilerplate (navbars, menus, cookie banners, footers, ads) using base `trafilatura` (minimal dependency footprint, no `trafilatura[all]`), falling back to `markitdown`/`BeautifulSoup` if necessary.
4. **Auto-Crawl & Live HTMX Polling:** Asynchronous background thread execution with live HTMX polling so the web worker is never blocked.
5. **Automated Delta Sync & Vector Hygiene:** On-demand check for updates that indexes newly created pages, re-embeds modified pages (purging stale vectors), and purges embeddings for remote 404/deleted pages.
6. **Zero External Daemon Overhead:** Runs completely within the existing Django application environment without requiring Celery, Redis, or headless browser binaries.

### Out of Scope (Non-Goals)
- Scraping JavaScript-heavy Single Page Applications (SPAs) that require full client-side DOM execution (Option 2).
- Bypassing CAPTCHAs, Cloudflare Turnstile, or authenticated paywalls/logins.
- Unbounded open-web crawling across third-party domains.
- Automated cron/celery daemon scheduling (on-demand user trigger for MVP).

---

## 2. Tech Stack

- **Backend Framework:** Django 5 / 6 + Django REST Framework
- **Runtime & Language:** Python 3.10+ (macOS / Linux)
- **Vector Indexing & Retrieval:** LlamaIndex Core (`VectorStoreIndex`, `Settings`), `PGVectorStore` (PostgreSQL), `GeminiEmbedding` (`gemini-embedding-001`)
- **HTTP Client & Spider:** `httpx` (async/sync HTTP client), `BeautifulSoup4` (link extraction and DOM fallback)
- **Content Cleaning & Markdown:** `trafilatura` (standard base package, no extras), Microsoft `markitdown`
- **Frontend / Interactivity:** HTMX (dynamic polling & out-of-band swaps), Bootstrap 5, Vanilla CSS

---

## 3. Commands

```bash
# Environment setup
source .venv/bin/activate
pip install trafilatura beautifulsoup4

# Local server execution
python manage.py runserver

# Unit test execution
DJANGO_ENV=testing .venv/bin/pytest Testing/unit/documents/test_web_scraper.py -v
DJANGO_ENV=testing .venv/bin/pytest Testing/unit/documents -v

# Regression test execution
DJANGO_ENV=testing .venv/bin/pytest Testing/regression -v

# Run all test suites
DJANGO_ENV=testing .venv/bin/pytest Testing/unit -v

# Production deployment
./deploy.sh
```

---

## 4. Project Structure

```
my_rag/
├── src/
│   └── apps/
│       ├── projects/
│       │   ├── models.py                  → Project model (display_name, storage_type, project_id)
│       │   ├── views.py                   → Project creation wizard with Website Preset
│       │   └── urls.py                    → Project routes
│       ├── documents/
│       │   ├── models.py                  → WebSource, WebPage data models
│       │   ├── web_crawler_services.py    → Discovery (Sitemap/BFS), Trafilatura cleaning, delta checks
│       │   ├── services.py                → LlamaIndexIngestionPipeline, get_vector_store
│       │   ├── views.py                   → HTMX endpoints: web_sync, web_index_new, web_status, web_reindex
│       │   └── urls.py                    → Web source routing
│       └── chat/
│           ├── views.py                   → Grounded chat execution over vector store
│           └── llm_router.py              → LiteLLM unified routing
├── templates/
│   └── partials/
│       ├── web_source_section.html        → Dedicated HTMX web source dashboard & KPI cards
│       ├── web_status_partial.html        → Real-time polling progress bar partial
│       └── project_create_modal.html      → Project creation modal with Website Preset tab
├── Testing/
│   └── unit/
│       └── documents/
│           ├── test_web_crawler.py        → Unit tests for sitemap parser, spider, Trafilatura extractor
│           └── test_web_views.py          → Unit tests for HTMX web endpoints and permissions
└── Design/
    └── Sep-26/
        └── Sep1/
            └── sep1-specs.md              → This specification document
```

---

## 5. Code Style & Conventions

- **Formatting:** PEP 8 compliance, 4-space indentation.
- **Strings:** Use double quotes (`"..."`) instead of single quotes (`'...'`).
- **String Interpolation:** Always use f-strings (`f"..."`) instead of `%` or `.format()`.
- **Type Hints:** Type hints and docstrings are required for all non-trivial Python classes and functions.
- **Frontend Interactivity:** Strictly use HTMX (`hx-get`, `hx-post`, `hx-trigger`, `hx-swap`) for dynamic updates rather than introducing custom JavaScript frameworks.
- **URL Routing:** Never hardcode URLs; always use `reverse()` in Python and `{% url '...' %}` in Django templates.

### Reference Code Snippet

```python
"""
Web crawler service for sitemap-first discovery, HTML sanitization, and delta sync.
"""

import logging
from typing import Any, Dict, List, Optional
import httpx
import trafilatura

logger = logging.getLogger(__name__)


def extract_clean_markdown(html_content: str) -> Optional[str]:
    """
    Extract semantic Markdown from raw HTML using base Trafilatura.
    Falls back to empty string if content cannot be extracted.
    """
    if not html_content or len(html_content.strip()) < 50:
        return None

    extracted: Optional[str] = trafilatura.extract(
        html_content,
        output_format="markdown",
        include_links=True,
        include_tables=True,
        favor_recall=True,
    )
    return extracted.strip() if extracted else None
```

---

## 6. Testing Strategy

- **Test Framework:** `pytest` using `pytest-django` and `pytest-mock`.
- **Test Directory:** Tests strictly belong under `Testing/unit/documents/` (never `Tests/`).
- **Hermeticity & Isolation:**
  - Automated tests must **never** make live outbound HTTP network calls.
  - All outbound requests to `sitemap.xml`, `robots.txt`, and web pages must be mocked using `pytest-mock` or `httpx.MockTransport`.
  - Use in-memory SQLite database (`DJANGO_ENV=testing`) for testing database operations.
- **Test Coverage Requirements:**
  1. **URL Sanitization & Bounding:** Tests verifying subpath locking and domain boundary enforcement.
  2. **Sitemap Discovery:** Tests parsing standard XML urlsets, sitemap index files, and missing sitemaps.
  3. **Spider BFS Traversal:** Tests link queueing, depth limits, and cycle detection.
  4. **Content Extraction:** Tests verifying boilerplate stripping (nav/footer/cookie banners) via Trafilatura.
  5. **Delta Sync & Hash Comparison:** Tests confirming `PENDING` states for new URLs and `MODIFIED` for hash changes.
  6. **Vector Purge on 404:** Tests ensuring deleted pages trigger vector deletions.
  7. **HTMX Views & Status Polling:** Tests for view status codes, permissions, and partial rendering.

---

## 7. Boundaries

| Category | Rules & Invariants |
| :--- | :--- |
| **ALWAYS DO** | - Run `DJANGO_ENV=testing .venv/bin/pytest Testing/unit/documents -v` before finalizing tasks.<br>- Follow PEP 8, double quotes, type annotations, and docstrings.<br>- Use `Project.project_id` as the stable lookup key across URLs, views, and vector tables.<br>- Enforce user project ownership and permission checks on all web endpoints.<br>- Respect `robots.txt` Disallow directives and domain boundaries.<br>- Strip tracking query parameters (`utm_*`, `fbclid`) and URL fragments. |
| **ASK FIRST** | - Adding new heavyweight dependencies (e.g., `trafilatura[all]`, Playwright, Celery, Redis).<br>- Modifying existing core columns on the `Project` or `Document` models.<br>- Altering global authentication or authorization middleware.<br>- Changing default crawl limits beyond 100 pages. |
| **NEVER DO** | - Run modifying git commands (`git add`, `git commit`, `git push`, `git checkout`, `git reset`).<br>- Make unmocked outbound HTTP calls during automated pytest test runs.<br>- Block Django WSGI request threads with synchronous long-running web crawls (always use background threading).<br>- Hardcode URLs in views, services, or templates. |

---

## 8. Resolved Design Decisions (Grill-Me Alignment)

| Decision Area | Selected Strategy | Rationale & Tradeoffs |
| :--- | :--- | :--- |
| **Model Architecture** | **Hybrid Architecture** | Source Connector (`WebSource` 1-to-1 with `Project`) under the hood preserves existing `postgres` / `google` vector retrieval, chat routing, and evaluation logic without code duplication; a dedicated "Website Project" preset in the creation UI gives the user a streamlined mental model. |
| **Execution Model** | **Asynchronous Background Thread + Live HTMX Polling** | Long crawls (up to 100 pages) run in `threading.Thread`, avoiding Gunicorn HTTP request timeouts. The dashboard uses `hx-trigger="every 2s"` to poll status and render a live progress bar. |
| **Incremental Updates Policy** | **Auto-Handle New & Modified Pages** | Ingests new URLs, and detects modified pages via SHA-256 hash or sitemap `<lastmod>`, automatically purging old vector chunks before re-embedding to prevent hallucinated duplicate citations. |
| **Remote 404 / Deletion Policy** | **Automatic Vector Purge** | If a previously indexed page returns `404 Not Found`, `410 Gone`, or vanishes from the site graph during a sync, its vector embeddings are purged from the index and the record is marked `DELETED`. |
| **Crawl Boundary Rules** | **Subpath-Bounded with Entire Domain Toggle** | Defaults to crawling strictly under the provided subpath (e.g. `https://example.com/docs/*`), with an optional *"Crawl entire domain"* checkbox for full-site coverage. |
| **Extraction Engine & Dependencies** | **Base `trafilatura` with `markitdown` Fallback** | Use standard `trafilatura` (without `trafilatura[all]` extras like Spacy/PycURL) to keep the install footprint tiny, falling back to `markitdown`/`BeautifulSoup` if Trafilatura yields empty text. |
| **Trigger Mechanism** | **On-Demand Only (MVP)** | Users click *"Check for Updates"* and *"Index New Pages"* directly in the dashboard UI. No periodic cron daemon is required. |
| **Crawl Limits & Quotas** | **100 Pages Default (Max 500 Ceiling)** | Balances fast initial indexing (~25–45s) with low server load on 1 vCPU droplets. Max depth: 4. Politeness delay: 250ms. |

---

## 9. Data Model Specifications

Located in [`src/apps/documents/models.py`](file:///Users/chrys/Projects/my_rag/src/apps/documents/models.py):

### 9.1. `WebSource` Model
One-to-one relationship with `Project`.

```python
class WebSource(models.Model):
    SYNC_STATUS_CHOICES = [
        ("IDLE", "Idle"),
        ("DISCOVERING", "Discovering Pages"),
        ("INDEXING", "Indexing Vectors"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]

    project = models.OneToOneField(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="web_source",
        help_text="The project this website source belongs to",
    )
    root_url = models.URLField(
        max_length=1024,
        help_text="Entrypoint website URL",
    )
    allowed_domain = models.CharField(
        max_length=255,
        help_text="Allowed domain/host (e.g. docs.example.com)",
    )
    subpath_only = models.BooleanField(
        default=True,
        help_text="Whether crawling is strictly constrained to the root URL subpath",
    )
    max_depth = models.PositiveIntegerField(
        default=4,
        help_text="Maximum link recursion depth",
    )
    max_pages = models.PositiveIntegerField(
        default=100,
        help_text="Maximum total pages to crawl",
    )
    sync_status = models.CharField(
        max_length=20,
        choices=SYNC_STATUS_CHOICES,
        default="IDLE",
    )
    total_pages_count = models.IntegerField(default=0)
    indexed_pages_count = models.IntegerField(default=0)
    pending_pages_count = models.IntegerField(default=0)
    failed_pages_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Web Source for {self.project.display_name} ({self.root_url})"
```

### 9.2. `WebPage` Model
Tracks individual crawled URLs and their vector state.

```python
class WebPage(models.Model):
    PAGE_STATES = [
        ("PENDING", "Pending Indexing"),
        ("INDEXING", "Indexing Vectors"),
        ("INDEXED", "Successfully Indexed"),
        ("MODIFIED", "Modified on Remote Site"),
        ("FAILED", "Failed"),
        ("DELETED", "Deleted from Remote Site"),
    ]

    web_source = models.ForeignKey(
        WebSource,
        on_delete=models.CASCADE,
        related_name="pages",
    )
    url = models.URLField(max_length=2048, db_index=True)
    title = models.CharField(max_length=500, blank=True)
    depth = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=PAGE_STATES,
        default="PENDING",
    )
    content_hash = models.CharField(max_length=64, blank=True, db_index=True)
    etag = models.CharField(max_length=255, blank=True)
    last_modified_header = models.CharField(max_length=255, blank=True)
    http_status = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    last_scraped_at = models.DateTimeField(null=True, blank=True)
    last_indexed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["url"]
        unique_together = [["web_source", "url"]]

    def __str__(self):
        return f"{self.url} [{self.status}]"
```

---

## 10. UI & HTMX Interaction Specifications

### 10.1. Project Creation Modal
- Add a dedicated **Website Project** preset in the Project Creation modal.
- Form inputs:
  - **Project Name:** e.g., `"Stripe Docs"`
  - **Website URL:** e.g., `"https://docs.stripe.com/api"`
  - **Crawl Limit:** Dropdown: 50, 100 *(default)*, 250, 500 pages.
  - **Crawl Scope:** Checkbox: *"Constrain strictly to this subpath"* *(checked by default)*.
  - **Storage Backend:** Defaults to `Postgres RAG` (`postgres`).
- On submit: Project is created, `WebSource` is provisioned, and the background thread launches the auto-crawl & index immediately.

### 10.2. Web Source Dashboard Section
When viewing a project backed by a `WebSource` in [`apps/documents/views.py`](file:///Users/chrys/Projects/my_rag/src/apps/documents/views.py):
1. **Live Status & KPI Cards:**
   - **Total Pages:** e.g., `85`
   - **Indexed Pages:** `80` (Green badge)
   - **Pending / Modified:** `5` (Amber badge)
   - **Failed / Deleted:** `0` (Red badge)
   - **Last Synced:** `Sep 8, 2026, 17:05`
2. **Real-Time Polling Progress Bar:**
   - If `sync_status` is `DISCOVERING` or `INDEXING`, the partial includes:
     ```html
     <div hx-get="{% url 'documents:web_status' project.project_id %}" 
          hx-trigger="every 2s" 
          hx-swap="outerHTML">
       <!-- Dynamic Progress Bar (e.g. 65%) -->
     </div>
     ```
3. **Action Buttons:**
   - **`Check for Updates` Button (`POST /rag/<store_id>/web/sync/`):**
     - Scans for new or modified pages; updates counts and status table.
   - **`Index New / Modified Pages` Button (`POST /rag/<store_id>/web/index-new/`):**
     - Runs targeted background ingestion of `PENDING` and `MODIFIED` pages.
   - **`Full Re-Index` Button (`POST /rag/<store_id>/web/reindex/`):**
     - Confirmation modal before re-crawling and re-embedding everything.
4. **Pages Table:**
   - Columns: `URL` (external link), `Title`, `Depth`, `Status Badge`, `HTTP Code`, `Last Indexed`, `Actions` (Individual retry button).
   - Instant search filter by URL or Title.

---

## 11. Success Criteria

- [ ] Creating a project with a valid website URL triggers an asynchronous background crawl and auto-indexes discovered pages up to the configured limit.
- [ ] Base `trafilatura` cleanly extracts article text into Markdown, omitting navbars, cookie banners, scripts, and footers.
- [ ] During crawl, the HTMX dashboard polls and updates the progress indicator without page reloads or Gunicorn worker timeouts.
- [ ] Clicking "Check for Updates" discovers newly added pages and sets their state to `PENDING` without touching indexed pages.
- [ ] Clicking "Index New / Modified Pages" processes only `PENDING` and `MODIFIED` pages, updating vector embeddings and purging obsolete chunks for modified pages.
- [ ] Disappearing / 404 pages have their vector chunks purged and are marked `DELETED`.
- [ ] All automated unit tests in `Testing/unit/documents/` pass without live internet access.
