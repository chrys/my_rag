# My RAG

My RAG is a Django 6 application for managing retrieval-augmented generation workflows across multiple storage backends.

It exposes:
- A server-rendered dashboard under `/rag/`
- A Django REST Framework API under `/api/`

The application currently supports three project/document backends:
- `google`
- `local`
- `postgres`

## Who This README Is For
- Users and developers who need to run or extend the project
- AI agents that need a fast, accurate entry point before making changes

For agent-specific working rules, see `AGENTS.md` and `project-context.md`.

## Project Overview
- `apps/chat/`: chat views, APIs, models, and templates
- `apps/projects/`: project creation, listing, deletion, and project settings flows
- `apps/documents/`: document upload, indexing, listing, and deletion
- `apps/evaluate/`: evaluation views and APIs
- `apps/api/`: shared DRF routing and API endpoints
- `my_rag_project/`: Django settings, root URLs, ASGI, and WSGI
- `src/`: shared integrations for Google File Search, local storage, PostgreSQL RAG, and prompt storage
- `templates/`: shared templates and partials
- `Testing/unit/`: primary pytest test suites
- `Testing/regression/`: regression tests for previously fixed production bugs

## Architecture Notes
- The dashboard uses Django templates and app partials rather than a separate SPA frontend.
- Projects and documents are tracked in Django models, even when the backing storage is external.
- Some migration-era compatibility paths still exist from an earlier Flask implementation.
- Root routing is split in `my_rag_project/urls.py`:
  - `/rag/` for the dashboard
  - `/api/` for programmatic access

## Key Conventions
- Use `Project.project_id` as the stable identifier in routes, frontend interactions, and most application lookups.
- Do not substitute Django primary keys into route or frontend flows unless the surrounding implementation already expects them.
- For Google-backed projects, `external_store_id` is only for calls to the Google File Search backend.
- `external_store_id` may contain slashes, so it is not safe as a URL path lookup.
- Current active storage types are `local`, `google`, and `postgres`.
- Older comments or tests may still mention `rag`; treat that as legacy wording unless the current code path explicitly uses it.

## Requirements
- Python 3.11+ is recommended
- A local virtual environment at `.venv/`
- Environment variables in `.env` for any external services you use

Main Python dependencies include:
- Django 6
- Django REST Framework
- django-cors-headers
- llama-index
- txtai
- google-genai
- psycopg2-binary

## Local Setup
1. Create and activate a virtual environment.
2. Install dependencies.
3. Ensure your `.env` is configured for the services you want to use.
4. Run the Django server.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py runserver
```

Open the app at `http://127.0.0.1:8000/rag/`.

## Settings And Environments
Settings are selected through `DJANGO_ENV` and resolved from `my_rag_project/settings/`.

Supported values in this repo:
- `development`
- `testing`
- `production`

Examples:

```bash
DJANGO_ENV=development python manage.py runserver
DJANGO_ENV=testing pytest Testing/unit -v
```

Important detail:
- `pytest.ini` points at `my_rag_project.settings`, but the active settings module still depends on `DJANGO_ENV`.
- Use `DJANGO_ENV=testing` when you want the test configuration, including the in-memory SQLite database.

## Testing
Run focused tests first.

Common commands:

```bash
DJANGO_ENV=testing pytest Testing/unit -v
DJANGO_ENV=testing pytest Testing/unit/projects -v
DJANGO_ENV=testing pytest Testing/unit/documents -v
DJANGO_ENV=testing pytest Testing/regression -v
```

Regression coverage is especially important when changing:
- project creation or deletion
- document upload or deletion
- prompt saving
- routing that touches project identifiers

See `Testing/regression/README.md` for historical bug coverage.

## Data Ownership And Safety
- Django records are the source of truth for projects and documents.
- Preserve user ownership filtering where it already exists.
- Some legacy local-storage fallbacks remain for backward compatibility. Do not remove them unless the task is explicitly about deprecating migration support.

## Useful Files To Read First
- `project-context.md`: repo-specific guidance for AI agents and developers
- `AGENTS.md`: workspace behavior rules for AI agents
- `my_rag_project/urls.py`: root routing and app registration
- `my_rag_project/settings/base.py`: installed apps, middleware, and defaults
- `apps/projects/views.py`: project creation and identifier behavior
- `apps/documents/views.py`: upload and deletion flows across storage backends
- `Documentation/USER_MANAGEMENT.md`: authentication and ownership rules
- `Testing/regression/README.md`: prior regressions and what caused them

## Deployment Notes
- Production configuration lives under `live_configuration/`.
- Deployment automation currently includes `deploy.sh` and a systemd unit for Gunicorn.
- Production uses `DJANGO_ENV=production`.

## Documentation
- `Documentation/API/README.md`: API overview
- `Documentation/Google_File_Search/README.md`: Google File Search notes
- `Documentation/local_projects/README.md`: local project storage notes
- `Documentation/USER_MANAGEMENT.md`: user isolation and authentication behavior

## For AI Agents
Before making assumptions or editing code:
- Read `AGENTS.md`
- Read `project-context.md`
- Match existing patterns in the target app before introducing abstractions
- Prefer focused tests over broad runs
- Be careful with `project_id`, `external_store_id`, and storage backend branching