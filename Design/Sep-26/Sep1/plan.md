# Implementation Plan: Native In-Process Website Scraping & Incremental Indexing Engine (Option 1)

---

## Overview
Implement Option 1 for website scraping and incremental indexing in `my_rag`: allowing users to create a RAG project from a website URL, crawl and extract clean Markdown in an asynchronous background thread, monitor progress live via HTMX polling, and perform on-demand incremental delta syncs (indexing new pages, re-embedding modified pages, and purging deleted 404 pages).

---

## Architecture Decisions & Constraints
1. **Hybrid Architecture:** `WebSource` (1-to-1 with `Project`) and `WebPage` (ForeignKey to `WebSource`) in `src/apps/documents/models.py`. Vector storage defaults to `postgres` (PGVector), preserving all existing retrieval, HyDE, chat, and evaluation flows.
2. **Asynchronous Execution:** Long crawls run in a background `threading.Thread` to avoid Gunicorn worker timeouts. Status is updated in the database (`sync_status='DISCOVERING'`, `INDEXING`, `COMPLETED`), polled every 2 seconds by HTMX.
3. **Extraction Stack:** Base `trafilatura` (standard package, no heavy extras) as primary extractor, with `BeautifulSoup` + `markitdown` fallback.
4. **Hermetic Testing:** Zero live internet calls in `Testing/unit/documents/`; all outbound requests (`robots.txt`, sitemaps, web pages) are mocked via `pytest-mock` or `httpx.MockTransport`.

---

## Task List & Vertical Slices

### Phase 1: Foundation & Data Models
- [x] **Task 1.1: Dependencies & Data Models (`WebSource`, `WebPage`)**
  - Add `trafilatura` and `beautifulsoup4` to `requirements/requirements.txt` and `requirements/requirements-prod.txt`.
  - Define `WebSource` and `WebPage` models in `src/apps/documents/models.py`.
  - Create and apply Django database migrations.
  - *Verify:* `python manage.py makemigrations` and `python manage.py migrate`.

---

### Phase 2: Core Crawler Services
- [x] **Task 2.1: URL Sanitizer, Boundary Validator & Sitemap Parser**
  - Implement URL sanitization (fragment/UTM stripping, scheme normalization).
  - Implement subpath and domain boundary validators in `src/apps/documents/web_crawler_services.py`.
  - Implement XML sitemap parser (`sitemap.xml`, `sitemap_index.xml`) extracting `<loc>` and `<lastmod>`.
  - *Verify:* Unit tests in `Testing/unit/documents/test_web_crawler.py`.

- [x] **Task 2.2: Bounded BFS Spider & Robots.txt Compliance**
  - Implement FIFO queue-based breadth-first spider for link discovery when sitemap is missing.
  - Enforce `max_depth` (default 4), `max_pages` (default 100), and `robots.txt` compliance using `urllib.robotparser`.
  - Filter out binary and non-HTML assets.
  - *Verify:* Unit tests in `Testing/unit/documents/test_web_crawler.py`.

- [x] **Task 2.3: Content Extraction & Vector Ingestion Pipeline**
  - Implement `extract_clean_markdown()` using base `trafilatura`, with `BeautifulSoup` + `markitdown` fallback.
  - Integrate extracted markdown with `LlamaIndexIngestionPipeline` (storing chunk metadata: `source_url`, `title`, `project_id`).
  - Update `WebPage` status (`INDEXED`, `content_hash`, `last_indexed_at`).
  - *Verify:* Unit tests with mocked vector store in `Testing/unit/documents/test_web_crawler.py`.

### Checkpoint 1: Crawler & Ingestion Services
- [x] `DJANGO_ENV=testing .venv/bin/pytest Testing/unit/documents/test_web_crawler.py -v` passes with 100% mocked transport.

---

### Phase 3: Incremental Sync & Vector Hygiene
- [x] **Task 3.1: Delta Discovery, Modification Detection & Vector Purge**
  - Implement `run_web_lifecycle(web_source, mode='sync')`:
    - Delta discovery: Mark new URLs as `PENDING`.
    - Modification detection: Compare SHA-256 `content_hash` or `<lastmod>`; flag changed pages as `MODIFIED`.
    - Remote 404/410 handling: Delete vector chunks from `PGVectorStore` and mark page as `DELETED`.
    - Purge stale chunks before re-embedding `MODIFIED` pages.
  - *Verify:* Unit tests in `Testing/unit/documents/test_web_crawler.py`.

---

### Phase 4: UI & HTMX Workflows
- [x] **Task 4.1: Project Creation Wizard with Website Preset**
  - Update Project creation modal in `templates/partials/` and `src/apps/projects/views.py` with a "Website Project" preset.
  - On submit, provision `Project` with storage type `postgres`, create `WebSource`, and trigger the initial crawl in a background thread.
  - *Verify:* Unit tests in `Testing/unit/projects/test_dashboard_views.py`.

- [x] **Task 4.2: Web Source Dashboard Section & HTMX Endpoints**
  - Create HTMX template `templates/partials/web_source_section.html` and polling progress partial `templates/partials/web_status_partial.html`.
  - Implement endpoints in `src/apps/documents/views.py`:
    - `web_status`: Returns live progress bar during `DISCOVERING` and `INDEXING`.
    - `web_sync`: Triggers delta update check.
    - `web_index_new`: Triggers targeted indexing of `PENDING` and `MODIFIED` pages.
    - `web_reindex`: Triggers full re-crawl.
  - Wire URLs in `src/apps/documents/urls.py`.
  - *Verify:* Unit tests in `Testing/unit/documents/test_web_views.py`.

### Checkpoint 2: End-to-End Integration & Regression Gate
- [x] `DJANGO_ENV=testing .venv/bin/pytest Testing/unit/documents -v` passes.
- [x] `DJANGO_ENV=testing .venv/bin/pytest Testing/unit/projects -v` passes.
- [x] `DJANGO_ENV=testing .venv/bin/pytest Testing/regression -v` passes.
- [x] Update API documentation in `Documentation/API/` if any new REST routes were exposed.

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
| :--- | :--- | :--- |
| **Gunicorn worker timeout on large crawls** | High | Entire crawl/scrape lifecycle runs in a detached `threading.Thread`; HTTP responses return immediately with an HTMX polling trigger (`hx-trigger="every 2s"`). |
| **Infinite link cycles / spider traps** | Med | Strict enforcement of `max_depth=4` and `max_pages=100`, plus URL query stripping if path depth exceeds 6 segments. |
| **Target server rate-limiting (HTTP 429)** | Med | Built-in politeness delay (250ms), exponential backoff on 429s, and graceful termination saving partial progress. |
| **Hallucinated citations from deleted/modified pages** | High | Purge old vector embeddings from `PGVectorStore` whenever a page is modified or deleted. |
