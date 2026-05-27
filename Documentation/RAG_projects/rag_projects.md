# Postgres RAG Projects

This document describes the current behavior for Postgres RAG projects.

## Overview

The product supports three project types:

- Local projects
- Google File Search projects
- Postgres RAG projects

Postgres RAG projects provide project-scoped document indexing and retrieval backed by PostgreSQL (PGVector), LlamaIndex, Gemini embeddings (`models/text-embedding-004`), and Gemini LLM answer generation (`models/gemini-2.5-flash-lite`).

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
- Prompt lookup is keyed by the owning `Project` record.
- When a chat request does not pass an explicit system prompt, the saved project prompt is loaded automatically.
- Empty prompt behavior falls back to an empty string.
- Prompt access is blocked for non-owners when the project has an owner.

### 3. Document upload and indexing

Implemented behavior:

- The upload flow detects Postgres RAG projects from `project_id` values beginning with `postgres_` (or `rag_`).
- Supported file types are `.pdf`, `.txt`, and `.md`.
- Unsupported file types are rejected in the request layer with an explicit `400` response before indexing begins.
- Successful indexing creates or updates the Django `Document` record with:
	- `document_name`
	- `display_name`
	- `state='INDEXED'`
	- `indexed_at`
	- cleared `error_message`
- Failed indexing creates or updates the Django `Document` record with `state='FAILED'` and the error.

Readiness and storage behavior:

- Postgres RAG indexing utilizes `llama-index-core`, `llama-index-vector-stores-postgres`, `llama-index-embeddings-gemini`, and `llama-index-llms-gemini` specified in `requirements-ai.txt`.
- Embeddings are computed via `GeminiEmbedding` (`models/text-embedding-004`) and stored in a PostgreSQL database using `PGVectorStore`.
- The database table for a project's vector store is dynamically named based on the `store_id` (e.g., `rag_project_<store_id>`).

### 4. Chat behavior

Implemented behavior:

- The chat flow detects Postgres RAG projects from `project_id` values beginning with `postgres_` (or `rag_`).
- Chat access is blocked for non-owners when the project has an owner.
- Chat uses LlamaIndex's `VectorStoreIndex` connected to the `PGVectorStore` to retrieve relevant documents.
- Chat uses the saved `SystemPrompt` content when no explicit prompt is passed.
- Gemini answer generation uses the `Gemini` LLM class from LlamaIndex with `models/gemini-2.5-flash-lite`.

Response shape:

- The JSON chat response includes `source_documents`, extracted from the metadata of LlamaIndex's source nodes.
- The HTMX chat response renders a `Sources` block containing the same document names.

### 5. Cleanup behavior

Implemented behavior:

- Deleting a Postgres RAG document removes the matching entry from the Postgres vector store and the Django database.
- Deleting a Postgres RAG project drops the associated vector table from the Postgres database.
- Cleanup is scoped by `project_id` and the project's own `Document` records.

## Current End-To-End Flow

1. The user creates a project with `storage_type=postgres`.
2. The backend creates a Django `Project` record using a stable `postgres_*` project id.
3. The user optionally saves a custom project prompt.
4. The user uploads a supported document.
5. The upload flow validates the file type, passes the file to `LlamaIndexIngestionPipeline`, embeds the content via `GeminiEmbedding`, stores vectors in PGVector, and updates the Django `Document` record state.
6. The user opens chat for the same project.
7. The chat flow loads the `VectorStoreIndex` from the project's Postgres table and queries it with the `Gemini` LLM.
8. Matching content is sent to the LLM to generate the answer.
9. The response includes document source attribution.
10. If the user deletes a document or the whole project, the Postgres vector entries and Django database records are cleaned up for that scope.

## Operational Notes

- Postgres RAG features require the specific LlamaIndex dependencies defined in `requirements-ai.txt`.
- The full query path (indexing + chat) requires `GOOGLE_API_KEY`.
- LlamaIndex uses `models/text-embedding-004` for vector embeddings.
- LlamaIndex uses `models/gemini-2.5-flash-lite` for LLM generation.
- The system must be connected to a valid PostgreSQL database (`default` database in Django settings) with PGVector enabled.
