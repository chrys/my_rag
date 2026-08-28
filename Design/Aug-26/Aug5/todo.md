# Task Checklist: Sprint Aug 5 - Unified Multi-Backend RAG with LiteLLM Router & SSE Streaming

**Sprint:** August 2026 (Aug 5)  
**Spec Document:** `Design/Aug-26/Aug5/aug5-specs.md`  
**Plan Document:** `Design/Aug-26/Aug5/plan.md`  
**Todo Path:** `Design/Aug-26/Aug5/todo.md`  

---

## Phase 1: Dependencies & Core LiteLLM Router Foundation

- [ ] **Task 1.1: Add LiteLLM Dependencies**
  - **Description:** Add `litellm` and `llama-index-llms-litellm` to `requirements/base.txt` and verify imports.
  - **Acceptance:** `litellm` and `llama_index.llms.litellm` can be imported in the virtualenv without errors.
  - **Verify:** `python -c "import litellm; from llama_index.llms.litellm import LiteLLM; print(litellm.__version__)"`
  - **Files:** `requirements/base.txt`

- [ ] **Task 1.2: Refactor LLM Router (`llm_router.py`)**
  - **Description:** Implement `generate_llm_response()` and `stream_llm_response()` using `litellm.completion()`, with normalized Ollama offline error mapping, thinking flags, and global fallbacks.
  - **Acceptance:** Sync generation returns clean response text; streaming generator yields SSE `data: {"token": "...", "done": false}\n\n` chunks.
  - **Verify:** `DJANGO_ENV=testing pytest Testing/unit/chat/test_llm_router.py -v`
  - **Files:** `src/apps/chat/llm_router.py`

- [ ] **Task 1.3: Router Unit Tests**
  - **Description:** Add comprehensive unit tests in `Testing/unit/chat/test_llm_router.py` testing sync completions, streaming generators, error handling, and parameter normalization.
  - **Acceptance:** 100% pass rate on all router tests.
  - **Verify:** `DJANGO_ENV=testing pytest Testing/unit/chat/test_llm_router.py -v`
  - **Files:** `Testing/unit/chat/test_llm_router.py`

---

## Phase 2: Project Model Configuration & Free-Text Model Input

- [ ] **Task 2.1: Update Project Model for Free-Text LLM Input**
  - **Description:** Change `Project.llm_model` in `src/apps/projects/models.py` to a `CharField(max_length=255, default='gemini/gemini-2.5-flash-lite')` without rigid choices, allowing any LiteLLM string.
  - **Acceptance:** Model accepts any valid LiteLLM identifier string.
  - **Verify:** `DJANGO_ENV=testing pytest Testing/unit/projects/test_models.py -v`
  - **Files:** `src/apps/projects/models.py`

- [ ] **Task 2.2: Generate and Apply Django Migrations**
  - **Description:** Create Django migration for `Project.llm_model` update and apply to database.
  - **Acceptance:** Migration applies cleanly on clean SQLite and PostgreSQL setups.
  - **Verify:** `DJANGO_ENV=testing python manage.py migrate`
  - **Files:** `src/apps/projects/migrations/0015_alter_project_llm_model.py`

- [ ] **Task 2.3: Update Admin & Serializers**
  - **Description:** Update Django Admin form and DRF serializers for `Project` to support free-text `llm_model` with helpful provider format hints.
  - **Acceptance:** Admin UI and DRF endpoints accept and validate `llm_model`.
  - **Verify:** `DJANGO_ENV=testing pytest Testing/unit/projects/test_serializers.py -v`
  - **Files:** `src/apps/projects/admin.py`, `src/apps/projects/serializers.py`, `src/apps/projects/views.py`

---

## Phase 3: Intent Classification & Adaptive HyDE via LiteLLM

- [ ] **Task 3.1: Refactor Intent Classification Service**
  - **Description:** Refactor `src/apps/chat/intent_service.py` to use `litellm.completion` with JSON structured mode and fast cloud routing (`gemini/gemini-2.5-flash-lite`).
  - **Acceptance:** Greetings/chitchat are intercepted with 0 vector searches; structured classification returns valid IntentType enum.
  - **Verify:** `DJANGO_ENV=testing pytest Testing/unit/chat/test_intent_classification.py -v`
  - **Files:** `src/apps/chat/intent_service.py`

- [ ] **Task 3.2: Refactor Adaptive HyDE Service**
  - **Description:** Refactor `generate_adaptive_hyde_passage()` in `src/apps/chat/services.py` to use `llm_router.generate_llm_response()`.
  - **Acceptance:** Conceptual queries generate hypothetical passages using project's configured model; direct lookups bypass HyDE.
  - **Verify:** `DJANGO_ENV=testing pytest Testing/unit/chat/test_chat_intent_integration.py -v`
  - **Files:** `src/apps/chat/services.py`

---

## Phase 4: Multi-Backend Chat View & SSE Streaming

- [ ] **Task 4.1: Wire PostgreSQL RAG & LlamaIndex with LiteLLM**
  - **Description:** Update `src/apps/chat/views.py` to use `llama_index.llms.litellm.LiteLLM` for PostgreSQL RAG query engines.
  - **Acceptance:** Queries execute against Postgres vector store and synthesize using the selected `llm_model`.
  - **Verify:** `DJANGO_ENV=testing pytest Testing/unit/chat/test_chat_rag_llm.py -v`
  - **Files:** `src/apps/chat/views.py`

- [ ] **Task 4.2: Wire Local FAISS & Google File Search with LiteLLM**
  - **Description:** Update Local FAISS and Google File Search routing in `src/apps/chat/views.py` to synthesize responses through LiteLLM.
  - **Acceptance:** Context and citations extracted properly across all 3 storage types.
  - **Verify:** `DJANGO_ENV=testing pytest Testing/unit/chat/test_chat_views.py -v`
  - **Files:** `src/apps/chat/views.py`, `src/google_file_search.py`

- [ ] **Task 4.3: Implement SSE Streaming in Chat View**
  - **Description:** Add support for `stream=true` parameter in `chat()` view, returning `StreamingHttpResponse` with SSE event chunks and final citation payload.
  - **Acceptance:** Streaming request returns `text/event-stream` with chunk deltas; sync request returns standard `JsonResponse`.
  - **Verify:** `DJANGO_ENV=testing pytest Testing/unit/chat/test_chat_views.py -k test_streaming -v`
  - **Files:** `src/apps/chat/views.py`

- [ ] **Task 4.4: Persist Streamed Messages to ChatMessage DB**
  - **Description:** Ensure the accumulated bot response is stored in `ChatMessage` upon completion of the SSE stream.
  - **Acceptance:** `ChatMessage.objects.filter(session_id=...)` contains complete prompt and answer after streaming completes.
  - **Verify:** `DJANGO_ENV=testing pytest Testing/unit/chat/test_chat_views.py -v`
  - **Files:** `src/apps/chat/views.py`

---

## Phase 5: Evaluation Suite Integration

- [ ] **Task 5.1: Update Synthetic QA Evaluator with LiteLLM**
  - **Description:** Refactor `src/apps/evaluate/eval_services.py` to use LiteLLM for synthetic question-answer dataset generation.
  - **Acceptance:** Synthetic datasets generate across different configured models.
  - **Verify:** `DJANGO_ENV=testing pytest Testing/unit/evaluate/test_synthetic_qa_eval.py -v`
  - **Files:** `src/apps/evaluate/eval_services.py`

- [ ] **Task 5.2: LLM-as-a-Judge Evaluation with LiteLLM & Judge Override**
  - **Description:** Update faithfulness, answer relevancy, and context recall evaluations to use LiteLLM, with support for optional Judge Model override in `EvaluationRun`.
  - **Acceptance:** Evaluation runs calculate metrics properly using LiteLLM judge.
  - **Verify:** `DJANGO_ENV=testing pytest Testing/unit/evaluate/test_local_llm_eval.py -v`
  - **Files:** `src/apps/evaluate/eval_services.py`, `src/apps/evaluate/admin_views.py`

---

## Phase 6: Frontend SSE Stream Reader & UI Polish

- [ ] **Task 6.1: Client-Side SSE Stream Reader**
  - **Description:** Implement SSE stream consumer in `static/js/chat.js` (or chat template partial) using `fetch` + `ReadableStreamDefaultReader` with markdown parsing.
  - **Acceptance:** Assistant bubble renders tokens live in real-time and appends citations at stream completion.
  - **Verify:** Manual verification in browser with live server (`python manage.py runserver`).
  - **Files:** `static/js/chat.js`, `templates/chat/chat.html`

---

## Phase 7: Full End-to-End Regression & System Verification

- [ ] **Task 7.1: Run Full Unit Test Suite**
  - **Command:** `DJANGO_ENV=testing pytest Testing/unit -v`
- [ ] **Task 7.2: Run Full Regression Test Suite**
  - **Command:** `DJANGO_ENV=testing pytest Testing/regression -v`
- [ ] **Task 7.3: Check Style and Linter**
  - **Command:** `flake8 src/ apps/ Testing/`
