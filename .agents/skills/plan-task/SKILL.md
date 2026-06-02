---
name: plan-task
description: Break work into small verifiable tasks with acceptance criteria and dependency ordering
arguments:
  - name: specification_file
    required: true
    description: "The path to the specification file (referenced as $1)"
---

# Skill: Planning and Task Breakdown

Invoke the planning-and-task-breakdown skill to analyze a finalized specification, identify dependencies, vertically slice implementation details, and output a technical plan and a checklist of verifiable tasks.

## Inputs
1. **Specification File ($1):** The absolute or relative path to the finalized specification file. The generated planning and task list files will be saved in the same directory as this specification file.

## Execution Steps

1. **Enter Plan Mode:**
   Enter plan mode. Focus entirely on reading the codebase, analyzing the system architecture, and designing the implementation. Do not make any source code changes in the codebase during this phase.

2. **Analyze Dependency Graph:**
   Map the dependencies between components. Ensure that base components (such as Django models and migrations) are implemented first, followed by services, views, URLs, templates, and tests.

3. **Slice Work Vertically:**
   Slice the implementation tasks vertically. Each task should represent a complete, testable path or chunk of functionality (e.g., model creation with tests, CSV parsing service with validation tests, HTMX progress spinner view with template) rather than horizontal architecture layers.

4. **Create the Technical Plan:**
   Formulate a technical implementation plan including:
   - Component dependency analysis.
   - Database migration and schema plans.
   - Service function and view signatures.
   - Verification checkpoints between development phases.

   Write this planning document to `plan.md` in the same directory as the specification file (e.g., `dirname($1)/plan.md`).

5. **Create the Task Checklist:**
   Break down the plan into a highly structured `todo.md` checklist in the same directory as the specification file (e.g., `dirname($1)/todo.md`). Each task must include:
   - **Task Title:** Clear description of the work.
   - **Acceptance Criteria:** Concrete, testable conditions for completion.
   - **Verify:** Specific verification commands (e.g., `pytest` commands) or manual checks.
   - **Files:** The list of files that will be created or modified.

   Use the standard markdown task format:
   ```markdown
   - [ ] Task: [Title]
     - Acceptance: [Conditions]
     - Verify: [Verification commands/checks]
     - Files: [Files list]
   ```

6. **Present for Review:**
   Present both the plan and the todo checklist to the user for review and explicit approval before proceeding to the build/execution phase.
