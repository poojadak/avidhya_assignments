# Skill: PR Code Review
# Version: 1.2.0
# Status: stable
# Owner: platform-team
# Category: code-quality
# Created: 2026-04-01
# Updated: 2026-04-20

---

## Purpose

Reviews a pull request diff for code quality, correctness, readability, and maintainability.
Produces structured review comments grouped by priority (MUST_FIX, SHOULD_FIX, NICE_TO_HAVE).

Does NOT cover security vulnerabilities — use `skills/security-audit/` for that.
Does NOT suggest architectural changes — that is a separate design review process.
Does NOT generate tests — use `skills/test-coverage/` to identify gaps first.

---

## Input

| Parameter | Required | Description | Example |
|---|---|---|---|
| `SCOPE` | Yes | Module or file path being reviewed | `app/vitals.py` |
| `DIFF` | Yes | Output of `git diff main` for the changed file | *(paste full diff)* |
| `CONTEXT` | Yes | Full content of `CLAUDE.md` project context | *(paste file content)* |
| `PR_DESC` | No | PR title and description for additional context | `"Add retry logic to record_vitals"` |

---

## Prompt

```
You are a senior software engineer reviewing a pull request for {{SCOPE}}.

FOCUS ONLY ON:
- Correctness: does the code do what it claims? Are there logic errors?
- Readability: is the code clear to a new team member?
- Maintainability: will this code be easy to change in 6 months?
- Test coverage gaps: are there obvious cases not covered by tests?

DO NOT:
- Review security vulnerabilities — that is handled by skills/security-audit/
- Suggest architectural changes — that is a separate design review
- Rewrite the implementation — comment and suggest, do not replace
- Praise the code — only flag things that need attention

INPUT:
- CLAUDE.md project context (coding standards, module map, out-of-scope items)
- git diff for {{SCOPE}}
- PR description (if provided): {{PR_DESC}}

OUTPUT FORMAT — respond ONLY with this markdown structure. No preamble. No explanation outside these sections:

## MUST_FIX
[Numbered list. Each item: filename:line — description. Fix: specific recommendation.
Leave blank with "None found" if no MUST_FIX items.]

## SHOULD_FIX
[Numbered list. Same format. Leave blank with "None found" if empty.]

## NICE_TO_HAVE
[Numbered list. Same format. Leave blank with "None found" if empty.]

## SUMMARY
[Exactly 2 sentences. Overall assessment and merge recommendation.]
```

---

## Output Spec

Real example from test run on `app/vitals.py` retry logic PR:

```
## MUST_FIX
1. app/vitals.py:52 — `record_vitals()` has no guard against `value=None`.
   `_execute_write()` will receive None and crash silently.
   Fix: add `if value is None: raise ValueError("value cannot be None")` at line 35.

2. app/vitals.py:61 — Retry loop catches bare `Exception` — this masks
   programming errors (e.g. TypeError from bad input) as DB failures.
   Fix: catch `DBTimeoutError` specifically, re-raise all other exceptions.

## SHOULD_FIX
3. app/vitals.py:44 — Variable name `r` is not descriptive in the retry loop.
   Rename to `attempt` for clarity.

## NICE_TO_HAVE
4. app/vitals.py:38 — Inline comment on the backoff formula would help new devs.
   Add: `# exponential backoff: 1s, 2s, 4s`

## SUMMARY
Two correctness issues must be fixed before merge: a None guard is missing
and the exception handler is too broad. All other items are optional improvements.
```

---

## Limitations

- Does NOT cover security vulnerabilities — run `skills/security-audit/` separately
- Effective on diffs up to ~400 lines; chunk larger PRs into modules
- Cannot detect runtime issues (race conditions, memory leaks, deadlocks)
- Cannot evaluate whether the tests in the diff actually pass
- May not catch subtle business logic errors without deeper domain knowledge

---

## Tests

| # | Input | Expected | Actual | Pass? |
|---|---|---|---|---|
| 1 — Typical | `app/vitals.py` retry logic diff (~80 lines) | 2 MUST_FIX, 2 SHOULD_FIX, structured markdown | 2 MUST_FIX (None guard, bare except), 1 SHOULD_FIX — correct format | ✅ |
| 2 — Edge: clean diff | `app/routes.py` 3-line bugfix diff | "None found" in MUST_FIX and SHOULD_FIX | All sections present, MUST_FIX: None found | ✅ |
| 3 — Minimal: empty diff | Blank diff string | Graceful response, no crash | Summary noted no changes to review | ✅ |

---

## Changelog

### v1.2.0 — 2026-04-20
- ADDED: `PR_DESC` optional input parameter — improves context for larger PRs
- ADDED: `SUMMARY` section to output spec
- IMPROVED: DO NOT list now explicitly names adjacent Skills by path
- Tested on: 12 PRs across 3 teams (vitals, auth, alerts modules)
- Tested by: platform-team

### v1.1.0 — 2026-03-15
- ADDED: `NICE_TO_HAVE` output section
- IMPROVED: output format now requires filename:line prefix on every item

### v1.0.0 — 2026-02-01
- Initial release
- Tested by: platform-team (5 PRs on app/vitals.py)
