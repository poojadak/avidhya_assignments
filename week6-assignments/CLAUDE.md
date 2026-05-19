# CLAUDE.md — HealthTrack API

## What This Project Is

HealthTrack is a patient vital-signs tracking API used by clinic nurses and doctors.
Staff record readings (heart rate, blood pressure, SpO2, temperature) via a REST API.
The system fires alerts when readings fall outside safe thresholds.

This repo is the teaching project for Claude Code Mastery Week 5:
- Session 9: Multi-Agent Collaboration
- Session 10: Skills & Plugin Architecture

---

## Module Map

| Module | Purpose | Known Issues (intentional) |
|---|---|---|
| `app/vitals.py` | Record & retrieve vital readings | SQL injection, no input validation, hardcoded DB creds, PII over-exposure |
| `app/auth.py` | Staff login & session tokens | MD5 passwords, no token expiry, logs plaintext passwords |
| `app/alerts.py` | Alert management & escalation | No ward boundary check, PII in SMS body, no pagination |
| `app/routes.py` | Flask HTTP routes | Thin wrappers — issues live in service modules above |
| `tests/test_vitals.py` | Unit tests | Intentionally sparse — many edge cases missing |

---

## Skills Library

| Skill | Version | Status | Run with |
|---|---|---|---|
| PR Code Review | v1.2.0 | stable | `python plugins/run_skill.py pr-review` |
| Security Audit | v1.1.0 | stable | `python plugins/run_skill.py security-audit` |
| Test Coverage Report | v2.0.1 | stable | `python plugins/run_skill.py test-coverage` |

Full library: `skills/README.md`

---

## Coding Standards

- Python 3.11+
- Type hints on all public functions
- Parameterised SQL only — no f-string queries
- Secrets via environment variables (`os.getenv`) — never hardcoded
- Logging via `logging` module — never log PII or credentials
- Functions ≤ 40 lines — extract helpers if larger
- All public functions must have docstrings

---

## Agent Scope Guidance

When running agents during the Week 5 sessions:

**Session 9 recommended scope:** `app/vitals.py`
**Session 10 Skills scope:** start with `app/vitals.py`, expand to `app/auth.py` for stretch

Always pass this CLAUDE.md as context to every agent session.

---

## Out of Scope for Lab

- Database migrations or real DB setup
- Flask app deployment or Docker configuration
- Frontend or admin UI
- Celery tasks or async workers
