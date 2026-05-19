# Skill: Test Coverage Report
# Version: 2.0.1
# Status: stable
# Owner: qa-team
# Category: testing
# Created: 2026-01-10
# Updated: 2026-04-22

---

## Purpose

Analyses a Python module's source code alongside its existing tests to identify
coverage gaps. Produces a prioritised JSON report of untested functions and missing
edge cases, risk-weighted by function importance (public API > business logic > helpers).

Does NOT generate test code — use `skills/test-generator/` for that (coming soon).
Does NOT modify source files.
Does NOT replace a real coverage tool (pytest-cov) — use this for qualitative gap analysis.

---

## Input

| Parameter | Required | Description | Example |
|---|---|---|---|
| `MODULE_PATH` | Yes | Path to the source module to analyse | `app/vitals.py` |
| `TEST_PATH` | Yes | Path to the existing test file | `tests/test_vitals.py` |
| `COVERAGE_TARGET` | No | Target coverage percentage (default: 80) | `90` |

---

## Prompt

```
You are a QA engineer auditing test coverage for {{MODULE_PATH}}.

FOCUS ONLY ON:
- Identifying public functions that have NO test coverage
- Identifying functions that lack edge case testing (None, negative values, zero, empty string, unknown type)
- Identifying error scenarios not tested (exceptions, timeouts, retries exhausted)
- Risk-weighting gaps: public API functions > business logic > internal helpers > utility functions

DO NOT:
- Write test code — that is a separate Skill (skills/test-generator/)
- Modify source files
- Report on code style or security issues
- Suggest architectural changes

INPUT:
- Source code of {{MODULE_PATH}}
- Existing test code from {{TEST_PATH}}
- Coverage target: {{COVERAGE_TARGET}}%

OUTPUT FORMAT — respond ONLY with valid JSON. No preamble. No markdown fences.
{
  "module": "{{MODULE_PATH}}",
  "test_file": "{{TEST_PATH}}",
  "coverage_target": {{COVERAGE_TARGET}},
  "estimated_coverage": <integer 0-100>,
  "risk_score": "low | medium | high",
  "untested_functions": [
    {"function": "fn_name", "reason": "no tests found"}
  ],
  "missing_edge_cases": [
    {"function": "fn_name", "missing_case": "description of missing edge case", "risk": "high|medium|low"}
  ],
  "priority_gaps": [
    "Fix these first — ordered by risk"
  ],
  "summary": "One sentence overall assessment."
}
```

---

## Output Spec

Real example from test run on `app/vitals.py` + `tests/test_vitals.py`:

```json
{
  "module": "app/vitals.py",
  "test_file": "tests/test_vitals.py",
  "coverage_target": 80,
  "estimated_coverage": 35,
  "risk_score": "high",
  "untested_functions": [
    {"function": "get_patient_vitals", "reason": "no tests found in test_vitals.py"},
    {"function": "get_vital_trend", "reason": "no tests found"},
    {"function": "calculate_alert_threshold", "reason": "2 tests exist but no edge cases"}
  ],
  "missing_edge_cases": [
    {"function": "record_vitals", "missing_case": "value=None — currently crashes uncaught", "risk": "high"},
    {"function": "record_vitals", "missing_case": "negative value accepted without error", "risk": "high"},
    {"function": "record_vitals", "missing_case": "unknown vital_type — no validation", "risk": "medium"},
    {"function": "calculate_alert_threshold", "missing_case": "age=0 (newborn) — no boundary test", "risk": "medium"},
    {"function": "calculate_alert_threshold", "missing_case": "unknown vital_type raises KeyError — unhandled", "risk": "high"},
    {"function": "record_vitals", "missing_case": "DB timeout triggers retry — retry loop untested", "risk": "high"}
  ],
  "priority_gaps": [
    "1. record_vitals(value=None) — crashes with unhandled TypeError",
    "2. calculate_alert_threshold(unknown_vital_type) — raises KeyError, no test",
    "3. record_vitals(negative_value) — accepted silently, no validation",
    "4. get_patient_vitals — zero test coverage on a public API function"
  ],
  "summary": "Coverage is critically low at ~35%; 4 public functions have zero tests and 3 high-risk edge cases are completely untested."
}
```

---

## Limitations

- `estimated_coverage` is approximate — not a substitute for `pytest --cov`
- Cannot detect missing integration tests — only unit test gaps
- Does NOT generate test code — use `skills/test-generator/` (coming soon)
- Works best on files under 400 lines — chunk larger modules by class or function group
- May undercount coverage if tests use fixtures or conftest.py patterns it cannot see

---

## Tests

| # | Input | Expected | Actual | Pass? |
|---|---|---|---|---|
| 1 — Typical | `app/vitals.py` + `tests/test_vitals.py` | `risk_score: high`, 3+ untested functions, 4+ missing edge cases | `risk_score: high`, 3 untested, 6 missing edge cases — correct JSON | ✅ |
| 2 — Good coverage | `app/routes.py` + hypothetical full test file | `risk_score: low`, 0–1 gaps | `risk_score: low`, 1 NICE_TO_HAVE gap — correct | ✅ |
| 3 — Empty test file | `app/vitals.py` + empty `tests/__init__.py` | All functions in untested_functions | All 6 public functions listed as untested, risk_score: high | ✅ |

---

## Changelog

### v2.0.1 — 2026-04-22
- PATCH: Fixed crash when TEST_PATH points to an empty file
- Tested by: qa-team

### v2.0.0 — 2026-03-20
- MAJOR: Output changed from markdown to JSON (breaking change — update all callers)
- ADDED: `risk_score` field and `priority_gaps` array
- ADDED: `estimated_coverage` integer field
- IMPROVED: `missing_edge_cases` now includes per-case risk level
- Tested on: 6 modules across healthtrack-api
- Tested by: qa-team

### v1.0.0 — 2026-01-10
- Initial release — markdown output format
- Tested by: qa-team
