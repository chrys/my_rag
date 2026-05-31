---
description: Initialize Phase 1 (Define) using the spec-driven-development skill.
agent: plan
---
You are initializing a formal engineering review for this specific project. Execute the exact phase workflow defined in your global skills database for `spec-driven-development`.

### Your Task
Begin by understanding what the user wants to build. Ask clarifying questions about:
1. The objective and target users
2. Core features and acceptance criteria
3. Tech stack preferences and constraints
4. Known boundaries (what to always do, ask first about, and never do)

Then generate a structured spec covering all six core areas: objective, commands, project structure, code style, testing strategy, and boundaries.



### Execution Rule
Do not output any application code yet. Do not generate migrations. Present the complete Specification and wait for explicit user approval before moving to the /plan phase.

---
### TARGET FILE PATH:
$1

### USER'S SPECIFIC INSTRUCTIONS:
$2-

### CURRENT FILE CONTENTS TO IMPROVE:
!`cat $1`
---

# INSTRUCTION TO AGENT
Modify the file using the edit directive:
!edit($1)