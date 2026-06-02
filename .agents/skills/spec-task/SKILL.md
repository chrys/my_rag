---
name: spec-task
description: Start spec-driven development — write a structured specification before writing code
arguments:
  - name: draft_spec
    required: true
    description: "The path to the draft specification file to be refined and updated (referenced as $1)"
---

# Skill: Spec-Driven Development

This skill serves as a task-focused entry point that **invokes the global `spec-driven-development` skill** under the hood. It configures and guides the agent to accept a draft specification file path (`$1`) as input and refine it in-place using the spec-driven development process.

## Inputs
1. **Draft Specification Path ($1):** The absolute or relative path to the draft specification file that needs to be refined, structured, and updated.

## Execution Steps

1. **Understand and Clarify:**
   Begin by thoroughly reading and analyzing the existing draft specification at `$1`. Identify any gaps, ambiguities, or underspecified requirements. Ask the user clarifying questions if needed, focusing on:
   - The primary objective and target users.
   - Core features, expected user flows, and clear acceptance criteria.
   - Tech stack preferences, database requirements, and architectural constraints.
   - Known boundaries (what to always do, what to ask first about, and what to never do).

2. **Generate Structured Specification:**
   Refine the draft into a highly structured, comprehensive specification covering these six core areas:
   - **Objective & Scope:** Clear definition of the problem, background context, target audience, and scope of work.
   - **Common & Required Commands:** Relevant shell commands for setup, database migrations, running the server, and executing tests.
   - **Project Structure:** Logical directory layout, component breakdown, and key file mappings.
   - **Code Style & Guidelines:** Coding conventions (e.g., PEP 8, double quotes, type hints, docstrings, architectural preferences like function-based views).
   - **Testing Strategy:** Guidelines for test-driven development (TDD), directory structure for tests (e.g., under `Testing/unit/`), and testing command execution.
   - **Guardrails & Boundaries:** Explicitly listed "Dos" (always do), "Ask Before" (decisions requiring approval), and "Don'ts" (never do).

3. **Update the Target File:**
   Directly write/update the structured, finalized specification back to the target file path at `$1`. Ensure that all draft details are preserved and refined into the professional 6-part schema.
