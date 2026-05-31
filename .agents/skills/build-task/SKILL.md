---
name: build
description: Implements the next pending task from a specified todo.md checklist file, tracks task state changes, and writes build or test logs on failure.
---
# Build Task Skill
When the user invokes this skill, you must take a target markdown checklist file path, parse its contents, and incrementally build the next unit of work using test-driven development.

## 1. Locate and Mark the Active Task
- Read the markdown file provided by the user. 
- Look for the very first line item containing an empty checkbox: `- [ ]`.
- Immediately modify that checkbox from `- [ ]` to `- [~]` to indicate that work has started. Save the file.

## 2. Implementation Cycle
- Review the acceptance criteria for that active task.
- Locate the relevant files in the local codebase (e.g., your Django applications, settings, or views).
- Write an isolated, failing unit test targeting the requirement (RED).
- Implement the absolute minimum code required to make the test pass (GREEN).
- Run your validation check by executing the local testing command: `python manage.py test`.

## 3. Error Handling and Logging
If a compilation error, syntax crash, or test runner failure happens while executing your build loop:
- Do not clear existing errors.
- Extract a concise summary of the traceback or regression.
- Locate the parent folder of the active todo file, and append the failure details to a file named `errlog.md` in that exact directory.
- Follow a strict error-recovery routine to fix the codebase.

## 4. Completion Tracking
- Once the task code passes all local validation tests, update the checkbox state in the markdown file from `- [~]` to `- [X]`.
- Commit the changes to git with a clear, descriptive message highlighting the completed task.