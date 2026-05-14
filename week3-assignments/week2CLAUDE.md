# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the development server (http://localhost:5000)
python run.py

# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run a single test
pytest tests/test_url_shortener.py::TestClassName::test_function_name -v
```

## Architecture

This is a Flask URL shortener with a clean three-layer architecture:

**Routes → Services → Models/Validators**

- `src/__init__.py` — App factory `create_app(config_object=None)`. Initializes extensions, registers blueprints, creates DB tables on startup. Overridable config dict is used in tests.
- `src/extensions.py` — Shared `db` (SQLAlchemy) and `limiter` (Flask-Limiter) instances to avoid circular imports.
- `src/routes.py` — Flask Blueprint. Three endpoints: `POST /api/shorten`, `GET /<code>` (redirect), `GET /api/urls/<code>/stats`. Handles HTTP concerns only; delegates all logic to services.
- `src/services.py` — Business logic with no Flask dependencies. Functions: `create_short_url()`, `resolve_redirect()`, `get_stats()`. Raises domain-specific exceptions (`NotFoundError`, `ExpiredUrlError`, `DuplicateUrlError`, `AliasConflictError`) that routes catch and convert to HTTP errors.
- `src/models.py` — Single `UrlRecord` SQLAlchemy model with analytics fields (`click_count`, `last_accessed`, `referrer`) and optional expiry. Soft-deleted via `is_active` flag.
- `src/validators.py` — Pure functions `validate_url()` and `validate_alias()` used by the service layer.

## Key Behaviors

- **Short codes:** 6-character random alphanumeric, or a custom alias (3–20 chars).
- **Duplicate detection:** If an identical active, non-expired URL is submitted again, returns the existing short code rather than creating a new one.
- **Expiry:** Stored and compared as UTC-aware datetimes. Expired URLs return 410 Gone.
- **Rate limiting:** `/api/shorten` is limited to 60 requests/minute per IP. Disabled in tests via `RATELIMIT_ENABLED: False`.
- **Domain blocklist:** Configured in `create_app()` under `BLOCKED_DOMAINS`; raises a validation error for blocked hosts.
- **Database:** SQLite at `urls.db` by default; tests use in-memory SQLite (`:memory:`).

## Spec & Traceability Docs

- `specs/url-shortener.yaml` — Formal spec with 16 requirements (REQ-SHORT-001 through REQ-API-002), Gherkin scenarios, and OpenAPI contract.
- `docs/traceability-matrix.md` — Maps every requirement to its implementing file and test function.
- `prompts/` — YAML prompt templates used during AI-assisted development (spec-writer, architect, code-reviewer, test-generator).
