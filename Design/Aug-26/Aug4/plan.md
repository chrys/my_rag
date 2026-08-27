# Implementation Plan: Sprint Aug 4 - Admin Governance, Tenant Isolation & Intent Classification

**Document Path:** `Design/Aug-26/Aug4/plan.md`  
**Specification Reference:** [`Design/Aug-26/Aug4/aug4-specs.md`](file:///Users/chrys/Projects/my_rag/Design/Aug-26/Aug4/aug4-specs.md)  
**Status:** Pending Review  

---

## 1. Overview

This implementation delivers enterprise security, robust tenant boundaries, and pre-retrieval compute optimization across the RAG platform:
1. **Admin-Only RBAC (Task 1):** Locks down DRF endpoints (`/api/projects/`, `/api/keys/`, `/api/usage/`, `/api/datasets/`, `/api/runs/`) to staff/superusers, while keeping scoped project access for client API keys and authenticated users.
2. **Tenant Isolation (Task 2):** Enforces strict project scoping on API keys and deterministic database-level `project_id` & `user_id` query scoping, eliminating cross-tenant leakage.
3. **Intent Classification (Task 3):** Adds a hybrid pre-retrieval routing layer that intercepts greetings and ambiguous queries, providing instant responses and bounded clarification without executing wasteful vector searches.

---

## 2. Architecture & Design Decisions

- **DRF Permissions:** Encapsulate RBAC in reusable `IsAdminUserOnly` and `IsAdminOrProjectReadOnly` permission classes inside `src/apps/api/permissions.py`.
- **API Key Scoping Policy:** Strict project scoping for client API keys. Any non-admin request attempting to access an unauthorized or cross-tenant `project_id` fails immediately with `403 Forbidden` prior to retrieval or token usage.
- **Database Context Filtering:** Guarantee deterministic metadata filtering (`project_id`) at the SQL / vector store query layer in `PostgresRAGEngine` and `DocumentViewSet`.
- **Intent Routing Strategy:** Fast regex/heuristic filter first for zero-latency greetings/chitchat; Gemini Flash structured output classifier for ambiguity detection and bounded disambiguation. All conversational turns persist in `ChatMessage`.

---

## 3. Dependency Graph & Phases

```text
Phase 1: Admin Governance & Custom Permissions
   │ (IsAdminUserOnly, IsAdminOrProjectReadOnly, ProjectViewSet, APIKeyViewSet, Eval Viewsets)
   ▼
Phase 2: Secure Tenant Isolation & Key Scoping
   │ (Strict API key validation, Database query scoping, DocumentViewSet protection)
   ▼
Phase 3: Pre-Retrieval Intent Classification & Disambiguation
   │ (Hybrid intent service, Chat pipeline integration, ChatMessage history persistence)
   ▼
Phase 4: Full Verification & Regression Testing
```

---

## 4. Phase Breakdown & Tasks

### Phase 1: Foundation & Admin RBAC Governance (Task 1)

- **Task 1.1: Custom DRF Permission Classes**
  - Create `IsAdminUserOnly` and `IsAdminOrProjectReadOnly` in `src/apps/api/permissions.py`.
  - Ensure standard JSON error format: `{"error": "You do not have permission to perform this action. Administrator privileges required."}` on 403.
  - *Files:* `src/apps/api/permissions.py`
  - *Verification:* Unit tests in `Testing/unit/api/test_rbac_permissions.py`.

- **Task 1.2: Project Governance Endpoint Permissions**
  - Update `ProjectViewSet` in `src/apps/projects/api_views.py`:
    - `list`/`retrieve`: Scoped to user's projects or staff.
    - `create`/`update`/`partial_update`/`destroy`: Restricted to `is_staff` or `is_superuser`.
  - *Files:* `src/apps/projects/api_views.py`
  - *Verification:* Test non-admin `POST /api/projects/` -> 403, admin `POST` -> 201.

- **Task 1.3: API Key, Telemetry & Evaluation Endpoint Governance**
  - Update `APIKeyViewSet` & `APIUsageViewSet` in `src/apps/api/api_views.py` with `permission_classes = [IsAdminUserOnly]`.
  - Update `EvaluationDatasetViewSet`, `EvaluationRunViewSet`, and `EvaluationResultMetricsViewSet` in `src/apps/evaluate/api_views.py` with `permission_classes = [IsAdminUserOnly]`.
  - *Files:* `src/apps/api/api_views.py`, `src/apps/evaluate/api_views.py`
  - *Verification:* Test non-admin `POST /api/keys/` and `POST /api/runs/` -> 403.

#### Checkpoint 1: RBAC Governance
- [ ] Run `DJANGO_ENV=testing pytest Testing/unit/api Testing/unit/projects Testing/unit/evaluate -v`
- [ ] All RBAC endpoints return 403 Forbidden for non-admins and 200/201 for staff admins.

---

### Phase 2: Secure Tenant Isolation & Context Boundaries (Task 2)

- **Task 2.1: Strict API Key Scoping in Chat and Document Endpoints**
  - Enforce in `src/apps/chat/views.py` that client API keys must have `project_id` matching the target project.
  - Disallow unscoped API keys for non-admin chat.
  - Return `403 Forbidden` (`{"error": "API key is not authorized for this project store."}`) immediately with zero token leakage.
  - *Files:* `src/apps/chat/views.py`, `src/apps/documents/api_views.py`
  - *Verification:* Test API key from project A querying project B -> 403 Forbidden.

- **Task 2.2: Hard Database-Level Metadata Filtering**
  - Update `PostgresRAGEngine` in `src/postgres_rag.py` and document services to inject deterministic `project_id` filters in all vector search/document queries.
  - Prevent cross-tenant document access or deletion.
  - *Files:* `src/postgres_rag.py`, `src/apps/documents/services.py`
  - *Verification:* Unit tests attempting cross-tenant retrieval verify zero leaked chunks.

#### Checkpoint 2: Tenant Isolation
- [ ] Run `DJANGO_ENV=testing pytest Testing/unit/chat/test_tenant_isolation.py Testing/unit/documents -v`
- [ ] Cross-tenant queries fail deterministically with 403 and zero DB chunk leakage.

---

### Phase 3: Pre-Retrieval Intent Classification & Disambiguation (Task 3)

- **Task 3.1: Hybrid Intent Classification Service**
  - Implement `src/apps/chat/intent_service.py` with:
    - Regex pattern matcher for standard greetings, polite conversational turns, and meta prompts.
    - Structured intent classifier using `gemini-2.5-flash` with output schema (`intent`, `clarification_prompt`, `direct_response`).
    - Handlers for `GREETING_OR_CHITCHAT`, `VECTOR_SEARCH`, `CLARIFICATION_NEEDED`, `OUT_OF_SCOPE`.
  - *Files:* `src/apps/chat/intent_service.py`
  - *Verification:* Unit tests testing greeting matches, ambiguous queries, and search queries.

- **Task 3.2: Pipeline Integration & History Persistence**
  - Integrate intent classification into `chat` view in `src/apps/chat/views.py`:
    - Fast greeting path: Returns direct conversational reply without executing vector search.
    - Clarification path: Returns structured clarification prompt when query ambiguity is detected.
    - Search path: Proceeds to tenant-isolated vector search.
    - Save all message turns in `ChatMessage` history.
  - *Files:* `src/apps/chat/views.py`
  - *Verification:* Test chat with "Hello" -> 0 vector queries executed, 1 ChatMessage recorded.

#### Checkpoint 3: Intent Classification
- [ ] Run `DJANGO_ENV=testing pytest Testing/unit/chat -v`
- [ ] Greeting and clarification queries succeed with zero vector searches and persist to database.

---

### Phase 4: Full System Verification & Regression Suite

- **Task 4.1: End-to-End Suite Run**
  - Run full unit tests: `DJANGO_ENV=testing pytest Testing/unit -v`
  - Run regression suite: `DJANGO_ENV=testing pytest Testing/regression -v`
  - *Verification:* 100% test pass rate across all suites.

---

## 5. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Latency overhead from intent classification on every query | Medium | Fast regex heuristics handle ~80% of common non-search queries (greetings/thanks) in <1ms without LLM calls. |
| Over-aggressive clarification triggering | Low | Calibrate classification prompt and ensure only clearly ambiguous/incomplete queries trigger clarification. |
| Breaking legacy test cases expecting open API key creation | Medium | Update test fixtures to use staff credentials for administrative endpoints. |
