# Implementation Plan: Sprint Aug 6 - Dashboard Redesign & Document Management Solution

**Sprint:** August 2026 (Aug 6)  
**Spec Reference:** `Design/Aug-26/Aug6/aug6-specs.md`  
**Plan Document Path:** `Design/Aug-26/Aug6/plan.md`  
**Todo Path:** `Design/Aug-26/Aug6/todo.md`  

---

## 1. Overview & Architecture Strategy

This plan delivers the complete implementation of **Sprint Aug 6**, structured into vertically sliced phases:
1. **Pico.css Dashboard Shell**: Lightweight semantic layout with sticky top bar, project selector, and 5-section left sidebar.
2. **Configuration Workspace (1.1, 1.2, 1.3)**: Interactive Parameters, System Prompt, and API Key management.
3. **Advanced Sources & Document Management (2.1)**: Multi-tier deduplication (SHA-256 + SimHash), search/filters, chunk inspection, single/bulk deletion, and PGVector synchronization.
4. **Integrated Chat & Evaluation (3, 4, 5)**: Native Pico.css multi-model SSE streaming chat, synthetic QA generation, evaluation scorecards, and monitoring placeholder.
5. **Quality Assurance & Verification**: Full unit and regression test suite validation.

```
┌─────────────────────────────────────────────────────────────┐
│                      Pico.css Base Shell                    │
│      [Top Nav: Brand + Project Selector + Dark Mode]        │
├──────────────────────────┬──────────────────────────────────┤
│    Sidebar Navigation    │       Dynamic Workspace Area     │
│  1. Configuration        │       (#dashboard-workspace)    │
│     1.1 Parameters       │                                  │
│     1.2 Prompt           │   • Partial HTMX Swapping        │
│     1.3 API Keys         │   • Instant <50ms Transitions    │
│  2. Index                │   • Full Session Scoping         │
│     2.1 Sources          │   • Multi-Tier Deduplication     │
│  3. Chat                 │   • LiteLLM SSE Streaming        │
│  4. Evaluate             │   • Evaluation Scorecards        │
│  5. Monitor              │                                  │
└──────────────────────────┴──────────────────────────────────┘
```

---

## 2. Dependency Graph & Phase Sequencing

```
Phase 1: Pico.css Dashboard Shell & Routing
    │
    ├── Phase 2: Configuration Suite (1.1 Parameters, 1.2 Prompt, 1.3 API Keys)
    │
    ├── Phase 3: Sources & Document Management (Multi-Tier Deduplication + Filtering + PGVector Sync)
    │
    └── Phase 4: Native Chat & Evaluation Tabs (LiteLLM SSE Chat + Synthetic QA & Benchmarks)
            │
            ▼
Phase 5: Full Regression Testing & Verification Checkpoint
```

---

## 3. Detailed Phase Breakdown

### Phase 1: Pico.css Layout Foundation & Navigation Routing
* **Goal**: Establish the base dashboard shell, custom blue theme tokens, sticky project selector, and HTMX partial routing.
* **Key Tasks**:
  * Setup `static/css/pico.custom.css` with primary blue palette (`#2563eb`) and dark mode overrides.
  * Create `templates/dashboard/base.html` and `templates/dashboard/workspace.html`.
  * Implement `DashboardView` and project switcher routing in `src/apps/projects/views.py` and `urls.py`.

### Phase 2: Configuration Workspace (1.1 Parameters, 1.2 Prompt, 1.3 API Keys)
* **Goal**: Implement the Configuration menu category as native Pico.css partial views.
* **Key Tasks**:
  * **1.1 Parameters**: Project settings form, LiteLLM model identifier selector, parameter constraints, and HTMX save action.
  * **1.2 Prompt**: Monospace system prompt editor, custom prompt toggle, prompt presets, and HTMX save action.
  * **1.3 API Keys**: Active/revoked key listing, key generation dialog, copy-to-clipboard, and delete key.

### Phase 3: Sources & Document Management Solution (2.1 Sources)
* **Goal**: Build the multi-tier deduplication pipeline, search & multi-axis filtering, and document actions.
* **Key Tasks**:
  * **Multi-Tier Deduplication**: Tier 1 SHA-256 exact binary matching + Tier 2 SimHash textual near-duplicate detection in `src/apps/documents/services.py`.
  * **Interactive Modals**: Duplicate document modal (Skip vs Force Replace) and Revision Detected modal (Replace vs Stack vs Cancel).
  * **Search & Filters**: Real-time debounced search by name, date uploaded range, file extension, and ingestion status.
  * **Document Actions & PGVector Sync**: Chunk inspector modal, single atomic delete with PostgreSQL PGVector cleanup, multi-select bulk delete, and re-indexing parser override.
  * **Connectors Accordion**: Obsidian vault and Google Calendar sync panels.

### Phase 4: Native Chat, Evaluate & Monitor Workspace (3, 4, 5)
* **Goal**: Integrate Chat, Evaluation workflows, and Monitoring placeholder into the unified Pico.css layout.
* **Key Tasks**:
  * **3. Chat**: Multi-model query input, LiteLLM SSE streaming, source attribution accordions, and thumbs-up/down feedback.
  * **4. Evaluate**: Synthetic QA pair generator, automated evaluation runs, scorecards, manual judge mode, and local LLM benchmark runners.
  * **5. Monitor**: Telemetry and latency analytics placeholder card.

### Phase 5: Verification & Regression Testing
* **Goal**: Ensure 100% test pass rate across unit and regression test suites.
* **Key Tasks**:
  * Run and update unit test suites (`Testing/unit/`).
  * Run regression test suite (`Testing/regression/`).
  * Verify document isolation, PGVector table dropping, and multi-project switching.

---

## 4. Risks & Mitigations

| Risk | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Orphaned PGVector Chunks** | High | Wrap document deletions in atomic transactions that query and drop matching vector rows by `file_name` / `project_id`. |
| **Near-Duplicate False Positives** | Medium | Calibrate SimHash threshold to $85\%$ and provide explicit user choice (*"Index as Separate Document"* vs *"Replace Old Version"*). |
| **HTMX State Desynchronization** | Medium | Maintain active `project_id` in URL parameters and session state so refreshing preserves active tab and project. |

---

## 5. Definition of Done

- All 5 main navigation sections operational with Pico.css blue styling.
- Multi-tier deduplication successfully blocks exact duplicates and manages revisions.
- Search, multi-axis filtering, and single/batch deletion function seamlessly.
- All unit and regression tests pass with 0 failures.
