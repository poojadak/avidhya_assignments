# Skill Review Checklist — REVIEW_TEMPLATE.md

Fill this out when submitting a PR for a new or updated Skill.
The reviewer uses the same form to score the Skill before approving.

**Skill name:** ___________________________
**Version:** ___________________________
**Author:** ___________________________
**Reviewer:** ___________________________
**Date:** ___________________________

---

## Section 1 — Header & Metadata (15 pts)

| Criterion | Points | Score | Notes |
|---|---|---|---|
| Header has: Name, Version, Status, Owner, Category, Created date | 5 | | |
| Status is `draft` (not `stable`) until review is complete | 5 | | |
| Category matches one of: code-quality, security, testing, documentation, deployment | 5 | | |

**Section 1 total: ___ / 15**

---

## Section 2 — Purpose (15 pts)

| Criterion | Points | Score | Notes |
|---|---|---|---|
| One clear paragraph — not a bullet list | 5 | | |
| States what the Skill produces (specific output, not "reviews code") | 5 | | |
| States what the Skill does NOT do (references adjacent Skills by name) | 5 | | |

**Section 2 total: ___ / 15**

---

## Section 3 — Input Spec (15 pts)

| Criterion | Points | Score | Notes |
|---|---|---|---|
| All required inputs listed with types and examples | 5 | | |
| Optional inputs clearly marked as optional | 5 | | |
| No hardcoded values — all runtime values are parameters | 5 | | |

**Section 3 total: ___ / 15**

---

## Section 4 — Prompt Body (30 pts)

| Criterion | Points | Score | Notes |
|---|---|---|---|
| ROLE is specific (one job, not "helpful AI assistant") | 5 | | |
| SCOPE or FOCUS section is explicit — what the Skill covers | 5 | | |
| DO NOT section is explicit — at least 2 exclusions, each naming an adjacent Skill | 5 | | |
| All runtime values use `{{VARIABLE}}` syntax — no hardcoded paths | 10 | | |
| OUTPUT FORMAT specifies exact structure — JSON schema or markdown section headers | 5 | | |

**Section 4 total: ___ / 30**

---

## Section 5 — Output Spec & Limitations (15 pts)

| Criterion | Points | Score | Notes |
|---|---|---|---|
| Output Spec has a real example (from an actual test run, not a placeholder) | 5 | | |
| Limitations section has at least 3 specific limitations | 5 | | |
| Limitations are honest — they set real expectations, not marketing copy | 5 | | |

**Section 5 total: ___ / 15**

---

## Section 6 — Tests & Changelog (10 pts)

| Criterion | Points | Score | Notes |
|---|---|---|---|
| Tests table has at least 3 rows: typical, edge case, minimal/empty | 5 | | |
| Actual output column is filled in (not blank or "TBD") | 3 | | |
| Changelog has a v1.0.0 entry with date and tester name | 2 | | |

**Section 6 total: ___ / 10**

---

## Overall Score: ___ / 100

**Pass threshold for `stable` status: 80 / 100**

---

## Written Feedback (required — vague responses fail)

**One thing that is well done:**

> 

**One specific thing that must be fixed before approval:**

> 

**Would you use this Skill on your own work? Why or why not?**

> 

---

## Reviewer Decision

- [ ] **Approve** — ready to merge, change status to `stable`
- [ ] **Approve with changes** — merge after the required fix above
- [ ] **Request changes** — do not merge, resubmit after fixes

Reviewer signature: ___________________________ Date: ___________
