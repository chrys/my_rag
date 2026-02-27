# Local Projects Documentation

## Overview
Local Projects in My RAG are designed to run entirely on your local machine, ensuring maximum privacy and data security. These projects use local storage for both project metadata and the vector embeddings generated from your documents.

## Storage Architecture

### Project Metadata (`src/local_project_storage.py`)
- **Storage Location:** Project metadata is stored in a JSON file located at `configuration/local_projects.json`.
- **Data Structure:** Each project is assigned a unique ID (e.g., `local_20231027_153000_my_project`) and contains its display name, creation timestamp, and a dictionary of indexed documents.
- **Operations:** The `LocalProjectStorage` class handles all CRUD (Create, Read, Update, Delete) operations for project metadata. It ensures data consistency by saving changes directly to the JSON file after any modification.

### Vector Embeddings and RAG Engine (`src/local_rag.py`)
- **Storage Location:** Document embeddings and associated metadata are stored in the `rag_data/<project_id>` directory.
- **Engine:** The system uses `LocalRAGEngine` which leverages the `llama-index` framework.
- **Vector Store:** `faiss-cpu` (Facebook AI Similarity Search) is used to index and search embeddings efficiently on the CPU. It utilizes `IndexIDMap` to allow mapping vectors to specific document IDs, which facilitates document deletion.
- **LLM & Embeddings:** The system relies on an Ollama instance running locally (typically at `http://localhost:11434`).
  - **Embeddings Model:** `embeddinggemma`
  - **LLM Model:** `gemma3:4b`
- **Data Files:**
  - `faiss_index.bin`: The binary FAISS index containing the vector embeddings.
  - `metadata.json`: A JSON file linking the vector IDs to document metadata (name, file path, etc.) and storing the raw text for context generation.

## Document Ingestion Flow
1. **Upload:** A user uploads a document (e.g., PDF, TXT, MD) to a local project.
2. **Extraction:** The `LocalRAGEngine` extracts the text from the document using libraries like `pypdf`.
3. **Embedding:** The extracted text is passed to the local Ollama embeddings model (`embeddinggemma`) to generate vector representations.
4. **Indexing:** The vectors are added to the FAISS index with a unique ID, and the metadata/raw text is updated in the `metadata.json` file. The index is then saved to disk.
5. **Metadata Update:** The `LocalProjectStorage` updates the global `local_projects.json` file to reflect the newly added document.

## Query Flow (Chat)
1. **Query:** A user submits a query in the chat interface.
2. **Embedding:** The query is embedded using the same Ollama model used for ingestion.
3. **Search:** The FAISS index is searched to find the most similar document embeddings (typically top 3).
4. **Context Generation:** The raw text associated with the top matching vectors is retrieved from the `metadata.json` file.
5. **LLM Response:** The query and the retrieved context are sent to the local Ollama LLM (`gemma3:4b`), which generates an answer based on the provided documents.

## Limitations
- Performance relies heavily on the local machine's hardware capabilities, particularly for the Ollama instance running the LLM and embeddings models.
- Currently, the local FAISS implementation loads the entire index into memory when initialized.
