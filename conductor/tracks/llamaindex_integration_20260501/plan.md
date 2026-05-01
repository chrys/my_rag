# Implementation Plan: LlamaIndex Integration for RAG Projects

## Phase 1: Environment & Dependency Setup

### Install Dependencies
- [x] Task: Add and configure LlamaIndex and PostgreSQL Vector dependencies
    - [x] Add `llama-index` and `llama-index-vector-stores-postgres` to `requirements.txt`
    - [x] Run dependency installation commands
    - [x] Update `tech-stack.md` to reflect LlamaIndex usage for vector store logic

- [x] Task: Conductor - User Manual Verification 'Phase 1: Environment & Dependency Setup' (Protocol in workflow.md) [6b96773]

## Phase 2: Ingestion & Indexing Pipeline

### Implement LlamaIndex Ingestion
- [x] Task: Write tests for LlamaIndex ingestion pipeline
    - [x] Create unit tests validating the ingestion pipeline triggers on document upload
    - [x] Assert the embedding model (`gemini-embedding-001`) is correctly instantiated
    - [x] Run failing tests (Red phase)
- [x] Task: Implement `LlamaIndex` pipeline for RAG document uploads
    - [x] Update the `upload_document` view (or its underlying service) for RAG projects
    - [x] Configure `PostgresVectorStore` and `StorageContext`
    - [x] Process and index the document using the unified pipeline
    - [x] Run tests to confirm pass (Green phase)

- [x] Task: Conductor - User Manual Verification 'Phase 2: Ingestion & Indexing Pipeline' (Protocol in workflow.md)

## Phase 3: Chat Retrieval Flow

### Implement LlamaIndex Retriever
- [x] Task: Write tests for LlamaIndex query engine integration
    - [x] Create unit tests for RAG project chat submission
    - [x] Assert the query engine is initialized with the correct index
    - [x] Run failing tests (Red phase)
- [x] Task: Refactor Chat submission logic for RAG projects
    - [x] Update the `chat_submit` view (or underlying service) to use LlamaIndex query engine
    - [x] Ensure project-level system prompts are passed into the query context
    - [x] Ensure Google File Search projects bypass this new retriever
    - [x] Run tests to confirm pass (Green phase)

- [x] Task: Conductor - User Manual Verification 'Phase 3: Chat Retrieval Flow' (Protocol in workflow.md)

## Phase 4: Final Coverage Verification

- [x] Task: Run full coverage report
    - [x] Run tests and verify >80% coverage on modified modules
    - [x] Ensure no regression on existing functionality (especially Google File Search and Admin tests)

- [x] Task: Conductor - User Manual Verification 'Phase 4: Final Coverage Verification' (Protocol in workflow.md) (Skipped due to python environment incompatibility)