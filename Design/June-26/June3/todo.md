# Todo List: Task1 - SyntheticQA Project-Level Evaluation

## Phase 1: Database Models & Schema Migrations
- [x] Task: Define ORM Models and Generate Migrations
  - Acceptance: `EvaluationDataset`, `EvaluationRun`, and `EvaluationResultMetrics` models defined in `src/apps/evaluate/models.py` with correct UUID primary keys and foreign keys.
  - Verify: Run `python manage.py makemigrations evaluate && python manage.py migrate` and confirm tables exist in database.
  - Files:
    - [MODIFY] [models.py](file:///Users/chrys/Projects/my_rag/src/apps/evaluate/models.py)

---

## Phase 2: Service Layer & Background Threading
- [x] Task: Implement gemini-2.5-flash-lite QA Synthesizer
  - Acceptance: `generate_synthetic_qas(project_id, num_questions)` service function partitions the question count, fetches chunks, calls `gemini-2.5-flash-lite` with structured prompt, parses JSON response, and saves pairs to `EvaluationDataset` table.
  - Verify: Run unit tests checking that chunks are parsed and saved under Mock setups.
  - Files:
    - [NEW] [eval_services.py](file:///Users/chrys/Projects/my_rag/src/apps/evaluate/eval_services.py)

- [x] Task: Implement Ragas Evaluation Background Task
  - Acceptance: `execute_evaluation_run(run_id)` function runs in standard background worker thread, performs PGVector similarity searches, generates answers via Gemini, computes Ragas metrics using `gemini-2.5-flash-lite`, and stores metrics.
  - Verify: Run focused unit test simulating full Ragas evaluation on mock trace datasets.
  - Files:
    - [MODIFY] [eval_services.py](file:///Users/chrys/Projects/my_rag/src/apps/evaluate/eval_services.py)

---

## Phase 3: UI & HTMX Views
- [x] Task: Design Unfold Dashboard Workspace and URLs
  - Acceptance: Evaluation dashboard template and URLs integrated under `/rag/dashboard/evaluate/` with list of all projects and clean Unfold styles.
  - Verify: Navigate to `/rag/dashboard/evaluate/` and check project grid rendering.
  - Files:
    - [MODIFY] [urls.py](file:///Users/chrys/Projects/my_rag/src/apps/evaluate/urls.py)
    - [MODIFY] [views.py](file:///Users/chrys/Projects/my_rag/src/apps/evaluate/views.py)
    - [NEW] [dashboard.html](file:///Users/chrys/Projects/my_rag/src/apps/evaluate/templates/evaluate/dashboard.html)

- [x] Task: Implement Manual QA and CSV Uploader Form
  - Acceptance: Dropdown dynamically switches between "Write own QAs" and "Generate QAs". User is able to save manual typed entries or upload a CSV file with `Question` and `Answer` headers, saving rows mapped to `Project`.
  - Verify: Upload sample valid CSV and verify items are created in `EvaluationDataset` database.
  - Files:
    - [MODIFY] [views.py](file:///Users/chrys/Projects/my_rag/src/apps/evaluate/views.py)
    - [NEW] [manual_qa.html](file:///Users/chrys/Projects/my_rag/src/apps/evaluate/templates/evaluate/manual_qa.html)

- [x] Task: Implement Automatic Generation UI with Progress Spinner
  - Acceptance: Selecting "Generate QAs" exposes a question quantity field. Submission spins up the background thread and displays an HTMX spinner that polls `/status/` until complete, then swaps out for the loaded QA list.
  - Verify: Trigger generation and verify spinner shows and polls until database rows appear.
  - Files:
    - [MODIFY] [views.py](file:///Users/chrys/Projects/my_rag/src/apps/evaluate/views.py)
    - [NEW] [run_progress.html](file:///Users/chrys/Projects/my_rag/src/apps/evaluate/templates/evaluate/run_progress.html)

- [x] Task: Implement RAG Evaluation Run Trigger & Metrics Rendering
  - Acceptance: Clicking "Run Evaluation" triggers execution in background thread and polls the run status. Once finished, displays aggregated scores with color-coded compliance indicators (Green >= 0.85, Yellow 0.70-0.84, Red < 0.70).
  - Verify: Execute test evaluation run and verify grid renders color-coded metrics correctly upon SUCCESS.
  - Files:
    - [MODIFY] [views.py](file:///Users/chrys/Projects/my_rag/src/apps/evaluate/views.py)
    - [NEW] [metrics_grid.html](file:///Users/chrys/Projects/my_rag/src/apps/evaluate/templates/evaluate/metrics_grid.html)

- [x] Task: Implement Deep-Dive Drill Down Panel
  - Acceptance: Clicking any completed or failed run pulls up an inline drill-down details layout matching individual questions to their scores, showing retrieved contexts and answers for quick diagnostics.
  - Verify: Click on run item and verify context drill-down details display correctly.
  - Files:
    - [MODIFY] [views.py](file:///Users/chrys/Projects/my_rag/src/apps/evaluate/views.py)
    - [NEW] [metrics_grid.html](file:///Users/chrys/Projects/my_rag/src/apps/evaluate/templates/evaluate/metrics_grid.html)

---

## Phase 4: Final Verification
- [x] Task: Write and Run Unit Tests
  - Acceptance: Full test coverage under `Testing/unit/evaluate/test_synthetic_qa_eval.py` for models, services, CSV validation, and HTMX views.
  - Verify: Running `DJANGO_ENV=testing .venv/bin/pytest Testing/unit/evaluate/ -v` completes with all tests passing.
  - Files:
    - [NEW] [test_synthetic_qa_eval.py](file:///Users/chrys/Projects/my_rag/Testing/unit/evaluate/test_synthetic_qa_eval.py)
