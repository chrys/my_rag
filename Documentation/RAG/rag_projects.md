# Postgres RAG Projects

This document describes the shipped Apr2 behavior for Postgres RAG projects.

## Overview

The product supports three project types:

- Local projects
- Google File Search projects
- Postgres RAG projects

Postgres RAG projects provide project-scoped document indexing and retrieval backed by file-based numpy embedding storage, Gemini embedding API search (gemini-embedding-001), and Gemini answer generation (gemini-2.5-flash-lite).

## Current Postgres RAG Behavior

### 1. Project creation

Implemented behavior:

- The project creation flow accepts `storage_type=postgres`.
- Creating a Postgres RAG project stores a Django `Project` record with:
	- a generated `project_id` starting with `postgres_`
	- the requested `display_name`
	- `storage_type='postgres'`
	- the authenticated user as owner when available
- The generated `project_id` is the stable identifier used by prompt, document, chat, and cleanup flows.

### 2. Project prompt management

Implemented behavior:

- Postgres RAG prompt reads and writes use the Django `SystemPrompt` model.
- Prompt lookup is keyed by the owning `Project` record rather than the legacy JSON prompt helper.
- When a chat request does not pass an explicit system prompt, the saved project prompt is loaded automatically.
- Empty prompt behavior falls back to an empty string.
- Prompt access is blocked for non-owners when the project has an owner.

### 3. Document upload and indexing

Implemented behavior:

- The upload flow detects Postgres RAG projects from `project_id` values beginning with `postgres_`.
- Supported file types for Apr2 are `.pdf`, `.txt`, and `.md`.
- Unsupported file types are rejected in the request layer with an explicit `400` response before indexing begins.
- Successful indexing creates or updates the Django `Document` record with:
	- `document_name`
	- `display_name`
	- `state='INDEXED'`
	- `indexed_at`
	- cleared `error_message`
- Failed indexing creates or updates the Django `Document` record with:
	- `state='FAILED'`
	- `indexed_at=None`
	- a useful `error_message`

Readiness and storage behavior:

- Postgres RAG indexing requires `google-genai` and `numpy` (both in `requirements.txt` and `requirements-prod.txt`). No optional `requirements-ai.txt` dependencies are needed.
- Postgres RAG indexing does **not** require PostgreSQL configuration — embeddings and content are stored as files.
- Each project's index is stored under `rag_data/indices/<project_id>/` as two files:
  - `embeddings.npy` — float32 numpy array of shape `(N, 768)`
  - `content.json` — list of `{"id": document_name, "text": ...}` records
- Retrieval uses cosine similarity (numpy) with no FAISS or ANN dependency.
- Indexed content uses stable `document_name` ids so later cleanup can target the correct records.

### 4. Chat behavior

Implemented behavior:

- The chat flow detects Postgres RAG projects from `project_id` values beginning with `postgres_`.
- Chat access is blocked for non-owners when the project has an owner.
- Chat uses the project-scoped numpy embedding index for retrieval (cosine similarity, top-k=3).
- Chat uses the saved `SystemPrompt` content when no explicit prompt is passed.
- Gemini answer generation uses the `google-genai` client with `gemini-2.5-flash-lite`.
- When no indexed documents are available, the engine returns a clear no-documents response.
- User-facing Postgres RAG responses expose document-name-only attribution for retrieved sources.

Response shape:

- The JSON chat response includes `source_documents`, a deduplicated list of document names.
- The HTMX chat response renders a `Sources` block containing the same document names.
- Score, snippet, and richer citation metadata are intentionally not rendered in Apr2.

### 5. Cleanup behavior

Implemented behavior:

- Deleting a Postgres RAG document removes the matching entry from `embeddings.npy` and `content.json` by `document_name` and re-saves both files.
- Deleting a Postgres RAG project removes the entire `rag_data/indices/<project_id>/` directory (pure filesystem, no API call needed).
- Cleanup is scoped by `project_id` and the project's own `Document` records.
- Delete-only cleanup paths do not require Gemini client initialization.

## Current End-To-End Flow

1. The user creates a project with `storage_type=postgres`.
2. The backend creates a Django `Project` record using a stable `postgres_*` project id.
3. The user optionally saves a custom project prompt.
4. The user uploads a supported document.
5. The upload flow validates the file type, embeds the content via `gemini-embedding-001` (`RETRIEVAL_DOCUMENT` task type), and updates the `Document` record state.
6. The per-project index (`embeddings.npy` + `content.json`) is persisted under `rag_data/indices/<project_id>/`.
7. The user opens chat for the same project.
8. The chat flow loads the same project prompt and the same project numpy index.
9. Matching content is sent to Gemini to generate the answer.
10. The response includes document-name-only source attribution.
11. If the user deletes a document or the whole project, the indexed Postgres RAG artifacts are cleaned up for that scope.

## Operational Notes

- Postgres RAG features require `google-genai` and `numpy` — both listed in `requirements.txt` and `requirements-prod.txt`. `requirements-ai.txt` has no remaining entries.
- The full query path (indexing + chat) requires `GOOGLE_API_KEY`.
- Cleanup (document and project deletion) is pure filesystem — no API key needed.
- Supported upload formats are PDF, plain text, and Markdown files.
- Embedding model: `gemini-embedding-001`, output dimension 768, task type `RETRIEVAL_DOCUMENT` for indexing and `RETRIEVAL_QUERY` for chat.
- Indexes created under the old txtai format are incompatible. Documents must be re-uploaded to regenerate indexes in the current `.npy` + `.json` format.
- To uninstall the no-longer-needed AI packages on the VPS:
  ```bash
  pip uninstall -y txtai torch torchvision torchaudio transformers sentence-transformers \
    faiss-cpu huggingface-hub tokenizers safetensors accelerate
  ```
  This frees approximately 2–3 GB of disk space and eliminates the OOM risk at startup.

## Summary

Apr2 (updated Apr 29) ships Postgres RAG as a project-scoped flow with:

- Django-model-backed prompt persistence
- ownership checks for prompt and chat access
- explicit readiness failures for missing dependencies and configuration
- file-based embedding storage (numpy `.npy` + JSON) with Gemini embedding API
- cosine similarity retrieval — no FAISS or ANN dependency
- explicit document success and failure state tracking
- cleanup for document and project deletion (pure filesystem, no API needed)
- document-name-only source attribution in chat responses
