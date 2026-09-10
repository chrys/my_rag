# Tasks: Native In-Process Website Scraping & Incremental Indexing (Option 1)

---

## Phase 1: Foundation & Data Models

### Task 1.1: Dependencies & Data Models (`WebSource`, `WebPage`)
- [x] Add `trafilatura` and `beautifulsoup4` to `requirements/requirements.txt` and `requirements/requirements-prod.txt`.
- [x] Define `WebSource` model in `src/apps/documents/models.py` (OneToOneField with `Project`, `root_url`, `allowed_domain`, `subpath_only`, `max_depth`, `max_pages`, `sync_status`, counters).
- [x] Define `WebPage` model in `src/apps/documents/models.py` (ForeignKey with `WebSource`, `url`, `title`, `depth`, `status`, `content_hash`, `etag`, `last_modified_header`, `http_status`, `error_message`, timestamps).
- [x] Generate and run Django migrations.
- [x] **Acceptance Criteria:** `WebSource` and `WebPage` tables exist in database; relationships and string representations pass checks.
- [x] **Verification:** `python manage.py makemigrations && python manage.py migrate` succeeds without warnings.
- [x] **Files touched:**
  - `requirements/requirements.txt`
  - `requirements/requirements-prod.txt`
  - `src/apps/documents/models.py`
  - `src/apps/documents/migrations/000X_websource_webpage.py`

---

## Phase 2: Core Crawler Services

### Task 2.1: URL Sanitizer, Boundary Validator & Sitemap Parser
- [x] Create `src/apps/documents/web_crawler_services.py`.
- [x] Implement `sanitize_url(url: str) -> str`: Normalizes scheme, removes fragments and UTM/marketing query parameters.
- [x] Implement `is_within_boundary(url: str, base_url: str, subpath_only: bool) -> bool`.
- [x] Implement `parse_sitemap(sitemap_url: str, client: httpx.Client) -> list[dict]`: Parses standard XML urlset and sitemap index files, extracting `<loc>` and `<lastmod>`.
- [x] **Acceptance Criteria:** Correctly parses nested/single sitemaps and enforces subpath and domain boundaries.
- [x] **Verification:** Hermetic unit tests in `Testing/unit/documents/test_web_crawler.py`.
- [x] **Files touched:**
  - `src/apps/documents/web_crawler_services.py`
  - `Testing/unit/documents/test_web_crawler.py`

### Task 2.2: Bounded BFS Spider & Robots.txt Compliance
- [x] Implement `check_robots_txt(base_url: str, target_url: str) -> bool` using `urllib.robotparser`.
- [x] Implement `crawl_site_bfs(root_url: str, max_depth: int, max_pages: int, subpath_only: bool) -> list[dict]`:
  - Queue-based BFS spider discovering links from raw HTML.
  - Skips non-HTML extensions (`.png`, `.pdf`, `.zip`, etc.) and non-HTTP schemes.
  - Enforces `crawl_delay_ms` politeness pause between outbound requests.
- [x] **Acceptance Criteria:** Spider stops at `max_depth` and `max_pages`, rejects binary links, handles redirect chains up to 5 hops, and obeys `robots.txt`.
- [x] **Verification:** Hermetic unit tests with mocked HTML in `Testing/unit/documents/test_web_crawler.py`.
- [x] **Files touched:**
  - `src/apps/documents/web_crawler_services.py`
  - `Testing/unit/documents/test_web_crawler.py`

### Task 2.3: Content Extraction & Vector Ingestion Pipeline
- [x] Implement `extract_clean_markdown(html_content: str) -> str | None`:
- [x] Implement `process_web_page_indexing(web_page: WebPage, project_id: str) -> bool`:
  - Enriches chunk metadata (`source_url`, `title`, `project_id`).
  - Feeds into `LlamaIndexIngestionPipeline`.
  - Updates `content_hash` (SHA-256) and `last_indexed_at` on `WebPage`.
- [x] **Acceptance Criteria:** Clean Markdown is extracted without header/footer noise; vectors are stored in PGVectorStore with metadata.
- [x] **Verification:** Unit tests in `Testing/unit/documents/test_web_crawler.py`.
- [x] **Files touched:**
  - `src/apps/documents/web_crawler_services.py`
  - `Testing/unit/documents/test_web_crawler.py`

---

## Checkpoint 1: Crawler & Ingestion Services
- [x] Run `DJANGO_ENV=testing .venv/bin/pytest Testing/unit/documents/test_web_crawler.py -v`
- [x] Confirm all crawler tests pass without any outbound network calls.

---

## Phase 3: Incremental Sync & Vector Hygiene

### Task 3.1: Delta Discovery, Modification Detection & Vector Purge
- [x] Implement `run_web_lifecycle(web_source: WebSource, mode: str = 'sync') -> dict`:
  - `mode='discover'`: Scans site, discovers new URLs, populates `WebPage` with `status='PENDING'`.
  - `mode='sync'`: Checks existing pages; if HTTP 404/410, calls `engine.delete_document(page.url)` and marks `DELETED`. If SHA-256 changed, flags `MODIFIED`.
  - `mode='index_new'`: Indexes only `PENDING` and `MODIFIED` pages (purging stale vectors for `MODIFIED` before re-embedding).
  - `mode='full'`: Full re-crawl and re-index of all pages.
- [x] Update `project.document_count` and `web_source.indexed_pages_count`.
- [x] **Acceptance Criteria:** New pages get indexed without re-indexing untouched pages; modified pages have old chunks purged; 404 pages are removed from vector store.
- [x] **Verification:** Unit tests in `Testing/unit/documents/test_web_crawler.py`.
- [x] **Files touched:**
  - `src/apps/documents/web_crawler_services.py`
  - `Testing/unit/documents/test_web_crawler.py`

---

## Phase 4: UI & HTMX Workflows

### Task 4.1: Project Creation Wizard with Website Preset
- [x] Update `templates/partials/project_create_modal.html` with a dedicated **Website Project** tab/card.
- [x] Update `create_project` view in `src/apps/projects/views.py`:
  - When `storage_type == 'website'` (or preset is selected), set project storage to `postgres`.
  - Create attached `WebSource` with `root_url`, `subpath_only`, and `max_pages`.
  - Trigger initial crawl & indexing in a detached `threading.Thread`.
- [x] **Acceptance Criteria:** Creating a website project immediately spins up background crawl and redirects to the project dashboard.
- [x] **Verification:** Unit tests in `Testing/unit/projects/test_dashboard_views.py`.
- [x] **Files touched:**
  - `templates/partials/project_form.html`
  - `src/apps/projects/views.py`
  - `src/apps/projects/urls.py`
  - `Testing/unit/projects/test_dashboard_views.py`

### Task 4.2: Web Source Dashboard Section & HTMX Endpoints
- [x] Create `templates/partials/web_source_section.html`:
  - KPI cards (Total Pages, Indexed, Pending/Modified, Failed/Deleted).
  - Action buttons: "Check for Updates", "Index New / Modified Pages", "Full Re-Index".
  - Discovered Pages table with status badges and instant search.
- [x] Create `templates/partials/web_status_partial.html`:
  - Progress bar polling with `hx-get="{% url 'documents:web_status' store_id %}" hx-trigger="every 2s"`.
- [x] Implement HTMX view handlers in `src/apps/documents/views.py`:
  - `web_status(request, store_id)`
  - `web_sync(request, store_id)`
  - `web_index_new(request, store_id)`
  - `web_reindex(request, store_id)`
- [x] Wire routes in `src/apps/documents/urls.py`.
- [x] **Acceptance Criteria:** Real-time polling updates progress bar without page reloads; clicking buttons triggers background actions and swaps partials cleanly.
- [x] **Verification:** Unit tests in `Testing/unit/documents/test_web_views.py`.
- [x] **Files touched:**
  - `templates/partials/web_source_section.html`
  - `templates/partials/web_status_partial.html`
  - `templates/partials/document_list.html`
  - `src/apps/documents/views.py`
  - `src/apps/documents/urls.py`
  - `Testing/unit/documents/test_web_views.py`

---

## Checkpoint 2: Full Integration & Regression Gate
- [x] Run `DJANGO_ENV=testing .venv/bin/pytest Testing/unit/documents -v`
- [x] Run `DJANGO_ENV=testing .venv/bin/pytest Testing/unit/projects -v`
- [x] Run `DJANGO_ENV=testing .venv/bin/pytest Testing/regression -v`
- [x] Confirm OpenAPI documentation in `Documentation/API/` is updated if new API endpoints were introduced.
- [ ] Human review of the completed feature.
