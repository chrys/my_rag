# Task Checklist: Google Calendar Integration & Sync Engine

---

- [X] Task 1: Create GoogleCalendarSource & GoogleCalendarEvent Django Models
  - Acceptance: Models defined with OneToOne relationship to Project, choices for status (`PENDING`, `INDEXED`, `FAILED`), tokens, lookback/lookahead days, syncToken, and progress metrics. Database migrations generated and applied.
  - Verify: `DJANGO_ENV=testing .venv/bin/pytest Testing/unit/documents/test_google_calendar_models.py --tb=short`
  - Files: `src/apps/documents/models.py`, `Testing/unit/documents/test_google_calendar_models.py`

- [X] Task 2: Implement Google Calendar API & Markdown Sync Service (`google_calendar_services.py`)
  - Acceptance: OAuth token exchange using `git_ignore/client_secret_*.json`, token auto-refreshing, Calendar event fetching, Markdown file builder with YAML frontmatter saved under `rag_data/<store_id>/Calendar/`, and non-blocking `threading.Thread` background sync worker.
  - Verify: `DJANGO_ENV=testing .venv/bin/pytest Testing/unit/documents/test_google_calendar_services.py --tb=short`
  - Files: `src/apps/documents/google_calendar_services.py`, `Testing/unit/documents/test_google_calendar_services.py`

- [X] Task 3: Implement OAuth Callback, Preference Settings, Sync, and Index Views
  - Acceptance: Handles `/rag/google/oauth2callback/` full-page redirect, save preferences, sync events, index new events, and status polling view (`hx-trigger="every 2s"`).
  - Verify: `DJANGO_ENV=testing .venv/bin/pytest Testing/unit/documents/test_google_calendar_views.py --tb=short`
  - Files: `src/apps/documents/views.py`, `src/apps/documents/urls.py`, `src/apps/api/api_urls.py`, `Testing/unit/documents/test_google_calendar_views.py`

- [X] Task 4: Implement HTMX Frontend Components (`google_calendar_section.html` & `document_list.html`)
  - Acceptance: Radio button toggle updated (`TYPE: Document | Obsidian | Google Calendar`), renders OAuth connect button if unauthenticated, multi-select calendar checkboxes, sync window inputs, action buttons (`Sync`, `Index New Events`, `Full Re-Index`), live progress bar, and events status table.
  - Verify: Load Document Manager UI in browser, test HTMX state switching, and run pytest suite `DJANGO_ENV=testing .venv/bin/pytest Testing/unit/documents/ --tb=short`.
  - Files: `templates/partials/document_list.html`, `templates/partials/google_calendar_section.html`

- [X] Task 5: End-to-End Verification & Documentation Update
  - Acceptance: All 365+ unit tests pass 100%, background worker runs non-blocking syncs, and changelog is recorded in `Design/Aug-26/aug1-changelog.md`.
  - Verify: `DJANGO_ENV=testing .venv/bin/pytest Testing/unit Testing/regression --tb=short -q`
  - Files: `Design/Aug-26/aug1-changelog.md`
