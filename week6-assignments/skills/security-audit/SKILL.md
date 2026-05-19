# Skill: Security Audit
# Version: 1.2.0
# Status: stable
# Owner: platform-team
# Category: security
# Created: 2026-02-01
# Updated: 2026-05-03

---

## Purpose

Scans a Python module for OWASP Top 10 security vulnerabilities.
Returns a JSON array of findings ranked by severity.

Does NOT suggest refactoring — use `skills/pr-review/` for that.
Does NOT write tests — use `skills/test-coverage/` for that.

---

## Input

| Parameter | Required | Description | Example |
|---|---|---|---|
| `SCOPE` | Yes | Path to the Python module to scan | `app/vitals.py` |
| `CONTEXT` | Yes | Full content of `CLAUDE.md` | *(paste file content)* |
| `DIFF` | No | `git diff` output — focuses review on changed lines only | *(paste diff)* |

---

## Prompt

```
You are an application security engineer conducting an OWASP Top 10 audit.

SCOPE: {{SCOPE}} only.

FOCUS ONLY ON:
- A03 Injection — SQL built with f-strings; unsanitised inputs
- A02 Cryptographic Failures — hardcoded passwords, API keys; MD5/SHA1
- A09 Logging Failures — PII written to logs
- A01 Broken Access Control — missing authorisation checks
- A07 Authentication Failures — tokens that never expire; plaintext passwords in logs

DO NOT:
- Suggest refactoring or code style changes
- Write tests
- Propose architectural changes

INPUT: CLAUDE.md context + source code of {{SCOPE}}.
Git diff (if provided): {{DIFF}}

OUTPUT FORMAT — respond ONLY with a JSON array. No preamble:
[{
  "severity": "CRITICAL | HIGH | MEDIUM | LOW",
  "owasp": "A0X - Category Name",
  "file": "{{SCOPE}}",
  "line": <integer>,
  "description": "what the issue is and why it is dangerous",
  "fix": "specific code-level fix recommendation"
}]
```

---

## Output Spec

```json
[
  {
    "severity": "CRITICAL",
    "owasp": "A03 - Injection",
    "file": "app/vitals.py",
    "line": 38,
    "description": "SQL built with f-string. patient_id injected directly.",
    "fix": "Use parameterised queries: cursor.execute(sql, (patient_id,))"
  }
]
```

---

## Limitations

- Does NOT scan dependencies for CVEs
- Does NOT cover infrastructure vulnerabilities
- Files over ~500 lines should be chunked
- May miss runtime vulnerabilities requiring execution context

---

## Tests

| # | Input | Expected | Actual | Pass? |
|---|---|---|---|---|
| 1 — Typical | `app/vitals.py` | 2+ CRITICAL findings | 4 findings: 2 CRITICAL, 1 HIGH, 1 MEDIUM | ✅ |
| 2 — With DIFF | Only retry logic diff | Findings scoped to diff | 1 finding for changed lines | ✅ |
| 3 — Clean module | `app/routes.py` | 0–1 findings | 1 MEDIUM | ✅ |

---

## Changelog

### v1.2.0 — 2026-05-03
- MAJOR: Output schema changed — added required field "remediation_effort" (low/medium/high)
- All callers must update to handle the new field
- Tested on: 6 runs
- Tested by: platform-team

### v1.1.0 — 2026-04-15
- ADDED: Optional `DIFF` input parameter — focus review on changed lines only
- ADDED: A07 Authentication Failures to focus list
- IMPROVED: description field now requires plain-language explanation of risk
- Tested on: 8 PRs across healthtrack-api
- Tested by: platform-team

### v1.0.0 — 2026-02-01
- Initial release — A03, A02, A09, A01
- Tested on: app/vitals.py (5 runs)
- Tested by: platform-team
