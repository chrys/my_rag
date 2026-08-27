---
name: spec-task
description: Start spec-driven development — write a structured specification before writing code
---

Invoke the spec-driven-development skill.

Begin by understanding what the user wants to build. Ask clarifying questions about:
1. The objective and target users
2. Core features and acceptance criteria
3. Tech stack preferences and constraints
4. Known boundaries (what to always do, ask first about, and never do)

Then generate a structured spec covering all six core areas: objective, commands, project structure, code style, testing strategy, and boundaries.

This workflow accepts the specs file path as an argument ($1). Load the specifications file from this path, update it with the requested changes, and save the updated specifications directly to the same file. If no path is specified as an argument, default to SPEC.md in the project root.
