---
description: Break work into small verifiable tasks with acceptance criteria and dependency ordering based on a spec file.
agent: plan
---
Invoke the `planning-and-task-breakdown` engineering skill.

You are entering a read-only plan mode. Analyze the existing specification file provided below and cross-reference relevant codebase sections. 

### Your Core Tasks:
1. Identify the dependency graph between components (establish bottom-up implementation order).
2. Slice the required work vertically (one complete path per task delivering testable functionality, not horizontal layers).
3. Write individual tasks featuring clean description blocks, strict acceptance criteria, and specific verification steps (e.g., using `python manage.py test` rules).
4. Add verification checkpoints between major phases.
5. Present the finalized plan for human review.

### Execution Rule:
Directly write the comprehensive plan output and the corresponding task list to their designated system file paths below using the edit directive. Do not output any implementation application code.

---
### TARGET SPECIFICATION FILE:
$1

### SPECIFICATION CONTENTS TO PARSE:
!`cat $1`
---

# INSTRUCTIONS TO AGENT (SAVE ARTIFACTS)
Write the comprehensive master plan to this file:
!write(!dirname($1)/plan.md)

Write the structured todo checklist to this file:
!write(!dirname($1)/todo.md)