# Refined Specification: Sprint June-26 Features

This document provides a highly structured and comprehensive specification covering the five main RAG Dashboard tasks for the **Sprint June-26** release. 

---

## 1. OBJECTIVE

The core objective is to deliver advanced project, document ingestion, quality control, and automated evaluation features in the Django RAG Dashboard.

### Target Users
- **RAG Dashboard Users:** Need higher retrieval accuracy, automatic document lifecycle handling (expiration tracking), and quality verification during ingestion.
- **AI/RAG Admins:** Need tools to run programmatic evaluation tests to check context citations and verify RAG performance.

### Key Use Cases
1. **Precision Formatting Retention (Task 1):** Allow RAG projects to parse files into high-quality Markdown before indexing using Microsoft's `markitdown` pipeline, retaining table and formatting details.
2. **Document Lifecycle Expiration (Task 2):** Allow users to schedule documents to expire. Expired documents are clearly highlighted in red to ensure content currency, but remain fully active for query retrieval.
3. **Automated Ingestion Quality Gates (Task 3):** Validate document text structures using Gemini before embedding. Block garbage text (e.g. OCR fragmentation, spacing mashups) with clear user-facing alerts.
4. **Clean Workspaces (Task 4):** Clean up legacy, unused evaluation metrics ("Ingestion Latency") to focus evaluation on generation and retrieval accuracy.
5. **Synthetic QA Retrieval Validation (Task 5):** Automate RAG retrieval recall validation. Fetch database nodes, generate synthetic questions using Gemini, test the chat vector search engine, and calculate precise retrieval recall percentages.

---

## 2. COMMANDS

The following commands guide database migrations, local execution, and verification testing:

### Database & Migrations
- Expose current migrations status:
  ```bash
  python manage.py showmigrations
  ```
- Generate schema changes for new fields:
  ```bash
  python manage.py makemigrations projects documents
  ```
- Apply migrations:
  ```bash
  python manage.py migrate
  ```

### Development Server
- Run the local dev server (requires running `./run.sh` to forward the remote PostgreSQL port `5432`):
  ```bash
  python manage.py runserver
  ```

### Test Suite Execution
Run the focused pytests in a sandboxed, in-memory environment by setting `DJANGO_ENV=testing`:
- **Run MarkItDown Ingestion tests:**
  ```bash
  DJANGO_ENV=testing pytest Testing/unit/documents/test_markitdown_integration.py -v
  ```
- **Run Expiration Tracking tests:**
  ```bash
  DJANGO_ENV=testing pytest Testing/unit/documents/test_document_expiration.py -v
  ```
- **Run Structural Quality Grading tests:**
  ```bash
  DJANGO_ENV=testing pytest Testing/unit/documents/test_structural_grading.py -v
  ```
- **Run Synthetic QA Evaluation tests:**
  ```bash
  DJANGO_ENV=testing pytest Testing/unit/evaluate/test_synthetic_qa_eval.py -v
  ```
- **Run full unit test suite:**
  ```bash
  DJANGO_ENV=testing pytest Testing/unit -v
  ```

---

## 3. PROJECT STRUCTURE

The following specifies the files and paths affected by the implementation:

### Model & Administrative Files
- **`[MODIFY] src/apps/projects/models.py`**
  - Add `use_markitdown` (BooleanField) and `use_structural_grading` (BooleanField) to the `Project` model.
- **`[MODIFY] src/apps/projects/admin.py`**
  - Expose the boolean toggles in the "Parameters" tab inside `ProjectAdmin`.
- **`[MODIFY] src/apps/documents/models.py`**
  - Add `is_expired_checked` (BooleanField) and `expiration_date` (DateTimeField, nullable) to `Document`.

### Ingestion & Pipeline Controllers
- **`[NEW] src/apps/documents/converters.py`**
  - Create a lightweight thread-safe converter encapsulating Microsoft's `markitdown` library.
  - Implement a fallback for non-convertible files or already-plain text files.
- **`[MODIFY] src/apps/documents/views.py`**
  - Update `upload_document` to coordinate conversion, structural quality checks, database records, and pipeline calls.
  - Parse and store expiration tracking fields.
  - Return rendered list partials indicating failed states or custom error messages cleanly.

### Evaluation Workflow Elements
- **`[NEW] src/apps/evaluate/eval_services.py`**
  - Define `SyntheticQAEvaluator` which connects to the project's vector store database, extracts nodes, generates synthetic questions, queries the retrieval pipeline, and computes recall stats.
- **`[MODIFY] src/apps/evaluate/admin_views.py`**
  - Add a POST route `RunEvaluationView` at `/dashboard/evaluate/run/` to process synthetic QA calculations or fallback to open RAG.
- **`[MODIFY] templates/admin/evaluation_workflow.html`**
  - Clean up ingestion latency options.
  - Add a document selection panel, evaluation selector, and recall breakdown table driven by HTMX.

### Template & UI Partials
- **`[MODIFY] templates/partials/document_list.html`**
  - Insert the toggling HTML uploader fields for **Expired** (with a checkbox and `datetime-local` selector).
- **`[MODIFY] templates/partials/document_items.html`**
  - Add conditional HTML badge rendering for expired documents.
  - Render high-fidelity error text in case of ingestion quality gate blocking.

---

## 4. CODE STYLE

- **Double Quotes:** Use double quotes `""` for strings except when single quotes are required inside strings.
- **Formatting:** Adhere to Python PEP 8 guidelines.
- **F-Strings:** Use f-strings instead of `%` or `.format()`.
- **Type Hints:** Include explicit type hints for arguments and return types for all non-trivial Python code.
- **Docstrings:** Use NumPy-style docstrings for all new or materially modified classes, methods, and functions. Example:
  ```python
  def convert_to_markdown(input_path: str) -> str:
      """
      Convert the input file to Markdown using Microsoft's MarkItDown.

      Parameters
      ----------
      input_path : str
          Absolute filesystem path to the uploaded document.

      Returns
      -------
      str
          The converted Markdown string content.

      Raises
      ------
      ValueError
          If file format conversion is unsupported or fails.
      """
  ```

---

## 5. TESTING STRATEGY

### Architectural Guidelines for Tests
- **API Mocking:** Avoid executing live HTTP calls to external APIs. Mock the Gemini LLM client (`genai.Client` and `GoogleGenAI`) to return structured, pre-defined JSON or text responses.
- **Database VPS Mocking:** Mock database connections or handle the SQLite/PostgreSQL differences inside testing context safely.
- **TDD Flow:** Write tests inside `Testing/unit/` verifying correct branching and assertions *before* final implementation code is completed.
- **Fixture Re-use:** Re-use `django_db` fixtures and mock users to maintain clean transactions.

---

## 6. BOUNDARIES & GUARDRAILS

### ALWAYS DO
- **Lazy Load Heavy Imports:** Import `markitdown` lazily inside the converter helper to keep the main Django process startup fast.
- **Handle Temporary Files Cleanly:** Explicitly delete temporary files (`os.unlink()`) inside `finally` blocks after successful or failed processing.
- **Check Post Connection First:** Maintain the pre-flight connection check for PostgreSQL RAG storage projects before beginning document uploads.
- **Preserve Existing Logic:** Keep the Google and Local storage ingestion paths intact.

### ASK FIRST
- **Migrations:** Inform the user when generating database schema changes and migrations for validation.
- **Dependencies:** Add the lightweight `markitdown` dependency only to `requirements/requirements.txt`.

### NEVER DO
- **No Hardcoded Credentials:** Never store Google API keys, database credentials, or passwords in files. Read them dynamically from Django settings or environment variables.
- **No Heavy OCR Pipelines:** Never add heavy multi-gigabyte models (e.g. PyTorch-based text extraction) that slow down execution.
- **No Ad-Hoc CSS/JS Frameworks:** Stick entirely to vanilla CSS, standard Tailwind (compatible with Unfold), and HTMX features. Do not introduce React, Vue, or bulky custom Javascript files.

---

# Architectural Specifications for Active Tasks

## TASK 1: MarkItDown Integration (Postgres RAG)
- **Model Change:** Add field `use_markitdown` (BooleanField, default=False) to `Project` model in `src/apps/projects/models.py`.
- **Admin Tab Mapping:** Add `use_markitdown` to `ProjectAdmin.fieldsets` within the `"Parameters"` tab category.
- **Conversion Flow:**
  - Create `src/apps/documents/converters.py` containing thread-safe conversion helper.
  - If a `.md` or `.txt` file is uploaded, bypass `markitdown` conversion entirely and return raw content to preserve existing layout structure and minimize ingestion latency.
  - For `.pdf`, `.docx`, etc., instantiate `MarkItDown()` and retrieve `.text_content`.
  - Write this string to a temporary `.md` file, retaining the initial filename in references, and pass the path to `LlamaIndexIngestionPipeline.index_document()`.
  - Ensure any execution error is caught and stored as a structured indexing failure message.

## TASK 2: Document Expiration Tracking
- **Model Change:** Add fields `is_expired_checked` (BooleanField, default=False) and `expiration_date` (DateTimeField, null=True, blank=True) to `Document` model in `src/apps/documents/models.py`.
- **Upload Form Integration:**
  - Modify `templates/partials/document_list.html` to add checkbox `Expired` and the `expiration_date` date picker (`datetime-local`).
  - Use simple CSS (`class="hidden"`) toggled by JS `onchange` to reveal the date picker only when the checkbox is checked.
- **Ingestion Parameter Parsing:**
  - Read `is_expired` and `expiration_date` parameters from incoming POST in `upload_document`.
  - If `is_expired` is checked, validate that a valid date is passed. Use `django.utils.timezone.make_aware` (or Django standard datetime parsers) to prevent naive-timezone warnings.
  - Save these fields inside `Document` object during creation.
- **Expiration Evaluation & Rendering:**
  - Update `_doc_adapter(doc)` inside `views.py` to evaluate the current status:
    ```python
    from django.utils import timezone
    is_expired = False
    if doc.is_expired_checked and doc.expiration_date:
        is_expired = timezone.now() > doc.expiration_date
    ```
  - Pass `"is_expired": is_expired` into the template context.
  - In `templates/partials/document_items.html`, render a bold red badge saying `EXPIRED` if the document has expired. Expired documents remain fully indexed and searchable; the badge is purely a visual warning indicator for the user.

## TASK 3: Automated Ingestion Quality Grading
- **Model Change:** Add `use_structural_grading` (BooleanField, default=False) to the `Project` model. Expose it under the "Parameters" tab in `ProjectAdmin`.
- **Evaluation Gate:**
  - If `use_structural_grading` is active (specifically for Postgres RAG vector ingestion), extract the first 1000 characters from the document string.
  - Connect to the Gemini API (`models/gemini-2.5-flash-lite`) requesting a structured JSON response.
  - Structured Prompt:
    ```text
    You are a Data Quality Inspector. Review the following text snippet extracted from a document. 
    Determine if the text structure is intact and readable, or if the layout parser failed.

    Look for these failure signs:
    - Words mashed together without spaces (e.g., "TheCompanyReport2024")
    - Shattered sentences from misread columns (e.g., "Revenue $5M Introduction to")
    - Excessive raw font artifact codes (e.g., "CID:12 CID:44")

    Score the text quality from 1 (Complete Garbage) to 10 (Perfectly Readable).
    Respond ONLY with a JSON object in this format:
    {"score": integer, "reason": "string"}

    Snippet to evaluate:
    {text_sample}
    ```
  - Parse the score and reason. If the parsed score is 7 or lower (`score <= 7`), immediately stop the ingestion pipeline, mark the document's state as `FAILED`, save the `error_message` as `f"Extraction quality too low (Score: {score}/10). Reason: {reason}"`, and render the failure UI.

## TASK 5: Automated Retrieval Accuracy Evaluation via Synthetic QA
- **UI Workspace Elements:**
  - Update `templates/admin/evaluation_workflow.html`.
  - When a target project is selected and "Retrieval Accuracy" is the active tab, render all documents in the project having `INDEXED` status.
  - Allow standard logged-in users to select one document and pick between **Synthetic QA Generation** and **Open RAG Eval** (radio buttons).
  - Add an **Evaluate** button.
  - If **Open RAG Eval** is clicked, block and trigger an alert: `"Not implemented yet"`.
  - If **Synthetic QA Generation** is clicked, use HTMX to post to `/dashboard/evaluate/run/` with parameters `project_id`, `document_id`, and `eval_method`.
- **Backend Evaluator Service:**
  - Create `src/apps/evaluate/eval_services.py` containing `SyntheticQAEvaluator`.
  - **Step 1: Fetch Nodes**
    - Connect to the PostgreSQL database using settings `REMOTE_POSTGRES_CONFIG` and table name `rag_project_<project_id>`.
    - Retrieve up to 5 nodes associated with the target document using a metadata JSONB query:
      ```sql
      SELECT id, text, node_id, metadata_ 
      FROM data_rag_project_<project_id> 
      WHERE metadata_->>'file_name' = '<document_name>';
      ```
  - **Step 2: Generate Questions**
    - For each of the five nodes, send the node's `text` to Gemini (`models/gemini-2.5-flash-lite`) requesting three questions.
    - Prompt: `"Generate 3 questions that can be answered only using this text. Output each question on a new line."`
    - Parse the questions by splitting the response on newlines.
  - **Step 3: Ground Truth Map**
    - Build a ground-truth mapping linking each generated question to its source node's UUID.
  - **Step 4: Test Run**
    - Programmatically run each question through the project's vector store index query engine.
    - Inspect the retrieved `source_nodes` collection inside the query engine's response.
    - Check if the source nodes include the UUID of the originating node (`node.node.node_id == expected_node_id`).
  - **Step 5: Recall Scoring**
    - Compute the final Retrieval Recall percentage: `Recall = Matches / Total Questions`.
    - Render a premium scorecard displaying the Recall score and a tabular log showing every test question, its expected source document node, whether a match succeeded, and the list of actual citations.
