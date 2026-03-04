# Changelog — March 1, 2026

## Track: Unit Tests for Admin and Chat Tabs

This changelog documents the implementation of comprehensive unit tests for the Admin and Chat tabs, along with the bugs discovered and fixed during the process.

---

## 1.0 Bugs Discovered & Fixed

### 1.1 Model Type Mismatch in Chat History
- **Location:** `apps/chat/views.py`
- **Issue:** The code was attempting to assign a string `store_id` (e.g., `'local_...'`) to the `project` field of `ChatMessage`. Since this is a Foreign Key to the `Project` model, Django expected an integer ID, causing a `ValueError`.
- **Fix:** Added logic to look up the `Project` instance via `store_id` and pass the object to the creation call.

### 1.2 Missing API Endpoint
- **Location:** `apps/chat/urls.py`
- **Issue:** Reference to `/api/chat/` existed in documentation and tests, but the route was not defined in the URL configuration.
- **Fix:** Registered `views.chat` under the path `api/chat/`.

### 1.3 Crash in Document API Lookup
- **Location:** `apps/documents/api_views.py`
- **Issue:** The `get_object` method called `.isdigit()` on the primary key. When an integer was passed directly (common in DRF testing), it raised an `AttributeError`.
- **Fix:** Forced the lookup value to a string (`str(lookup_value).isdigit()`) before verification.

### 1.4 Test vs. Implementation Inconsistency
- **Location:** `Testing/unit/projects/test_models.py` & `test_api_views.py`
- **Issue:** Existing tests asserted that PostgreSQL storage types should be identified as `'rag'`, but the production code and constants use `'postgres'`.
- **Fix:** Updated legacy tests to use the correct `'postgres'` value.

---

## 2.0 New Test Cases Created

### Admin Tab — Project Management (`Testing/unit/admin/`)
- **`test_admin_project_views.py`**
    - `test_create_project_google`: Verifies project creation with Google File Search store mocking.
    - `test_create_project_postgres`: Verifies project creation for local PostgreSQL.
    - `test_delete_project_google`: Verifies deletion including external store cleanup.
    - `test_delete_project_postgres`: Verifies deletion without external dependencies.
- **`test_admin_project_services.py`**
    - `test_create_project_service_call`: Asserts correct service arguments for project creation.
    - `test_delete_project_service_call`: Asserts correct service arguments for project deletion.

### Admin Tab — Document Management (`Testing/unit/admin/`)
- **`test_admin_document_views.py`**
    - `test_list_documents_google`: Verifies document listing from Google backend.
    - `test_list_documents_postgres`: Verifies document listing from local database.
    - `test_list_documents_local_legacy`: Verifies listing for legacy FAISS projects.
    - `test_upload_document_local`: Tests local file ingestion.
    - `test_delete_document_local`: Tests local file removal.
    - `test_upload_document_google`: Verifies Google File Search upload flow.
    - `test_upload_document_postgres`: Verifies PostgreSQL RAG ingestion flow.
    - `test_delete_document_google`: Verifies Google document removal.
    - `test_delete_document_postgres`: Verifies PostgreSQL document removal.

### Admin Tab — Custom Prompts (`Testing/unit/admin/`)
- **`test_admin_prompt_views.py`**
    - `test_add_custom_prompt`: Verifies adding a new system prompt via `manage_prompt`.
    - `test_edit_custom_prompt`: Verifies updating an existing prompt.
    - `test_system_prompt_passed_to_llm`: Asserts that the stored prompt is correctly forwarded to the LLM during chat.

### Chat Tab — Real LLM & Logic (`Testing/unit/chat/`)
- **`test_chat_google_llm.py`**
    - `test_chat_google_related_answer`: Real LLM query against "Test File Search" project.
    - `test_chat_google_unrelated_answer`: Verifies restrictive system prompt prevents off-topic answers.
- **`test_chat_rag_llm.py`**
    - `test_chat_rag_related_answer`: Real LLM query against "Test RAG" project.
    - `test_chat_rag_unrelated_answer`: Verifies prompt adherence for RAG backend.
- **`test_chat_views.py`**
    - `test_chat_submit_authenticated`: Verifies chat history persistence for logged-in users.
    - `test_chat_submit_local`: Tests chat submission flow for local storage.
    - `test_chat_api_local`: Tests the `/api/chat/` JSON endpoint for local storage.
    - `test_chat_api_authenticated`: Verifies user association in the JSON API.
    - `test_chat_submit_rag`: Verifies the HTML submission flow for RAG projects.
    - `test_chat_api_missing_params`: Ensures proper error handling for invalid payloads.

---

## 3.0 Final Coverage Status
- **`apps/projects/views.py`**: 82%
- **`apps/documents/views.py`**: 81%
- **`apps/chat/views.py`**: 81%
