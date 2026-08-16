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

---

### 3. Dynamic `<customer_profile>` Context Support in Chat
- **Chat Formatting & System Prompt Services (`src/apps/chat/services.py`)**:
  - `format_customer_profile(customer_profile)`: Formats string or dictionary profile inputs into `<customer_profile>\n...\n</customer_profile>` tags. Returns `""` if missing or empty.
  - `build_effective_system_prompt(system_prompt, customer_profile)`: Appends the formatted `<customer_profile>` block to the base system prompt when present, and completely omits `<customer_profile>` tags when missing or empty.
- **Chat Views & RAG Routing (`src/apps/chat/views.py`)**:
  - `chat` (`POST /rag/api/chat/`) & `chat_submit` (`POST /rag/submit/`): Injects `customer_profile` dynamically into system context across all backends (PostgreSQL/LlamaIndex, Fallback LLM Router, Google File Search, and Local RAG).

---

### 4. Project-Scoped API Keys & Project Admin Tab UI
- **Database Model & Migration (`src/apps/api/models.py`, `src/apps/api/migrations/0002_apikey_project.py`)**:
  - Added `project` ForeignKey on `APIKey` so keys are strictly scoped to a single project.
  - Auto-generation of secure prefixed keys (`rag_key_...`) on save.
- **Project Admin Tab UI (`src/apps/projects/admin.py` & templates)**:
  - Configured dedicated tabs: `Parameters` | `Prompt` | `Sources` | `API Keys` | `Feedback`.
  - Dedicated **Prompt** tab for viewing and editing the project's custom system prompt with auto-save synchronization to `SystemPrompt`.
  - `templates/admin/projects/project_apikey_tab.html` & `templates/partials/project_apikey_section.html`: Interactive HTMX management providing key creation, one-click copy, active toggle, revocation, and ready-to-use cURL integration snippets.
- **Dashboard Sidebar Navigation (`src/apps/my_rag_project/settings/base.py`, `src/apps/api/admin.py`)**:
  - Registered `APIKey` and `APIUsage` with `custom_admin_site` (Unfold) and added **"API Keys"** item (🔑) to sidebar navigation.
- **Chat API Authentication & Scoping Enforcement (`src/apps/chat/views.py`)**:
  - Validates `X-API-Key` and `Authorization: Bearer <key>` headers.
  - Blocks cross-project key queries with `403 Forbidden`.
  - Tracks `last_used_at` timestamps on successful queries.

---

### 5. Chatbot Feedback API & Project Admin Feedback Tab
- **Database Model & Migration (`src/apps/chat/models.py`, `src/apps/chat/migrations/0002_chatfeedback.py`)**:
  - `ChatFeedback` model: stores `project`, `message_id`, `conversation_id`, `customer_id`, `value` (`up`/`down`), `timestamp`, and `created_at`.
- **API Endpoint (`/api/chatbot/feedback/` & `/rag/api/chatbot/feedback/`)**:
  - `chatbot_feedback` view in `src/apps/chat/views.py`: parses thumbs up / down feedback, validates payload, resolves target project via `store_id` or `X-API-Key`, and persists feedback record.
- **Project Admin Feedback Tab (`src/apps/projects/admin.py`, `templates/admin/projects/project_feedback_tab.html`, `templates/partials/project_feedback_section.html`)**:
  - Added **Feedback** tab under Project Admin.
  - Live metrics bar displaying: Total feedback count, 👍 Thumbs Up count & %, 👎 Thumbs Down count & %.
  - Chronological feedback log table with copyable message IDs, conversation IDs, customer IDs, and client/server timestamps.

---

## 🧪 Unit Test Suite

- **Google Calendar & Obsidian Suites (`Testing/unit/documents/`)**:
  1. `test_google_calendar_models.py`
  2. `test_google_calendar_services.py`
  3. `test_google_calendar_views.py`
  4. `test_obsidian_models.py`
  5. `test_obsidian_services.py`
  6. `test_obsidian_lifecycle.py`
  7. `test_obsidian_views.py`

- **Customer Profile & Chat Prompt Suite (`Testing/unit/chat/`)**:
  8. `test_customer_profile_prompt.py`: 10 test cases.

- **Project-Scoped API Keys Suite (`Testing/unit/api/`)**:
  9. `test_project_scoped_apikey.py`: 9 test cases.

- **Chatbot Feedback Suite (`Testing/unit/chat/`)**:
  10. `test_chatbot_feedback.py`: 6 test cases.

**Test Run Result:** `378 passed` (unit) + `15 passed` (regression) across the entire test suite (total 393 passed).


