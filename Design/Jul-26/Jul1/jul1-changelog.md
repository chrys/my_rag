# Sprint Changelog - Jul1 (July 2026)

## Features Added

### 1. Manual Evaluation Method in Evaluation Workflow
- **Third Evaluation Method**: Added **Manual Evaluation** alongside RAGAS and Synthetic QA in the RAG Evaluation Workspace dashboard.
- **Flexible Question Input**:
  - **Type Questions**: Input test questions line-by-line via text area.
  - **Upload CSV**: Upload CSV files containing a `questions` or `question` column header using an interactive drag-and-drop file picker with selection confirmation badges.
- **RAG API Answer Generation**:
  - Per-row "Generate Answer" buttons to fetch answers for individual questions.
  - "Generate All Answers" batch button for bulk execution across all pending questions in a session.
  - Invokes project's native vector store retriever and Gemini LLM synthesis, capturing supporting context chunk citations in a collapsible viewer.
- **Interactive Human Color Scoring**:
  - Judge Q&A pairs manually using color rating pills:
    - 🔴 **Bad** (`RED`)
    - 🟠 **Needs Improvement** (`ORANGE`)
    - 🟢 **Good** (`GREEN`)
  - Live summary metrics bar tracking totals for Good, Needs Improvement, Bad, and Unrated items with instant HTMX feedback.
- **Database Persistence**:
  - Created `ManualEvaluationRun` and `ManualEvaluationItem` database models.
  - Applied Django database migration `0002_manualevaluationrun_manualevaluationitem.py`.
- **Unit Test Coverage**:
  - Added test suite in `Testing/unit/evaluate/test_manual_eval.py` covering model creation, CSV/text question parsing, answer generation services, rating updates, and views (9 unit tests passed).

### 2. Project Parameters & Custom Prompt Management
- **Parameters Tab Field Cleanup**:
  - Removed unsupported placeholder choices (`pymupdf` from `document_parsing`; `google-2` and `gemma` from `embedding_model`) on the `Project` model ([models.py](file:///Users/chrys/Projects/my_rag/src/apps/projects/models.py#L74-L100)).
- **Immutable Parameter Field Protection**:
  - Identified parameters that cannot change after indexing (`embedding_model`, `document_parsing`, `use_markitdown`, `chunking`).
  - Enhanced `ProjectAdminForm.__init__` in [admin.py](file:///Users/chrys/Projects/my_rag/src/apps/projects/admin.py#L31-L39) to automatically disable these fields (`disabled=True`) and display a lock warning badge (`"🔒 Locked: Cannot be changed after the first source has been indexed."`) when documents have already been indexed in the project (`document_count > 0` or documents exist).
- **Tab Layout Restructuring**:
  - Relocated `use_structural_grading` from the **Parameters** tab to the **Sources** tab in `ProjectAdmin.fieldsets` ([admin.py:L99](file:///Users/chrys/Projects/my_rag/src/apps/projects/admin.py#L99)) to keep quality inspection gates grouped with document management.
- **Dynamic Custom Prompt Interface**:
  - Created `ProjectAdminForm` with an inline `custom_prompt_text` textarea field for entering system prompt instructions.
  - Automatically creates/updates the related `SystemPrompt` database model on save and auto-enables `custom_prompt = True` when text is provided.
  - Added [custom_prompt_toggle.js](file:///Users/chrys/Projects/my_rag/static/admin/js/custom_prompt_toggle.js) to dynamically show or hide the prompt text area when the `custom_prompt` checkbox is toggled.
- **Documentation & Unit Tests**:
  - Updated [FUNCTIONALITY.md](file:///Users/chrys/Projects/my_rag/Documentation/Project/FUNCTIONALITY.md#L28-L46) with a detailed reference guide covering parameter fields, immutability constraints, and tab placements.
  - Added automated tests in [test_admin_prompt_views.py](file:///Users/chrys/Projects/my_rag/Testing/unit/admin/test_admin_prompt_views.py#L117-L172) and [test_models.py](file:///Users/chrys/Projects/my_rag/Testing/unit/projects/test_models.py#L236) covering custom prompt saving, choice updates, and field locking when sources exist (all tests passed).

