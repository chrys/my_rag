# Spec: Sprint Aug 4 - Admin Governance, Tenant Isolation & Intent Classification

**Sprint:** August 2026 (Aug 4)  
**Document Path:** `Design/Aug-26/Aug4/aug4-specs.md`  
**Status:** Aligned & Approved Specification  

---

## 1. Objective

To provide an enterprise-grade, secure, and cost-efficient RAG platform by achieving three core objectives:
1. **Admin-Only Governance & RBAC (Task 1):** Restrict DRF REST API endpoints for project provisioning (`POST/PUT/DELETE /api/projects/`), API key management (`/api/keys/`), telemetry (`/api/usage/`), and evaluation benchmarks (`/api/datasets/`, `/api/runs/`, `/api/results/`) strictly to **Staff / Superuser Administrators**. Client API keys are restricted to scoped project operations (`/chat/`, `/documents/`, `/prompt/`).
2. **Secure Tenant Isolation & Context Boundaries (Task 2):** Enforce strict project scoping for API keys (all client keys must be tied to a specific `project_id`). Enforce deterministic database-level context boundaries (mandatory `project_id` and `user_id` metadata filters) on all vector searches and document retrievals. Unauthorized attempts abort before vector retrieval with zero token leakage to the LLM.
3. **Pre-Retrieval Intent Classification (Task 3):** Implement a hybrid query routing layer (fast regex heuristics for greetings/chitchat + structured Gemini Flash intent classification for ambiguity detection) to intercept greetings, meta-prompts, and ambiguous queries before executing vector searches. Ambiguous queries prompt the user for clarification, and all conversation turns are preserved in `ChatMessage` history.

---

## 2. Tech Stack

- **Backend Framework:** Django 4.x / Django REST Framework (DRF)
- **RAG & Vector Retrieval:** LlamaIndex, PostgreSQL / PGVector (`psycopg2`), Local RAG, Google GenAI SDK (`google-genai`)
- **LLM & Embeddings:** Gemini Models (`gemini-2.5-flash`, `gemini-embedding-001`)
- **Frontend / Client Surface:** Bootstrap, HTMX, REST API (`/api/` and `/rag/api/`)
- **Testing:** Pytest, pytest-django, unittest

---

## 3. Commands

- **Run Dev Server:** `python manage.py runserver`
- **Run All Unit Tests:** `DJANGO_ENV=testing pytest Testing/unit -v`
- **Run Focused RBAC Tests:** `DJANGO_ENV=testing pytest Testing/unit/api Testing/unit/projects -v`
- **Run Intent Classification & Isolation Tests:** `DJANGO_ENV=testing pytest Testing/unit/chat Testing/unit/documents -v`
- **Run Regression Suite:** `DJANGO_ENV=testing pytest Testing/regression -v`
- **Check Linter / Style:** `flake8 src/ apps/`

---

## 4. Project Structure

```text
src/
  apps/
    api/              # DRF endpoints, API Key management, Usage telemetry
      api_views.py    # APIKeyViewSet, APIUsageViewSet (Admin-restricted)
      permissions.py  # Custom DRF permissions (IsAdminUserOnly, IsAdminOrProjectReadOnly)
    projects/         # Project lifecycle & prompt management
      api_views.py    # ProjectViewSet (Admin-only CRUD, scoped read)
    evaluate/         # Benchmark datasets & run execution
      api_views.py    # EvaluationDatasetViewSet, EvaluationRunViewSet (Admin-only)
    chat/             # Chat UI, conversational endpoints, feedback
      views.py        # chat API, intent routing, bounded disambiguation
      services.py     # Intent classifier, routing heuristics, response builders
    documents/        # Document uploads, indexing, vector store metadata
      api_views.py    # DocumentViewSet (Tenant-isolated scoped access)
      services.py     # Deterministic query filtering & store handlers
  postgres_rag.py     # Postgres / PGVector engine with hard metadata filtering
  local_rag.py        # Local vector index engine
Testing/
  unit/               # Unit test suites for permissions, isolation, and intent
```

---

## 5. Code Style

- Use **f-strings** for formatting (no `%` or `.format()` formatting).
- Use **double quotes** (`"..."`) consistently for strings.
- Use explicit **type hints** (`def route_query(query: str, project_id: str) -> IntentResult:`) and clear docstrings.
- Follow **PEP 8** standard conventions and idiomatic DRF permission handling.

```python
# Code Style Example: Custom DRF Permission
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.request import Request
from rest_framework.views import APIView


class IsAdminOrProjectReadOnly(BasePermission):
    """
    Grants read-only access (GET/HEAD/OPTIONS) to authenticated users/scoped keys,
    while restricting write operations (POST/PUT/PATCH/DELETE) strictly to staff/superusers.
    """

    def has_permission(self, request: Request, view: APIView) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user.is_staff or request.user.is_superuser)
```

---

## 6. Testing Strategy

- **Test Framework:** `pytest` with `pytest-django` running under `DJANGO_ENV=testing`.
- **Test Locations:**
  - `Testing/unit/api/test_rbac_permissions.py` (Tests Scenarios 1–5: Admin-only CRUD, keys, eval, telemetry).
  - `Testing/unit/chat/test_tenant_isolation.py` (Tests Scenarios 6–7: Scoped API key access, cross-tenant rejection).
  - `Testing/unit/chat/test_intent_classification.py` (Tests Task 3: Greetings bypass retrieval, ambiguous queries trigger clarification).
- **Mocking Policy:** Mock external GenAI embedding/completion calls in unit tests to ensure deterministic and fast CI runs.

---

## 7. Boundaries

- **Always:**
  - Verify project ownership and attach deterministic `project_id` and `user_id` filters on all vector retrieval queries.
  - Return standard JSON error responses (`{"error": "..."}`) with appropriate HTTP status codes (401, 403, 400).
  - Persist all chat turns (including greetings and clarification requests) in `ChatMessage` history.
- **Ask First:**
  - Altering existing database schema migrations or core model structures.
  - Introducing new external third-party packages outside of `google-genai` and Django ecosystem.
- **Never:**
  - Never allow an API key to execute vector queries or document operations across projects outside its assigned `project_id`.
  - Never trigger vector embedding or similarity search for trivial greetings or out-of-scope queries.
  - Never leak model prompt tokens or internal document excerpts upon 401/403 unauthorized attempts.

---

## 8. Detailed Task Specifications

### TASK 1: Admin-Only Governance & Role-Based Access Control (RBAC)

#### Role & Permission Matrix
| Endpoint Group | Resource / URL | External / Client API Key | Authenticated Regular User | Staff / Superuser Admin |
|---|---|:---:|:---:|:---:|
| **Chat & Q&A** | `POST /chat/`<br>`POST /chatbot/feedback/`<br>`GET /messages/` | ✅ Allowed (Scoped Project) | ✅ Allowed (Own Projects) | ✅ Full Access |
| **Document Mgmt** | `GET, POST, DELETE /documents/`<br>`GET /projects/{id}/documents/` | ✅ Allowed (Scoped Project) | ✅ Allowed (Own Projects) | ✅ Full Access |
| **System Prompts** | `GET, POST /projects/{id}/prompt/`<br>`GET, PUT /prompts/{id}/` | ✅ Allowed (Scoped Project) | ✅ Allowed (Own Projects) | ✅ Full Access |
| **Project Info** | `GET /projects/{id}/` | ✅ Read-Only (Scoped Project) | ✅ Read-Only (Assigned) | ✅ Full Access |
| **Project Admin** | `POST /projects/`<br>`PUT, DELETE /projects/{id}/` | ❌ **FORBIDDEN (403)** | ❌ **FORBIDDEN (403)** | ✅ Allowed |
| **API Keys** | `GET, POST, DELETE /keys/` | ❌ **FORBIDDEN (403)** | ❌ **FORBIDDEN (403)** | ✅ Allowed |
| **Telemetry** | `GET /usage/*` | ❌ **FORBIDDEN (403)** | ❌ **FORBIDDEN (403)** | ✅ Allowed |
| **Datasets & Eval** | `GET, POST /datasets/*`<br>`GET, POST /runs/*`<br>`GET /results/*` | ❌ **FORBIDDEN (403)** | ❌ **FORBIDDEN (403)** | ✅ Allowed |

#### Custom DRF Permissions
1. `IsAdminUserOnly`: Restricts all actions on `/keys/`, `/usage/`, `/datasets/`, `/runs/`, and `/results/` to `request.user.is_staff or request.user.is_superuser`.
2. `IsAdminOrProjectReadOnly`: Allows `GET`/`HEAD`/`OPTIONS` on `/projects/` for assigned users / scoped keys, but restricts `POST`, `PUT`, `PATCH`, `DELETE` to staff/superusers.

---

### TASK 2: Secure Tenant Isolation & Context Boundaries

1. **Strict Key Scoping:**
   - External client API keys must have `project_id` assigned. Unscoped keys (`project=None`) are rejected for non-admin chat and document operations.
2. **Deterministic Filter Enforcement:**
   - Vector search queries in `PostgresRAGEngine` and `src/apps/chat/views.py` mandate pre-execution verification of `project_id` and authenticated `user_id`.
   - SQL queries and vector store operations inject hard `WHERE project_id = :project_id` filters into every database query, ensuring zero cross-tenant chunk leakage even under prompt injection attempts.
3. **Pre-Execution Validation:**
   - Any query attempt where the incoming API key does not match the requested `project_id` immediately aborts with `403 Forbidden` (`"API key is not authorized for this project store."`) with zero tokens sent to GenAI.

---

### TASK 3: Pre-Retrieval Intent Classification & Bounded Disambiguation

1. **Hybrid Architecture:**
   - **Fast Heuristic Stage:** Evaluate the incoming query against standard conversational intents (e.g. greetings, thanks, farewells) via fast regex/pattern matching. Returns immediate conversational responses with **0 vector searches** and minimal latency.
   - **Structured Intent Classifier (Gemini Flash):** For non-trivial queries, classify the query into execution paths:
     - `GREETING_OR_CHITCHAT`: Casual dialogue -> Respond directly without vector search.
     - `VECTOR_SEARCH`: Informational query requiring document retrieval -> Proceed to filtered vector search.
     - `CLARIFICATION_NEEDED`: Query is vague, underspecified, or ambiguous -> Return structured clarification prompt asking the user to specify their question, halting retrieval.
     - `OUT_OF_SCOPE`: System instructions or off-topic prompts -> Respond with guardrail boundary message.
2. **Bounded Disambiguation:**
   - If ambiguity is detected or query clarity is insufficient, prompt the user for clarification directly instead of executing low-similarity, noisy vector lookups.
3. **Session Persistence:**
   - All turns (greetings, clarification requests, direct answers, and document-backed answers) are logged to `ChatMessage` to ensure conversation continuity in the chat UI.

---

## 9. Acceptance Criteria & Test Scenarios

- [ ] **Scenario 1:** Non-admin user calls `POST /rag/api/projects/` -> Receives `403 Forbidden`.
- [ ] **Scenario 2:** Non-admin user calls `DELETE /rag/api/projects/{id}/` -> Receives `403 Forbidden`.
- [ ] **Scenario 3:** Staff/Superuser admin calls `POST /rag/api/projects/` -> Receives `201 Created`.
- [ ] **Scenario 4:** Non-admin user calls `POST /rag/api/keys/` -> Receives `403 Forbidden`.
- [ ] **Scenario 5:** Non-admin user calls `POST /rag/api/runs/` -> Receives `403 Forbidden`.
- [ ] **Scenario 6:** External client with project-scoped API key calls `POST /rag/api/chat/` for its assigned project -> Receives `200 OK` with citations.
- [ ] **Scenario 7:** External client with project-scoped API key calls `POST /rag/api/chat/` for a different project -> Receives `403 Forbidden` (0 retrieval queries, 0 token leakage).
- [ ] **Scenario 8:** External client with project-scoped API key calls `GET /rag/api/projects/{id}/documents/` for its assigned project -> Receives `200 OK`.
- [ ] **Scenario 9:** Casual greeting (e.g. "Hello", "Good morning") sent to `/chat/` -> Receives friendly reply with **0 database vector queries** executed.
- [ ] **Scenario 10:** Ambiguous query below confidence threshold -> Receives structured clarification prompt without triggering low-confidence vector search.
