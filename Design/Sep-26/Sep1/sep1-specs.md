# Specification: Native In-Process Website Scraping & Incremental Indexing Engine (Option 1)

---

## 1. Objective & Scope

### Problem Statement & Background Context
The platform currently supports indexing local files, Obsidian vaults ([ObsidianSource](file:///Users/chrys/Projects/my_rag/src/apps/documents/models.py#L141-L182)), and Google Calendar events ([GoogleCalendarSource](file:///Users/chrys/Projects/my_rag/src/apps/documents/models.py#L238-L306)) into PostgreSQL PGVector and Google File Search. However, users frequently need to ground AI assistants against live websites and documentation portals. 

This specification defines the functional requirements and architectural specifications for **Option 1: Native In-Process Sitemap & HTTP Spider Web Scraping with Incremental Re-Indexing**. It enables users to create a project by entering a root URL, automatically scrape and index all sub-pages under that domain, and subsequently check for and index newly published or updated web pages on demand.

### High-Level Goals
1. **Seamless Project Creation:** Allow users to create a RAG project by specifying a website root URL.
2. **Sitemap-First Discovery with Spider Fallback:** Automatically discover site pages via `sitemap.xml` (or `robots.txt` discovery), falling back to a bounded, recursive HTML link spider (BFS).
3. **High-Fidelity Text Extraction & Hygiene:** Strip boilerplate (navbars, menus, cookie consent banners, footers, ads) and convert raw HTML into clean, semantic Markdown enriched with URL and page metadata.
4. **On-Demand Incremental Indexing:** Provide a delta-sync mechanism where the user can trigger an inspection for newly added or modified pages, queueing and vector-indexing only the diff without reprocessing unchanged pages.
5. **Zero External Infrastructure Overhead:** Execute entirely within the Django application runtime using lightweight Python libraries (`httpx`, `BeautifulSoup4`, `trafilatura` / `markitdown`), avoiding heavy headless browser daemons.

### Out of Scope (Non-Goals for Option 1)
- Scraping JavaScript-heavy Single Page Applications (SPAs) that require full client-side DOM execution (covered by Option 2: Headless Browser).
- Bypassing CAPTCHAs, Cloudflare Turnstile, or authenticated paywalls/logins.
- Cross-domain or unconstrained recursive crawling across the entire open web.

---

## 2. User Personas & Core User Stories

### User Personas
- **Knowledge Worker / Researcher:** Wants to ground a chatbot on a public product documentation site, API guide, or institutional wiki.
- **Project Administrator:** Wants to monitor an evolving corporate site or blog and periodically bring new articles into the existing vector store without manual file uploads.

### Core User Stories
1. **Initial Site Ingestion:**
   *As a user, when I create a new project, I want to enter a website URL (e.g. `https://docs.example.com/`) so that all valid content pages under that site are scraped, converted to Markdown, and embedded into my project's vector store.*
2. **Reviewing Discovered Pages:**
   *As a user, I want to view a dedicated "Web Sources" table showing each discovered page URL, its title, HTTP status, indexing state (`PENDING`, `INDEXED`, `FAILED`), and last-scraped timestamp.*
3. **On-Demand Incremental Sync ("Index New Pages"):**
   *As a user, when new articles or pages are published on the website, I want to click "Check for New Pages" to discover them, and then click "Index New" to vectorize only the newly added or updated pages without wasting tokens on existing content.*
4. **Full Re-Index:**
   *As a user, if the website has undergone a major restructure, I want to trigger a full re-scrape and re-index that refreshes all existing pages.*

---

## 3. Functional Requirements & System Architecture

```
                                  [ User Enters URL ]
                                           │
                                           ▼
                       ┌───────────────────────────────────────┐
                       │       1. Domain & URL Validator       │
                       │ (Normalize scheme, domain boundary)   │
                       └───────────────────┬───────────────────┘
                                           │
                                           ▼
                       ┌───────────────────────────────────────┐
                       │     2. Sitemap-First Discovery        │
                       │   (Check robots.txt / sitemap.xml)    │
                       └───────┬───────────────────────┬───────┘
                      Sitemap  │                       │ No Sitemap
                       Found   ▼                       ▼
               ┌───────────────────────┐       ┌───────────────────────┐
               │ Fast Sitemap Extractor│       │ Bounded BFS Spider    │
               │ (URLs & <lastmod>)    │       │ (Same-domain recursion)│
               └───────────────┬───────┘       └───────┬───────────────┘
                               │                       │
                               └───────────┬───────────┘
                                           │ Discovered URLs
                                           ▼
                       ┌───────────────────────────────────────┐
                       │      3. State Registry & Diff Gate    │
                       │ (Compare with existing WebPage table) │
                       └───────┬───────────────────────┬───────┘
                    New URL    │                       │ Existing URL (Sync Mode)
                               ▼                       ▼
               ┌───────────────────────┐       ┌───────────────────────┐
               │ Status: PENDING       │       │ HTTP HEAD (ETag/mtime)│
               └───────────────┬───────┘       └───────┬───────────────┘
                               │                       │ Changed
                               └───────────┬───────────┘
                                           │ User Triggers "Index New"
                                           ▼
                       ┌───────────────────────────────────────┐
                       │    4. Clean & Extract Pipeline        │
                       │ (Trafilatura/MarkItDown boilerplate   │
                       │  removal -> semantic Markdown)        │
                       └───────────────────┬───────────────────┘
                                           │ Clean Markdown + Metadata
                                           ▼
                       ┌───────────────────────────────────────┐
                       │ 5. LlamaIndex Vector Ingestion Engine │
                       │ (PGVectorStore / Google File Search)  │
                       └───────────────────────────────────────┘
```

### 3.1. Project & Source Configuration
- **Root URL Normalization:** Strip query parameters, tracking fragments (`#...`), and ensure trailing slash consistency (`https://example.com/docs/`).
- **Domain Boundary Lockdown:** Restrict crawling strictly to the same Fully Qualified Domain Name (FQDN) or subpath prefix (e.g. if `https://example.com/docs/` is given, URLs under `https://example.com/blog/` or `https://other.com` are skipped unless explicitly permitted).
- **Crawl Limits:** Configurable project defaults:
  - `max_pages`: Maximum pages to crawl per job (default: 250, hard ceiling: 1,000).
  - `max_depth`: Maximum link traversal depth from root (default: 4).
  - `crawl_delay_ms`: Politeness delay between outbound requests (default: 250ms).

### 3.2. Page Discovery Engine
1. **Sitemap-First Pass:**
   - Attempt retrieval of `{root_url}/sitemap.xml`, `{root_url}/sitemap_index.xml`, and inspect `{root_url}/robots.txt` for `Sitemap:` directives.
   - Parse XML sitemaps recursively (handling sitemap indices and standard urlsets).
   - Extract `<loc>` (URL) and `<lastmod>` (ISO timestamp).
2. **Recursive Spider Pass (Fallback or Augmentation):**
   - If no sitemap is available or if sitemap yields fewer pages than anticipated:
     - Initialize a Queue with the root URL.
     - Extract all `<a href="...">` anchor tags.
     - Resolve relative links against the base URL.
     - Enforce domain boundary, depth limit, and ignore non-content schemes (`mailto:`, `tel:`, `javascript:`, `ftp:`).
     - Filter out binary file extensions (`.jpg`, `.jpeg`, `.png`, `.gif`, `.svg`, `.mp4`, `.zip`, `.tar`, `.exe`, `.dmg`).

### 3.3. HTML Hygiene & Content Extraction
- **Boilerplate Removal:**
  - Strip non-content HTML structures: `<nav>`, `<header>`, `<footer>`, `<aside>`, `<script>`, `<style>`, `<noscript>`, SVG graphics, cookie banner modals, and social share widgets.
- **Conversion to Markdown:**
  - Convert the extracted article container into semantic GitHub Flavored Markdown (preserving headers `#`, lists, tables, and fenced code blocks).
- **Metadata Tagging:**
  - Every extracted page must generate enriched chunk metadata:
    - `source_url`: Full canonical URL of the web page.
    - `title`: Extracted `<title>` or OpenGraph `og:title` / `<h1>`.
    - `description`: `<meta name="description">` or first paragraph summary.
    - `published_date`: Extracted `<article:published_time>` or sitemap `<lastmod>`.
    - `project_id`: Target RAG project identifier.

### 3.4. Incremental Discovery & Delta Detection Requirements
When the user requests to check for new web pages:
1. **Discovery Diffing:**
   - Run the discovery pass (re-inspecting `sitemap.xml` and/or re-scanning links from root).
   - Compare discovered URLs against the project's existing `WebPage` records in the database.
   - Any URL not found in the database is created with state `PENDING`.
2. **Modification Detection (Known Pages):**
   - If the sitemap provides `<lastmod>`, compare with `WebPage.last_scraped_at`. If `lastmod > last_scraped_at`, flag page as `MODIFIED`.
   - If no sitemap, issue lightweight HTTP `HEAD` requests using `If-Modified-Since` and `If-None-Match` (`ETag`). If `304 Not Modified` is returned, skip download.
   - If HTTP `GET` is executed, compute SHA-256 `content_hash` of the cleaned Markdown body. If the hash matches the stored hash, leave status as `INDEXED`; if it differs, flag as `MODIFIED`.
3. **Execution Separation:**
   - **Step A: "Check for Updates" (Discovery):** Scans the website and updates database counters (*e.g., "Found 8 new pages, 2 updated pages"*), without performing vector indexing yet.
   - **Step B: "Index New / Modified Pages":** Only fetches, converts, and vector-indexes pages whose state is `PENDING` or `MODIFIED`.

---

## 4. Data Model Specifications

Following the pattern established by `ObsidianSource` / `GoogleCalendarSource` in [`src/apps/documents/models.py`](file:///Users/chrys/Projects/my_rag/src/apps/documents/models.py):

### 4.1. `WebSource` Model (One-to-One with Project)
Represents the website configuration for a project.

| Field | Type | Attributes | Description |
| :--- | :--- | :--- | :--- |
| `project` | OneToOneField | `Project`, on_delete=CASCADE, related_name='web_source' | Associated RAG project. |
| `root_url` | URLField | max_length=1024 | The starting entrypoint URL (e.g. `https://docs.mycompany.com/`). |
| `allowed_domain` | CharField | max_length=255 | Normalized domain boundary (e.g. `docs.mycompany.com`). |
| `max_depth` | PositiveIntegerField | default=4 | Maximum link depth traversal limit. |
| `max_pages` | PositiveIntegerField | default=250 | Hard cutoff for total crawled pages. |
| `sync_status` | CharField | max_length=20, default='IDLE' | `IDLE`, `DISCOVERING`, `INDEXING`, `COMPLETED`, `FAILED`. |
| `total_pages_count` | IntegerField | default=0 | Total discovered URLs. |
| `indexed_pages_count` | IntegerField | default=0 | Total successfully indexed pages. |
| `pending_pages_count` | IntegerField | default=0 | Pages awaiting indexing. |
| `failed_pages_count` | IntegerField | default=0 | Pages that failed scraping/indexing. |
| `last_synced_at` | DateTimeField | null=True, blank=True | Timestamp of last discovery/sync run. |
| `created_at` | DateTimeField | auto_now_add=True | Creation timestamp. |
| `updated_at` | DateTimeField | auto_now=True | Last update timestamp. |

### 4.2. `WebPage` Model (ForeignKey to WebSource)
Tracks individual URLs, their content hashes, and vector indexing states.

| Field | Type | Attributes | Description |
| :--- | :--- | :--- | :--- |
| `web_source` | ForeignKey | `WebSource`, on_delete=CASCADE, related_name='pages' | Parent WebSource. |
| `url` | URLField | max_length=2048, db_index=True | Normalized URL of the page. |
| `title` | CharField | max_length=500, blank=True | Page title extracted from `<title>` / `<h1>`. |
| `depth` | PositiveIntegerField | default=0 | Discovery depth from root. |
| `status` | CharField | max_length=20, default='PENDING' | `PENDING`, `INDEXING`, `INDEXED`, `MODIFIED`, `FAILED`. |
| `content_hash` | CharField | max_length=64, blank=True | SHA-256 hash of extracted clean Markdown content. |
| `etag` | CharField | max_length=255, blank=True | HTTP ETag header value for cache validation. |
| `last_modified_header` | CharField | max_length=255, blank=True | HTTP Last-Modified header value. |
| `http_status` | IntegerField | null=True, blank=True | Last recorded HTTP response code (e.g. 200, 404). |
| `error_message` | TextField | blank=True | Details if scraping, parsing, or vector indexing failed. |
| `last_scraped_at` | DateTimeField | null=True, blank=True | When the HTML was last retrieved. |
| `last_indexed_at` | DateTimeField | null=True, blank=True | When embeddings were last stored in vector DB. |
| `created_at` | DateTimeField | auto_now_add=True | Record creation timestamp. |
| `updated_at` | DateTimeField | auto_now=True | Record update timestamp. |

*Constraints:* `unique_together = [['web_source', 'url']]`

### 4.3. Lifecycle State Machine

```
                   [ Discovery Pass ]
                           │
                           ▼
                     [ PENDING ] ◄────────────────┐
                           │                      │
                   (Start Indexing)          (Content Differs)
                           │                      │
                           ▼                      │
                     [ INDEXING ]                 │
                     │          │                 │
            (Success)│          │(Failure)        │
                     ▼          ▼                 │
                [ INDEXED ]   [ FAILED ]          │
                     │                            │
             (Check for Updates)                  │
                     │                            │
                     └───────► [ MODIFIED ] ──────┘
```

---

## 5. UI / UX Specifications & Workflows

### 5.1. Project Creation Flow
- In the project creation modal/screen, alongside storage backend choices, allow the user to select **Source Type: Website**.
- Input field: **Website Root URL** (with immediate client/server validation for valid HTTP/HTTPS syntax).
- Checkbox / Options:
  - *Max Pages* (Dropdown: 50, 100, 250, 500).
  - *Include Subpaths Only* (Enforce strict URL prefix bounding).
- On submit, Django creates the `Project` and associated `WebSource`, and automatically triggers Stage 1 Discovery.

### 5.2. Web Source Dashboard Partial (HTMX-Driven)
The document management view for website projects renders a dedicated **Web Management Section** (mirroring the UX of `partials/obsidian_section.html`):

1. **Header & Statistics Bar:**
   - Root URL display with outbound link.
   - Status KPI cards:
     - **Total Discovered Pages**
     - **Indexed Pages** (Green)
     - **Pending Indexing** (Amber badge)
     - **Failed Pages** (Red badge)
     - **Last Synced Timestamp**
2. **Action Controls:**
   - **`Check for Updates` Button (`POST /rag/<store_id>/web/sync/`):**
     - Triggers delta discovery.
     - HTMX swaps statistics and alerts: *"Discovered 14 new pages (14 pending indexing)."*
   - **`Index New Pages` Button (`POST /rag/<store_id>/web/index-new/`):**
     - Processes only pages in `PENDING` or `MODIFIED` state.
     - Updates progress bar in real time via HTMX polling.
   - **`Full Re-Index` Button (`POST /rag/<store_id>/web/reindex/`):**
     - Confirmation modal before clearing and re-crawling all pages.
3. **Discovered Pages Data Table:**
   - Columns: `URL` (truncated link), `Page Title`, `Depth`, `HTTP Status`, `State Badge` (`INDEXED`, `PENDING`, `FAILED`), `Last Indexed At`, `Actions` (Individual "Retry" or "Exclude").
   - Filter bar: Filter by status (`All`, `Pending`, `Indexed`, `Failed`) and search by URL keyword.

---

## 6. Safety, Rate Limiting & Politeness Policies

1. **`robots.txt` Compliance:**
   - Parse `robots.txt` using Python's `urllib.robotparser`.
   - Respect `Disallow` rules for the platform's User-Agent.
   - If a custom `Crawl-delay` is declared in `robots.txt`, adjust delay accordingly (bounded by a maximum ceiling of 5 seconds).
2. **Politeness Throttling:**
   - Concurrency is restricted to single-threaded sequential crawling per domain with a default inter-request delay (250ms).
   - Avoid flooding target hosts or triggering automated rate limits.
3. **Request Timeouts & Retries:**
   - Connect timeout: 5 seconds; Read timeout: 15 seconds.
   - Maximum retries: 2 with exponential backoff on transient errors (HTTP 502, 503, 504).
4. **Binary & Asset Guard:**
   - Check HTTP `Content-Type` header before streaming response bodies.
   - Immediately discard responses with non-HTML MIME types (e.g. `image/*`, `video/*`, `application/zip`, `application/octet-stream`), avoiding unnecessary memory usage.

---

## 7. Edge Cases & Error Handling Matrix

| Scenario | System Behavior & Fallback |
| :--- | :--- |
| **No Sitemap & Bounded Crawl Disabled** | Gracefully fallback to parsing only the root page, recording discovered links in the queue; notify user if only 1 page was reachable. |
| **HTTP 403 / 401 Forbidden** | Log HTTP status in `WebPage.http_status`, mark `status='FAILED'`, record error message *"Access denied by target web server"*. Do not crash the crawler. |
| **HTTP 429 Too Many Requests** | Crawler immediately pauses for 10 seconds, backs off delay to 2.0s, and retries once. If 429 persists, abort crawl job and alert user. |
| **Infinite Spider Traps (Calendars/Faceted Navigation)** | Guarded by strict `max_depth` (default 4) and `max_pages` cutoff. Also sanitize URLs by dropping query strings if path exceeds 6 segments. |
| **Redirect Loops (301/302)** | Follow redirects up to a maximum of 5 hops; store final canonical URL in `WebPage.url`. |
| **JavaScript-Only Blank Body** | If cleaned markdown content length is `< 50` characters, flag `WebPage.status='FAILED'` with warning: *"Page requires JavaScript rendering (static HTML empty)."* |
| **Page Deleted on Remote Site** | If a previously indexed page returns `HTTP 404` or `410 Gone` during sync: Mark `status='FAILED'` / `DELETED`, and optionally delete corresponding document vectors from `PGVectorStore`. |

---

## 8. Acceptance Criteria & Verifiable Scenarios

### Scenario 1: Initial Crawl via Sitemap
- **GIVEN** a new project created with root URL `https://example.com/` which has a valid `sitemap.xml` containing 25 URLs,
- **WHEN** the initial project indexing is triggered,
- **THEN** all 25 URLs are discovered, populated in the `WebPage` table with `PENDING`, scraped into clean Markdown, embedded into the vector store, and marked as `INDEXED` with `indexed_pages_count = 25`.

### Scenario 2: Incremental Discovery of Newly Created Pages
- **GIVEN** an existing project where all 25 original pages are `INDEXED`,
- **WHEN** the remote website publishes 3 new pages and the user clicks "Check for Updates",
- **THEN** the system discovers the 3 new URLs, creates 3 new `WebPage` records with `status='PENDING'`, updates `pending_pages_count = 3`, and displays a notification to the user without touching the 25 already indexed pages.

### Scenario 3: Targeted Indexing of Pending Pages
- **GIVEN** a project with 3 `PENDING` web pages,
- **WHEN** the user clicks "Index New Pages",
- **THEN** only the 3 pending pages are scraped and vectorized; previously indexed vectors are not recomputed, and upon completion all 28 pages are in state `INDEXED`.

### Scenario 4: Modified Content Detection
- **GIVEN** an indexed page whose content has changed on the live website,
- **WHEN** an incremental sync runs,
- **THEN** the SHA-256 content hash mismatch is detected, the page is flagged as `MODIFIED`, and the user can re-index only the modified page to update its vector representations.
