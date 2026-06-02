# Spec: Task1 - SyntheticQA Project-Level Evaluation

## 1. Objective & Scope
The objective is to implement a project-level evaluation suite in the Django-based RAG dashboard utilizing `gemini-2.5-flash-lite` and the Ragas (RAG Assessment) framework. This implementation runs entirely within the unified Django monolith application without relying on FastAPI or external API processes. It replaces all legacy references to Ollama, gemma4, and standalone API services.

All asynchronous background processing (such as QA generation and RAG evaluation runs) must be executed using lightweight **background worker threads** (`threading.Thread`), rather than Celery or other external message brokers, to keep the operational overhead minimal.

### Core User Flow
1. **Evaluation Workflow Selection:** The administrator enters the main evaluation dashboard.
2. **Project Selection:** The user selects a target PostgreSQL RAG project from the project list.
3. **Workflow & Input Method Choice:** The user chooses the "SyntheticQA" evaluation workflow and selects one of two dataset acquisition methods from a dropdown:
   - **Write own QAs:** The user is presented with a screen allowing them to type questions and reference ground-truth answers manually, or upload a CSV file containing `Question` and `Answer` columns. These questions are always general project-level validation QAs (mapping `document` to `None` in the database).
   - **Generate QAs:** The user inputs a target quantity of questions to generate. The system uses `gemini-2.5-flash-lite` to automatically synthesize the requested number of QA pairs from the text chunks of the project's documents.
4. **Evaluation Execution:** The user triggers an evaluation run. The system retrieves contexts from the project vector space, generates answers using the active RAG pipeline, computes Ragas metrics (Context Recall, Context Precision, Faithfulness, Answer Relevancy), and stores the structured results for dashboard viewing.

---

## 2. Common & Required Commands
All commands should be executed inside the virtual environment (`source .venv/bin/activate`).

```bash
# Database Migrations
python manage.py makemigrations evaluate
python manage.py migrate

# Running the local Django development server
python manage.py runserver

# Running Unit Tests
DJANGO_ENV=testing .venv/bin/pytest Testing/unit/evaluate -v
```

---

## 3. Project Structure
All evaluation code is housed in the `evaluate` app and shared services:

```
src/apps/evaluate/
├── __init__.py
├── models.py          # Schema for EvaluationDataset, EvaluationRun, and EvaluationResultMetrics
├── views.py           # HTMX-driven Django views for workflow, manual QAs, CSV upload, and runs
├── urls.py            # URL route routing within /rag/dashboard/evaluate/
├── eval_services.py   # Synthesizer and Ragas execution services using gemini-2.5-flash-lite
└── templates/         # UI templates for evaluation workspace, metrics grids, and drill-downs
    └── evaluate/
        ├── dashboard.html
        ├── manual_qa.html
        ├── metrics_grid.html
        └── run_progress.html
```

---

## 4. Data Schema (PostgreSQL via Django ORM)

Three models manage the evaluation life cycle in `src/apps/evaluate/models.py`:

### 4.1 EvaluationDataset
Stores reference questions and ground-truth answers. Supports both document-specific generated QAs and project-level user-written/CSV-uploaded QAs.
- `id`: UUIDField (Primary Key)
- `project`: ForeignKey to `apps.projects.models.Project` (on_delete=CASCADE)
- `document`: ForeignKey to `apps.documents.models.Document` (on_delete=CASCADE, null=True, blank=True)
- `question`: TextField (The query to run against the RAG system)
- `ground_truth`: TextField (The reference gold-standard answer)
- `source`: CharField (choices: `GENERATED`, `MANUAL`, `CSV_UPLOAD`)
- `created_at`: DateTimeField

> [!NOTE]
> For manually written and CSV-uploaded datasets, the `document` field is always `None`, signifying they are general project-level questions.

### 4.2 EvaluationRun
Represents a project-level execution event of a dataset.
- `id`: UUIDField (Primary Key)
- `project`: ForeignKey to `apps.projects.models.Project` (on_delete=CASCADE)
- `started_at`: DateTimeField
- `completed_at`: DateTimeField (null=True)
- `status`: CharField (choices: `PENDING`, `RUNNING`, `SUCCESS`, `FAILED`)
- `error_message`: TextField (blank=True)

### 4.3 EvaluationResultMetrics
Stores Ragas scores for individual questions and the overall aggregated run performance.
- `id`: UUIDField (Primary Key)
- `run`: ForeignKey to `EvaluationRun` (on_delete=CASCADE)
- `dataset_item`: ForeignKey to `EvaluationDataset` (on_delete=SET_NULL, null=True)
- `context_recall`: FloatField (null=True)
- `context_precision`: FloatField (null=True)
- `faithfulness`: FloatField (null=True)
- `answer_relevancy`: FloatField (null=True)

---

## 5. Technical Execution & Phase Breakdown

### Phase 1: Dataset Acquisition

#### Option A: User-Written / CSV-Uploaded QAs
1. If the user selects "Write own QAs", a form enables typing manual QA pairs directly.
2. Alternatively, a file input allows uploading a CSV file. The CSV must have headers `Question` and `Answer` (case-insensitive).
3. The uploaded rows are validated and parsed, writing records to the `EvaluationDataset` table with `source='CSV_UPLOAD'`, `document=None`, and mapping them to the active `Project`.

#### Option B: Automatic Generation (SyntheticQA)
1. The user inputs a target quantity of questions to generate (`num_questions`) via the UI control panel.
2. The background worker thread partitions the target quantity dynamically across the ingested text chunks of the project's documents to distribute the load evenly.
3. For each selected text chunk, `gemini-2.5-flash-lite` is invoked using LlamaIndex's `GoogleGenAI` wrapper.
4. The Synthesis Prompt:
   ```
   You are an advanced QA Engine. Inspect the following text chunk taken from an isolated corporate document:
   """
   {chunk_text}
   """

   Generate two realistic user search questions and two corresponding ideal, factual answers based STRICTLY on the text provided. Do not extrapolate.
   Respond ONLY with a valid JSON array matching this schema:
   [
     {"question": "string", "ground_truth": "string"},
     {"question": "string", "ground_truth": "string"}
   ]
   ```
5. Parse the JSON response and write the records to `EvaluationDataset` with `source='GENERATED'`.

### Phase 2: RAG Execution & Tracing
1. The admin selects a Project and triggers an evaluation run, creating an `EvaluationRun` with `status="RUNNING"`.
2. The system fetches all `EvaluationDataset` records associated with the project.
3. For each dataset item, the system executes RAG retrieval and generation inside an asynchronous Python **background worker thread** (`threading.Thread`):
   - Perform a vector similarity search across the project's vector store to capture the top-$k$ returned records into an array: `contexts`.
   - Send the query and `contexts` to `gemini-2.5-flash-lite` to synthesize the `answer`.
   - Store the tracing record: `question`, `contexts` (Array of strings), `answer`, and `ground_truth`.

### Phase 3: Ragas Evaluation
1. Convert the collected traces into standard Pandas formatting.
2. Invoke Ragas metrics inside the **background worker thread** using `gemini-2.5-flash-lite` as the evaluator model (`GoogleGenAI`) and `models/gemini-embedding-001` (`GeminiEmbedding`).
3. Compute the four metrics:
   - **Retrieval:** `context_recall`, `context_precision`
   - **Generation:** `faithfulness`, `answer_relevancy`
4. Save the calculated floats (0.0 to 1.0) into `EvaluationResultMetrics` and set the `EvaluationRun` status to `SUCCESS`.

---

## 6. Code Style & Guidelines
- **Syntax rules:** PEP 8 compliance, double quotes for all strings, and explicit variable names. Use f-strings for string formatting.
- **Type safety:** All new Python service functions and view helpers must include type hints and NumPy-style docstrings.
- **No external API processes:** All executions must occur directly within Django's request-response lifecycle or standard background threading. Do not use FastAPI or external REST services.
- **Model Target:** Always target `gemini-2.5-flash-lite` for LLM operations.

---

## 7. Testing Strategy
- All tests must go under `Testing/unit/evaluate/`.
- Use unittest/pytest mock assertions to mock Gemini LLM responses and embedding calls, ensuring tests run isolated without using real tokens or requiring external network availability.
- Verify coverage using: `DJANGO_ENV=testing .venv/bin/pytest Testing/unit/evaluate -v`.

---

## 8. Guardrails & Boundaries

### Always Do
- Run `python manage.py showmigrations` and review any migration scripts before migrating the database.
- Validate CSV file structures and column headers prior to processing.
- Gracefully catch and log API and Ragas library connection errors, updating the `EvaluationRun` to `FAILED` with details.
- Secure all views using appropriate Django auth decorators (e.g. `@login_required`).

### Ask First
- Upgrading or adding new third-party Python packages.
- Adjusting prompt configurations or Ragas metrics.

### Never Do
- Use Celery or external message brokers (use standard Python background threads instead).
- Execute LLM-intensive evaluation runs synchronously within the main request-response HTTP thread (always run asynchronously in a background worker thread).
- Expose raw traceback strings or database exceptions to the end-user dashboard.


# Task2: Added bugsink to the project