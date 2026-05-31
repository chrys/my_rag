description = "Conduct a five-axis code review against a specific requirements file and output findings locally."

prompt = """
Invoke the code-review-and-quality skill.

Inputs:
1. Target Specification: Use the provided file `$1` as the source of truth for the functional requirements and business logic.
2. Changeset: Evaluate the provided Git diff representing the active changes (staged or recent commits).

Review the Git diff across all five axes:
1. **Correctness** — Does the changed code match the explicit requirements defined in `$1`? Are edge cases handled? Are tests adequate?
2. **Readability** — Clear names? Straightforward logic? Well-organized?
3. **Architecture** — Follows existing project patterns? Clean boundaries? Right abstraction level?
4. **Security** — Input validated? Secrets safe? Auth checked? (Use security-and-hardening skill)
5. **Performance** — No N+1 queries? No unbounded ops? (Use performance-optimization skill)

Output Execution Rules:
- Categorize findings as Critical, Important, or Suggestion.
- Provide structured feedback including specific file:line references and actionable fix recommendations.
- Write this structured report using the following file-system directive: `!write(!dirname($1)/findings.md)`. Overwrite the file if it already exists.
"""

---
### TARGET SPECIFICATION FILE:
$1

### SPECIFICATION CONTENTS TO PARSE:
!`cat $1`
---