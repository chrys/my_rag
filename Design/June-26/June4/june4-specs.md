# Spec: Evaluation Workflow Switcher and Synthetic QA Retrieval Validation

## 1. Objective & Scope

This specification defines the restoration of the "Synthetic QA Retrieval Validation" feature (originally Task 5 of June 2) and its integration with the Ragas project-level evaluation workflow implemented in June 3. It introduces an Evaluation Method selector that lets users choose between:
1. **RAGAS:** Project-level Ragas metrics (Context Recall, Context Precision, Faithfulness, Answer Relevancy) evaluated using the configured dataset.
2. **Synthetic QA:** Document-level retrieval recall validation using Gemini-generated questions compared against actual vector database citations.

### Core User Flow
1. **Project Selection:** The user selects a target PostgreSQL RAG project from the dropdown. The project dropdown displays only the display name of each project (without showing the QA items count).
2. **Evaluation Method Switcher:** A new dropdown field appears allowing the user to select either "RAGAS" or "Synthetic QA".
3. **RAGAS View:** 
   - Displays the RAGAS dataset status information box.
   - Shows the "Configure QA Dataset" link and "Run Benchmark Evaluation" button.
   - Triggers the existing asynchronous background Ragas evaluation workflow when clicked.
4. **Synthetic QA View:**
   - Displays a dynamic target document list selector that fetches documents in the `INDEXED` status for the selected project using HTMX.
   - Allows the user to select one document.
   - Shows the **Evaluate** button.
   - Clicking Evaluate posts the form to `/rag/dashboard/evaluate/run/` using HTMX with parameters `project_id`, `document_id`, and `eval_method="synthetic_qa"`, rendering a premium scorecard and citations log table in the results pane.

---

## 2. Common & Required Commands

All commands should be executed inside the virtual environment (`source .venv/bin/activate`):

```bash
# Running the local Django development server
python manage.py runserver

# Running Unit Tests for Evaluate App
DJANGO_ENV=testing .venv/bin/pytest Testing/unit/evaluate -v
```

---

## 3. Project Structure

The following specifies the files and paths affected by the implementation:

### Core Python Code
- **`[MODIFY] src/apps/evaluate/eval_services.py`**
  - Restore `SyntheticQAEvaluator` class which connects to the PostgreSQL database, retrieves document text nodes, generates synthetic questions using Gemini, queries the LlamaIndex retrieval pipeline, and computes the retrieval recall percentage.
- **`[MODIFY] src/apps/evaluate/admin_views.py`**
  - Restore `RunEvaluationView` class, which handles the POST request to execute retrieval recall tests and renders the scorecard.
- **`[MODIFY] src/apps/my_rag_project/admin.py`**
  - Re-register the custom admin URL route `evaluate/run/` mapping to `RunEvaluationView`.

### Templates & UI Components
- **`[MODIFY] templates/admin/evaluation_workflow.html`**
  - Update the project select option text to exclude the QA items count.
  - Implement the "Evaluation Method" dropdown and its JavaScript toggle behavior.
  - Integrate the Target Document selection container and HTMX evaluation trigger for Synthetic QA.
- **`[NEW] templates/admin/evaluation_scorecard.html`**
  - Create the UI template to render the premium scorecard, optimization insights, and citation log tables for Synthetic QA evaluation runs.

---

## 4. Code Style & Guidelines

- **Double Quotes:** Use double quotes `""` for strings except when single quotes are required inside strings.
- **Formatting:** Adhere to Python PEP 8 guidelines.
- **F-Strings:** Use f-strings instead of `%` or `.format()`.
- **Type Hints:** Include explicit type hints for arguments and return types for all non-trivial Python code.
- **Docstrings:** Use NumPy-style docstrings for all new or materially modified classes, methods, and functions.

---

## 5. Testing Strategy

### Verification Plan
- **Mocking External APIs:** In testing, mock the Gemini client (`genai.Client` and `GoogleGenAI`) to prevent live API network calls.
- **Tests to Execute:**
  - `Testing/unit/evaluate/test_synthetic_qa_eval.py`:
    - Add/update tests verifying `SyntheticQAEvaluator` fetches nodes, generates synthetic questions, runs queries against the mocked vector store, and calculates recall correctly.
    - Test the `RunEvaluationView` POST response under various parameters.
- Run tests:
  ```bash
  DJANGO_ENV=testing .venv/bin/pytest Testing/unit/evaluate/test_synthetic_qa_eval.py -v
  ```

---

## 6. Guardrails & Boundaries

### Always Do
- Keep the existing RAGAS evaluation flow completely intact.
- Handle database connection cleanup properly by closing the PostgreSQL cursor and connection.

### Ask First
- Changing database schemas or generating migrations.
- Adding third-party dependencies.

### Never Do
- Hardcode API credentials. Read `GOOGLE_API_KEY` dynamically from the environment.
- Render raw exception stack traces in the UI. Gracefully handle errors and render them in the scorecard error panel.
