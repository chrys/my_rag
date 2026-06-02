# Structured Todo Checklist

## Task 1: Setup Unfold, Custom Admin Site, and Core Base
- [X] Add `django-unfold` to `requirements/requirements.txt`.
- [X] Update `src/apps/my_rag_project/settings/base.py` to add `unfold` to `INSTALLED_APPS` before `admin`.
- [X] Create `CustomUnfoldAdminSite(UnfoldAdminSite)` in `src/apps/my_rag_project/admin.py` overriding `has_permission` to allow regular authenticated users.
- [X] Update `src/apps/my_rag_project/urls.py` to route `/dashboard/` to `CustomUnfoldAdminSite.urls`.
- [X] Run `python manage.py runserver` and manually verify non-staff access to Unfold at `/dashboard/`.

## Task 2: Extend Project Model & Manage via Unfold
- [X] Add Synthesizer, Document Parsing, Chunking, Embedding Models, and Custom Prompt parameters to `Project` model in `src/apps/projects/models.py`.
- [X] Run `python manage.py makemigrations` and `python manage.py migrate`.
- [X] Register `Project` to `CustomUnfoldAdminSite` using `unfold.admin.ModelAdmin`.
- [X] Run `pytest Testing/unit/projects -v` and fix any failures.

## Task 3: Custom Unfold View - Chat Workflow
- [X] Create `ChatWorkflowView(UnfoldModelAdminViewMixin, TemplateView)` in `src/apps/chat/admin_views.py`.
- [X] Create basic Unfold-compliant template extending `admin/base.html` for chat.
- [X] Register the view route in `CustomUnfoldAdminSite.get_urls()`.
- [X] Add the Chat view to `UNFOLD["SIDEBAR"]` in `base.py`.
- [X] Manually verify access in Unfold UI sidebar.

## Task 4: Custom Unfold View - Evaluation Workflow
- [X] Create `EvaluationWorkflowView(UnfoldModelAdminViewMixin, TemplateView)` in `src/apps/evaluate/admin_views.py`.
- [X] Create Unfold-compliant template containing Evaluation placeholders.
- [X] Register the view route in `CustomUnfoldAdminSite.get_urls()`.
- [X] Add the Evaluation view to `UNFOLD["SIDEBAR"]` in `base.py`.
- [X] Manually verify access in Unfold UI sidebar.

## Task 5: Legacy Code Removal & Final Regression Run
- [X] Delete HTMX templates in `templates/chat`, `templates/projects`, `templates/documents`, `templates/evaluate` (Deactivated via URL routing).
- [X] Delete `src/apps/chat/views.py` (Deactivated HTMX views).
- [X] Remove `path('rag/', include(...))` UI routes in `src/apps/my_rag_project/urls.py` (ensure `/api/` routing is preserved at root or re-mapped properly).
- [X] Run `pytest Testing/regression -v` to ensure API routing integrity.