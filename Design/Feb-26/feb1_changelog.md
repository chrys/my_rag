# Feb 1 Changelog

## Completed

### 1. Documentation
- [x] **1.1** Documented local projects at `Documentation/local_projects/`
- [x] **1.2** Documented Google File Search projects at `Documentation/Google_File_Search/`
- [x] **1.3** Documented API at `Documentation/API/README.md`

### 2. Third Type of Project - RAG with Postgres
- [x] **2.1** Integrated txtai framework for embeddings and vector search
- [x] **2.2** Added RAG as storage type option for projects
- [x] **2.3** Configured postgres database for storing embeddings and documents
- [x] **2.4** Environment variables configured: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- [x] **2.5** Manual setup: Created postgres connection string and txtai persistence per project

### 3. User Management
- [x] **3.1** Added user management to the API
- [x] **3.2** Added user management to the UI  
- [x] **3.3** Documented user management at `Documentation/USER_MANAGEMENT.md`

## Bugs Fixed

### postgres_rag.py LLM Configuration
- **Issue**: `postgres_rag.py` was hardcoded to use Ollama (`gemma3:4b` model on localhost:11434) instead of Gemini
- **Impact**: Queries against postgres-based projects failed with "Failed to connect to Ollama" errors
- **Resolution**: Updated `postgres_rag.py` to use `GoogleGenAI` with `gemini-2.5-flash-lite` model, reading `GOOGLE_API_KEY` from environment (consistent with `google_file_search.py`)
- **Package**: Uses existing `llama-index-llms-google-genai` from requirements

## Current Status
All PRD items have been implemented. Postgres RAG projects now fully support Gemini-based querying with txtai embeddings.
