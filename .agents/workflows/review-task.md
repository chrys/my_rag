---
name: review-task
description: Conduct a five-axis code review — correctness, readability, architecture, security, performance
---

Invoke the code-review-and-quality skill.

This workflow accepts the specs file path as an argument ($1). Review the current changes (staged or recent commits) across all five axes relative to the specification:

1. **Correctness** — Does it match the spec? Edge cases handled? Tests adequate?
2. **Readability** — Clear names? Straightforward logic? Well-organized?
3. **Architecture** — Follows existing patterns? Clean boundaries? Right abstraction level?
4. **Security** — Input validated? Secrets safe? Auth checked? (Use security-and-hardening skill)
5. **Performance** — No N+1 queries? No unbounded ops? (Use performance-optimization skill)

## Output Execution Rules
* Categorize findings clearly as **Critical**, **Important**, or **Suggestion**.
* Provide structured feedback including specific `file:line` references and actionable fix recommendations.
* Do not stream the final report to standard chat output. Write this structured report using the following file-system directive: `!write(!dirname($1)/findings.md)`. Overwrite the file if it already exists.
