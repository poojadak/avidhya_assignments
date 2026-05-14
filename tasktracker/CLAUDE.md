# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the development server (http://127.0.0.1:5000)
python run.py

# Run with Flask CLI (alternative)
flask --app run run --debug

# Run tests
pytest tests/ -v

# Run a single test file
pytest tests/test_routes.py -v
```

## Architecture

Flask application package (`app/`) with in-memory storage (`tasks` dict keyed by UUID).

```
app/
  __init__.py   # create_app() factory; registers blueprint and error handlers
  routes.py     # all task routes via Blueprint
run.py          # entry point — calls create_app().run()
tests/
  test_routes.py
```

**Endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| GET | `/tasks` | List all tasks; accepts `?status=` filter |
| POST | `/tasks` | Create task (`title` required, `status` defaults to `todo`) |
| GET | `/tasks/<id>` | Fetch a single task |
| PUT | `/tasks/<id>` | Partial update (any subset of fields) |
| DELETE | `/tasks/<id>` | Delete a task (returns 204) |

**Task schema:**
```json
{
  "id": "<uuid>",
  "title": "string",
  "description": "string",
  "status": "todo | in_progress | done",
  "created_at": "<ISO-8601 UTC>"
}
```

**Storage:** In-memory `dict` — data resets on server restart. To add persistence, replace `tasks = {}` and the CRUD operations with a database layer (SQLite via Flask-SQLAlchemy is the natural next step).

**Error responses** are JSON `{"error": "<message>"}` with the appropriate HTTP status code (400 or 404).
