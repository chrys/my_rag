# Technical Implementation Plan: Response Mode, Document Parsers & Adaptive HyDE

## Objective
Implement the specifications in [jul2-specs.md](file:///Users/chrys/Projects/my_rag/Design/Jul-26/Jul2/jul2-specs.md) across three structured phases:
1. **Phase 1 (TASK 1)**: Response Mode Optimization (`response_mode="compact"`).
2. **Phase 2 (TASK 2)**: Document-Type Specific Node Parsers (`MarkdownNodeParser`, `CodeSplitter`, `HierarchicalNodeParser`, `SentenceSplitter`).
3. **Phase 3 (TASK 3)**: Adaptive HyDE & Query Transformation Engine.

---

## 1. Architecture & Dependency Analysis

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Project & Document Models                        │
│ - Project: response_mode ("compact"), use_hyde (BooleanField)          │
│ - Document: chunking_strategy ("auto_detect", etc.)                    │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
         ┌─────────────────────────┴─────────────────────────┐
         ▼                                                   ▼
┌──────────────────────────────┐            ┌──────────────────────────────┐
│ Ingestion Pipeline           │            │ Chat & Query Engine          │
│ - select_node_parser()       │            │ - ResponseMode.COMPACT       │
│ - CodeSplitter fallback      │            │ - Single-turn HyDE Router    │
│ - IngestionPipeline workers  │            │ - Final Synthesis            │
└──────────────────────────────┘            └──────────────────────────────┘
```

---

## 2. Component Implementation Details

### Phase 1: TASK 1 — Response Mode Optimization
- **Model Modifications (`src/apps/projects/models.py`)**:
  - Add `response_mode` choice field (`compact`, `refine`, `tree_summarize`, default=`"compact"`).
- **Admin Configuration (`src/apps/projects/admin.py`)**:
  - Add `response_mode` to the Unfold Admin fieldsets.
- **Query Engine Updates (`src/apps/chat/views.py`, `src/postgres_rag.py`)**:
  - Pass `response_mode=project.response_mode` to `as_query_engine()`.

### Phase 2: TASK 2 — Document-Type Specific Node Parsers
- **Model Modifications (`src/apps/documents/models.py`)**:
  - Add `chunking_strategy` choice field (`auto_detect`, `markdown`, `code`, `hierarchical`, `sentence`, `project_default`, default=`"auto_detect"`).
- **Service Factory (`src/apps/documents/services.py`)**:
  - Implement `select_node_parser(file_path: str, strategy: str)`.
  - Handle missing dependencies (e.g. `tree-sitter`) with fallback to `SentenceSplitter(chunk_size=512)` and warning logging.
- **Ingestion Pipeline (`src/apps/documents/services.py`)**:
  - Connect `select_node_parser` inside `LlamaIndexIngestionPipeline`.
- **UI & HTMX Partials (`templates/partials/document_upload.html`, `templates/partials/document_items.html`)**:
  - Add chunking strategy selector dropdown to document upload form.
  - Render strategy badge tags on document list.

### Phase 3: TASK 3 — Adaptive HyDE Engine & Query Transformation
- **Model Modifications (`src/apps/projects/models.py`)**:
  - Add `use_hyde` boolean field (`default=False`).
- **HyDE Service (`src/apps/chat/services.py` / `src/apps/chat/views.py`)**:
  - Single-turn intent classifier and HyDE document generator using raw text completion + regex extraction.
  - Classification into `DIRECT_LOOKUP` (bypasses HyDE) vs `CONCEPTUAL` (generates hypothetical passage for vector query).

---

## 3. Verification & Testing Strategy
- Django migrations check: `python manage.py makemigrations` and `python manage.py test`.
- Unit test suites covering Project/Document schema changes, parser selection with mock missing dependencies, and HyDE query router logic.
