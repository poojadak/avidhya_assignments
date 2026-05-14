# Skill: Security Vulnerability Auditor
# Version: 1.0.0
# Status: draft
# Owner: week5-student
# Category: security
# Created: 2026-05-14

---

## Purpose

This Skill runs an application security specialist persona against a single Python module and produces a structured list of vulnerabilities mapped to the OWASP Top 10. Use it as the second step in a code review pipeline, after the Architect Agent has produced a design.md. It is focused on finding real security issues, not architectural problems or test gaps. The output is a JSON array of findings ordered by severity, which can be consumed programmatically or fed into a consolidation step.

---

## Input

| Parameter | Required | Description |
|---|---|---|
| `SCOPE` | Yes | Module or file path to audit (e.g. `payments/processor.py`) |
| `CONTEXT` | Yes | CLAUDE.md project context file |
| `DESIGN` | Yes | design.md produced by the Architect Agent — gives the security agent structural context without re-reading the code from scratch |

---

## Prompt

```
You are an application security specialist. You find vulnerabilities in Python backend code using the OWASP Top 10 (2021 edition) as your framework.

SCOPE: {{SCOPE}} only.

FOCUS ONLY ON:
- Injection vulnerabilities (SQL, command, etc.)
- Broken access control
- Insecure secrets and credential management
- Cryptographic failures (weak hashing, key exposure)
- Security logging failures (logging PII, not logging failures)
- Input validation failures with security consequences

DO NOT:
- Rewrite or fix the code
- Review architecture or module design (that is the Architect Agent's job)
- Write test cases
- Comment on code style, readability, or performance
- Review files outside {{SCOPE}}

You will receive: CLAUDE.md project context + design.md (architectural analysis) + {{SCOPE}}.
Use only these three as your source of truth.

OUTPUT FORMAT:
Respond in JSON only. No markdown. No preamble. No text outside the JSON array.

Output a JSON array. Each item must have these exact fields:
{
  "id": "SEC-001",
  "owasp_category": "A03:2021 – Injection",
  "location": "function name and line number if identifiable",
  "severity": "CRITICAL | HIGH | MEDIUM | LOW",
  "description": "Plain English description of the vulnerability and why it is exploitable",
  "recommendation": "One sentence on what should be done to fix it"
}

Order findings by severity: CRITICAL first, then HIGH, MEDIUM, LOW.
```

---

## Output Spec

```json
[
  {
    "id": "SEC-001",
    "owasp_category": "A07:2021 – Identification and Authentication Failures",
    "location": "module level, line 16",
    "severity": "CRITICAL",
    "description": "Live API key hardcoded in source. Anyone with repo access can obtain a production credential.",
    "recommendation": "Load the key from an environment variable and fail loudly on startup if it is not set."
  },
  {
    "id": "SEC-002",
    "owasp_category": "A03:2021 – Injection",
    "location": "record_transaction(), SQL query construction",
    "severity": "CRITICAL",
    "description": "SQL query built with f-string embedding user-supplied user_id. Enables SQL injection.",
    "recommendation": "Replace with a parameterised query using database driver placeholders."
  }
]
```

---

## Limitations

- This Skill does NOT cover architecture, testing, or code quality — use separate Skills for those
- The Skill can only report on what is visible in the input file; it cannot trace vulnerabilities that span multiple modules
- OWASP category mappings are best-effort; a finding may legitimately fit more than one category
- Results may vary slightly between runs — if a finding is borderline, run twice and compare

---

## Tests

| Test Run | Input | Expected Output | Actual Output | Pass? |
|---|---|---|---|---|
| 1 — Typical | `payments/processor.py` (full file) + design.md | JSON array with at least 5 findings; CRITICAL items for hardcoded key and SQL injection | Returned 7 findings; hardcoded key and both SQL injection points flagged CRITICAL | ✅ |
| 2 — Edge case | Truncated `processor.py` missing last two functions | Findings only for visible code; ideally agent flags possible truncation | Agent returned 2 findings with no truncation flag — added fallback note to submission | ❌ — documented in fallback_notes.txt |
| 3 — Minimal | File with only import statements and a pass | Empty JSON array `[]` or single LOW finding about unused imports | Returned empty array `[]` | ✅ |

---

## Changelog

### v1.0.0 — 2026-05-14
- Initial release
- Tested on: OrderFlow sample repo (payments/processor.py)
- Tested by: week5-student
- Note: truncated input produces a silent miss — pipeline should validate input size before running this Skill
