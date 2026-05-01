# Implementation Plan: Apr2 Postgres RAG Completion

## Overview

This plan implements the approved Apr2 scope for Postgres RAG projects in small, independently testable slices. The order follows the dependency chain from model and persistence alignment, to engine behavior, to request flows, and finally to cleanup and response shaping.

## Architecture Decisions

- Treat `postgres` as the canonical runtime storage type for Postgres RAG projects.
- Keep indexing synchronous in Apr2 and improve validation and failure reporting instead of introducing background jobs.
- Move active prompt reads and writes to the Django model layer without requiring one-time migration of legacy JSON prompt data.
- Remove SQLite fallback for Postgres RAG indexing and require explicit PostgreSQL-backed readiness.
- Expose document-name-only source attribution in Postgres RAG chat responses.
- Fully delete project-related RAG artifacts when a Postgres RAG project is deleted.

## Task List

### Phase 1: Model And Persistence Alignment

## Task 1: Align Postgres project model semantics

**Description:**
Make the project model and any directly related model-level logic explicitly recognize `postgres` as the active storage type used by the runtime code so downstream request flows stop depending on an implicit mismatch.

**Acceptance criteria:**
- [x] The `Project` model accepts `postgres` as a first-class storage type.
- [x] Model-level tests cover creation and retrieval of Postgres RAG projects using `storage_type='postgres'`.
- [x] No existing runtime path needs legacy `rag` storage type values to operate for Apr2 behavior.

**Verification:**
- [x] Tests pass: `DJANGO_ENV=testing pytest Testing/unit/projects -v`
- [x] Manual check: create a Postgres project through the existing flow and confirm the stored type is `postgres`.

**Dependencies:** None

**Rollback:**
- Revert the model/storage-type alignment change if it breaks existing project creation or lookup behavior before downstream slices are updated.

**Files likely touched:**
- `apps/projects/models.py`
- `Testing/unit/projects/*`

**Estimated scope:** Small

## Task 2: Move active prompt persistence to Django model

**Description:**
Replace active Postgres RAG prompt reads and writes with `SystemPrompt` model-backed behavior while keeping legacy JSON prompt migration out of scope for Apr2.

**Acceptance criteria:**
- [x] Prompt get/set behavior for Postgres RAG projects reads from and writes to the Django model layer.
- [x] Empty prompt behavior is explicitly defined and covered by tests.
- [x] Legacy JSON prompt data is not required for the Apr2 happy path.

**Verification:**
- [x] Tests pass: `DJANGO_ENV=testing pytest Testing/unit/projects -v`
- [x] Manual check: save a prompt for a Postgres project and retrieve it through the existing flow.

**Dependencies:** Task 1

**Rollback:**
- Restore the prior prompt helper usage if model-backed prompt operations fail or block chat entirely.

**Files likely touched:**
- `apps/projects/views.py`
- `apps/projects/models.py`
- `src/prompt_storage.py`
- `Testing/unit/projects/*`

**Estimated scope:** Medium

### Checkpoint: Foundation

- [x] Project creation and prompt persistence tests pass.
- [x] Postgres projects and prompt records can be created through the current application flow.
- [ ] No broader regression has been introduced in project management basics.

### Phase 2: Authorization And Readiness Controls

## Task 3: Enforce project ownership for prompt and chat access

**Description:**
Apply project-scoped ownership checks to the Postgres RAG prompt and chat flows so one user cannot read or act on another user's project data.

**Acceptance criteria:**
- [x] Prompt read/write operations enforce project ownership where ownership applies.
- [x] Chat access enforces project ownership where ownership applies.
- [x] Unauthorized access returns a clear error path rather than falling through to normal processing.

**Verification:**
- [x] Tests pass: `DJANGO_ENV=testing pytest Testing/unit/projects Testing/unit/chat -v`
- [x ] Manual check: authenticated user A cannot use prompt or chat flows for user B's Postgres project.

**Dependencies:** Task 2

**Rollback:**
- Revert ownership enforcement only if it blocks legitimate owner access and the issue cannot be corrected within the slice.

**Files likely touched:**
- `apps/projects/views.py`
- `apps/chat/views.py`
- `Testing/unit/projects/*`
- `Testing/unit/chat/*`

**Estimated scope:** Medium

## Task 4: Add Postgres RAG readiness checks

**Description:**
Make Postgres RAG flows fail clearly when required infrastructure is missing, including missing AI dependencies, Gemini configuration, or PostgreSQL-backed txtai prerequisites.

**Acceptance criteria:**
- [x] Postgres RAG creation or use surfaces a clear readiness failure when prerequisites are absent.
- [x] Chat readiness failures are distinct from no-results behavior.
- [x] Indexing readiness failures happen before any silent fallback to SQLite or partial indexing behavior.

**Verification:**
- [x] Tests pass: `DJANGO_ENV=testing pytest Testing/unit/chat Testing/unit/documents Testing/unit/projects -v`
- [ ] Manual check: misconfigured Postgres or Gemini environment yields explicit failure messaging.

**Dependencies:** Tasks 1-3

**Rollback:**
- Restore the previous readiness behavior only if the new checks produce false negatives that block configured environments.

**Files likely touched:**
- `src/postgres_rag.py`
- `apps/chat/views.py`
- `apps/documents/views.py`
- `apps/projects/views.py`
- `Testing/unit/chat/*`
- `Testing/unit/documents/*`

**Estimated scope:** Medium

### Checkpoint: Access And Readiness

- [x] Unauthorized project access is blocked.
- [x] Missing dependency and config states fail clearly.
- [x] Existing valid Postgres RAG flows still succeed in a configured environment.

### Phase 3: Indexing Lifecycle

## Task 5: Remove SQLite fallback and enforce PostgreSQL-backed indexing

**Description:**
Change the Postgres RAG engine so indexing for Postgres projects requires PostgreSQL-backed txtai content storage and never silently downgrades to SQLite.

**Acceptance criteria:**
- [x] Postgres RAG indexing no longer falls back to SQLite.
- [x] Indexing setup clearly requires PostgreSQL-backed txtai content storage.
- [x] Failure to configure PostgreSQL correctly stops indexing cleanly.

**Verification:**
- [x] Tests pass: `DJANGO_ENV=testing pytest Testing/unit/documents -v`
- [ ] Manual check: misconfigured database settings fail before indexing begins.

**Dependencies:** Task 4

**Rollback:**
- Revert only if the engine cannot operate against correctly configured PostgreSQL after the fallback removal.

**Files likely touched:**
- `src/postgres_rag.py`
- `Testing/unit/documents/*`
- `Testing/unit/chat/test_postgres_rag.py`

**Estimated scope:** Small

## Task 6: Improve synchronous indexing state handling

**Description:**
Keep indexing in-request for Apr2, but make success and failure states explicit in document records and user-visible responses.

**Acceptance criteria:**
- [x] Successful indexing writes consistent `Document` state and timestamps.
- [x] Failed indexing writes a failed state and useful failure details.
- [x] Unsupported file types are rejected clearly.
- [x] The request flow returns explicit success or failure results without partial silent success.

**Verification:**
- [x] Tests pass: `DJANGO_ENV=testing pytest Testing/unit/documents -v`
- [x] Manual check: upload supported and unsupported files to a Postgres project and confirm state transitions.

**Dependencies:** Task 5

**Rollback:**
- Revert the failure-state update logic if it corrupts existing document record behavior or leaves documents stuck in incorrect states.

**Files likely touched:**
- `apps/documents/views.py`
- `apps/documents/models.py`
- `src/postgres_rag.py`
- `Testing/unit/documents/*`

**Estimated scope:** Medium

## Task 7: Implement full cleanup for document and project deletion

**Description:**
Define and implement the cleanup path that removes all Postgres RAG artifacts for deleted documents and deleted projects, including persisted ANN indexes and project-scoped stored content.

**Acceptance criteria:**
- [x] Deleting a Postgres RAG document removes its related index/content artifacts according to the Apr2 cleanup contract.
- [x] Deleting a Postgres RAG project removes all project-related persisted ANN indexes and stored content.
- [x] Cleanup logic is scoped safely to the target document or project.

**Verification:**
- [x] Tests pass: `DJANGO_ENV=testing pytest Testing/unit/documents Testing/unit/projects -v`
- [ x] Manual check: delete a Postgres project and confirm related persisted artifacts are removed.

**Dependencies:** Tasks 5-6

**Rollback:**
- Disable full cleanup if project scoping is found to be unsafe, then restore prior delete behavior until corrected.

**Files likely touched:**
- `apps/documents/views.py`
- `apps/projects/views.py`
- `src/postgres_rag.py`
- `Testing/unit/documents/*`
- `Testing/unit/projects/*`

**Estimated scope:** Medium

### Checkpoint: Indexing Lifecycle

- [x] Postgres indexing is PostgreSQL-only.
- [x] Synchronous indexing reports success and failure correctly.
- [x] Deletion cleanup removes the intended Postgres RAG artifacts and nothing else.

### Phase 4: Chat Response Completion

## Task 8: Add document-name-only attribution to chat responses

**Description:**
Expose the names of retrieved source documents in the Postgres RAG chat response without adding richer citation metadata in Apr2.

**Acceptance criteria:**
- [x] Postgres RAG chat responses expose document-name-only attribution for retrieved sources.
- [x] The attribution shape is consistent across the relevant response path used by the product.
- [x] No score or snippet rendering is required for Apr2.

**Verification:**
- [x] Tests pass: `DJANGO_ENV=testing pytest Testing/unit/chat -v`
- [ ] Manual check: a Postgres RAG answer shows the names of the source documents used in retrieval.

**Dependencies:** Tasks 3-7

**Rollback:**
- Remove the new attribution field if it breaks the current response contract, then reintroduce it after contract alignment.

**Files likely touched:**
- `src/postgres_rag.py`
- `apps/chat/views.py`
- `Testing/unit/chat/*`

**Estimated scope:** Small

## Task 9: Update documentation to match shipped Apr2 behavior

**Description:**
Bring the current-state RAG documentation in line with the completed Apr2 implementation so the docs describe actual behavior rather than pre-Apr2 gaps.

**Acceptance criteria:**
- [x] The RAG documentation reflects shipped Postgres RAG behavior after Apr2 implementation.
- [x] Any Apr2 notes accurately describe prompt storage, PostgreSQL-only indexing, cleanup behavior, and document-name-only attribution.

**Verification:**
- [ ] Manual check: documentation matches the final implemented behavior and no longer describes resolved gaps as unresolved.

**Dependencies:** Tasks 1-8

**Rollback:**
- Revert documentation updates if they claim behavior not yet implemented.

**Files likely touched:**
- `Documentation/RAG/rag_projects.md`
- `Design/Apr-26/Apr2/*`

**Estimated scope:** Small

### Checkpoint: Complete

- [x] Focused tests for projects, documents, and chat all pass.
- [x] Postgres RAG creation, prompting, upload/indexing, chat, and deletion work end-to-end.
- [x] Apr2 documentation matches shipped behavior.

## Risks And Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Model/runtime storage-type mismatch breaks existing lookups | High | Land model alignment first and verify project creation before touching downstream flows |
| Prompt model switch disrupts chat behavior | Medium | Isolate prompt persistence in its own slice and verify prompt-backed chat before continuing |
| Removing SQLite fallback exposes environment issues immediately | Medium | Add explicit readiness checks before removing fallback and test both configured and misconfigured states |
| Ownership enforcement blocks legitimate access | Medium | Add focused owner/non-owner tests before broadening changes |
| Full cleanup deletes too broadly | High | Scope cleanup by `project_id`, add targeted tests, and checkpoint before shipping |
| Attribution change breaks response contracts | Low | Add attribution in a narrow slice at the end and verify the active response path only |

## Dependency Order Summary

1. Model alignment
2. Prompt persistence
3. Ownership enforcement
4. Readiness checks
5. PostgreSQL-only engine behavior
6. Synchronous indexing state handling
7. Cleanup behavior
8. Chat attribution
9. Documentation update

## Rollback Strategy

- Roll back by slice, not as a single large revert.
- If a foundation task fails, stop and fix before proceeding to dependent tasks.
- If a cleanup task proves unsafe, disable cleanup logic first and keep the rest of the Apr2 slices intact.
- If response-shape changes break UI behavior, revert the attribution slice independently without undoing core authorization or indexing fixes.
