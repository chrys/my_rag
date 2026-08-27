---
name: plan-task
description: Break work into small verifiable tasks with acceptance criteria and dependency ordering
---

Invoke the planning-and-task-breakdown skill.

This workflow accepts the specs file path as an argument ($1). Read the specifications from the provided file. Then:

1. Enter plan mode — read only, no code changes
2. Identify the dependency graph between components
3. Slice work vertically (one complete path per task, not horizontal layers)
4. Write tasks with acceptance criteria and verification steps
5. Add checkpoints between phases
6. Present the plan for human review

Save the plan to plan.md and task list to todo.md in the same directory as the specifications file (e.g., in `dirname($1)/plan.md` and `dirname($1)/todo.md`).
