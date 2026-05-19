# Skill: [YOUR SKILL NAME]
# Version: 1.0.0
# Status: draft
# Owner: [your-name]
# Category: [code-quality | security | testing | documentation]
# Created: [YYYY-MM-DD]

---

## Purpose

[One paragraph. What does this Skill do? When should someone use it?
What does it produce? Be specific — "reviews code" is not enough.]

---

## Input

| Parameter | Required | Description | Example |
|---|---|---|---|
| `SCOPE` | Yes | File or module path to analyse | `app/vitals.py` |
| `CONTEXT` | Yes | CLAUDE.md project context | Pass full file content |
| `[PARAM]` | No | [description] | [example value] |

---

## Prompt

```
You are a [SPECIFIC ROLE].

Your job is to [ONE CLEAR RESPONSIBILITY].

SCOPE: {{SCOPE}} only.

FOCUS ONLY ON:
- [concern 1]
- [concern 2]

DO NOT:
- [thing another Skill handles]
- [out-of-scope concern]

You will receive: CLAUDE.md + {{SCOPE}} source code.

OUTPUT FORMAT — respond ONLY with this structure, no preamble:
[paste exact output structure here]
```

---

## Output Spec

Example output (fill with real data from your first test run):

```
[paste example here]
```

---

## Limitations

- Does NOT cover [adjacent concern]
- May miss issues in files longer than ~400 lines — chunk input
- [other known limitation]

---

## Tests

| # | Input | Expected | Actual | Pass? |
|---|---|---|---|---|
| 1 — Typical | `app/vitals.py` | [describe] | [describe] | ✅ |
| 2 — Edge case | [input] | [describe] | [describe] | ✅ |
| 3 — Minimal | [input] | [describe] | [describe] | ✅ |

---

## Changelog

### v1.0.0 — [date]
- Initial release
- Tested on: HealthTrack API (`app/vitals.py`)
- Tested by: [your name]
