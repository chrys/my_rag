# Project Context

## What This Repository Is
- It serves two main surfaces:
  - HTML dashboard and auth flows under `/rag/`
  - DRF API endpoints under `/api/`
- The product supports multiple storage backends for projects and documents: `google`, `local`, and `postgres`.

## Key Project Structure
- `my_rag_project/`: Django project configuration, settings package, root URL routing.
- `apps/chat/`: chat UI, chat APIs, chat data models.
- `apps/projects/`: project creation, listing, deletion, and project-scoped settings.
- `apps/documents/`: document upload, listing, deletion, and indexing state.
- `apps/evaluate/`: evaluation UI and APIs.
- `apps/api/`: DRF routing and API views across the product.
- `src/`: shared backend integration code for local RAG, PostgreSQL RAG, Google File Search, and prompt/local project storage.
- `templates/`: shared Django templates and partials used by the dashboard.
- `Testing/unit/`: primary pytest unit test suite.
- `Testing/regression/`: regression coverage for previously fixed bugs.

## Settings And Environment
- Activate the local environment with `source .venv/bin/activate`.
- Settings are selected by `DJANGO_ENV` through `my_rag_project/settings/`.
- Valid environment values used in the repo are:
  - `development`
  - `testing`
  - `production`
- `pytest.ini` points to `my_rag_project.settings`, but the actual settings variant still depends on `DJANGO_ENV`.
- Use `DJANGO_ENV=testing` when running tests that should use the test settings and in-memory SQLite database.

## Common Commands
- Install dependencies: `pip install -r requirements.txt`
- Run the app locally: `python manage.py runserver`
- Run all unit tests: `DJANGO_ENV=testing pytest Testing/unit -v`
- Run regression tests: `DJANGO_ENV=testing pytest Testing/regression -v`
- Run a focused app test suite: `DJANGO_ENV=testing pytest Testing/unit/projects -v`

## Project-Specific Conventions
- Use `Project.project_id` as the stable identifier for routes, frontend interactions, and most UI/API lookups.
- Do not replace route or frontend identifiers with Django primary keys unless the surrounding code already does so intentionally.
- For Google-backed projects, `external_store_id` is only for calls to the Google File Search backend.
- `external_store_id` may contain slashes, so it should not be used as a URL path lookup value.
- Active `storage_type` values in current code are `local`, `google`, and `postgres`.
- Older code, comments, or tests may still mention `rag`; treat that as legacy terminology unless the current implementation explicitly uses it.

## Data And Ownership Rules
- Django database records are the source of truth for projects and documents.
- Some views still contain legacy fallbacks to local storage for backward compatibility; preserve them unless the task is explicitly about removing migration-era behavior.
- User ownership matters: project and document queries should remain scoped to the authenticated user where that behavior already exists.

## Known Pitfalls
- The repo still contains migration-era compatibility code from an earlier Flask-based implementation.
- There is a naming mismatch between generic agent guidance and this repo: tests live under `Testing/`, not `Tests/`.
- Google File Search regressions have previously come from confusing `project_id` with `external_store_id`.
- PostgreSQL-backed projects should use the `postgres` storage type in active code paths, even if some legacy notes still say `rag`.

## Files Worth Checking Before Risky Changes
- `my_rag_project/urls.py`: root route prefixes and app wiring.
- `my_rag_project/settings/base.py`: installed apps, middleware, templates, and default database behavior.
- `apps/projects/views.py`: project identifier usage and storage backend branching.
- `apps/documents/views.py`: document upload/delete flows across local, Google, and PostgreSQL backends.
- `Testing/regression/README.md`: historical bugs that should not be reintroduced.