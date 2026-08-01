# Technical Implementation Plan: Multi-Model AI Management & Obsidian Vault Integration

---

## 1. Overview & Architecture

This technical plan outlines the vertical slicing, database migrations, service abstractions, UI templates, and unit testing strategy required to implement Task 1 (Multi-Model AI Management) and Task 2 (Native Obsidian Vault Integration) as specified in `jul3-specs.md`.

---

## 2. Component Dependency Analysis

```
[Django Models & Schema]
  ├── Project (llm_model, embedding_model, immutability check)
  └── ObsidianSource & ObsidianFile (vault_path, status, file_mtime)
         │
[Service Abstractions]
  ├── LLM Router (Gemini Cloud vs Ollama Local http://localhost:11434/api/generate)
  └── Obsidian Vault Ingestion Engine (Traversal, Markdown Sanitizer, Metadata Enrichment, 3-Stage Sync)
         │
[Views & Controllers]
  ├── Project ViewSet & Admin Forms
  └── Obsidian Partial Views & Async Action Endpoints (/rag/projects/<id>/obsidian/...)
         │
[Frontend & UI]
  ├── Sources Tab Type Selector (Document vs Obsidian)
  └── Obsidian Section (Path input, buttons, status table)
         │
[Testing & Verification]
  ├── Unit Tests (Projects, Documents, Chat)
  └── End-to-End Migration & Command Verification
```

---

## 3. Data Model & Migration Strategy

### 3.1. `Project` Model Extensions (`src/apps/projects/models.py`)
- **`llm_model`**: `models.CharField`
  - Choices: `[("gemini-2.5-flash-lite", "Gemini 2.5 Flash Lite (Cloud)"), ("gemma4:12b-mlx", "Gemma 4 12B MLX (Local Ollama")]`
  - Default: `"gemini-2.5-flash-lite"`
- **`embedding_model`**: Update choices:
  - Choices: `[("models/gemini-embedding-001", "Gemini Embedding 001 (768-dim)")]`
  - Default: `"models/gemini-embedding-001"`
- **Immutability Guardrail**:
  - In `clean()`, if `self.pk` exists and `self.document_count > 0`, raise `ValidationError` if `embedding_model` has been modified.

### 3.2. `ObsidianSource` & `ObsidianFile` Models (`src/apps/documents/models.py`)
- **`ObsidianSource`**:
  - `project`: `OneToOneField(Project, related_name='obsidian_source', on_delete=models.CASCADE)`
  - `vault_path`: `models.CharField(max_length=1024)`
  - `source_type`: `models.CharField(max_length=20, choices=[('document', 'Document'), ('obsidian', 'Obsidian')], default='document')`
  - `last_synced_at`: `models.DateTimeField(null=True, blank=True)`
- **`ObsidianFile`**:
  - `obsidian_source`: `models.ForeignKey(ObsidianSource, related_name='files', on_delete=models.CASCADE)`
  - `relative_path`: `models.CharField(max_length=1024)`
  - `folder_name`: `models.CharField(max_length=255)`
  - `status`: `models.CharField(max_length=20, choices=[('PENDING', 'Pending'), ('INDEXED', 'Indexed'), ('FAILED', 'Failed')], default='PENDING')`
  - `file_mtime`: `models.FloatField()`
  - `last_indexed_at`: `models.DateTimeField(null=True, blank=True)`

---

## 4. Service Functions & Signatures

### 4.1. LLM Router (`src/apps/chat/llm_router.py`)
```python
def generate_llm_response(prompt: str, model_id: str, system_prompt: str = "") -> str:
    """
    Route LLM generation to cloud Gemini API or local Ollama server depending on model_id.
    - 'gemini-2.5-flash-lite': Uses google.genai Client
    - 'gemma4:12b-mlx': Uses requests.post to http://localhost:11434/api/generate
    """
```

### 4.2. Obsidian Ingestion Engine (`src/apps/documents/services.py`)
```python
def scan_obsidian_vault(vault_path: str) -> list[dict]:
    """Scan vault path applying exclusion rules (folders, media, canvas, untitled drafts)."""

def sanitize_obsidian_markdown(text: str) -> str:
    """Convert [[Note|Alias]] -> Alias and [[Note]] -> Note."""

def enrich_chunk_metadata(chunk: dict, folder: str, file_name: str, project_id: str) -> dict:
    """Attach folder (immediate parent), file_name, and project_id to chunk dictionary."""

def sync_obsidian_vault(project_id: str) -> dict:
    """Run 3-stage sync lifecycle: scan, compare timestamps, update status table & index."""
```

---

## 5. Verification Checkpoints

1. **Phase 1 (Models & Migrations):** Run `python manage.py makemigrations` and `python manage.py migrate`. Verify models via Django shell and unit tests.
2. **Phase 2 (LLM Router & Services):** Run unit tests in `Testing/unit/chat/` and `Testing/unit/documents/` validating dynamic routing, vault scanning, link sanitization, and metadata tagging.
3. **Phase 3 (Views & HTMX Templates):** Run server `./run.sh`, access `/rag/dashboard/` and project Sources tab, switch between Document and Obsidian modes, trigger sync/indexing, and verify status table updates.
4. **Phase 4 (Full Test Suite):** Execute `pytest` to confirm 100% regression clean test run.
