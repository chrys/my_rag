---
description: Implement the next pending task from your todo.md, tracking progress and logging build errors.
agent: build
---
Invoke the `incremental-implementation` skill alongside `test-driven-development`.

You are modifying files in this repository. Parse the user's provided `todo.md` path to identify, mark, and implement the next sequential unit of work.

### State-Tracking Protocol:
1. **Locate the Task:** Read the file provided in `$1`. Look for the **first** line item marked with an empty checkbox `[ ]`. Do not skip ahead.
2. **Mark Active:** Before executing code changes or test suites, update that task's checkbox from `[ ]` to `[~]` to indicate active state tracking.
3. **Mark Completed:** Once the task meets all acceptance criteria, passes its target tests, and is successfully committed, change the checkbox from `[~]` to `[X]`.

### Implementation Lifecycle:
1. Read the active task's descriptive criteria and check the current directory context.
2. Write an isolated, failing test targeting the new layout (RED).
3. Implement the minimum code updates required to turn the test green (GREEN).
4. Run your test commands via `python manage.py test`.

### Error Logging Protocol:
If a compilation crash, syntax breakdown, or test runner error occurs during your build processing loop:
- Extract the raw tracebacks and structural problems.
- Append a brief summary of the error alongside the failing file components to `errlog.md` in the exact same directory as your todo file. Use this syntax: `!write(!dirname($1)/errlog.md)`.
- Follow the `debugging-and-error-recovery` routine to fix the codebase. Do not clear the `errlog.md` file entries; allow them to aggregate so the user can audit persistent structural problems.

---
### TARGET TODO FILE PATH:
$1

### CURRENT TODO STATE:
!`cat $1`
---

# SYSTEM INSTRUCTION TO AGENT
Execute file updates to your active todo sheet using the edit engine:
!edit($1)