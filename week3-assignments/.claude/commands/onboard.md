# /onboard — New Team Member Onboarding Guide

Generate a personalised architecture summary, key file map, and day-1 checklist
for someone joining the project for the first time.

## Steps

1. Read these files in order:
   - `CLAUDE.md`
   - `README.md` (if it exists)
   - `requirements.txt`
   - `src/__init__.py`
   - `src/models.py`
   - `src/services.py`
   - `src/routes.py`
   - `src/validators.py`
   - `tests/test_url_shortener.py`

2. Run `git log --oneline -10` to show the last 10 commits and give a sense of recent activity.

3. Run `python -m pytest tests/ -v --tb=short 2>&1` to confirm the test suite passes.

4. Generate the following onboarding document:

---

## 👋 Welcome to the URL Shortener Service

### What this project does
<2-3 sentence plain-English summary>

### Tech stack
| Layer | Technology | Why |
|-------|-----------|-----|
| Web framework | Flask | ... |
| ORM | SQLAlchemy | ... |
| DB (dev) | SQLite | ... |
| Tests | pytest | ... |

### Architecture — how the layers connect
<Mermaid diagram showing the request flow: routes → services → models → DB>

### Key files — where things live
| File | Purpose | When you'll edit it |
|------|---------|---------------------|
| `src/routes.py` | HTTP endpoints | Adding/changing API shape |
| `src/services.py` | Business logic | New features or bug fixes |
| `src/models.py` | DB schema | New fields or tables |
| `src/validators.py` | Input validation | New validation rules |
| `tests/` | Test suite | Always — after every change |
| `CLAUDE.md` | Team rules | When conventions change |
| `.claude/hooks/` | Safety guardrails | When adding new governance |

### How to run it locally
```bash
cd url-shortener/
pip install -r requirements.txt
python run.py
# API available at http://localhost:5000
```

### How to run the tests
```bash
python -m pytest tests/ -v
python -m pytest tests/ --cov=src --cov-report=term-missing
```

### The 5 slash commands you'll use every day
| Command | When to use |
|---------|-------------|
| `/review` | Before every commit |
| `/test-gen` | After writing new code |
| `/commit` | When tests pass and review is green |
| `/ship` | When a feature is ready for PR |
| `/onboard` | Run again if architecture changes |

### Workflow for your first feature
1. `git checkout -b feature/<ticket>-<description>`
2. Make your changes in `src/`
3. `git add <files>`
4. `/review` — fix anything flagged
5. `/test-gen` — tests generated + run
6. `/ship` — commit + push + PR description

### Recent commits (last 10)
<paste git log output>

### Test suite status
<paste pytest output>

### Things to ask your team lead
- Where to find open tickets
- How to access staging environment
- Slack channel for code review requests

---

5. Save this document to `docs/onboarding-<YYYY-MM-DD>.md`.
6. Print: "✅ Onboarding guide saved. Share docs/onboarding-<date>.md with your new teammate."
