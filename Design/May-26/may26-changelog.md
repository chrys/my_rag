# Changelog - May 26 & May 27, 2026

A comprehensive log of architectural and integration changes made to the "My RAG" system during the late-May 2026 sprint, focusing on VPS PostgreSQL integrations, connectivity gating, compatibility fixes, and modernizing the LLM backend.

---

## 1. Remote VPS PostgreSQL Integration
* **Dynamic Configuration**: Added a new settings module configuration `REMOTE_POSTGRES_CONFIG` in `src/apps/my_rag_project/settings/base.py` that reads the `#remote postgres` variables (`postgres_name`, `postgres_user`, `postgres_password`, `postgres_host`, `postgres_port`) from the `.env` file.
* **Unified DB Parameters**: Updated `LlamaIndexIngestionPipeline` and `get_vector_store` inside `src/apps/documents/services.py` to automatically connect to the remote VPS PostgreSQL database via SSH port-forwarding rather than hardcoding local defaults.
* **Embedding Dimension Alignment**: Adjusted the vector store table schema embedding dimension from `768` to `3072` in `services.py` to cleanly align with the exact dimensions output by the Google `gemini-embedding-001` model, resolving database insertion mismatch exceptions.

---

## 2. Real-Time Connection Gating & HTMX Error Swaps
* **Database Utility**: Added `test_postgres_connection()` in `src/apps/projects/db_utils.py` using `psycopg2` and a socket-level timeout of 5 seconds to query remote DB availability.
* **Gated Project Creation**: Updated `create_project` in `src/apps/projects/views.py` to test connection validity on form submission.
  * **On Connection Failure**: Immediately blocks project record creation and triggers a styled HTMX out-of-band (`OOB`) swap, rendering a clean alert banner inside the UI error container (`#project-error-container`).
  * **On Connection Success**: Sets a custom `HX-Trigger: projectCreated` header to signal the modal to close and refreshes the project list.
* **Gated Ingestion Pipeline**: Gated document uploads inside `src/apps/documents/views.py`. The connection check is run immediately.
  * **On Connection Failure**: Bypasses loading heavy LlamaIndex dependencies entirely, transitions the SQLite `Document` status cleanly to `FAILED`, and sends a formatted JSON `500` error to the browser.

---

## 3. Global Python 3.14 Protobuf Compatibility Hotfixes
* **C-Extension Override**: Resolved a C-extension import crash with `protobuf` under Python 3.14 (`TypeError: Metaclasses with custom tp_new are not supported`) by injecting a global interceptor:
  ```python
  import sys, os
  sys.modules["google._upb._message"] = None
  os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
  ```
* **Wide Hotfix Injection**: Applied this interceptor globally across `manage.py`, `src/apps/my_rag_project/settings/base.py`, and `Testing/unit/conftest.py` to completely eliminate import-time collection crashes.

---

## 4. Chat System Modernization & Gemini Fallback Fixes
* **Resolved 404 Embedding Error**: Standardized the view imports inside `src/apps/chat/views.py` to use `llama_index.embeddings.google.GeminiEmbedding` rather than the legacy `llama_index.embeddings.gemini` wrapper.
* **Global Settings Propagation**: Configured `Settings.embed_model` and `Settings.llm` dynamically inside the chat views to ensure retriever and synthesizer routines use `gemini-embedding-001` instead of falling back to default/unsupported `models/text-embedding-004`.
* **Migrated Legacy LLM**: Replaced the deprecated `Gemini` wrapper class with the modern `GoogleGenAI` class from `llama_index.llms.google_genai` to utilize the unified `google-genai` SDK. This permanently resolved the signature crash:
  `TypeError: ChatSession.send_message() got an unexpected keyword argument 'request_options'`.
* **Type-Safe Checks**: Implemented `isinstance` checks against `BaseEmbedding` and `LLM` before setting global LlamaIndex parameters to ensure unit tests mocking these classes did not raise `AssertionError` exceptions.

---

## 5. Test Suite Enhancements & Mock Assertions
* **Isolated Environment Mocking**: Updated all RAG-related test cases in `Testing/unit/chat/test_chat_views.py` and `Testing/unit/chat/test_chat_rag_llm.py` to mock both `Gemini` and `GoogleGenAI` classes. This ensures that no real outbound connections are attempted, completely avoiding sandbox blockages.
* **Full Integration Success**: 
  * **Chat Views and API Tests**: `test_chat_views.py` — **10/10 PASSED**
  * **Chat RAG LLM Tests**: `test_chat_rag_llm.py` — **2/2 PASSED**
  * **LlamaIndex Ingestion Tests**: `test_llama_ingestion.py` — **2/2 PASSED**
  * **PostgreSQL Connectivity Tests**: `test_postgres_connectivity.py` — **5/5 PASSED**
