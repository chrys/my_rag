# Sprint Changelog: Sep 1 - Native Website Scraping & Incremental Indexing

**Sprint:** `Sep 1 (September 2026)`  
**Focus:** Native in-process website crawling, automated content extraction, real-time discovery tracking, incremental delta synchronization, and unified multi-source knowledge base management.

---

## 1. Overview

Sprint Sep 1 introduces the **Website Project** type to My RAG Studio. Users can now point the system to any website or documentation URL and automatically transform the entire site into a searchable, citation-backed AI knowledge base without needing external scraping tools or manual file uploads.

---

## 2. New Features & Functional Improvements

### A. Website Project Creation
* **One-Click Website Setup**: Users can create a new project by simply entering a website address (e.g. `https://example.com/docs/`).
* **Flexible Crawl Scopes**:
  * **Subpath Only**: Limits crawling strictly to the specified URL path and its sub-pages (ideal for specific documentation sections or product guides).
  * **Full Domain**: Allows discovery across all pages under the same domain.
* **Crawl Page Limits**: Configurable maximum page limits (up to 100 pages by default) to keep crawls fast and focused.
* **Project Dropdown Integration**: Added an immediate "➕ Create New Project..." option directly inside the top navigation bar project selector.

### B. Automated Web Discovery & Content Extraction
* **Smart Sitemap & Spider Crawling**: Automatically detects and reads XML sitemaps; if no sitemap is available, it gracefully falls back to discovering links page by page.
* **Polite Crawling**: Automatically checks and respects website rules (`robots.txt`) and applies built-in rate limiting to prevent overloading target servers.
* **Clean Text Extraction**: Strips away website headers, navigation menus, ads, footers, and boilerplate, indexing only the primary human-readable content and page titles.

### C. Real-Time Status & Progress Dashboard
* **Live Status Banner**: Displays real-time crawling and vector indexing status (Discovering, Indexing, Completed, or Error) with an animated progress bar and percentage indicator.
* **KPI Metrics Overview**: Four summary metric cards provide an at-a-glance breakdown:
  * **Total Discovered** pages
  * **Indexed** pages ready for querying
  * **Pending / Modified** pages awaiting processing
  * **Failed / Deleted** pages
* **One-Click Crawler Actions**:
  * **Check for Updates**: Quickly checks the website for newly published or modified pages without re-crawling untouched content.
  * **Index New / Modified Pages**: Ingests and embeds only newly discovered or altered pages.
  * **Full Re-Index**: Re-scrapes the entire site from scratch when a complete refresh is desired.

### D. Discovered Web Pages Explorer
* **Comprehensive Page Inventory**: A structured table listing all discovered URLs, page titles, crawl depth, indexing status badges, HTTP status codes (e.g. 200, 404), and last indexed timestamps.
* **Instant Search & Filter**: A fast search bar to filter discovered web pages by keyword or URL in real time.
* **Optimized Card Layout**: Cleanly formatted and responsive table where long URLs truncate with full-text tooltips, ensuring all status and timestamp columns remain visible.

### E. Incremental Delta Synchronization & Knowledge Hygiene
* **Automatic Modification Detection**: Identifies when an existing page's content has changed and flags it for re-indexing.
* **Stale Knowledge Purging**: When a web page is modified or deleted (404/410), previous AI vector representations are automatically deleted, preventing the AI from citing outdated or nonexistent content.
* **Error Transparency**: Surfaces server errors or broken links directly in the page list with descriptive warning indicators.

### F. Multi-Source Knowledge Support (Website + Files)
* **Unified Knowledge Base**: A Website Project seamlessly accepts both crawled website pages and supplementary uploaded documents (PDFs, Markdown notes, text documents) within the same project.
* **Collapsible Supplementary Uploads**: For Website Projects, the document upload card and file library are tucked into a neat, optional collapsible section to keep the crawler interface clean while maintaining full support for supplementary file ingestion.
* **Simultaneous Search & Citations**: During chat interactions, the AI retrieves information from both crawled website pages and uploaded documents, providing direct links back to the original source web pages.
