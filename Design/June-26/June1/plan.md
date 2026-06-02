# Comprehensive Master Plan

## 1. Goal and Dependency Graph
The goal is to replace the existing dashboard with a modern, native `django-unfold` interface that serves as the primary frontend for all authenticated users, effectively replacing the current legacy `/rag/` paths.

**Dependency Graph (Bottom-Up Implementation):**
1.  **Foundation (Dependencies & Site Base):** Install `django-unfold`. Configure a custom `UnfoldAdminSite` subclass to override the `has_permission` check (so all authenticated users can access the dashboard, bypassing the default `is_staff` requirement).
2.  **Data Models:** Add the requested "To be defined later" parameter placeholders to the `Project` model in `src/apps/projects/models.py`.
3.  **UI Components (Admin Classes & Custom Views):** 
    *   Build a custom `ModelAdmin` for `Project` rendering the new parameters natively.
    *   Build custom class-based views inheriting from `UnfoldModelAdminViewMixin, TemplateView` for the Chat and Evaluation interfaces.
4.  **Navigation & Routing:** Configure the `UNFOLD["SIDEBAR"]` settings in `base.py` to register our custom models and views to the navigation sidebar. Route `/dashboard/` in the root URLs to our new Custom Admin Site.
5.  **Clean-Up:** Remove legacy `/rag/` routes, `apps/chat/views.py` HTMX endpoints, and legacy Bootstrap HTML templates.

## 2. Vertical Task Slices

### Task 1: Setup Unfold, Custom Admin Site, and Core Base
*   **Description:** Install `django-unfold`. Create a custom `UnfoldAdminSite` in `src/apps/my_rag_project/admin.py` overriding `has_permission(self, request)` to allow `request.user.is_active`. Add `unfold` to `INSTALLED_APPS` (before `django.contrib.admin`). Configure root `urls.py` to point `/dashboard/` to the custom admin site.
*   **Acceptance Criteria:** A non-staff authenticated user can visit `/dashboard/` and successfully see the Unfold dashboard interface.
*   **Verification:** `python manage.py runserver` - visually test logging in with a non-staff test user. Run `pytest Testing/unit/` to ensure no base URL regression.

### Task 2: Extend Project Model & Manage via Unfold
*   **Description:** Add fields to `src/apps/projects/models.py`: Synthesizer (Boolean), Document Parsing (CharField choices), Chunking (CharField choices), Embedding Models (CharField choices), and Custom Prompt (Boolean/Text field connection). Generate migrations. Create `ProjectAdmin` in `src/apps/projects/admin.py` mapping to our custom site.
*   **Acceptance Criteria:** The `Project` model handles the new configuration schemas. The Django Unfold UI successfully displays the model and enables creation/editing using Unfold's Tailwind models.
*   **Verification:** Run `pytest Testing/unit/projects -v`. Load the UI at `/dashboard/projects/project/` to confirm layout.

### Task 3: Custom Unfold View - Chat Workflow
*   **Description:** Implement `ChatWorkflowView` inheriting from `unfold.views.UnfoldModelAdminViewMixin` and `TemplateView`. Register this in a custom `urls.py` override in the AdminSite, and add it to `UNFOLD["SIDEBAR"]["navigation"]` in settings.
*   **Acceptance Criteria:** The sidebar contains a "Chat" link. Clicking it renders the Chat UI within the Unfold administrative chrome.
*   **Verification:** Validate UI rendering and ensure users without custom permissions can still load the `chat` template.

### Task 4: Custom Unfold View - Evaluation Workflow
*   **Description:** Implement `EvaluationWorkflowView` leveraging the same Unfold mixins. Add placeholders for Retrieval, Generation, and Ingestion evaluation types in the view's template block. Register to the Sidebar nav similarly.
*   **Acceptance Criteria:** "Evaluation" is visible in the sidebar, and clicking it displays the placeholder workflow correctly styled inside Unfold.
*   **Verification:** Visual test to ensure view is available.

### Task 5: Legacy Code Removal & Final Regression Run
*   **Description:** Delete `src/apps/chat/views.py` (legacy HTMX views), `templates/chat/`, `templates/documents/`, `templates/projects/`, and `templates/evaluate/`. Remove the `rag/` include path in `src/apps/my_rag_project/urls.py`. 
*   **Acceptance Criteria:** All legacy paths are eradicated. DRF API endpoints residing in `/rag/api/` should be properly re-mapped or tested to ensure no regressions.
*   **Verification:** Run `pytest Testing/regression -v` and strictly verify `/api/` endpoints behave appropriately.