# Task Checklist: Local LLM Benchmark Evaluation Workflow

---

- [X] Task 1: Create LocalLLMEvaluationRun & LocalLLMResultMetric Django Models
  - Acceptance: Models defined with fields for evaluated models, 7 criteria scores (Faithfulness, Context Utilization, Citation Accuracy, TPS, Reply Time, Instruction Following, Markdown Compatibility), overall score, summary scores JSON, and relationships. Migrations created and applied cleanly.
  - Verify: `DJANGO_ENV=testing .venv/bin/pytest Testing/unit/evaluate/test_local_llm_models.py --tb=short`
  - Files: `src/apps/evaluate/models.py`, `src/apps/evaluate/admin.py`, `Testing/unit/evaluate/test_local_llm_models.py`

- [X] Task 2: Implement Ollama Model Discovery & Tolerant CSV Parsing Service
  - Acceptance: `fetch_available_ollama_models` queries Ollama `/api/tags` with error handling, and `parse_benchmark_csv` extracts question and answer pairs while ignoring extra columns across varied encodings.
  - Verify: `DJANGO_ENV=testing .venv/bin/pytest Testing/unit/evaluate/test_local_llm_eval.py -k "test_ollama_discovery or test_csv_parser" --tb=short`
  - Files: `src/apps/evaluate/eval_services.py`, `Testing/unit/evaluate/test_local_llm_eval.py`

- [X] Task 3: Implement 7-Metric Scoring Algorithms & Local LLM Benchmark Runner
  - Acceptance: Ollama query execution with warmup and timing isolation (`eval_duration`), Gemini judge scoring for qualitative criteria, 7-criterion normalization (0.0 to 10.0), exact arithmetic mean Overall Score, and pipeline execution saving results to the database.
  - Verify: `DJANGO_ENV=testing .venv/bin/pytest Testing/unit/evaluate/test_local_llm_eval.py --tb=short`
  - Files: `src/apps/evaluate/eval_services.py`, `Testing/unit/evaluate/test_local_llm_eval.py`

- [X] Task 4: Implement HTMX Admin Views & 12-Column CSV Export Endpoint
  - Acceptance: `LocalLLMModelListView` renders dynamic model selection partial, `RunLocalLLMBenchmarkView` executes the benchmark and returns the scorecard HTML, and `ExportLocalLLMCSVEvaluationView` generates the exact 12-column CSV download. Routes registered in `urls.py` and `my_rag_project/admin.py`.
  - Verify: `DJANGO_ENV=testing .venv/bin/pytest Testing/unit/evaluate/test_local_llm_views.py --tb=short`
  - Files: `src/apps/evaluate/admin_views.py`, `src/apps/evaluate/urls.py`, `src/apps/my_rag_project/admin.py`, `Testing/unit/evaluate/test_local_llm_views.py`

- [X] Task 5: Implement Frontend UI in Evaluation Workflow & Comparative Scorecard
  - Acceptance: `Local LLMs` option added to method dropdown in `evaluation_workflow.html`, interactive model checkboxes with Ollama live status badge, CSV dropzone with selected filename indicator, client-side spinner & dynamic progress milestone messages, and `local_llm_scorecard.html` with side-by-side comparative table, best model badge, and CSV download button.
  - Verify: Load `/rag/dashboard/evaluate/` in browser, switch to Local LLMs method, test UI interactions and run `DJANGO_ENV=testing .venv/bin/pytest Testing/unit/evaluate/ --tb=short`.
  - Files: `templates/admin/evaluation_workflow.html`, `templates/admin/local_llm_scorecard.html`, `templates/admin/partials/local_llms_controls.html`

- [X] Task 6: Full Regression Verification & Documentation
  - Acceptance: Run complete pytest test suite across all apps, verify 0 regressions, and produce final walkthrough documentation.
  - Verify: `DJANGO_ENV=testing .venv/bin/pytest Testing/unit/ --tb=short`
  - Files: `Design/Aug-26/Aug2/walkthrough.md`
