# HealthTrack API — Teaching Project

**Claude Code Mastery · Week 5 · Sessions 9 & 10**

A patient vital-signs REST API used across both sessions as the hands-on teaching project.

---

## Project Structure

```
healthtrack-api/
├── CLAUDE.md                        ← Always pass this to every agent session
├── README.md
├── requirements.txt
│
├── app/                             ← Flask application (intentional issues for teaching)
│   ├── vitals.py                    ← Primary teaching target — SQL injection, hardcoded creds
│   ├── auth.py                      ← MD5 passwords, no token expiry, logs plaintext passwords
│   ├── alerts.py                    ← No ward-boundary check, PII in SMS body
│   └── routes.py                    ← Thin Flask wrappers
│
├── tests/
│   └── test_vitals.py               ← Intentionally sparse — gives agents real gaps to find
│
├── skills/                          ← Session 10: Skill library
│   ├── README.md                    ← Skill index + governance rules
│   ├── SKILL_TEMPLATE.md            ← Copy to start a new Skill
│   ├── REVIEW_TEMPLATE.md           ← Peer review checklist (100-point rubric)
│   ├── pr-review/SKILL.md           ← v1.2.0  PR Code Review Skill
│   ├── security-audit/SKILL.md      ← v1.1.0  Security Audit Skill
│   └── test-coverage/SKILL.md       ← v2.0.1  Test Coverage Report Skill
│
├── plugins/
│   ├── README.md                    ← How to use the plugin runner
│   └── run_skill.py                 ← Run any Skill from the command line
│
└── .github/workflows/
    └── ai-skill-review.yml          ← GitHub Actions: Skills in CI/CD pipeline
```

---

## Quick Start

```bash
pip install flask anthropic pytest
export ANTHROPIC_API_KEY="sk-ant-..."

# Run existing (sparse) tests
pytest tests/ -v

# List available Skills
python plugins/run_skill.py --list

# Run Security Audit Skill on the vitals module
python plugins/run_skill.py security-audit \
  --scope app/vitals.py \
  --context CLAUDE.md
```

---

## Session Guide

| Session | What you build | Primary file |
|---|---|---|
| Session 9 | 3-agent pipeline (Architect → Security → Test → Consolidate) | `app/vitals.py` |
| Session 10 | Skills library — package those agents as reusable SKILL.md files | `skills/` |

Always pass `CLAUDE.md` to every agent session — it is the project context.

---

## Intentional Issues (Teaching Targets)

All issues are deliberate. Do not fix them before the session.

| Module | Issues |
|---|---|
| `app/vitals.py` | SQL injection via f-strings, hardcoded `DB_PASSWORD`, no input validation, PII over-exposure |
| `app/auth.py` | MD5 password hashing, no token expiry, logs plaintext password on failed login |
| `app/alerts.py` | No ward-boundary authorisation, PII in SMS escalation body, no pagination |
