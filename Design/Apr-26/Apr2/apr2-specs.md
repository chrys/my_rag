# Spec: Apr2 Postgres RAG Completion

## Assumptions I'm Making

1. Apr2 is focused on closing the currently documented functional gaps for Postgres RAG projects rather than redesigning all three project types.
2. The existing Django dashboard, HTMX flows, and function-based view patterns remain the preferred delivery path.
3. PostgreSQL is the required backing store for Postgres RAG projects in production and SQLite fallback is not acceptable for this feature scope.
4. Google Gemini remains the answer-generation model for Postgres RAG chat in this phase.
5. The existing optional AI dependency split using `requirements-ai.txt` remains in place.

## Objective

Define the Apr2 implementation scope needed to make Postgres RAG projects behave as a production-ready project type for creation, prompt management, document indexing, and chat.

Success for Apr2 means a Postgres RAG project is consistently backed by PostgreSQL, uses project-scoped prompts stored in the application data model, enforces project ownership in its main flows, and fails clearly when required infrastructure is not available.

## Problem Statement

Postgres RAG projects exist today, but their behavior is incomplete and inconsistent with the product requirement. The current implementation mixes live `postgres` behavior with older model choices, persists prompts outside the main database model, silently falls back to SQLite when PostgreSQL is not configured, and lacks project ownership safeguards in prompt and chat flows. This makes the feature operationally risky and weakens confidence that a Postgres RAG project is truly isolated, persistent, and backed by the intended infrastructure.

## Constraints

- Follow the existing Django app structure under `apps/projects`, `apps/documents`, `apps/chat`, and `src/`.
- Preserve the existing user-facing concept of three project types: Local, Google File Search, and Postgres RAG.
- Keep `Project.project_id` as the stable identifier used by routes, prompt lookup, document indexing, and chat.
- Do not add new external dependencies unless the current implementation gap cannot be closed with the existing stack.
- Do not replace Gemini with a different answer-generation provider in this phase.
- Do not broaden Apr2 into a full RAG architecture rewrite or a full background-jobs platform unless explicitly approved later.

## Scope

### In Scope

- Align the Postgres RAG project model semantics with the active `postgres` runtime behavior.
- Define expected creation-time validation for Postgres RAG prerequisites.
- Move project prompt persistence from JSON-file storage into the Django model layer.
- Switch active prompt reads and writes to the Django model layer without requiring one-time migration of existing JSON prompt data.
- Enforce project-scoped authorization for Postgres RAG prompt and chat access.
- Require PostgreSQL-backed txtai content storage for Postgres RAG indexing.
- Define clearer indexing lifecycle behavior for success, failure, and cleanup expectations.
- Keep indexing synchronous for Apr2, with improved validation and error handling in the request flow.
- Define readiness requirements for Postgres RAG chat, including dependency and Gemini credential availability.
- Define minimum acceptable source attribution behavior for responses returned from Postgres RAG chat.

### Out of Scope

- Replacing txtai with another embeddings/search framework.
- Replacing Google Gemini with another LLM provider.
- Redesigning Local project or Google File Search project behavior beyond shared validation patterns.
- Building a full async task system for every document workflow in the product.
- Requiring background execution for Postgres RAG indexing in Apr2.
- Introducing multi-turn memory, agent workflows, or advanced orchestration beyond the current retrieval-plus-generation flow.
- Adding new document parsers beyond clarifying the supported types for this phase.

## Commands

Dev server: `python manage.py runserver`

Focused tests: `DJANGO_ENV=testing pytest Testing/unit -v`

Postgres RAG slice tests: `DJANGO_ENV=testing pytest Testing/unit/chat Testing/unit/documents Testing/unit/projects -v`

Regression tests: `DJANGO_ENV=testing pytest Testing/regression -v`

Dependency install: `pip install -r requirements.txt`

Optional AI dependency install: `pip install -r requirements-ai.txt`

## Project Structure

`apps/projects/` → project creation, deletion, and prompt management flows

`apps/documents/` → document upload, list, and delete flows for project documents

`apps/chat/` → chat request handling and response persistence

`src/postgres_rag.py` → Postgres RAG indexing and retrieval engine

`apps/projects/models.py` → `Project` and `SystemPrompt` data model definitions

`apps/documents/models.py` → `Document` tracking and indexing state metadata

`Documentation/RAG/` → current-state RAG documentation

`Design/Apr-26/Apr2/` → Apr2 planning and specification artifacts

## Code Style And Design Expectations

- Match existing Django patterns already used in the repo: function-based views, explicit branching by `storage_type`, and ORM-backed ownership checks.
- Prefer explicit failure over silent fallback for infrastructure-dependent Postgres RAG behavior.
- Keep project-specific business rules out of templates.
- Use the Django model layer as the source of truth for prompts, projects, and document metadata.
- Keep public behavior consistent across UI and API paths where they touch the same Postgres RAG concept.

## Testing Strategy

- Add or update focused pytest coverage for each Postgres RAG slice changed in Apr2.
- Validate model-level behavior for `Project` storage types and `SystemPrompt` persistence.
- Validate prompt access and chat access are scoped to the owning authenticated user where ownership applies.
- Validate document upload fails clearly when PostgreSQL-backed txtai storage prerequisites are not met.
- Validate successful Postgres RAG indexing creates or updates `Document` state consistently.
- Validate chat behavior for:
	- missing dependencies
	- missing Gemini credentials
	- no indexed documents
	- successful retrieval with source information
- Run focused tests first, then broaden only if the changed surfaces require it.

## Feature Requirements And Acceptance Criteria

### A. Postgres RAG Project Creation

#### Requirement

A user can create a Postgres RAG project that is represented consistently across model, view, and UI behavior.

#### Acceptance Criteria

- The `Project` data model recognizes `postgres` as a first-class storage type used by the runtime code.
- Creating a Postgres RAG project produces a `Project` record that is internally consistent with downstream document and chat flows.
- The project creation flow surfaces a clear error or warning when required Postgres RAG prerequisites are unavailable.
- Deleting a Postgres RAG project has a defined cleanup contract for its persisted ANN index and project-scoped stored content.

### B. Project-Specific Prompt Management

#### Requirement

A user can create, update, and retrieve a prompt attached to a specific Postgres RAG project using the application data model.

#### Acceptance Criteria

- Prompt content for Postgres RAG projects is stored through the `SystemPrompt` Django model rather than the JSON-file helper.
- Prompt lookup is keyed by the owning project and not only by raw `store_id` string lookup in a file.
- Prompt reads and writes enforce the same ownership rules as the project itself.
- Chat uses the project's persisted prompt when no prompt is passed explicitly in the request.
- The system defines how empty prompts are handled for projects without custom prompt content.
- Apr2 does not require one-time migration of existing prompt JSON content into the database.

### C. Document Upload And Indexing

#### Requirement

A user can upload supported documents to a Postgres RAG project and have them indexed using txtai with PostgreSQL-backed content storage.

#### Acceptance Criteria

- The indexing flow fails fast when PostgreSQL-backed txtai storage is not configured correctly.
- Silent fallback to SQLite is removed or explicitly disallowed for Postgres RAG project indexing.
- Successful indexing updates the corresponding `Document` record with consistent indexed state and timestamp metadata.
- Failed indexing updates the corresponding `Document` record with a visible failed state and useful failure details.
- The system defines supported file types for Apr2 and rejects unsupported types clearly.
- Document deletion for Postgres RAG projects has a defined cleanup path for associated stored index/content artifacts.
- Indexing remains synchronous in Apr2 and returns a clear request-scoped success or failure result.

### D. Project-Scoped RAG Chat

#### Requirement

A user can chat with a Postgres RAG project and receive Gemini-generated answers based only on that project's indexed content and prompt configuration.

#### Acceptance Criteria

- Chat access is restricted to the project owner where project ownership applies.
- Chat fails clearly when the optional AI dependencies or Gemini configuration are unavailable.
- Retrieval uses only the target project's persisted txtai index.
- The generated answer includes project-scoped prompt context when a custom prompt exists.
- The user-facing response includes document-name-only source attribution for the documents used in retrieval.
- The system defines the fallback behavior when no indexed content exists for the project.
- Project deletion fully removes all project-related persisted ANN indexes and Postgres-backed txtai stored content.

## Non-Goals

- Implementing multi-turn memory or conversation summarization for Postgres RAG chat.
- Supporting arbitrary binary document formats beyond the explicitly approved file list.
- Solving large-scale indexing throughput, distributed workers, or bulk import workflows.
- Introducing cross-project search, shared prompts, or shared document pools.
- Reworking the Local and Google File Search project architectures in Apr2.

## Risks

- Model/runtime alignment risk: the current `Project` model and active `postgres` code path are inconsistent, which can create migration and compatibility work.
- Authorization risk: adding ownership checks may expose existing flows that currently assume unrestricted project access.
- Operational risk: removing SQLite fallback may surface environment setup problems earlier, which is desirable but may break currently permissive deployments.
- Cleanup risk: deleting project-scoped ANN indexes and stored content needs careful definition to avoid orphaned artifacts or accidental data loss.
- Cleanup risk: full deletion of all project-related artifacts raises the risk of accidental over-deletion if project scoping is wrong.

## Boundaries

### Always Do

- Keep Postgres RAG behavior project-scoped by `project_id`.
- Prefer database-backed persistence for application-owned state.
- Fail clearly when required infrastructure for Postgres RAG is missing.
- Add focused tests for each changed Postgres RAG behavior slice.

### Ask First

- Any schema or migration change beyond what is necessary to support prompt/model alignment.
- Adding new infrastructure dependencies such as task queues or external vector stores.
- Any change that alters public URL behavior or project identifiers.
- Any removal of compatibility behavior that might affect existing projects in production.

### Never Do

- Silently route a Postgres RAG project to non-Postgres persistence in the finished Apr2 behavior.
- Store project prompts only in filesystem JSON for the final Apr2 implementation.
- Expose one user's Postgres RAG project content or prompt to another user.
- Expand Apr2 into a broad architecture rewrite without a separate approved spec.

## Success Criteria

- The Apr2 implementation closes the currently documented missing functionality for Postgres RAG creation, prompts, document indexing, and chat.
- The source of truth for Postgres RAG prompts is the Django data model.
- Postgres RAG indexing is explicitly PostgreSQL-backed and no longer quietly downgrades to SQLite.
- The main Postgres RAG flows have clear authorization and readiness behavior.
- Postgres RAG project deletion removes all project-related indexed and stored artifacts.
- Focused automated tests exist for the changed slices and pass under the test environment.

## Open Questions

- None currently blocking spec approval.
