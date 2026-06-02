# Task 1: New Dashboard 

## 1. Objective and Target Users
*   **Goal:** Replace the existing dashboard with a modern, native `django-unfold` interface.
*   **Target Users:** All authenticated users, meaning the `django-unfold` interface will serve as the primary product frontend, not just a staff tool.
*   **Key Transitions:** The current `/rag/` paths and legacy Bootstrap templates will be completely removed. Unfold will be mounted at `/admin` and serve as the main application interface.

## 2. Core Features & Acceptance Criteria
*   **Main Navigation:**
    *   **Projects:** View, add (Google, Local, Postgres RAG), and delete projects.
    *   **Evaluation:** A custom Unfold admin view where a project can be selected for evaluation (with placeholders for Retrieval, Generation, and Ingestion evaluation types).
    *   **Parameters:** Project-level settings managed natively through the Unfold model forms.
    *   **Chat:** A custom Unfold admin view/component to handle chat interactions, completely replacing the existing HTMX Chat tab.
*   **Parameter Placeholders:** Add database model fields and UI inputs for features marked "to be defined later":
    *   *Synthesizer:* Enabled/Disabled toggle.
    *   *Document Parsing:* PyMUPDF, markitdown.
    *   *Chunking:* Fixed-size, Sentence/paragraph, Recursive, Document-structure, Semantic.
    *   *Embedding Models:* Gemini embedding 1, Google embedding 2, fkEmbeddingGemma.
    *   *Custom Prompt & Indexed Sources:* Standard management capabilities.

## 3. Project Structure & Dependencies
*   **Dependencies:** Install `django-unfold`.
*   **URL Routing:** Remove `apps/chat/views.py` HTMX views, `templates/`, and routes pointing to `/rag/`. Ensure the root or `/admin` points to the new Unfold interface.
*   **Admin Customization:** 
    *   Create custom Unfold `ModelAdmin` classes for `Project` to handle the new Parameter fields.
    *   Create custom Unfold views for Chat and Evaluation workflows, registering them in the Unfold navigation menu.
    *   Ensure authentication logic permits regular authenticated users to access the required Unfold views (typically Django admin requires `is_staff=True`, so we may need a custom `AdminSite` or to adjust permissions).

## 4. Code Style
*   Use f-strings and double quotes.
*   Use type hints and NumPy-style docstrings for non-trivial Python code.
*   Follow PEP 8.
*   Leverage `django-unfold` native styling and components (Tailwind-based) over custom CSS.

## 5. Testing Strategy
*   **Unit Tests (`Testing/unit/`):** Test the custom Unfold admin views, permission access, and the new model fields on the `Project` model.
*   **Regression Tests:** Ensure existing DRF APIs (`/api/`) are not disrupted by the removal of the `/rag/` dashboard routes.

## 6. Boundaries
*   **Always do:** Use Django's ORM. Strictly use Context7 to look up up-to-date Unfold documentation for custom pages/views.
*   **Ask first about:** Modifying the default Django User model (e.g., forcing `is_staff=True` for all users vs. creating a custom `AdminSite` for Unfold).
*   **Never do:** Do not implement the underlying logic for the "to be defined later" parameters (only build the DB fields and UI). Do not introduce any frontend framework outside of what Unfold provides natively.

## 7. Implemented Architecture and Customizations

*   **Admin Mount Point:** Unfold is mounted at `/dashboard/` using `CustomUnfoldAdminSite(name="custom_admin")` in `src/apps/my_rag_project/admin.py` to allow regular active authenticated users access without requiring `is_staff` privileges.
*   **Project Form Tabbed Layout:**
    *   **Parameters Tab:** Groups core project identifiers and settings (`project_id`, `display_name`, `description`, `is_active`, `synthesizer`, `document_parsing`, `chunking`, `embedding_model`, `custom_prompt`).
    *   **Sources Tab:** Groups storage configurations, statistics, and uploader features (`storage_type`, `external_store_id`, `document_count`, `last_indexed_at`, `created_at`, `updated_at`, `document_uploader_and_list`).
*   **Integrated Document Manager (HTMX-Powered):**
    *   Embedded inside the **Sources** tab using a custom `document_uploader_and_list` readonly admin field rendering the [project_sources_tab.html](file:///Users/chrys/Projects/my_rag/templates/admin/projects/project_sources_tab.html) template.
    *   Integrates native HTMX-driven document uploads and lists linking directly to remote ingestion pipelines.
    *   Provides explicit visual error tracking for database connection dropouts (e.g., presenting full `FAILED` tracebacks inline next to the affected file).
*   **Healed Routing and Model Fields:**
    *   Preserved `/rag/` routing specifically for document uploader endpoints (`/rag/documents/`) inside `urls.py`.
    *   Added a custom `.save()` trigger on the `Project` model in `models.py` to automatically auto-generate clean, backend-compliant `project_id` strings if left blank during admin creation.

