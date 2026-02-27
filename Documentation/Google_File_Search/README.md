# Google File Search Projects Documentation

## Overview
Google File Search Projects in My RAG leverage the official Google GenAI SDK to interact with the Gemini API's File Search capabilities. This feature allows users to create remote "Stores," upload documents, and query the Gemini model (`gemini-2.5-flash-lite`), grounding the answers exclusively in the uploaded documents.

## API Integration (`src/google_file_search.py`)

The core functionality is wrapped in `src/google_file_search.py`, which uses the `google-genai` library.

### Key Requirements
- **Authentication:** A valid `GOOGLE_API_KEY` must be present in the `.env` file or environment variables. This key is used for both the GenAI client initialization and direct REST API calls.

### Core Operations

#### 1. Store Management
- **Create Store (`create_new_file_search_store`):** Provisions a new, empty File Search Store on Google's backend. Returns a unique resource name (e.g., `fileSearchStores/abc-123`).
- **List Stores (`list_all_file_search_stores`):** Retrieves and lists all available File Search Stores associated with the API key.
- **Delete Store (`delete_file_search_store`):** Permanently deletes a specified store and all of its indexed contents.

#### 2. Document Management
- **Upload Document (`add_document_to_store`):** Uploads a local file to a specified store. The function polls the Google API operation status to ensure indexing is fully complete before returning the document's resource name.
- **List Documents (`list_documents_in_store`):** Retrieves a list of all documents currently indexed within a specific store, providing their display names and full resource IDs.
- **Delete Document (`delete_document_from_store`):** Deletes a specific document from a store. **Note:** Due to SDK limitations, this function currently bypasses the SDK and uses the direct REST API (`requests.delete`) to ensure reliable document removal.

#### 3. Querying (RAG)
- **Ask Question (`ask_store_question`):** Submits a user query to the Gemini model.
  - **Model:** Hardcoded to use `gemini-2.5-flash-lite`, which is optimized for File Search.
  - **Grounding:** The `FileSearch` tool is configured with the target `store_id`, ensuring the model's response is grounded *only* in the documents within that specific store.
  - **Citations:** The function automatically extracts grounding metadata from the response and appends the source file names to the final answer.

## Workflow Example
1. User creates a "Google File Search" project in the UI.
2. Backend calls `create_new_file_search_store("Project_Name")`.
3. User uploads `report.pdf`.
4. Backend calls `add_document_to_store(store_id, "path/to/report.pdf")` and waits for indexing.
5. User asks, "What is the summary of the report?"
6. Backend calls `ask_store_question(store_id, "What is the summary of the report?")`.
7. The system returns the Gemini-generated answer, appended with "Sources: report.pdf".

## Limitations & Considerations
- **Network Dependency:** Requires a stable internet connection as all operations communicate with Google's servers.
- **API Limits:** Subject to Google Gemini API rate limits and quotas associated with the API key.
- **Data Privacy:** Documents are uploaded to Google's servers for processing and indexing.
