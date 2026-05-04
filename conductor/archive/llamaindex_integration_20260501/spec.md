# Specification: LlamaIndex Integration for RAG Projects

## Overview
This track focuses on integrating LlamaIndex into the "My RAG" application to manage document indexing, embedding generation, and retrieval exclusively for local RAG projects. Google File Search projects will remain unaffected by this change.

## Functional Requirements

### FR-1: LlamaIndex Ingestion Pipeline
- **FR-1.1:** LlamaIndex shall be used as the default pipeline to handle document parsing, chunking, and node extraction when a new file is uploaded to a RAG-type project.
- **FR-1.2:** The pipeline shall use the `gemini-embedding-001` model to generate embeddings for all document chunks.
- **FR-1.3:** The generated embeddings and document nodes shall be stored and indexed using a PostgreSQL Vector storage backend managed via LlamaIndex.

### FR-2: Chat Retrieval Flow
- **FR-2.1:** When a user navigates to the Chat tab and selects a RAG project, LlamaIndex shall be utilized as the primary query engine.
- **FR-2.2:** When a user submits a query (via the Send button or Enter key), the query shall be passed to the LlamaIndex retriever.
- **FR-2.3:** The retriever shall execute the search against the PostgreSQL Vector index using the user's prompt and any associated project-level system prompts.

## Non-Functional Requirements
- **Performance:** The shift to LlamaIndex should not noticeably degrade the upload/indexing speed or the chat response latency.
- **Modularity:** LlamaIndex configurations (LLM, Embedding Model, Storage Context) must be encapsulated to allow future swaps or updates.

## Acceptance Criteria
1. Uploading a document to a RAG project successfully triggers LlamaIndex parsing and indexing.
2. Embeddings are verifiable in the PostgreSQL database using the `gemini-embedding-001` model.
3. Chat queries directed at a RAG project successfully retrieve relevant context and return an LLM response generated via LlamaIndex.
4. Google File Search projects continue to function exactly as they did prior to this integration.

## Out of Scope
- Migrating or integrating Google File Search into LlamaIndex.
- Replacing SQLite as the primary application database for users/projects.
- Building a custom UI exclusively for LlamaIndex graph visualization.