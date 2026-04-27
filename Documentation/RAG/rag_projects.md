# Postgres RAG Projects

This document describes the functionality that currently exists for Postgres RAG projects in the application.

## Overview

The product currently supports three project types:

- Local projects
- Google File Search projects
- Postgres RAG projects

Postgres RAG projects are the project type used when a user wants document indexing and retrieval backed by PostgreSQL content storage together with txtai embeddings-based search.

## What A Postgres RAG Project Currently Supports

The current implementation satisfies the following functional requirements.

### 1. A user can create a new Postgres RAG project

Implemented behavior:

- The project creation flow accepts `storage_type=postgres`.
- When selected, the server creates a Django `Project` record with:
	- a generated `project_id` starting with `postgres_`
	- the user-supplied `display_name`
	- `storage_type='postgres'`
	- the authenticated user as owner when available
- The generated `project_id` is the stable identifier used by the UI and backend flows for this project.

Operational note:

- The `Project` model still contains older storage type choices, but the active project creation and lookup code uses `postgres` as the live storage type for Postgres RAG projects.

Missing functionality:

- The `Project` model choices are not yet aligned with the active `postgres` storage type used by the views.
- There is no dedicated validation or UI-level confirmation that the Postgres-specific environment and optional AI dependencies are available when the project is created.
- Project deletion does not currently clean up the persisted per-project ANN index or any Postgres-backed txtai content for the project.

### 2. A user can add custom prompts to specific RAG projects

Implemented behavior:

- The prompt management flow accepts a `store_id`, which for Postgres RAG projects is the project's `project_id`.
- A custom prompt can be saved and later retrieved for that specific RAG project.
- During chat, if the client does not send a prompt explicitly, the chat flow loads the saved prompt for that `store_id` and uses it as the system prompt context.

Current persistence detail:

- Prompts are currently stored by `store_id` in `configuration/prompts.json` through `src/prompt_storage.py`.
- The `SystemPrompt` Django model exists, but the active Postgres RAG prompt flow is still using the file-backed prompt storage helper rather than the model.

Missing functionality:

- Prompt persistence is not yet stored in the Django `SystemPrompt` model, so prompt management is not integrated with the main database model layer.
- There is no project ownership or authorization check inside the prompt storage helper itself; prompts are keyed only by `store_id`.
- There is no prompt versioning, audit history, or fallback management for prompt changes.
- There is no validation layer for prompt length, content rules, or prompt update conflicts.

### 3. A user can upload documents that are indexed using Postgres embeddings and txtai

Implemented behavior:

- The document upload flow detects Postgres RAG projects from `store_id` values starting with `postgres_`.
- Uploaded files are first written to a temporary file on disk.
- The upload flow creates a `PostgresRAGEngine` for the target project and calls `index_document(filepath, filename)`.
- `PostgresRAGEngine`:
	- extracts text from supported file types
	- currently supports `.pdf`, `.txt`, and `.md`
	- builds a txtai `Embeddings` index configured with:
		- `path="sentence-transformers/nli-mpnet-base-v2"`
		- `content=<postgres connection url>` when Postgres environment variables are present
- The content backend stores text in PostgreSQL.
- The ANN index is persisted per project under `rag_data/indices/<project_id>` so the index survives restarts.
- After successful indexing, the Django `Document` record for that project is created or updated with:
	- `document_name`
	- `display_name`
	- `state='INDEXED'`
	- `indexed_at`

Important implementation detail:

- If the required database environment variables are missing, the engine falls back to a local SQLite txtai content store instead of PostgreSQL. In other words, true Postgres-backed storage depends on the production environment being configured with the expected database variables.

Missing functionality:

- The requirement says documents should be indexed using Postgres embeddings and txtai, but the current implementation silently falls back to SQLite instead of failing fast when Postgres is not configured.
- There is no explicit health check at upload time to confirm that txtai is actually using PostgreSQL rather than the fallback SQLite content store.
- Supported document types are limited to PDF, TXT, and Markdown; broader file support is not implemented.
- There is no background job or queue for indexing, so uploads and indexing happen inline in the request cycle.
- There is no robust failure reporting in the `Document` model for indexing exceptions beyond returning an error response.
- There is no implemented cleanup path that removes indexed vectors/content when a Postgres RAG document is deleted.

### 4. A user can chat with a chatbot that uses Google Gemini and the embeddings created before for the specific project

Implemented behavior:

- The chat flow detects Postgres RAG projects from `store_id` values beginning with `postgres_`.
- For a Postgres RAG project, chat creates a `PostgresRAGEngine` scoped to that project.
- The engine queries the project's txtai index and retrieves the top matching chunks for the user's question.
- The retrieved document text is assembled into a context block.
- The final answer is generated with Google Gemini using the `google-genai` client and the model `gemini-2.5-flash-lite`.
- If a custom prompt has been saved for the project, that prompt is prepended as the base instruction before the user question and retrieved document context are sent to Gemini.
- The response returned to the user is therefore project-specific in two ways:
	- it searches only the embeddings index loaded for that project's `project_id`
	- it applies the prompt saved for that same project

Fallback behavior:

- If no indexed documents are found for the project, the engine returns a message telling the user that no indexed documents are available yet.

Missing functionality:

- There is no explicit readiness check that blocks chat when the optional AI dependencies or Gemini credentials are missing; failures happen at runtime when the engine is constructed or queried.
- There is no token budgeting, truncation strategy, or chunk-selection policy beyond taking the first matching text slices returned by txtai.
- There is no citation rendering or structured source attribution in the user-facing response, even though source nodes are collected internally.
- There is no conversation memory beyond the per-request prompt and retrieved context; multi-turn retrieval refinement is not implemented.
- There is no authorization or ownership check in the chat flow to ensure the requested Postgres RAG project belongs to the current authenticated user.

## Current End-To-End Flow For Postgres RAG Projects

1. The user creates a project with `storage_type=postgres`.
2. The backend generates a `postgres_*` project identifier and stores the project in Django.
3. The user optionally saves a custom prompt for that project.
4. The user uploads supported documents.
5. The upload flow extracts text and indexes it with txtai for that project.
6. The text content is stored through the txtai content backend and the per-project ANN index is saved to disk.
7. The user opens chat for the same project.
8. The chat flow loads the same project-specific prompt and project-specific txtai index.
9. Matching document content is retrieved and sent to Google Gemini to generate the final answer.

## Current Caveats

- Postgres RAG features require the optional AI dependencies to be installed from `requirements-ai.txt`.
- Prompt persistence is currently file-backed rather than stored through the `SystemPrompt` model.
- Postgres-backed txtai content storage only happens when the expected Postgres environment variables are configured; otherwise the engine falls back to SQLite.
- Supported upload formats in the current engine are limited to PDF, text, and Markdown files.

## Summary Of Missing Functionality

- Align the Django `Project` model choices and deletion behavior with the active `postgres` project implementation.
- Move RAG prompt persistence from the JSON file helper into the `SystemPrompt` model.
- Remove the silent SQLite fallback for Postgres RAG uploads when PostgreSQL is required.
- Add indexing lifecycle handling such as validation, background processing, cleanup, and richer failure tracking.
- Add chat-layer safeguards for ownership, dependency readiness, Gemini configuration, and better source/citation handling.
