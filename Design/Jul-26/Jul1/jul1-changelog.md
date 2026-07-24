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
