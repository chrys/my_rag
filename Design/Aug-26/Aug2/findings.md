# Five-Axis Code Review: Local LLM Benchmark Evaluation

**Target Specification:** [`Design/Aug-26/Aug2/aug2-specs.md`](file:///Users/chrys/Projects/my_rag/Design/Aug-26/Aug2/aug2-specs.md)  
**Review Target:** Sprint Aug2 Implementation Changeset  
**Review Date:** August 17, 2026  
**Status:** **PASSED** (0 Critical, 0 Important, 2 Suggestions)

---

## Executive Summary

The implementation of the **Local LLM Benchmark Evaluation Workflow** fully satisfies all business logic, architectural constraints, and functional requirements specified in [`aug2-specs.md`](file:///Users/chrys/Projects/my_rag/Design/Aug-26/Aug2/aug2-specs.md). The test suite demonstrates complete coverage with **406 passing unit and integration tests** and zero regressions across existing RAGAS, Synthetic QA, and manual evaluation workflows.

---

## Five-Axis Evaluation

### 1. Correctness
* **Specification Compliance:** 
  - All 7 specified criteria (*Faithfulness*, *Context Utilization*, *Citation Accuracy*, *Tokens Per Second*, *Reply Time*, *Instruction Following*, *Markdown Compatibility*) are calculated and strictly normalized to the `0.0 – 10.0` scale.
  - Overall Score is computed as the exact arithmetic mean of the 7 criteria.
  - Multi-model comparative execution isolates pure token generation speed (`eval_duration`) from cold-start model VRAM load times, utilizing an initial 1-token warmup ping per model.
  - Tolerant CSV parser handles case-insensitive headers (`question`, `query`, `prompt`, `q`, `answer`, `ground_truth`, `gold_answer`, `a`), strips extraneous columns, and supports UTF-8 with BOM.
  - 12-column CSV download matches the exact header schema with `model_name` as the first column.
* **Edge Case Handling:**
  - Network timeouts and unreachable Ollama daemons are caught gracefully with user-friendly retry banners in the UI.
  - Empty CSV files and missing question/answer columns trigger descriptive validation messages.
  - Formatting AST parser handles unbalanced code fences, unclosed wikilinks, and unmatched bold asterisks without throwing runtime exceptions.
* **Test Coverage:**
  - Dedicated unit tests covering models ([`test_local_llm_models.py`](file:///Users/chrys/Projects/my_rag/Testing/unit/evaluate/test_local_llm_models.py)), scoring services ([`test_local_llm_eval.py`](file:///Users/chrys/Projects/my_rag/Testing/unit/evaluate/test_local_llm_eval.py)), and HTMX views / CSV export ([`test_local_llm_views.py`](file:///Users/chrys/Projects/my_rag/Testing/unit/evaluate/test_local_llm_views.py)).

### 2. Readability
* **Code Clarity & PEP 8:**
  - Functions in [`src/apps/evaluate/eval_services.py`](file:///Users/chrys/Projects/my_rag/src/apps/evaluate/eval_services.py) and [`src/apps/evaluate/admin_views.py`](file:///Users/chrys/Projects/my_rag/src/apps/evaluate/admin_views.py) feature comprehensive docstrings and explicit type hints.
  - Code follows standard Python formatting and descriptive variable naming (`raw_tps`, `eval_sec`, `qualitative_scores`, `summary_scores`).
* **UI Templates:**
  - HTML templates ([`templates/admin/evaluation_workflow.html`](file:///Users/chrys/Projects/my_rag/templates/admin/evaluation_workflow.html), [`templates/admin/local_llm_scorecard.html`](file:///Users/chrys/Projects/my_rag/templates/admin/local_llm_scorecard.html), [`templates/admin/partials/local_llms_controls.html`](file:///Users/chrys/Projects/my_rag/templates/admin/partials/local_llms_controls.html)) are cleanly structured with Tailwind CSS utility classes adhering to the Unfold Admin design system.

### 3. Architecture & Design
* **Separation of Concerns:**
  - Views remain thin and delegate inference, scoring, parsing, and context retrieval to `eval_services.py`.
  - Custom admin URLs and views inherit cleanly from `UnfoldModelAdminViewMixin` and are properly bound to the `custom_admin` site in [`src/apps/my_rag_project/admin.py`](file:///Users/chrys/Projects/my_rag/src/apps/my_rag_project/admin.py).
  - Database schema isolates evaluation metadata (`LocalLLMEvaluationRun`) from granular question-level results (`LocalLLMResultMetric`).
* **Non-Invasive Integration:**
  - Existing RAGAS and Synthetic QA pipelines operate independently without modification or side effects.

### 4. Security & Hardening
* **Authentication & Authorization:**
  - All admin endpoints inherit Django Unfold admin authentication guards. Non-staff/unauthenticated requests cannot trigger inference or download exports.
* **Input Validation & Sanitization:**
  - CSV file contents are read in-memory and parsed with `csv.DictReader` avoiding arbitrary file system execution or SSRF.
  - Ollama base URL defaults to localhost with environment variable configuration (`OLLAMA_BASE_URL`).
* **Secrets Protection:**
  - Google GenAI API keys are read from environment variables (`os.getenv("GOOGLE_API_KEY")`) and never logged or exposed in client responses.

### 5. Performance
* **Latency Isolation & Warmup:**
  - Warmup ping ensures model weights are loaded in GPU memory before benchmark timing begins.
  - Telemetry math isolates `eval_duration` for pure generation throughput (TPS) and `(prompt_eval_duration + eval_duration)` for reply time.
* **Database & Query Efficiency:**
  - Benchmark run metrics are retrieved via indexed foreign key relations (`run.item_metrics.all()`).
  - No N+1 query patterns observed in scorecard rendering or CSV streaming.

---

## Detailed Findings & Recommendations

### [Suggestion 1] Asynchronous Task Execution for Massive Benchmark Datasets
- **File Reference:** [`src/apps/evaluate/admin_views.py:440-490`](file:///Users/chrys/Projects/my_rag/src/apps/evaluate/admin_views.py#L440-L490)
- **Observation:** The benchmark pipeline runs synchronously in `RunLocalLLMBenchmarkView.post()`. For small-to-medium benchmark datasets (e.g., 5–25 questions across 2–3 models), execution takes under 15–30 seconds. If users upload hundreds of questions, HTTP gateway timeouts (e.g., 60s in production reverse proxies) could occur.
- **Actionable Recommendation:** For future sprints (post-MVP), consider providing a background task option (e.g., threading / Celery / background worker with HTMX polling) similar to `SyntheticQAEvaluator`.

### [Suggestion 2] Configurable Similarity Top-K for Context Retrieval
- **File Reference:** [`src/apps/evaluate/eval_services.py:915-925`](file:///Users/chrys/Projects/my_rag/src/apps/evaluate/eval_services.py#L915-L925)
- **Observation:** `retrieve_project_context_chunks()` hardcodes `top_k=3`.
- **Actionable Recommendation:** Expose `top_k` as an optional slider/input in the sidebar UI or project settings to evaluate how local models perform with varying context window lengths (e.g., top_k=2 vs top_k=5).

---

## Review Conclusion

The changeset meets all requirements defined in [`aug2-specs.md`](file:///Users/chrys/Projects/my_rag/Design/Aug-26/Aug2/aug2-specs.md). The code is clean, robust, and verified with a 100% test pass rate.
