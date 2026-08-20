# Specification: Google File Search Integration, Ingestion Hygiene & Unified Document Pipeline (Aug 3)

---

## 1. Objective & Scope

### Problem Statement & Background Context
The platform supports multiple storage backends (`postgres`, `local`, and `google`), but the **Google File Search (GFS)** integration currently operates with minimal validation, hardcoded model identifiers, lack of metadata enrichment, and unhandled server-side errors. Additionally, document parsing parameters (`document_parsing` vs `use_markitdown`) are fragmented across the codebase.

This specification unifies the document parsing architecture, establishes a robust **Document Format, Hygiene & Deduplication Gate**, implements a **3-Step Metadata Extraction & User Enrichment Pipeline** for Google File Search, defines project configuration parameters tailored for GFS, and lays the foundation for **GFS Metadata-Filtered Retrieval**.

### Target Users & Architectural Placement
- **Target Audience:** Enterprise knowledge managers, developers, and administrators configuring managed Google File Search knowledge stores with automated metadata classification and data hygiene.
- **Architectural Placement:**
  - `src/google_file_search.py`: Core client interface for Google GenAI File Search stores, indexing, querying, and metadata filter translation.
  - `src/apps/projects/`: Project lifecycle, GFS parameter constraints, and admin configuration workflows.
  - `src/apps/documents/`: Pre-upload hygiene, SHA-256 deduplication registry, MarkItDown conversion, system/AI metadata extraction, and review modals.
  - `src/apps/chat/`: Grounded query execution using model selection and GFS `FileSearch` tool configuration.

---

### Resolved Design Decisions (Grill-Me Alignment)

1. **Duplicate File & Hash Collision Policy:**
   - When a file's SHA-256 hash matches an existing record in the project's Local State Registry, prompt the user with an interactive dialog asking whether to **Skip** the upload or **Force Re-upload** (which deletes the old GFS document resource and re-indexes the fresh file).
2. **Metadata Review UI Flow:**
   - Use an **Interactive HTMX Modal**: Selecting a file triggers pre-flight hygiene checks and Gemini Flash AI pre-extraction in the background, renders an editable metadata review modal partial, and finalizes the upload when the user clicks **"Confirm & Index"**.
3. **AI Pre-Extraction Failure & Fallback Policy:**
   - If `gemini-2.5-flash-lite` pre-extraction fails (due to rate limit, network timeout, or API error), **gracefully fall back** to the extracted Python system metadata, show a subtle alert badge indicating that AI classification was temporarily unavailable, and allow the user to manually add tags in the review modal without blocking upload.
4. **Store Provisioning Lifecycle:**
   - **Immediate Provisioning:** Call `client.file_search_stores.create()` during Project creation in Django, persist `external_store_id`, and fail early with a clear error message if Google credentials or permissions are invalid.
5. **Noisy Artifact Stripping Approach:**
   - **Heuristic & Regex Engine:** Strip pagination markers (`Page X of Y`, `- X -`, trailing digits), running page headers/footers across page boundaries, and legal boilerplate using fast, deterministic heuristic pattern matching.

---

### Core Feature Specifications

#### 1. Missing Functionalities & Architecture Unification
1. **Synthesizer Scope:**
   - The Synthesizer module belongs exclusively to LlamaIndex-driven pipelines (PostgreSQL RAG).
   - For Google File Search projects, the Synthesizer parameter is strictly **disabled / hidden**, as Gemini performs unified grounding and answer generation directly via native tool calling.
2. **Chunking Options:**
   - Expand local/Postgres chunking strategies (semantic, sentence, markdown-aware).
   - For GFS projects, chunking is locked to **`Default (Managed)`**, delegating vector segmentation to Google's cloud pipeline.
3. **Unified MarkItDown Parameter:**
   - Consolidate `document_parsing = "markitdown"` (the model-level setting on `Project`) and `use_markitdown` (the runtime execution toggle).
   - When enabled on any project, non-markdown documents (PDF, DOCX, PPTX, XLSX, HTML) are converted to clean Markdown before downstream processing.

---

#### 2. Google File Search Project Parameter Configuration (`storage_type = 'google'`)
When creating or editing a project with `storage_type='google'`, enforce the following parameter rules:

| Parameter | Configuration | Technical Rationale & Behavior |
| :--- | :--- | :--- |
| **Response Mode** | **Disabled / Hidden** | GFS leverages Gemini's native `Tool(file_search=...)` grounding in a single generative step; iterative LlamaIndex modes (`compact`, `refine`, `tree_summarize`) do not apply. |
| **HyDE (`use_hyde`)** | **Disabled** | GFS tool calling relies on exact user query semantics for retrieval and source citation generation; hypothetical query transformations are bypassed. |
| **Synthesizer** | **Disabled** | GFS bypasses LlamaIndex synthesis in favor of direct Gemini model generation. |
| **Chunking** | **Default (Managed)** | Locked to `Default`. Uses Google's server-side structure/semantic chunking. |
| **Embedding Model** | **Default** | Locked to `Default`. Vector generation is managed server-side by Google (`text-embedding-004`). |
| **LLM Model** | **Restricted Choices** | Available models for GFS are strictly:<br>1. `gemini-2.5-flash-lite` *(fastest & most cost-effective)*<br>2. `gemini-3.5-flash-lite`<br>3. `gemini-3.7-flash` |

---

#### 3. Pre-Upload Document Format, Hygiene & Deduplication Gate
Before a document is indexed into Google File Search, it must pass through an automated four-phase hygiene and deduplication gate:

```
[Raw Upload] ──> [1. Pre-Flight Validation] ──> [2. Hash Deduplication] ──> [3. Integrity & Hygiene] ──> [4. Artifact Stripping] ──> [Metadata Pipeline]
```

1. **Pre-Flight Validation & Sanity Checks:**
   - **Allowed Formats:** Strictly whitelist supported extensions (`.pdf`, `.docx`, `.txt`, `.md`, `.html`, `.pptx`, `.xlsx`).
   - **Empty File Guard:** Reject 0-byte or whitespace-only files with a `400 Bad Request`.
   - **File Size Limit:** Enforce a strict single-file maximum limit of **100 MB**. Reject oversized files immediately with a `413 Payload Too Large` / `400 Bad Request`.
2. **Local State Registry & Hash-Check Deduplication:**
   - **SHA-256 Hashing:** Calculate a SHA-256 hash of the binary file stream before upload.
   - **Local State Registry:** Persist registry records in Django's database (`Document` model) tracking:
     - `source_file_id`: Internal document ID.
     - `store_file_id`: Remote Google Document resource name (`fileSearchStores/{store_id}/documents/{doc_id}`).
     - `content_hash`: Cryptographic SHA-256 hash string.
     - `indexed_at`: UTC timestamp of successful indexing.
   - **Deduplication Check:** If an identical `content_hash` already exists within the target project, prompt the user with an option to skip or force a re-upload (which deletes the old GFS index and re-indexes).
3. **Document Integrity & Format Normalization:**
   - **Integrity Verification:** Ensure binary stream readability; detect and reject password-encrypted/DRM-locked PDFs/DOCXs.
   - **Encoding Sanitization:** Enforce clean UTF-8 encoding; strip non-printable ASCII control characters (preserving standard linebreaks and tabs).
   - **Markdown Normalization:** If `use_markitdown` is enabled, convert complex binaries into clean Markdown. Normalize irregular indentation and line breaks (`\r\n` -> `\n`).
4. **Noisy Artifact Stripping:**
   - **Headers & Footers:** Strip repeated running page headers and footers across paginated sheets.
   - **Pagination Markers:** Remove standalone page counters (e.g., `Page 1 of 45`, `- 12 -`).
   - **Boilerplate & Disclaimers:** Filter out cookie notices, standard legal boilerplate, and privacy footers.
   - **HTML Scraped Content:** Strip residual DOM tags, navigation bars, scripts, and CSS wrappers from scraped web content.

---

#### 4. 3-Step Metadata Extraction & User Enrichment Pipeline

```
[Cleaned Document]
       │
       ▼
[Step 1: Python System & File Extraction] (file_name, size, ext, uploaded_by, page_count, author)
       │
       ▼
[Step 2: Gemini Flash AI Pre-Extraction]  (document_type, department, language, primary_topic)
       │
       ▼
[Step 3: User Review & Enrichment Modal]  (Inspect, add/edit key-value pairs)
       │
       ▼
[Upload & Index to GFS Store]             (custom_metadata: list of max 20 typed key-values)
```

1. **Step 1: System & Embedded Context Extraction (Python Utilities):**
   - Automatically extract technical parameters:
     - `file_name`: Uploaded filename.
     - `file_extension`: Normalized extension (e.g., `pdf`, `docx`, `md`).
     - `file_size_kb`: Numeric size in KB.
     - `uploaded_at`: ISO 8601 date (`YYYY-MM-DD`).
     - `uploaded_by`: Username/ID of the uploading user.
   - Extract embedded properties when present:
     - PDF: `page_count` (numeric) and embedded `author` (string) via `pypdf`.
     - DOCX: Embedded document properties (e.g. `title`, `author`).
2. **Step 2: AI-Powered Pre-Extraction (`gemini-2.5-flash-lite`):**
   - Extract the first 3 pages of text (or first ~3,000–5,000 characters).
   - Send excerpt to `gemini-2.5-flash-lite` with `response_mime_type="application/json"` and a structured Pydantic/JSON schema.
   - Auto-classify business attributes:
     - `document_type`: e.g., `contract`, `invoice`, `report`, `specification`, `meeting_notes`.
     - `department`: e.g., `finance`, `legal`, `engineering`, `hr`, `marketing`.
     - `language`: e.g., `en`, `es`, `fr`, `de`.
     - `primary_topic`: Concise topic summary (e.g., `quarterly_financial_review`).
3. **Step 3: User Review & Enrichment UI (Interactive HTMX Modal):**
   - Present auto-extracted metadata in an interactive review modal before upload finalization.
   - Allow users to add, edit, or remove key-value tags.
4. **GFS Metadata Rules & Constraints:**
   - **Max 20 Entries:** Up to 20 key-value pairs per document.
   - **Strict Value Typing:** Each item must contain strictly either `string_value` or `numeric_value` (mutually exclusive):
     ```python
     [
         {"key": "department", "string_value": "finance"},
         {"key": "file_size_kb", "numeric_value": 142.5},
         {"key": "page_count", "numeric_value": 3}
     ]
     ```
   - **Immutability:** Metadata cannot be modified once indexed in a Google File Search store. Updates require document deletion and re-indexing.

---

#### 5. GFS Retrieval & Metadata Filtering Support (Foundation)
- **Core Service Integration:** Extend `src/google_file_search.py` (`ask_store_question`) to support an optional `metadata_filters` parameter.
- **Filter Syntax:**
  - String comparisons: `key == "value"`, `key != "value"`
  - Numeric comparisons: `>`, `>=`, `<`, `<=`
  - Boolean expressions: `AND`, `OR`, `NOT`
- **Tool Configuration:**
  ```python
  file_search_config = genai_types.FileSearch(
      file_search_store_names=[store_id],
      metadata_filter=filter_expression
  )
  ```
- **Scope Boundary:** Implement the query builder and service methods in `src/google_file_search.py`. End-to-end wiring into the Chat UI, Evaluation runs, and DRF API views is explicitly deferred to a later phase.

---

## 2. Common & Required Commands

### Environment Setup
```bash
# Activate virtual environment
source .venv/bin/activate

# Verify environment dependencies
pip install -r requirements.txt
```

### Database Migrations
```bash
# Generate migrations for new Document and Project model fields
DJANGO_ENV=development python manage.py makemigrations

# Apply migrations
DJANGO_ENV=development python manage.py migrate
```

### Local Development Server
```bash
# Run local Django server
DJANGO_ENV=development python manage.py runserver
```

### Automated Unit Testing
```bash
# Run GFS and document unit tests
DJANGO_ENV=testing pytest Testing/unit/documents/ -v

# Run projects and parameter validation tests
DJANGO_ENV=testing pytest Testing/unit/projects/ -v

# Run chat integration tests
DJANGO_ENV=testing pytest Testing/unit/chat/ -v

# Run complete test suite
DJANGO_ENV=testing pytest Testing/unit/ -v
```

---

## 3. Project Structure & Key File Mappings

```
src/
├── google_file_search.py        # GFS store operations, metadata upload formatting, and filtered query execution
├── optional_dependencies.py     # LazyModuleProxy for resilient optional dependency loading
└── apps/
    ├── projects/
    │   ├── models.py            # Project model, storage_type='google' parameter validation, choices constraints
    │   ├── views.py             # Project creation, deletion, and immediate GFS store provisioning lifecycle
    │   └── serializers.py       # DRF serialization for Project parameters and choices
    ├── documents/
    │   ├── models.py            # Document model updated with content_hash, store_file_id, custom_metadata
    │   ├── views.py             # Pre-upload hygiene gate, 100MB check, deduplication modal, review modal handling
    │   └── services.py          # Metadata extraction pipeline (Python stats + Gemini Flash auto-classifier)
    └── chat/
        └── views.py             # Chat dispatch routing queries to GFS with model selection and system prompt

templates/
└── partials/
    ├── document_list.html       # Document list displaying GFS indexing status and metadata attributes
    ├── document_upload_modal.html # Modal for file selection, hygiene status, and metadata review/editing
    ├── document_duplicate_modal.html # Modal for duplicate collision handling (Skip vs Force Re-upload)
    └── project_form.html        # Dynamic form adjusting parameters when storage_type='google' is selected

Testing/
└── unit/
    ├── documents/
    │   ├── test_gfs_hygiene.py        # Unit tests for format validation, 100MB limit, and artifact stripping
    │   ├── test_gfs_deduplication.py  # Unit tests for SHA-256 hashing and Local State Registry duplicate prevention
    │   └── test_gfs_metadata.py       # Unit tests for Python/Gemini metadata extraction and GFS formatting
    └── projects/
        └── test_gfs_parameters.py     # Unit tests verifying GFS parameter locks (HyDE, Synthesizer, LLM models)
```

---

## 4. Code Style & Guidelines

- **PEP 8 Compliance:** Follow standard Python formatting conventions; use 4 spaces for indentation.
- **String Formatting:** Use double quotes (`"..."`) and Python 3.10+ f-strings (avoid `%` or `.format()` formatting).
- **Type Annotations & Docstrings:** Provide explicit type hints (`list[dict]`, `str | None`, etc.) and Google-style docstrings for all service functions.
- **Identifier Separation:**
  - Always use `project.project_id` for URL routing, frontend tokens, and Django ORM lookups.
  - Never expose or use `project.external_store_id` (e.g., `fileSearchStores/...`) as a URL parameter (as it contains slashes).
- **Error Handling & Graceful Degradation:**
  - Wrap external Google GenAI API calls in robust `try/except` blocks.
  - Handle rate limits (`429`), permission errors (`403`), and invalid stores with descriptive JSON/HTML error partials.
- **Frontend Interactivity:**
  - Use Vanilla JS + HTMX (`hx-post`, `hx-target`, `hx-swap`) for dynamic UI updates and modal flows. Avoid introducing third-party JS frameworks.

---

## 5. Testing Strategy

### Unit Tests (`Testing/unit/`)
1. **Hygiene & Sanity Checks (`Testing/unit/documents/test_gfs_hygiene.py`):**
   - Verify rejection of unsupported file extensions.
   - Verify rejection of 0-byte/empty files.
   - Verify rejection of files exceeding the 100 MB limit.
   - Test stripping of headers, footers, page numbers, and HTML boilerplate.
2. **Hash Deduplication & State Registry (`Testing/unit/documents/test_gfs_deduplication.py`):**
   - Test SHA-256 hash generation for binary files.
   - Verify that uploading an identical file detects existing `content_hash` and offers duplicate handling.
   - Verify database persistence of `source_file_id`, `store_file_id`, `content_hash`, and `indexed_at`.
3. **Metadata Extraction & Formatting (`Testing/unit/documents/test_gfs_metadata.py`):**
   - Test Python extraction of file size, date, user, and PDF page count.
   - Test mocked `gemini-2.5-flash-lite` JSON classification.
   - Verify metadata formatter ensures strictly typed `string_value` or `numeric_value` up to 20 items.
4. **Project Parameter Validation (`Testing/unit/projects/test_gfs_parameters.py`):**
   - Verify that when `storage_type == 'google'`, `chunking` and `embedding_model` lock to `Default`.
   - Verify `response_mode`, `use_hyde`, and `synthesizer` are disabled.
   - Verify only permitted Gemini models (`gemini-2.5-flash-lite`, `gemini-3.5-flash-lite`, `gemini-3.7-flash`) can be selected.
5. **Retrieval Filter Query Builder (`Testing/unit/chat/test_gfs_retrieval_filters.py`):**
   - Test translation of metadata filter dicts into valid GFS filter expressions (`==`, `!=`, `<`, `>`, `AND`, `OR`).

---

## 6. Guardrails & Boundaries

### Dos (Always Do)
- **Always** calculate SHA-256 content hashes and verify against the Local State Registry before issuing remote GFS upload calls.
- **Always** validate that each metadata entry passed to GFS has either `string_value` or `numeric_value` (never both) and that the total count $\le 20$.
- **Always** delete temporary files in a `finally` block after processing.
- **Always** maintain `project_id` as the internal routing key and keep `external_store_id` isolated for Google API calls.
- **Always** write comprehensive unit tests under `Testing/unit/` with mocked Google API responses.

### Ask Before (Decisions Requiring User Alignment)
- **Ask Before** adding new document MIME types beyond the standard whitelist.
- **Ask Before** modifying existing PostgreSQL RAG data models or tables.
- **Ask Before** wiring GFS metadata filtering into active user-facing Chat or Evaluation views.

### Don'ts (Never Do)
- **Never** send un-sanitized or oversized (>100 MB) files to the Google File Search API.
- **Never** use `external_store_id` in URL route parameters.
- **Never** execute git commands directly (`git commit`, `git push`, etc.).
- **Never** hardcode API keys or secret credentials in source files.
- **Never** break backwards compatibility for existing `local` and `postgres` projects.