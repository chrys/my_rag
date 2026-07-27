# Jul2 Error Log & AI Guardrails

This document tracks issues encountered during the Jul2 implementation sprint and defines generic instructions to prevent them in future tasks.

---

## 1. Encountered Errors & Root Causes

### Error 1: Database Migration Omission
- **Error**: `django.db.utils.OperationalError: no such column: projects_project.response_mode`
- **Root Cause**: Model schema changes were made in `models.py`, but database migrations (`makemigrations` / `migrate`) were not executed prior to starting the development server and rendering dashboard views.

### Error 2: Obsolete Admin Field References
- **Error**: `django.core.exceptions.FieldError: Unknown field(s) (use_structural_grading) specified for Project`
- **Root Cause**: A model field (`use_structural_grading`) was removed in a database migration, but `ProjectAdmin.fieldsets` in `admin.py` was not audited to remove the deleted field reference.

### Error 3: Obsolete View Field Access
- **Error**: `AttributeError: 'Project' object has no attribute 'use_structural_grading'`
- **Root Cause**: A deleted model field (`use_structural_grading`) was still referenced directly in `src/apps/documents/views.py` (Line 218) during document upload, causing a runtime AttributeError.

### Error 4: Accidental Variable Deletion during Refactoring
- **Error**: `NameError: name 'index' is not defined` in `src/apps/chat/views.py` (Line 148).
- **Root Cause**: During a code edit, the line initializing `index = VectorStoreIndex.from_vector_store(vector_store, embed_model=embed_model)` was accidentally omitted before `query_engine = index.as_query_engine(...)`.

### Error 5: Omission of Supported File Extensions Validation Set
- **Error**: `HTTP 400 Bad Request: Unsupported file type: .py` during document upload.
- **Root Cause**: `SUPPORTED_TEXT_FILE_EXTENSIONS` set in `src/apps/documents/views.py` only contained `{'.pdf', '.txt', '.md'}` and was not expanded when adding `.py`, `.js`, `.ts`, `.html` code parser support in TASK 2.

---

## 2. Generic AI Instructions to Prevent Errors

### Rule 1: Mandatory Database Migration Execution
Whenever adding, modifying, or deleting fields on Django models (`models.py`), the AI MUST automatically generate and apply database migrations immediately:
```bash
python manage.py makemigrations
python manage.py migrate
```
Do NOT mark a task as complete or test views in the browser until migrations have been successfully executed.

### Rule 2: Synchronized Admin Fieldset & Form Auditing
Whenever model fields are added, modified, or removed, the AI MUST audit `admin.py` and ensure that all `ModelAdmin.fieldsets`, `fields`, and `ModelForm` definitions precisely match the active model fields, removing any references to deleted/obsolete fields.

### Rule 3: Workspace-Wide Search for Deleted Model Attributes
Whenever a model field is removed, deleted, or renamed, the AI MUST perform a codebase-wide search (`grep_search`) across views, services, tasks, and templates to update or remove all references to the obsolete attribute, or safely access it using `getattr(obj, 'attr_name', default)`.

### Rule 4: Scope & Variable Dependency Verification During Edits
When modifying code blocks inside functions, the AI MUST verify that all referenced local variables (`index`, `vector_store`, `llm`, etc.) remain declared and initialized in local scope prior to usage.

### Rule 5: Synchronized Validation Constants Audit
When extending feature capabilities to support new file extensions or formats, the AI MUST audit and update all validation sets and constants (such as `SUPPORTED_TEXT_FILE_EXTENSIONS`) across upload views and validators.
