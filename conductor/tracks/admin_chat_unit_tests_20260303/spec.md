# Specification: Unit Tests for Admin and Chat Tabs

## Overview

This track adds comprehensive unit tests for the Admin tab and Chat tab of My RAG. The Admin tab covers project lifecycle management, document management, and custom prompt management. The Chat tab covers query routing and basic relevance validation. Both storage types — **Google File Search** and **PostgreSQL RAG** — must be covered.

Existing unit tests live in `Testing/unit/` and follow the pattern: `pytest` + `@pytest.mark.django_db`, `APIRequestFactory`, and `force_authenticate`. New tests must follow the same conventions.

## Functional Requirements

### FR-1: Admin Tab — Project Management

**FR-1.1 Create a Project**
- Tests cover view-level: `apps.projects.views.create_project` called via Django test client / APIRequestFactory.
- For `google` storage type: mock `google_file_search.create_new_file_search_store`; assert it is called and a `Project` DB record is created with `storage_type='google'`.
- For `postgres` storage type: no external service call needed; assert a `Project` DB record is created with `storage_type='postgres'`.
- Mocking strategy: `pytest-mock` (`mocker` fixture).
- A separate service-layer test verifies that the external service functions (`gfs.create_new_file_search_store`) are called with the correct arguments when `storage_type='google'`.

**FR-1.2 Delete a Project**
- Tests cover view-level: `apps.projects.views.delete_project`.
- For `google` storage type: mock `gfs.delete_file_search_store`; assert it is called with the correct `external_store_id` and the `Project` record is deleted from the DB.
- For `postgres` storage type: assert only the `Project` record is deleted (no external service call).

### FR-2: Admin Tab — Document Management

**FR-2.1 Upload a File**
- Tests cover view-level: `apps.documents.views.upload_document`.
- For `google` storage type: mock `gfs.add_document_to_store`; assert the mock is called with the correct store ID and the temp file path.
- For `postgres` / RAG storage type: mock `PostgresRAGEngine.index_document`; assert it is called, and a `Document` DB record is created with `state='INDEXED'`.
- Provide a minimal in-memory test file upload (using `SimpleUploadedFile`).

**FR-2.2 Delete a File**
- Tests cover view-level: `apps.documents.views.delete_document`.
- For `google` storage type: mock `gfs.delete_document_from_store`; assert the mock is called with the correct arguments.
- For `postgres` / RAG storage type: mock `PostgresRAGEngine.delete_document` (if applicable); assert the `Document` DB record is removed.
- **Critical:** Both mocked external service call assertions AND DB record checks must pass (assert both mock called + DB record removed where applicable).

### FR-3: Admin Tab — Custom Prompt Management

**FR-3.1 Add a Custom Prompt to a Project**
- Tests cover view-level: `apps.projects.views.manage_prompt` (POST).
- Mock `prompt_storage.set_prompt`; assert it is called with the correct `store_id` and `content`.
- Also assert the `SystemPrompt` DB record is created or updated.

**FR-3.2 Edit a Custom Prompt**
- Tests cover view-level: `apps.projects.views.manage_prompt` (POST with existing prompt).
- Assert the existing `SystemPrompt` content is updated.

**FR-3.3 Verify Custom Prompt is Used in Chat**
- Tests cover: `apps.chat.views.chat_submit` or `apps.chat.views.chat`.
- Mock `prompt_storage.get_prompt` to return a specific prompt string.
- Mock the LLM backend call; assert the prompt string is passed through to the backend.

### FR-4: Chat Tab — Google File Search (Real LLM)

Pre-existing test project: **"Test File Search"** (`storage_type='google'`). This project must exist in the DB and already have at least one file indexed.

**FR-4.1 Chat Returns Related Answers**
- Send a query known to be answerable from the indexed content.
- Assert the response is non-empty and does not indicate failure.

**FR-4.2 Chat Does Not Answer Unrelated Questions**
- Set a system prompt on the test project that restricts answers to only the indexed topic (e.g. "Only answer questions about [topic]. For anything else, say you cannot help.").
- Send an off-topic query.
- Assert the response contains a refusal or acknowledges inability to help.

### FR-5: Chat Tab — PostgreSQL RAG (Real LLM)

Pre-existing test project: **"Test RAG"** (`storage_type='postgres'`). This project must exist in the DB and already have at least one file indexed.

**FR-5.1 Chat Returns Related Answers**
- Same approach as FR-4.1 but using the `postgres` backend.

**FR-5.2 Chat Does Not Answer Unrelated Questions**
- Same approach as FR-4.2 but using the `postgres` backend.

## Non-Functional Requirements

- **Test Framework:** `pytest` + `pytest-django` (existing setup).
- **Mocking:** `pytest-mock` (`mocker` fixture) for all external service calls in Admin tests.
- **Coverage Target:** >80% coverage for `apps/projects/views.py`, `apps/documents/views.py`, and `apps/chat/views.py`.
- **Test Isolation:** Admin tests must not rely on pre-existing database state; use fixtures to create/clean up.
- **File Location:** New test files live under `Testing/unit/admin/` (Admin tab tests) and `Testing/unit/chat/` (new chat view tests). Chat real-LLM tests go in a new sub-module under `Testing/unit/chat/test_chat_views.py` or a new file.
- **Naming Convention:** Follow existing pattern: `test_<module>.py`, class-based `Test<Feature>`, method `test_<scenario>`.

## Acceptance Criteria

1. All tests in `Testing/unit/admin/` pass with `pytest`.
2. All tests in the new Chat tab test files pass.
3. For delete operations: both the external-service mock call assertion **and** the DB record removal are asserted.
4. For prompt tests: the system prompt is verifiably passed to the LLM backend.
5. Real LLM chat tests use existing "Test File Search" and "Test RAG" projects and produce non-empty responses.
6. Code coverage for the covered view files is ≥80%.
7. No existing tests are broken.

## Out of Scope

- Creating new production features or modifying existing application code.
- Testing the Evaluate tab.
- Testing authentication/authorization (already covered elsewhere).
- Testing the `local` (FAISS) storage type (not mentioned in PRD).
- Performance or load testing.
- End-to-end / browser-level tests.
