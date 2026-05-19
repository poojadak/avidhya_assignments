# HealthTrack Skills Library

Reusable, versioned, peer-reviewed prompt modules for the HealthTrack API engineering team.
Built during Claude Code Mastery — Week 5, Session 10.

---

## Skill Index

| Skill | Category | Version | Status | Owner | File |
|---|---|---|---|---|---|
| PR Code Review | code-quality | v1.2.0 | stable | platform-team | [skills/pr-review/SKILL.md](pr-review/SKILL.md) |
| Security Audit | security | v1.1.0 | stable | platform-team | [skills/security-audit/SKILL.md](security-audit/SKILL.md) |
| Test Coverage Report | testing | v2.0.1 | stable | qa-team | [skills/test-coverage/SKILL.md](test-coverage/SKILL.md) |

---

## Quick Usage

```bash
# PR Code Review — run before every merge request
python plugins/run_skill.py pr-review \
  --scope app/vitals.py \
  --diff "$(git diff main)" \
  --context CLAUDE.md

# Security Audit — run on any module before it ships
python plugins/run_skill.py security-audit \
  --scope app/vitals.py \
  --context CLAUDE.md

# Test Coverage Report — find gaps before writing tests
python plugins/run_skill.py test-coverage \
  --module app/vitals.py \
  --tests tests/test_vitals.py
```

---

## Directory Structure

```
skills/
├── README.md                    ← this file — Skill index and usage guide
├── SKILL_TEMPLATE.md            ← copy this to start a new Skill
├── REVIEW_TEMPLATE.md           ← fill this out before marking a Skill stable
│
├── pr-review/
│   ├── SKILL.md                 ← v1.2.0  Status: stable  Owner: platform-team
│   └── examples/
│       ├── vitals_run1.md       ← sample output from test run 1
│       └── alerts_run2.md       ← sample output from test run 2
│
├── security-audit/
│   ├── SKILL.md                 ← v1.1.0  Status: stable  Owner: platform-team
│   └── examples/
│       ├── vitals_run1.json     ← sample findings JSON from test run 1
│       └── auth_run2.json       ← sample findings JSON from test run 2
│
└── test-coverage/
    ├── SKILL.md                 ← v2.0.1  Status: stable  Owner: qa-team
    └── examples/
        ├── vitals_run1.json     ← sample coverage report from test run 1
        └── alerts_run2.json     ← sample coverage report from test run 2
```

---

## Adding a New Skill

1. Copy the template:
   ```bash
   cp skills/SKILL_TEMPLATE.md skills/[your-skill-name]/SKILL.md
   mkdir -p skills/[your-skill-name]/examples
   ```
2. Fill in all 5 sections: Header, Purpose, Input, Prompt, Output Spec
3. Add a `## Limitations` section — at least 3 specific limitations
4. Run the Skill on 3 different inputs, fill in the `## Tests` table
5. Fill out `skills/REVIEW_TEMPLATE.md` and open a PR
6. After approval, update the Skill Index table above and change status to `stable`

---

## Governance Rules

| Rule | Detail |
|---|---|
| Every Skill has one owner | Owner field in SKILL.md header. Accountable for updates and deprecation. |
| Changes require a PR | No direct edits. All changes reviewed using REVIEW_TEMPLATE.md. |
| 3 test runs before stable | Tests table must have 3 rows filled before status: draft → stable. |
| Semver versioning | MAJOR = breaking output change. MINOR = new capability. PATCH = bug fix. |
| Deprecate, don't delete | Set Status: deprecated. Keep 60 days. Announce replacement in team channel. |
