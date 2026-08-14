# Changelog & Implementation Record: Aug1 Branch

---

## 📋 Overview

The `Aug1` branch restores the **Native Obsidian Vault Integration** and delivers the **Google Calendar Integration & Sync Engine** alongside the **Multi-Model AI Management** system.

---

## 🚀 Key Features & Changes Delivered

### 1. Google Calendar Integration & Sync Engine
- **New Django Models (`src/apps/documents/models.py`)**:
  - `GoogleCalendarSource`: Tracks OAuth tokens (`access_token`, `refresh_token`), syncToken, selected calendars list, lookback/lookahead window days, sync_status, and progress counts.
  - `GoogleCalendarEvent`: Tracks individual Google Calendar events, Markdown relative paths (`rag_data/<store_id>/Calendar/`), start/end timestamps, and indexing state (`PENDING`, `INDEXED`, `FAILED`).
  - Added `'google_calendar'` to `ObsidianSource.SOURCE_TYPES`.

- **Google Calendar Services (`src/apps/documents/google_calendar_services.py`)**:
  - OAuth client credentials reader (`git_ignore/client_secret_*.json`).
  - `get_oauth_authorization_url` & `exchange_oauth_code_for_tokens`: OAuth authorization flow.
  - `convert_event_to_markdown`: Generates YAML frontmatter Markdown notes stored under `rag_data/<store_id>/Calendar/`.
  - Non-blocking `run_google_calendar_sync_lifecycle`: Event fetching, delta updates, and Markdown builder.

- **Endpoints & URL Routing (`src/apps/documents/views.py` & `urls.py`)**:
  - `/rag/google/oauth2callback/`: Google OAuth callback handler.
  - `/projects/<store_id>/google-calendar/connect/`: Auth redirect handler.
  - `/projects/<store_id>/google-calendar/preferences/`: Multi-calendar & sync window preferences handler.
  - `/projects/<store_id>/google-calendar/sync/`: Event discovery trigger.
  - `/projects/<store_id>/google-calendar/index-new/`: Vector embedding generator via `gemini-embedding-001`.
  - `/projects/<store_id>/google-calendar/full-reindex/`: Full re-sync & re-embed handler.
  - `/projects/<store_id>/google-calendar/status/`: HTMX polling endpoint (`hx-trigger="every 2s"`).

- **Frontend HTMX Template Integration**:
  - `templates/partials/document_list.html`: Updated TYPE radio toggle (`Document | Obsidian | Google Calendar`).
  - `templates/partials/google_calendar_section.html`: OAuth connect banner, multi-calendar checkboxes, lookback/lookahead inputs, progress indicators, action buttons, and indexed/pending events tables.

---

### 2. Native Obsidian Vault Integration Restoration
- **Restored Service Functions (`src/apps/documents/services.py`)**:
  - `sanitize_obsidian_markdown`: Strips double-bracket links (`[[Note|Alias]]` -> `Alias`).
  - `scan_obsidian_vault`: Vault directory scanner enforcing folder/file exclusion rules.
  - `enrich_chunk_metadata`: Structural chunk metadata tagger.
  - `discover_obsidian_vault_files`, `process_obsidian_file_indexing`, and `run_obsidian_lifecycle`: 3-stage vault indexing and sync engine.

- **Restored View Functions (`src/apps/documents/views.py`)**:
  - `set_source_type`: Handles switching project source type between `Document`, `Obsidian`, and `Google Calendar`.
  - `obsidian_save_path`, `obsidian_index`, `obsidian_index_new`, `obsidian_sync`, `obsidian_status`, `get_obsidian_context`, `render_obsidian_section`.

- **Restored URL Routing & Templates**:
  - Re-added `/projects/<store_id>/obsidian/*` routes and updated `partials/obsidian_section.html` to render Indexed Obsidian Notes table.

---

## 🧪 Unit Test Suite (`Testing/unit/documents/`)

7 unit test suites in `Testing/unit/documents/`:
1. `test_google_calendar_models.py`
2. `test_google_calendar_services.py`
3. `test_google_calendar_views.py`
4. `test_obsidian_models.py`
5. `test_obsidian_services.py`
6. `test_obsidian_lifecycle.py`
7. `test_obsidian_views.py`

**Test Run Result:** `377 passed` across the entire unit & regression test suite.
