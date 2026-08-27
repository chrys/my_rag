# Tasks Checklist: Sprint Aug 4 - Admin Governance, Tenant Isolation & Intent Classification

**Document Path:** `Design/Aug-26/Aug4/todo.md`  
**Specification Reference:** [`Design/Aug-26/Aug4/aug4-specs.md`](file:///Users/chrys/Projects/my_rag/Design/Aug-26/Aug4/aug4-specs.md)  
**Implementation Plan:** [`Design/Aug-26/Aug4/plan.md`](file:///Users/chrys/Projects/my_rag/Design/Aug-26/Aug4/plan.md)  

---

## Phase 1: Foundation & Admin RBAC Governance (Task 1)

- [x] **Task 1.1: Implement Custom DRF Permission Classes**
  - **Description:** Create `IsAdminUserOnly` and `IsAdminOrProjectReadOnly` in `src/apps/api/permissions.py` returning standard 403 error payloads.
  - **Acceptance:** Non-staff requests for restricted methods receive 403 Forbidden with proper JSON error message.
  - **Verify:** `DJANGO_ENV=testing pytest Testing/unit/api/test_rbac_permissions.py`
  - **Files:** `src/apps/api/permissions.py`

- [x] **Task 1.2: Enforce Project Governance Endpoint Permissions**
  - **Description:** Update `ProjectViewSet` in `src/apps/projects/api_views.py` so `create`, `update`, `partial_update`, and `destroy` require admin privileges (`IsAdminOrProjectReadOnly`).
  - **Acceptance:** Non-admin `POST /api/projects/` -> 403 Forbidden; staff admin `POST /api/projects/` -> 201 Created.
  - **Verify:** `DJANGO_ENV=testing pytest Testing/unit/projects/test_project_api.py`
  - **Files:** `src/apps/projects/api_views.py`

- [x] **Task 1.3: Enforce Admin-Only on API Keys, Telemetry & Evaluation Endpoints**
  - **Description:** Update `APIKeyViewSet`, `APIUsageViewSet`, `EvaluationDatasetViewSet`, `EvaluationRunViewSet`, and `EvaluationResultMetricsViewSet` with `IsAdminUserOnly`.
  - **Acceptance:** Non-admin `POST /api/keys/` and `POST /api/runs/` -> 403 Forbidden.
  - **Verify:** `DJANGO_ENV=testing pytest Testing/unit/api Testing/unit/evaluate`
  - **Files:** `src/apps/api/api_views.py`, `src/apps/evaluate/api_views.py`

- [x] **Checkpoint 1:** Run all Phase 1 RBAC unit tests.

---

## Phase 2: Secure Tenant Isolation & Context Boundaries (Task 2)

- [x] **Task 2.1: Enforce Strict API Key Scoping in Chat and Document Endpoints**
  - **Description:** Validate in `src/apps/chat/views.py` and `src/apps/documents/api_views.py` that client API keys must have matching `project_id`. Reject cross-project access and unscoped keys for non-admins immediately.
  - **Acceptance:** API key scoped to project A calling project B returns 403 Forbidden with 0 retrieval queries and 0 token leakage.
  - **Verify:** `DJANGO_ENV=testing pytest Testing/unit/chat/test_tenant_isolation.py`
  - **Files:** `src/apps/chat/views.py`, `src/apps/documents/api_views.py`

- [x] **Task 2.2: Enforce Hard Database-Level Metadata Filtering in Postgres RAG**
  - **Description:** Ensure `PostgresRAGEngine` in `src/postgres_rag.py` and document deletion services inject deterministic `project_id` filters into every SQL/vector query.
  - **Acceptance:** Retrieval queries against database strictly isolate project chunks.
  - **Verify:** `DJANGO_ENV=testing pytest Testing/unit/documents/test_document_isolation.py`
  - **Files:** `src/postgres_rag.py`, `src/apps/documents/services.py`

- [x] **Checkpoint 2:** Run all Phase 2 isolation and security tests.

---

## Phase 3: Pre-Retrieval Intent Classification & Disambiguation (Task 3)

- [x] **Task 3.1: Build Hybrid Intent Classification Service**
  - **Description:** Implement `src/apps/chat/intent_service.py` with fast regex heuristics for greetings/chitchat and structured Gemini Flash intent classification for ambiguity detection.
  - **Acceptance:** Intent classifier routes queries to `GREETING_OR_CHITCHAT`, `VECTOR_SEARCH`, `CLARIFICATION_NEEDED`, or `OUT_OF_SCOPE`.
  - **Verify:** `DJANGO_ENV=testing pytest Testing/unit/chat/test_intent_classification.py`
  - **Files:** `src/apps/chat/intent_service.py`

- [ ] **Task 3.2: Integrate Intent Pipeline in Chat View & Persist Chat History**
  - **Description:** Connect `intent_service` into `src/apps/chat/views.py` `chat()` handler. Bypass vector search for greetings/chitchat, return clarification prompt for ambiguous queries, and log all turns to `ChatMessage`.
  - **Acceptance:** Greetings execute 0 database vector searches; ambiguous queries prompt for clarification; all turns persist in `ChatMessage`.
  - **Verify:** `DJANGO_ENV=testing pytest Testing/unit/chat/test_chat_views.py`
  - **Files:** `src/apps/chat/views.py`

- [ ] **Checkpoint 3:** Run all Phase 3 chat and intent unit tests.

---

## Phase 4: System Verification & Regression Suite

- [ ] **Task 4.1: Run Full Test Suite & Verify 100% Pass Rate**
  - **Description:** Run all unit and regression test suites across the repository.
  - **Acceptance:** All tests pass with zero regressions.
  - **Verify:**
    - `DJANGO_ENV=testing pytest Testing/unit -v`
    - `DJANGO_ENV=testing pytest Testing/regression -v`
