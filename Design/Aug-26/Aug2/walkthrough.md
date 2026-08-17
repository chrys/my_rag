# Aug2 Sprint: Local LLM Benchmark Evaluation — Walkthrough & Verification

## Summary of Completed Work

We have successfully designed, built, and verified the **Local LLM Benchmark Evaluation** feature in Django Unfold Admin.

---

### 1. Key Features Delivered

1. **Django Benchmark Models & Database Persistence:**
   - [`LocalLLMEvaluationRun`](file:///Users/chrys/Projects/my_rag/src/apps/evaluate/models.py): Tracks execution status, models evaluated, dataset name, best performing model, best overall score, and aggregated per-model criteria breakdown JSON.
   - [`LocalLLMResultMetric`](file:///Users/chrys/Projects/my_rag/src/apps/evaluate/models.py): Stores item-level question, reference ground truth, retrieved RAG context, generated local model response, and 7 normalized criteria metrics.
   - Registered in Django Admin with filters and formatted previews.

2. **Ollama Discovery & Tolerant CSV Parser:**
   - [`fetch_available_ollama_models`](file:///Users/chrys/Projects/my_rag/src/apps/evaluate/eval_services.py): Live daemon inspection over `http://localhost:11434/api/tags` with timeout and offline handling.
   - [`parse_benchmark_csv`](file:///Users/chrys/Projects/my_rag/src/apps/evaluate/eval_services.py): Resilient parsing handling case-insensitive headers (`question`, `query`, `prompt`, `q`, `answer`, `ground_truth`, `gold_answer`, `a`), BOM encodings, and extra column stripping.

3. **7-Criterion Scoring System (0.0 – 10.0 scale):**
   - **Faithfulness / Hallucination Grounding**: LLM Judge scoring adherence to context without unverified claims.
   - **Context Utilization**: LLM Judge scoring fact extraction and relevance.
   - **Citation Accuracy**: LLM Judge scoring source note/heading accuracy.
   - **Instruction Following**: LLM Judge scoring directness and conciseness.
   - **Tokens Per Second (TPS)**: Pure generation speed normalized via Ollama `eval_duration` isolated from cold-start model load.
   - **Reply Time**: Time to first token + token generation duration normalized latency score.
   - **Markdown Compatibility**: Structural syntax verification (code fences, bold/italic pairing, wikilinks, markdown links).
   - **Overall Score**: Exact arithmetic mean of all 7 criteria.

4. **HTMX Interactive Dashboard & Comparative Scorecard:**
   - **Sidebar UI**: Added `Local LLMs` option to the method selector in [`evaluation_workflow.html`](file:///Users/chrys/Projects/my_rag/templates/admin/evaluation_workflow.html).
   - **Model Selector**: Live checkboxes with model sizes and online status indicator ([`local_llms_controls.html`](file:///Users/chrys/Projects/my_rag/templates/admin/partials/local_llms_controls.html)).
   - **CSV Ingestion**: Interactive drag-and-drop / click file picker with selected filename badge.
   - **Comparative Scorecard**: Side-by-side comparison table, top-performing model highlight banner, and question-level responses grid ([`local_llm_scorecard.html`](file:///Users/chrys/Projects/my_rag/templates/admin/local_llm_scorecard.html)).
   - **12-Column CSV Export**: [`ExportLocalLLMCSVEvaluationView`](file:///Users/chrys/Projects/my_rag/src/apps/evaluate/admin_views.py) endpoint downloading results formatted with `model_name` as the first column.

---

## Verification & Test Results

- **Unit & Integration Suite**: All **406 tests** across the entire project passed with 0 regressions.
  - Model tests: [`test_local_llm_models.py`](file:///Users/chrys/Projects/my_rag/Testing/unit/evaluate/test_local_llm_models.py) (PASSED)
  - Service tests: [`test_local_llm_eval.py`](file:///Users/chrys/Projects/my_rag/Testing/unit/evaluate/test_local_llm_eval.py) (PASSED)
  - View & export tests: [`test_local_llm_views.py`](file:///Users/chrys/Projects/my_rag/Testing/unit/evaluate/test_local_llm_views.py) (PASSED)

```bash
DJANGO_ENV=testing .venv/bin/pytest Testing/unit/ --tb=short -q
# ===================== 406 passed, 71719 warnings in 3.64s ======================
```
