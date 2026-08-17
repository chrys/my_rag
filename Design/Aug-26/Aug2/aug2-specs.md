# Specification: Local LLM Benchmark Evaluation Workflow

---

## 1. Objective & Scope

### Problem Statement & Background Context
Users need to evaluate the performance, speed, and quality of locally hosted Large Language Models (running via Ollama) when integrated with their RAG projects. While existing workflows support cloud-based RAGAS evaluation, Synthetic QA generation, and manual rating, this feature introduces **Local LLMs** as a dedicated evaluation method within the **Evaluation Workflow**. It provides automated multi-model comparative benchmarking using custom Q&A datasets (uploaded via CSV) and generates a standardized, multi-criteria scorecard rated out of 10 along with comprehensive CSV exports.

### Target Users & Architectural Placement
- **Target Audience:** Developers, data engineers, and RAG administrators optimizing local LLMs (e.g., Llama 3.1, Mistral, Gemma, Qwen) for cost, latency, and retrieval accuracy.
- **Placement:** Integrated directly into the Unfold Admin **Evaluation Workflow** dashboard (`/rag/dashboard/evaluate/`).

### Resolved Design Decisions & User Interaction Flow

1. **Evaluation Method Selection:**
   - In the Evaluation Config sidebar (`templates/admin/evaluation_workflow.html`), add `Local LLMs` as an option in the **Evaluation Method** dropdown (`#eval-method-select`).

2. **Local Model Discovery & Multi-Model Selection:**
   - When `Local LLMs` is selected, the client/backend queries the local Ollama instance (default: `http://localhost:11434/api/tags` or configured via `OLLAMA_BASE_URL`).
   - Dynamically populates a multi-select checkbox list of all available local Ollama models (e.g., `llama3.1:8b`, `mistral:latest`, `qwen2.5:7b`).
   - Supports selecting multiple models simultaneously for comparative side-by-side benchmarking.
   - **Model Load Isolation & Fair Benchmarking:**
     - Runs models sequentially.
     - Sends a 1-token warmup ping before timing benchmark items.
     - Uses Ollama's native server-side timing metadata (`eval_duration`, `eval_count`, `prompt_eval_duration`) to isolate pure generation latency from cold-start disk-to-VRAM model swapping.

3. **Benchmark Dataset Ingestion (CSV Upload):**
   - Provides a drag-and-drop CSV upload widget with interactive dropzone.
   - Requires columns:
     - `question` (or `questions`): The evaluation query.
     - `answer` (or `answers`, `ground_truth`): The reference gold-standard response.
   - **Tolerant Parsing:** Ignores any additional or extraneous columns in the CSV without failing. Handles UTF-8 and BOM encoding.

4. **Execution & Interactive Progress UI:**
   - User clicks the **Run Benchmark Evaluation** button.
   - UI displays an active loading spinner and dynamic progress status messages indicating the active stage (e.g., *"Retrieving context chunks..."*, *"Benchmarking llama3.1:8b (Q1/5)..."*, *"Running Gemini Evaluation Judge..."*).
   - For each Q&A item and selected model:
     1. Retrieves relevant context chunks from the selected RAG project (Postgres/PGVector or Local vector store).
     2. Queries the local Ollama model with context and prompt.
     3. Captures raw generation metrics (Time to First Token, total generation time, tokens per second, model answer).
     4. Evaluates qualitative metrics using Gemini / Primary Project LLM as an impartial judge returning structured JSON scores.

5. **Evaluation Dimensions & Scoring (Scale 0 to 10):**
   Each criterion is graded on a normalized **0 to 10 scale**:

   | Category | Criterion | Description & Scoring Method | Scale |
   | :--- | :--- | :--- | :--- |
   | **Grounding** | **Faithfulness / Hallucination** | Evaluated by Gemini judge: verifies if the model answer is strictly grounded in retrieved context without hallucinating unverified facts. | 0 – 10 |
   | **Grounding** | **Context Utilization** | Evaluated by Gemini judge: assesses how effectively the model extracts needle facts from large context chunks. | 0 – 10 |
   | **Grounding** | **Citation Accuracy** | Evaluated by Gemini judge: checks if the model accurately cites note titles, sources, or headings provided in context. | 0 – 10 |
   | **Speed** | **Tokens Per Second (TPS)** | Normalized throughput speed calculated via Ollama `eval_count / (eval_duration / 1e9)` (e.g., $<10\text{ tok/s} \to 3/10$, $20\text{ tok/s} \to 7/10$, $\ge 35\text{ tok/s} \to 10/10$). | 0 – 10 |
   | **Speed** | **Reply Time** | Total latency calculated from `(prompt_eval_duration + eval_duration) / 1e9` (e.g., $<1.5\text{s} \to 10/10$, $3\text{s} \to 8/10$, $>8\text{s} \to 3/10$). | 0 – 10 |
   | **Reasoning** | **Instruction Following** | Evaluated by Gemini judge: verifies strict adherence to prompt constraints, tone, and absence of conversational filler. | 0 – 10 |
   | **Reasoning** | **Markdown Compatibility** | Validates proper Markdown AST/formatting (headings, lists, task checkboxes `- [ ]`, code blocks, `[[WikiLinks]]`). | 0 – 10 |
   | **Overall** | **Overall Score** | **Exact arithmetic mean** of the above 7 criteria scores. | **0 – 10** |

6. **Results Presentation & Comparative Scorecard:**
   - Renders directly in the right pane (`#evaluation-content-pane`):
     - **Comparative Model Scorecard Table:** Displays side-by-side columns for each evaluated model with individual criteria scores and bold **Overall Score**.
     - **Best Performing Model Badge:** Highlights the top-scoring model across all criteria.
     - **Per-Question Breakdown Accordion:** Expandable details per question showing prompt, retrieved context, each model's answer, ground truth, latency, and individual item scores.
   - **Database Persistence:** Benchmark runs and item scores are persisted in `LocalLLMEvaluationRun` and `LocalLLMResultMetric` for historical review and tracking.

7. **CSV Export Capabilities:**
   - Includes a **"Download Benchmark CSV"** button (`/rag/evaluate/local-llm/<run_id>/export-csv/`).
   - Exports the complete dataset with the following exact columns:
     1. `model_name`
     2. `question`
     3. `answer`
     4. `model_answer`
     5. `faithfulness`
     6. `context_utilization`
     7. `citation_accuracy`
     8. `tokens_per_second`
     9. `reply_time`
     10. `instruction_following`
     11. `markdown_compatibility`
     12. `overall_score`

---

## 2. Common & Required Commands

### Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Local Development Server
```bash
python manage.py runserver
```

### Automated Unit Testing
```bash
# Run evaluation unit tests
./.venv/bin/pytest Testing/unit/evaluate/ -v

# Run full project test suite
./.venv/bin/pytest
```

### Ollama Verification
```bash
# Verify local Ollama daemon is active
curl http://localhost:11434/api/tags
```

---

## 3. Project Structure & Key Files

```
src/apps/evaluate/
├── models.py                   # LocalLLMEvaluationRun & LocalLLMResultMetric models
├── eval_services.py            # Ollama client, context retrieval, Gemini judge & 7-metric scoring algorithms
├── admin_views.py              # Ollama model discovery endpoint, benchmark execution & CSV export views
├── urls.py                     # Route registrations for Local LLM endpoints
└── admin.py                    # ModelAdmin registrations for Unfold admin

templates/admin/
├── evaluation_workflow.html    # Method switcher with Local LLMs multi-select controls & CSV upload pane
├── local_llm_scorecard.html    # Rendered comparative summary table & per-question drilldown
└── partials/
    └── local_llms_controls.html # Dynamic model selector and execution trigger

Testing/unit/evaluate/
├── test_local_llm_eval.py      # Unit tests for Ollama model listing, CSV parsing & metric scoring
└── test_local_llm_views.py     # View tests for HTMX benchmark execution & CSV export
```

---

## 4. Code Style & Guidelines

- **Architecture:** Keep views thin; encapsulate Ollama communication, Gemini judging, and metric scoring inside `src/apps/evaluate/eval_services.py`.
- **Typing & Formatting:** PEP 8 compliance, double quotes for strings, explicit type hints across all service functions.
- **Frontend Interactivity:** HTMX-driven partial swaps (`hx-post`, `hx-target="#evaluation-content-pane"`, `hx-swap="innerHTML"`) consistent with the Unfold admin UI.
- **Resilience:** Default `OLLAMA_BASE_URL` to `http://localhost:11434` with environment variable override. Handle network timeouts and connection refusal with user-friendly error alerts.
- **CSV Robustness:** Support case-insensitive column matching (`Question`, `QUESTIONS`, `Answer`, `Ground Truth`, etc.) and seamlessly ignore unneeded columns.

---

## 5. Testing Strategy

### Unit Tests (`Testing/unit/evaluate/`)
1. **`test_local_llm_eval.py`**:
   - Mock Ollama API responses (`/api/tags` and `/api/generate` with timing breakdown).
   - Test CSV parser with standard columns, case variations, extra ignored columns, and empty file validation.
   - Mock Gemini judge JSON evaluation responses.
   - Test individual scoring algorithms for all 7 criteria to ensure bounds are strictly between `0.0` and `10.0`.
   - Test arithmetic average calculation for Overall Score.

2. **`test_local_llm_views.py`**:
   - Test HTMX endpoint fetching available Ollama models.
   - Test benchmark initiation endpoint with mock dataset, models, and project.
   - Test scorecard template rendering with side-by-side comparative tables.
   - Test CSV export endpoint returning valid CSV matching the 12 specified columns.

---

## 6. Guardrails & Boundaries

### Dos (Always Do)
- **Always** normalize all criteria scores to a `0.0 – 10.0` scale.
- **Always** calculate Overall Score as the exact arithmetic mean of the 7 evaluated criteria.
- **Always** ignore extra columns in uploaded CSV files without raising errors.
- **Always** use Ollama's `eval_duration` to isolate token generation speed from initial model loading.
- **Always** persist evaluation runs in the database for tracking and reproducible CSV exports.

### Ask Before
- Changing the 7 core evaluation criteria or their score weighting.
- Introducing external heavy evaluation dependencies (e.g. Deepeval) rather than lightweight in-house metric scoring.

### Don'ts (Never Do)
- **Never** hardcode local Ollama URLs without `os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")`.
- **Never** crash or fail the entire evaluation run if a single Q&A generation encounters a timeout; log the error and record a 0 score for that item.
- **Never** alter existing RAGAS or Synthetic QA workflows while adding Local LLM capabilities.
