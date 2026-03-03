# Implementation Plan: Unit Tests for Admin and Chat Tabs

## Phase 1: Admin Tab — Project Management Tests

### Setup
- [x] Task: Write failing test stubs — Create `Testing/unit/admin/__init__.py` and `Testing/unit/admin/test_admin_project_views.py` with empty test class skeletons that fail on import or assertion. [6ba26a4]
    - [ ] Create `Testing/unit/admin/` directory
    - [ ] Create `Testing/unit/admin/__init__.py`
    - [ ] Create stub test file `test_admin_project_views.py` with failing tests for FR-1.1 and FR-1.2
    - [ ] Run `pytest Testing/unit/admin/` and confirm all stubs fail (Red phase)

### Implementation — Create Project
- [x] Task: Implement test_create_project_google — view-level test for `create_project` with `storage_type='google'` [b8c57f6]
    - [ ] Mock `google_file_search.create_new_file_search_store` with `mocker`
    - [ ] POST to `create_project` view with `display_name` and `storage_type='google'`
    - [ ] Assert mock was called
    - [ ] Assert `Project` DB record exists with `storage_type='google'`
    - [ ] Run tests and confirm pass (Green phase)
- [x] Task: Implement test_create_project_postgres — view-level test for `create_project` with `storage_type='postgres'` [b8c57f6]
    - [ ] POST to `create_project` view with `display_name` and `storage_type='postgres'`
    - [ ] Assert no external service is called
    - [ ] Assert `Project` DB record exists with `storage_type='postgres'`
    - [ ] Run tests and confirm pass

### Implementation — Delete Project
- [ ] Task: Implement test_delete_project_google — view-level test for `delete_project` with `storage_type='google'`
    - [ ] Create a `Project` fixture with `storage_type='google'` and `external_store_id`
    - [ ] Mock `gfs.delete_file_search_store` with `mocker`
    - [ ] Call `delete_project` view
    - [ ] Assert mock called with correct `external_store_id`
    - [ ] Assert `Project` record is deleted from DB
    - [ ] Run tests and confirm pass
- [ ] Task: Implement test_delete_project_postgres — view-level test for `delete_project` with `storage_type='postgres'`
    - [ ] Create a `Project` fixture with `storage_type='postgres'`
    - [ ] Call `delete_project` view
    - [ ] Assert no external service call
    - [ ] Assert `Project` record is deleted from DB
    - [ ] Run tests and confirm pass

### Service Layer Tests
- [ ] Task: Create `Testing/unit/admin/test_admin_project_services.py` with service-layer assertions
    - [ ] Write failing stub tests
    - [ ] Run stubs and confirm fail
    - [ ] Implement: assert `gfs.create_new_file_search_store` is called with correct `display_name`
    - [ ] Implement: assert `gfs.delete_file_search_store` is called with correct store ID
    - [ ] Run and confirm pass

- [ ] Task: Conductor - User Manual Verification 'Phase 1: Admin Project Management Tests' (Protocol in workflow.md)

---

## Phase 2: Admin Tab — Document Management Tests

### Setup
- [ ] Task: Write failing test stubs — Create `Testing/unit/admin/test_admin_document_views.py` with empty test skeletons
    - [ ] Create stub test file with failing test stubs for FR-2.1 and FR-2.2
    - [ ] Run and confirm fail (Red phase)

### Implementation — Upload File
- [ ] Task: Implement test_upload_document_google — view-level test for `upload_document` with Google project
    - [ ] Create `Project` fixture with `storage_type='google'` and `external_store_id`
    - [ ] Create a `SimpleUploadedFile` test file
    - [ ] Mock `gfs.add_document_to_store` with `mocker`
    - [ ] POST to `upload_document` view
    - [ ] Assert mock called with correct store ID
    - [ ] Run and confirm pass (Green phase)
- [ ] Task: Implement test_upload_document_postgres — view-level test for `upload_document` with postgres project
    - [ ] Create `Project` fixture with `storage_type='postgres'`
    - [ ] Create a `SimpleUploadedFile` test file
    - [ ] Mock `PostgresRAGEngine.index_document` with `mocker`
    - [ ] POST to `upload_document` view
    - [ ] Assert mock called
    - [ ] Assert `Document` DB record created with `state='INDEXED'`
    - [ ] Run and confirm pass

### Implementation — Delete File (with de-index verification)
- [ ] Task: Implement test_delete_document_google — view-level test for `delete_document` with Google project
    - [ ] Create `Project` fixture with `storage_type='google'` and `external_store_id`
    - [ ] Mock `gfs.delete_document_from_store` with `mocker`
    - [ ] Call `delete_document` view
    - [ ] Assert mock called with correct arguments
    - [ ] Run and confirm pass
- [ ] Task: Implement test_delete_document_postgres — view-level test for `delete_document` with postgres project
    - [ ] Create `Project` and `Document` fixtures with `storage_type='postgres'`
    - [ ] Mock any RAG engine delete method if applicable with `mocker`
    - [ ] Call `delete_document` view
    - [ ] Assert `Document` DB record is removed
    - [ ] Run and confirm pass

- [ ] Task: Conductor - User Manual Verification 'Phase 2: Admin Document Management Tests' (Protocol in workflow.md)

---

## Phase 3: Admin Tab — Custom Prompt Management Tests

### Setup
- [ ] Task: Write failing test stubs — Create `Testing/unit/admin/test_admin_prompt_views.py` with empty test skeletons
    - [ ] Create stub test file with failing stubs for FR-3.1, FR-3.2, FR-3.3
    - [ ] Run and confirm fail (Red phase)

### Implementation — Add & Edit Prompt
- [ ] Task: Implement test_add_custom_prompt — view-level test for `manage_prompt` POST (new prompt)
    - [ ] Create `Project` fixture
    - [ ] Mock `prompt_storage.set_prompt` with `mocker`
    - [ ] POST to `manage_prompt` view with `content`
    - [ ] Assert mock called with correct `store_id` and `content`
    - [ ] Assert response indicates success
    - [ ] Run and confirm pass
- [ ] Task: Implement test_edit_custom_prompt — view-level test for `manage_prompt` POST (updating existing)
    - [ ] Create `Project` and existing `SystemPrompt` fixture
    - [ ] Mock `prompt_storage.set_prompt` with `mocker`
    - [ ] POST updated content to `manage_prompt`
    - [ ] Assert mock called with new content
    - [ ] Run and confirm pass

### Implementation — Prompt Usage in Chat
- [ ] Task: Implement test_system_prompt_passed_to_llm — verify prompt is forwarded to LLM backend
    - [ ] Create `Project` fixture
    - [ ] Mock `prompt_storage.get_prompt` to return a specific prompt string with `mocker`
    - [ ] Mock the appropriate LLM backend call (`gfs.ask_store_question` or `rag_engine.query`) with `mocker`
    - [ ] POST to `chat_submit` view
    - [ ] Assert the mocked LLM call was invoked with the expected `system_prompt` argument
    - [ ] Run and confirm pass

- [ ] Task: Conductor - User Manual Verification 'Phase 3: Admin Prompt Management Tests' (Protocol in workflow.md)

---

## Phase 4: Chat Tab — Real LLM Tests (Google File Search)

### Setup
- [ ] Task: Write failing test stubs — Create `Testing/unit/chat/test_chat_google_llm.py` with empty test skeletons
    - [ ] Write stubs for FR-4.1 and FR-4.2 that fail (e.g., `assert False, "not implemented"`)
    - [ ] Run and confirm fail (Red phase)

### Implementation
- [ ] Task: Implement test_chat_google_related_answer — real LLM test using "Test File Search" project
    - [ ] Add fixture that fetches the "Test File Search" project from DB (skip if not found)
    - [ ] POST a query known to be answerable from the indexed document to `chat_submit` or `chat` view
    - [ ] Assert response is HTTP 200
    - [ ] Assert `bot_response` is non-empty and not an error message
    - [ ] Run and confirm pass
- [ ] Task: Implement test_chat_google_unrelated_answer — real LLM test for off-topic query
    - [ ] Fetch or create `SystemPrompt` for "Test File Search" that restricts answers to the topic
    - [ ] POST an off-topic query
    - [ ] Assert response contains a refusal or "cannot help" type message
    - [ ] Run and confirm pass

- [ ] Task: Conductor - User Manual Verification 'Phase 4: Chat Real LLM Tests (Google)' (Protocol in workflow.md)

---

## Phase 5: Chat Tab — Real LLM Tests (PostgreSQL RAG)

### Setup
- [ ] Task: Write failing test stubs — Create `Testing/unit/chat/test_chat_rag_llm.py` with empty test skeletons
    - [ ] Write stubs for FR-5.1 and FR-5.2 that fail
    - [ ] Run and confirm fail (Red phase)

### Implementation
- [ ] Task: Implement test_chat_rag_related_answer — real LLM test using "Test RAG" project
    - [ ] Add fixture that fetches the "Test RAG" project from DB (skip if not found)
    - [ ] POST a query known to be answerable
    - [ ] Assert response is HTTP 200 and `bot_response` is non-empty
    - [ ] Run and confirm pass
- [ ] Task: Implement test_chat_rag_unrelated_answer — real LLM test for off-topic query
    - [ ] Fetch or create `SystemPrompt` for "Test RAG" that restricts answers to the topic
    - [ ] POST an off-topic query
    - [ ] Assert response contains a refusal / "cannot help"
    - [ ] Run and confirm pass

- [ ] Task: Conductor - User Manual Verification 'Phase 5: Chat Real LLM Tests (RAG)' (Protocol in workflow.md)

---

## Phase 6: Coverage Verification and Cleanup

- [ ] Task: Run full coverage report for targeted view files
    - [ ] Run `pytest Testing/unit/ --cov=apps/projects/views --cov=apps/documents/views --cov=apps/chat/views --cov-report=term-missing`
    - [ ] Confirm coverage ≥80% for each targeted module
    - [ ] If below 80%, add additional tests to cover missing branches
- [ ] Task: Ensure no existing tests are broken
    - [ ] Run full test suite: `pytest Testing/unit/`
    - [ ] Confirm zero regressions
- [ ] Task: Conductor - User Manual Verification 'Phase 6: Coverage Verification' (Protocol in workflow.md)
