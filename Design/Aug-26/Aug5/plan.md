# Implementation Plan: Sprint Aug 5 - Unified Multi-Backend RAG with LiteLLM Router & SSE Streaming

**Sprint:** August 2026 (Aug 5)  
**Spec Document:** `Design/Aug-26/Aug5/aug5-specs.md`  
**Plan Document:** `Design/Aug-26/Aug5/plan.md`  
**Todo List:** `Design/Aug-26/Aug5/todo.md`  

---

## 1. Overview

This plan decomposes the integration of **LiteLLM** as the universal router in front of all project operations (Chat, Ingestion, Intent Routing, Adaptive HyDE, and Evaluation) across the three supported storage backends (**PostgreSQL RAG**, **Local FAISS RAG**, and **Google File Search**), along with real-time **Server-Sent Events (SSE) token streaming**.

---

## 2. Architecture Decisions & Dependency Graph

### Core Architectural Decisions:
1. **Unified Router Entry (`llm_router.py`):** All LLM completions (sync and streaming) flow through `src/apps/chat/llm_router.py`. Individual views and services do not import vendor-specific SDKs directly.
2. **Decoupled Storage & Generation:** Storage backends (Postgres, Local FAISS, Google File Search) manage embeddings and retrieval independently; LiteLLM performs answer synthesis using any admin-configured model.
3. **Dual-Mode Chat API:** `/rag/api/chat/` supports both SSE streaming (`stream=true` -> `text/event-stream`) and standard synchronous JSON (`stream=false` -> `application/json`).
4. **Pre-Retrieval Routing:** Dedicated fast cloud model (`gemini/gemini-2.5-flash-lite`) for `<200ms` intent classification; project's configured model for Adaptive HyDE and final response synthesis.
5. **Configuration via Free-Text Input:** `Project.llm_model` accepts any LiteLLM-compatible string (`provider/model-name`). Provider API keys are auto-detected from environment variables (`.env`).

### Dependency Graph:
```
Phase 1: Dependencies & Core LiteLLM Router (`llm_router.py`)
    │
    ├── Phase 2: Project Model Configuration & Migrations
    │       │
    │       ├── Phase 3: Intent Classification & Adaptive HyDE via LiteLLM
    │       │       │
    │       │       └── Phase 4: Multi-Backend Chat View & SSE Streaming
    │       │               │
    │       │               └── Phase 6: Frontend SSE Stream Reader & UI Polish
    │       │
    │       └── Phase 5: Evaluation Suite LiteLLM Integration
    │
    └── Phase 7: Full End-to-End Regression & Verification
```

---

## 3. Implementation Phases & Tasks

### Phase 1: Dependencies & Core LiteLLM Router Foundation
- [ ] **Task 1.1:** Add `litellm` and `llama-index-llms-litellm` to `requirements/` and update environment settings.
- [ ] **Task 1.2:** Refactor `src/apps/chat/llm_router.py` to implement `generate_llm_response()` and `stream_llm_response()` with unified exception mapping and thinking flag handling.
- [ ] **Task 1.3:** Create unit tests in `Testing/unit/chat/test_llm_router.py` validating sync completion, SSE streaming generator, and Ollama offline error handling.

### Checkpoint: Router Foundation
- [ ] `Testing/unit/chat/test_llm_router.py` passes 100%.

---

### Phase 2: Project Model Configuration & Free-Text Model Input
- [ ] **Task 2.1:** Update `Project.llm_model` in `src/apps/projects/models.py` to support free-text LiteLLM model identifiers (max_length=255, default='gemini/gemini-2.5-flash-lite').
- [ ] **Task 2.2:** Create and apply Django database migration for `llm_model`.
- [ ] **Task 2.3:** Update Django Admin (`src/apps/projects/admin.py`), serializers (`src/apps/projects/serializers.py`), and project forms.
- [ ] **Task 2.4:** Unit tests in `Testing/unit/projects/test_models.py` and `test_serializers.py`.

### Checkpoint: Project Configuration
- [ ] Database migrations execute cleanly with `DJANGO_ENV=testing python manage.py migrate`.
- [ ] Project unit tests pass.

---

### Phase 3: Intent Classification & Adaptive HyDE via LiteLLM
- [ ] **Task 3.1:** Refactor `src/apps/chat/intent_service.py` to use `litellm.completion` with JSON structured mode and fast model routing.
- [ ] **Task 3.2:** Refactor `src/apps/chat/services.py` (`generate_adaptive_hyde_passage`) to use LiteLLM router.
- [ ] **Task 3.3:** Unit tests in `Testing/unit/chat/test_intent_classification.py` and `test_chat_intent_integration.py`.

### Checkpoint: Pre-Retrieval Routing
- [ ] Intent classification correctly intercepts greetings with 0 vector searches.
- [ ] HyDE passages generate successfully across different model strings.

---

### Phase 4: Multi-Backend Chat View & SSE Streaming
- [ ] **Task 4.1:** Refactor `src/apps/chat/views.py` to wire LlamaIndex LiteLLM query engine for PostgreSQL RAG (`storage_type='postgres'`).
- [ ] **Task 4.2:** Wire Local FAISS engine (`storage_type='local'`) and Google File Search (`storage_type='google'`) to use LiteLLM router.
- [ ] **Task 4.3:** Implement dual-mode response handling in `chat()` view:
  - If `stream=true`: return `StreamingHttpResponse` with SSE event stream (`data: {"token": ...}`).
  - If `stream=false`: return standard `JsonResponse`.
- [ ] **Task 4.4:** Ensure `ChatMessage` records are saved to the database upon completion of both streaming and sync responses.
- [ ] **Task 4.5:** Comprehensive unit tests in `Testing/unit/chat/test_chat_views.py` and `Testing/unit/chat/test_chat_rag_llm.py`.

### Checkpoint: Multi-Backend Chat & Streaming
- [ ] All 3 storage backends (Postgres, Local, Google) respond via LiteLLM.
- [ ] Streaming and non-streaming test cases pass.

---

### Phase 5: Evaluation Suite Integration
- [ ] **Task 5.1:** Update `src/apps/evaluate/eval_services.py` to use LiteLLM for synthetic QA generation and LLM-as-a-judge scoring.
- [ ] **Task 5.2:** Add optional Judge Model override in `EvaluationRun` and evaluation APIs.
- [ ] **Task 5.3:** Unit tests in `Testing/unit/evaluate/test_synthetic_qa_eval.py` and `Testing/unit/evaluate/test_local_llm_eval.py`.

### Checkpoint: Evaluation Engine
- [ ] Synthetic QA generation and metric evaluations run successfully using LiteLLM.

---

### Phase 6: Frontend SSE Stream Reader & UI Integration
- [ ] **Task 6.1:** Update frontend chat client script (`static/js/chat.js` or chat template) to support SSE streaming reader (`fetch` + `ReadableStream`).
- [ ] **Task 6.2:** Add live token rendering, autoscroll, and citation presentation upon stream completion.

---

### Phase 7: Full End-to-End Regression & System Verification
- [ ] **Task 7.1:** Run all unit test suites (`DJANGO_ENV=testing pytest Testing/unit -v`).
- [ ] **Task 7.2:** Run full regression suite (`DJANGO_ENV=testing pytest Testing/regression -v`).
- [ ] **Task 7.3:** Verify tenant isolation, permission boundaries, and offline Ollama error handling.

---

## 4. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| **Ollama Offline Drops:** Local Ollama server is stopped while user has selected an Ollama model. | Medium | Catch `litellm.exceptions.APIConnectionError` and emit a clear 500 error with instructions to start Ollama on `http://localhost:11434`. |
| **Provider Rate Limits (429):** High-frequency API calls during evaluations or chat. | Medium | Configure LiteLLM retry policies and global fallback models in `settings.py`. |
| **Streaming Mid-Flight Network Cut:** Client disconnects while LLM is generating tokens. | Low | Handle generator `GeneratorExit` cleanly in Django `StreamingHttpResponse` and persist tokens received so far. |
| **Model String Typos:** Admin enters invalid model name in free-text field. | Medium | Wrap LiteLLM model initialization in safe validation and return descriptive provider error messages. |
