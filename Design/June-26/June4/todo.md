# Todo List: Switcher & Synthetic QA Restoration

## Phase 1: Service Layer Restoration
- [x] Task: Restore SyntheticQAEvaluator
  - Acceptance: `SyntheticQAEvaluator` class implemented in `src/apps/evaluate/eval_services.py` with `fetch_document_nodes` (using psycopg2), `generate_synthetic_questions` (using genai.Client), and `evaluate_retrieval_recall` methods.
  - Verify: Verify using test suite.
  - Files:
    - [MODIFY] [eval_services.py](file:///Users/chrys/Projects/my_rag/src/apps/evaluate/eval_services.py)

---

## Phase 2: Views and Routes Restoration
- [x] Task: Implement RunEvaluationView and Admin URL Routing
  - Acceptance: `RunEvaluationView` implemented in `src/apps/evaluate/admin_views.py` handling POST requests, running evaluation, and returning rendered template. URL route `evaluate/run/` added to custom admin site in `src/apps/my_rag_project/admin.py`.
  - Verify: Post to endpoint manually or via tests.
  - Files:
    - [MODIFY] [admin_views.py](file:///Users/chrys/Projects/my_rag/src/apps/evaluate/admin_views.py)
    - [MODIFY] [admin.py](file:///Users/chrys/Projects/my_rag/src/apps/my_rag_project/admin.py)

---

## Phase 3: Templates & UI Components
- [x] Task: Implement Evaluation Scorecard Template
  - Acceptance: `templates/admin/evaluation_scorecard.html` created rendering scorecard, optimization insights, and citation log table.
  - Verify: Scorecard template renders correctly with dummy context.
  - Files:
    - [NEW] [evaluation_scorecard.html](file:///Users/chrys/Projects/my_rag/templates/admin/evaluation_scorecard.html)

- [x] Task: Integrate Dropdown Method Switcher in Workflow Dashboard
  - Acceptance: Method switcher dropdown is added, and JavaScript toggling hides/reveals RAGAS controls or Synthetic QA document selection and Evaluate button. Project dropdown option text updated to exclude QA items count.
  - Verify: Project selection displays method dropdown. RAGAS displays configure/run benchmark; Synthetic QA displays document list.
  - Files:
    - [MODIFY] [evaluation_workflow.html](file:///Users/chrys/Projects/my_rag/templates/admin/evaluation_workflow.html)

---

## Phase 4: Final Verification
- [x] Task: Implement and Run Unit Tests
  - Acceptance: Unit tests in `test_synthetic_qa_eval.py` cover `SyntheticQAEvaluator` methods and `RunEvaluationView` POST view, passing successfully.
  - Verify: Run `DJANGO_ENV=testing .venv/bin/pytest Testing/unit/evaluate/test_synthetic_qa_eval.py -v`
  - Files:
    - [MODIFY] [test_synthetic_qa_eval.py](file:///Users/chrys/Projects/my_rag/Testing/unit/evaluate/test_synthetic_qa_eval.py)
