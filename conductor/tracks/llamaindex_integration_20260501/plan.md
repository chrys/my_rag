# Implementation Plan: LlamaIndex Integration for RAG Projects

## Phase 1: Environment & Dependency Setup

### Install Dependencies
- [ ] Task: Add and configure LlamaIndex and PostgreSQL Vector dependencies
    - [ ] Add `llama-index` and `llama-index-vector-stores-postgres` to `requirements.txt`
    - [ ] Run dependency installation commands
    - [ ] Update `tech-stack.md` to reflect LlamaIndex usage for vector store logic

- [ ] Task: Conductor - User Manual Verification 'Phase 1: Environment & Dependency Setup' (Protocol in workflow.md)

## Phase 2: Ingestion & Indexing Pipeline

### Implement LlamaIndex Ingestion
- [ ] Task: Write tests for LlamaIndex ingestion pipeline
    - [ ] Create unit tests validating the ingestion pipeline triggers on document upload
    - [ ] Assert the embedding model (`gemini-embedding-001`) is correctly instantiated
    - [ ] Run failing tests (Red phase)
- [ ] Task: Implement `LlamaIndex` pipeline for RAG document uploads
    - [ ] Update the `upload_document` view (or its underlying service) for RAG projects
    - [ ] Configure `PostgresVectorStore` and `StorageContext`
    - [ ] Process and index the document using the unified pipeline
    - [ ] Run tests to confirm pass (Green phase)

- [ ] Task: Conductor - User Manual Verification 'Phase 2: Ingestion & Indexing Pipeline' (Protocol in workflow.md)

## Phase 3: Chat Retrieval Flow

### Implement LlamaIndex Retriever
- [ ] Task: Write tests for LlamaIndex query engine integration
    - [ ] Create unit tests for RAG project chat submission
    - [ ] Assert the query engine is initialized with the correct index
    - [ ] Run failing tests (Red phase)
- [ ] Task: Refactor Chat submission logic for RAG projects
    - [ ] Update the `chat_submit` view (or underlying service) to use LlamaIndex query engine
    - [ ] Ensure project-level system prompts are passed into the query context
    - [ ] Ensure Google File Search projects bypass this new retriever
    - [ ] Run tests to confirm pass (Green phase)

- [ ] Task: Conductor - User Manual Verification 'Phase 3: Chat Retrieval Flow' (Protocol in workflow.md)

## Phase 4: Final Coverage Verification

- [ ] Task: Run full coverage report
    - [ ] Run tests and verify >80% coverage on modified modules
    - [ ] Ensure no regression on existing functionality (especially Google File Search and Admin tests)

- [ ] Task: Conductor - User Manual Verification 'Phase 4: Final Coverage Verification' (Protocol in workflow.md)