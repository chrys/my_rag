# Specification: Google Calendar Integration & Sync Engine

---

## 1. Objective & Scope

### Problem Statement & Background Context
Users need to seamlessly search across their Google Calendar schedule alongside existing documents and Obsidian notes within their RAG workspace. This feature introduces **Google Calendar** as a third native source type (`TYPE: Document | Obsidian | Google Calendar`) under the Document Manager interface.

### Key Functional Requirements & Resolved Design Decisions

1. **Source Selection & OAuth Authorization Flow**
   - Add a 3rd radio button `Google Calendar` under the `TYPE` selector in `templates/partials/document_list.html`.
   - **OAuth Redirect Flow:** Performs a standard full-page redirect to `/rag/google/oauth2callback/` which exchanges the authorization code for tokens using `git_ignore/client_secret_*.json`, stores OAuth access/refresh tokens in `GoogleCalendarSource`, and redirects back to the Document Manager UI (`/rag/documents/<store_id>/`).

2. **Sync Preferences Configuration**
   - **Multi-Calendar Selection:** Multi-select checkboxes allowing users to select multiple sub-calendars simultaneously (e.g., Primary + Work + Personal).
   - **Sync Window Range:**
     - `Lookback Days (Past)`: Default 30 days.
     - `Lookahead Days (Future)`: Default 365 days.

3. **First-Time Background Sync & Non-Blocking Workflow**
   - **Background Worker:** Uses a lightweight `threading.Thread` worker to perform the non-blocking 365-day API fetch and vector processing.
   - **HTMX Live Polling:** HTMX polls the status endpoint (`/rag/projects/<store_id>/google-calendar/status/`) using `hx-trigger="every 2s"` to update progress (`"Setting up your calendar..."` -> `"Setup complete. Syncing [N] events..."` -> progress bar -> `"All events indexed"`).
   - **Local Markdown Storage:** All generated calendar notes are saved strictly inside `rag_data/<store_id>/Calendar/` as structured Markdown files containing YAML frontmatter (`event_id`, `start_time`, `end_time`, `organizer`, `attendees`, `location`, `status`).
   - Store Google Calendar API `syncToken` in database for efficient incremental delta updates.

4. **Action Controls**
   - **Sync:** Calls Google Calendar API with `syncToken` (or 24-hour lookback), compares returned events with tracking table, creates/updates local Markdown notes in `rag_data/<store_id>/Calendar/`, and marks modified notes as `PENDING`. Displays HTMX status badge: `"Discovered X events total (Y pending indexing)"`.
   - **Index New Events:** Queries `PENDING` notes, sanitizes Markdown, generates 768-dimensional embeddings using `gemini-embedding-001`, saves to `PGVectorStore`, and updates status badge to `INDEXED`.
   - **Full Re-Index:** Wipes project calendar vectors in `PGVectorStore`, re-fetches full 365-day range, overwrites local Markdown notes, and batch re-embeds all notes from scratch with confirmation prompt.

---

## 2. Common & Required Commands

### Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Local Development Server
```bash
./run.sh
# or
python manage.py runserver
```

### Automated Unit Testing
```bash
DJANGO_ENV=testing .venv/bin/pytest Testing/unit/documents/ --tb=short
```

---

## 3. Project Structure & Key Files

```
src/apps/documents/
├── models.py                     # GoogleCalendarSource & GoogleCalendarEvent models
├── google_calendar_services.py  # OAuth token exchange, Calendar API client, Markdown builder & worker
├── views.py                      # OAuth callback, preference handlers, sync & index endpoints
└── urls.py                       # Route definitions for calendar OAuth & HTMX actions

templates/partials/
├── document_list.html            # TYPE radio toggle updated with 'Google Calendar'
└── google_calendar_section.html  # Preferences form, progress banner, action buttons & event table

Testing/unit/documents/
├── test_google_calendar_models.py
├── test_google_calendar_services.py
└── test_google_calendar_views.py
```

---

## 4. Code Style & Guidelines

- **Architecture:** Keep view functions thin; isolate Google Calendar API interactions, token refreshing, and Markdown generation inside `google_calendar_services.py`.
- **Formatting:** PEP 8 compliance, snake_case for functions/variables, explicit Python type hints (`def sync_calendar_events(source: GoogleCalendarSource) -> dict:`).
- **Asynchronous Execution:** Use `threading.Thread` worker tasks updating model progress fields, polled by HTMX using `hx-trigger="every 2s"`.
- **Frontend Interactivity:** Prefer HTMX partial updates (`hx-post`, `hx-target`, `hx-swap="outerHTML"`, `hx-indicator`) over full page reloads or custom JavaScript.

---

## 5. Testing Strategy

### Unit Tests (`Testing/unit/documents/`)
1. **`test_google_calendar_models.py`**: Model constraints, choices (`PENDING`, `INDEXED`, `FAILED`), and ForeignKeys.
2. **`test_google_calendar_services.py`**:
   - OAuth authorization URL building & token exchange mocking.
   - Conversion of Google Calendar API JSON payload into valid YAML frontmatter Markdown.
   - Incremental delta sync utilizing `syncToken`.
3. **`test_google_calendar_views.py`**:
   - HTMX endpoints (`set_source_type`, `google_calendar_save_preferences`, `google_calendar_sync`, `google_calendar_index_new`).
   - Rendering of live progress bars and event status tables.

---

## 6. Guardrails & Boundaries

### 👍 Dos
- Do automatically execute `makemigrations` and `migrate` whenever database models change.
- Do handle `syncToken` expiration (`410 Gone`) by falling back gracefully to a full sync.
- Do refresh expired OAuth access tokens automatically using stored refresh tokens.
- Do run unit tests after code modifications to ensure 100% test pass rate.

### ❓ Ask Before
- Ask before modifying OAuth client credentials stored in `git_ignore/`.
- Ask before changing shared database table schemas for existing RAG vector stores.

### 👎 Don'ts
- Don't block HTTP main thread when fetching 365 days of event data from Google API.
- Don't log unencrypted OAuth access/refresh tokens or client secrets to stdout or log files.
- Don't hardcode absolute URLs or API keys in source files.