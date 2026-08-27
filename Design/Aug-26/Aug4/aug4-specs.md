# Technical Specification: Admin-Only Governance & Role-Based Access Control (RBAC)

**Sprint:** August 2026 (Aug 4)  
**Document Path:** `Design/Aug-26/Aug4/aug4-specs.md`  
**Status:** Requirements Specification (Pending Implementation)  

---

## 1. Executive Summary & Problem Statement

Currently, any authenticated user can create, modify, or delete projects and generate API keys. To ensure robust security and separation of concerns between **Platform Administrators** and **External Systems / Mobile Clients (e.g. Logos)**:
- **Administrative Operations** (provisioning projects, deleting stores, generating API keys, dataset curation, and running evaluation benchmarks) must be strictly restricted to **Admins (Staff / Superusers)**.
- **Client Operations** (sending chat queries, submitting feedback, reading project metadata, managing documents in their assigned project, and adjusting their project's system prompt) must be permitted for **Authorized Project API Keys and assigned users**.

---

## 2. Role & Permission Matrix

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

---

## 3. Detailed Component Specifications

### 3.1 Project Governance (`src/apps/projects/api_views.py`)
- **`ProjectViewSet` Permissions:**
  - `list` / `retrieve`: Accessible to authenticated users and project-scoped API keys (filtered strictly to their assigned projects).
  - `create`: Restricted to `request.user.is_staff or request.user.is_superuser`. Non-admin attempts return `403 Forbidden` (`"Only administrators can create projects."`).
  - `update` / `partial_update` / `destroy`: Restricted to `request.user.is_staff or request.user.is_superuser`. Non-admin attempts return `403 Forbidden` (`"Only administrators can modify or delete projects."`).
- **Prompt & Document Sub-endpoints:**
  - `GET /projects/{id}/prompt/` & `POST /projects/{id}/prompt/`: Allowed for the assigned project owner or authorized project API key.
  - `GET /projects/{id}/documents/`: Allowed for the assigned project owner or authorized project API key.

---

### 3.2 API Key Governance (`src/apps/api/api_views.py`)
- **`APIKeyViewSet` Permissions:**
  - Change permission class from general `[IsAuthenticated]` to **Admin-Only** (`[IsAdminUser]` / `is_staff`).
  - Regular users and external API keys cannot list (`GET /keys/`), generate (`POST /keys/`), or delete (`DELETE /keys/{id}/`) API keys via the REST API. Key provisioning is managed exclusively through the Django Admin dashboard or by staff administrators.

---

### 3.3 Evaluation & Dataset Governance (`src/apps/evaluate/api_views.py`)
- **`EvaluationDatasetViewSet`, `EvaluationRunViewSet`, `EvaluationResultMetricsViewSet` Permissions:**
  - Enforce **Admin-Only** (`[IsAdminUser]`) on all evaluation endpoints.
  - External systems and non-admin users cannot trigger evaluation runs or view benchmark test results.

---

### 3.4 Usage Telemetry Governance (`src/apps/api/api_views.py`)
- **`APIUsageViewSet` Permissions:**
  - Enforce **Admin-Only** (`[IsAdminUser]`) on `/usage/`, `/usage/by_key/`, `/usage/by_endpoint/`, and `/usage/summary/`.

---

### 3.5 Client-Accessible Operations (Chat & Documents)
- **`chat` & `chatbot_feedback` (`src/apps/chat/views.py`):**
  - Verify project authorization via `X-API-Key` or user session. If the API key is scoped to `project_A`, querying `project_B` returns `403 Forbidden`.
- **`DocumentViewSet` (`src/apps/documents/api_views.py`):**
  - Allow listing, registering metadata, and deleting documents for the project linked to the authenticated user or API key.
  - Block cross-project document deletion.

---

## 4. Custom DRF Permission Classes

To enforce these rules cleanly across DRF viewsets, custom permission classes will be introduced:

```python
# Architecture Concept (For Implementation Phase)
class IsAdminOrProjectReadOnly(BasePermission):
    """
    - Allows GET/HEAD/OPTIONS for authenticated users on their assigned project.
    - Requires is_staff / is_superuser for POST, PUT, PATCH, DELETE.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user.is_staff or request.user.is_superuser)

class IsAdminUserOnly(BasePermission):
    """
    Requires request.user.is_staff or request.user.is_superuser for all methods.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser))
```

---

## 5. Security & Error Response Standards

1. **Unauthenticated Request (Missing/Invalid Token or API Key):**
   - Status: `401 Unauthorized`
   - Response: `{"error": "Authentication credentials were not provided."}`
2. **Unauthorized Action (Non-Admin attempting Admin Action):**
   - Status: `403 Forbidden`
   - Response: `{"error": "You do not have permission to perform this action. Administrator privileges required."}`
3. **Cross-Project Access Violation (API Key attempting access to another project):**
   - Status: `403 Forbidden`
   - Response: `{"error": "API key is not authorized for this project store."}`

---

## 6. Acceptance Criteria & Test Scenarios

- [ ] **Scenario 1:** Non-admin user calls `POST /rag/api/projects/` -> Receives `403 Forbidden`.
- [ ] **Scenario 2:** Non-admin user calls `DELETE /rag/api/projects/{id}/` -> Receives `403 Forbidden`.
- [ ] **Scenario 3:** Staff/Superuser admin calls `POST /rag/api/projects/` -> Receives `201 Created`.
- [ ] **Scenario 4:** Non-admin user calls `POST /rag/api/keys/` -> Receives `403 Forbidden`.
- [ ] **Scenario 5:** Non-admin user calls `POST /rag/api/runs/` -> Receives `403 Forbidden`.
- [ ] **Scenario 6:** External system with project-scoped API key calls `POST /rag/api/chat/` for its assigned project -> Receives `200 OK` with citations.
- [ ] **Scenario 7:** External system with project-scoped API key calls `POST /rag/api/chat/` for a different project -> Receives `403 Forbidden`.
- [ ] **Scenario 8:** External system with project-scoped API key calls `GET /rag/api/projects/{id}/documents/` for its assigned project -> Receives `200 OK`.
