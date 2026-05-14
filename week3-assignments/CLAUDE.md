# CLAUDE.md — URL Shortener Service
## Team Workflow Rules & Architecture Conventions

> This file is the single source of truth for how we build, review, test, and ship code.
> Claude Code reads this file automatically before every session. Keep it updated.

---

## Project Overview

Python + Flask REST API that shortens URLs, tracks analytics, and enforces expiry.
Target repo: `poojadak/avidhya_assignments` (Week 2 shortener in `url-shortener/`)

**Stack:** Python 3.12 · Flask 3.x · SQLAlchemy · SQLite (dev) · pytest

---

## Architecture Conventions

### Layer Rules
```
src/routes.py      → HTTP only. No business logic. No DB queries.
src/services.py    → All business logic. No Flask imports.
src/models.py      → SQLAlchemy models only. No service logic.
src/validators.py  → Pure functions. No side effects.
src/extensions.py  → Shared db/limiter singletons. Nothing else.
```

- **Never** import `flask.request` inside `services.py` or `models.py`
- **Never** put raw SQL in routes — always go through the service layer
- **Always** use the `ok()` / `err()` envelope helpers for JSON responses
- Response shape is always: `{ "success": bool, "data": object|null, "error": string|null }`

### File Naming
- Snake_case for all Python files and functions
- Module-level docstring on every new file listing which REQ-IDs it satisfies

### Database
- Use SQLAlchemy ORM exclusively — no raw `db.engine.execute()`
- Migrations via Flask-Migrate (Alembic); never edit the DB directly
- Every new column needs a migration file

---

## Code Style

- PEP 8 strictly enforced (max line length: 100)
- Type hints on all function signatures
- Docstrings on all public functions (Google style)
- No bare `except:` clauses — always catch specific exceptions
- f-strings preferred over `.format()` or `%`

---

## Testing Standards

- **Framework:** pytest + pytest-flask
- **Coverage target:** ≥ 85% on all new code
- **Test file location:** `tests/test_<module>.py` mirroring `src/<module>.py`
- **Naming:** `test_should_<outcome>_when_<condition>`
- **Fixtures:** Define in `tests/conftest.py`, never inline in test files
- Every test must have a `# Tests: REQ-XXX-NNN` comment
- No real DB or network calls in unit tests — use in-memory SQLite
- Integration tests go in `tests/integration/` and are tagged `@pytest.mark.integration`

---

## Git Workflow

### Branch Naming
```
feature/<ticket-id>-short-description
bugfix/<ticket-id>-short-description
hotfix/<ticket-id>-short-description
```

### Commit Message Format (Conventional Commits)
```
<type>(<scope>): <short description>

Body: what changed and why (not how)
Refs: #<ticket-id>
```
Types: `feat`, `fix`, `test`, `refactor`, `docs`, `chore`, `perf`
Scopes: `core`, `redirect`, `analytics`, `expiry`, `validation`, `api`, `hooks`, `ci`

### PR Rules
- Every PR needs: description, test evidence, screenshot/curl output if API change
- Minimum 1 approval before merge
- Squash merge only — no merge commits on main
- PR title must follow the same Conventional Commits format as commit messages

---

## Security Rules

- **Never** commit secrets, API keys, or passwords — use `.env` and `python-dotenv`
- **Never** use `shell=True` in `subprocess` calls
- Input validation happens in `src/validators.py` — nowhere else
- All SQL via ORM parameterised queries — string interpolation in queries is a firing offence
- Rate limiting is mandatory on all write endpoints

---

## Allowed Directories for AI Edits

Claude Code may only create or edit files in:
- `src/` — application source
- `tests/` — test suite
- `docs/` — documentation
- `.claude/` — governance config (hooks, commands)

Claude Code must **never** edit:
- `.env` or any secrets file
- `migrations/` without explicit user instruction
- `requirements.txt` without explicit user instruction

---

## Definition of Done

A task is done when ALL of these are true:
1. ✅ Code follows layering rules above
2. ✅ All existing tests still pass
3. ✅ New tests written covering the change (≥ 85% coverage on changed files)
4. ✅ No secrets or hardcoded config in code
5. ✅ Commit message follows Conventional Commits format
6. ✅ `/review` passes with no HIGH or CRITICAL findings
7. ✅ PR description filled out
