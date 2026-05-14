# Self-Critique Log
_Generated as part of the spec-driven development process (Part 3.2)_  
_Prompt used: `prompts/code-reviewer.yaml`_

---

## Cycle 1 — Initial Code Generation

**Files reviewed:** `src/models.py`, `src/services.py`, `src/routes.py`  
**Tool used:** `prompts/code-reviewer.yaml` (role: security-reviewer, OWASP Top 10 checklist)

### Issues Found by Reviewer

```json
{
  "summary": "Two defects found: a double-tuple return value bug causing a Flask TypeError, and a timezone-naive datetime comparison crash when SQLite stores datetimes without tzinfo.",
  "issues": [
    {
      "id": "ISSUE-001",
      "owasp_category": "A04 Insecure Design / Logic Error",
      "severity": "HIGH",
      "severity_score": 3,
      "line_number": 62,
      "description": "routes.py line 62: `return err(str(exc), 409), 409` wraps an already-complete (response, status) tuple inside another tuple. Flask cannot interpret a 3-item tuple where the first element is itself a (response, int) tuple, raising TypeError at runtime.",
      "remediation": "Remove the trailing `, 409` — `err()` already sets the status code."
    },
    {
      "id": "ISSUE-002",
      "owasp_category": "A04 Insecure Design / Runtime Crash",
      "severity": "HIGH",
      "severity_score": 3,
      "line_number": 46,
      "description": "models.py is_expired(): SQLite stores DATETIME columns without timezone info. Comparing `datetime.now(timezone.utc)` (offset-aware) against a naive SQLite-retrieved datetime raises `TypeError: can't compare offset-naive and offset-aware datetimes`, crashing every redirect for URLs that have an expires_at set.",
      "remediation": "Normalise the stored value before comparison: if `exp.tzinfo is None`, attach UTC via `exp.replace(tzinfo=timezone.utc)`."
    }
  ],
  "overall_score": 6,
  "approved": false
}
```

### Issues NOT Caught by Reviewer

- **No rate-limit integration tests** — the reviewer confirmed logic but couldn't exercise the `flask-limiter` middleware in the unit-test environment (limiter is disabled in tests via config). This is a known limitation of static review.
- **No check for very long URL inputs** — a URL of 100 000 characters would be accepted. A `MAX_URL_LENGTH` guard should be added in a future iteration.
- **`SECRET_KEY` default value** — the reviewer flagged the hardcoded `"change-me-in-production"` default (OWASP A02) as INFO severity. Acceptable for development; must be overridden via environment variable in production.

---

## Cycle 2 — Fix & Validate

### Fix applied for ISSUE-001 (`routes.py`)

```python
# Before (broken)
except DuplicateUrlError as exc:
    return err(str(exc), 409), 409   # double-wraps the tuple → TypeError

# After (fixed)
except DuplicateUrlError as exc:
    return err(str(exc), 409)        # err() already returns (response, status)
```

### Fix applied for ISSUE-002 (`models.py`)

```python
# Before (broken)
def is_expired(self) -> bool:
    if self.expires_at is None:
        return False
    return datetime.now(timezone.utc) > self.expires_at  # crashes if naive

# After (fixed)
def is_expired(self) -> bool:
    if self.expires_at is None:
        return False
    exp = self.expires_at
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)  # normalise to UTC
    return datetime.now(timezone.utc) > exp
```

### Re-run result

```
28 passed in 2.06s   ✅  (was 25 passed, 3 failed)
```

---

## Summary

| Cycle | Issues Found | Fixed | First-Run Pass Rate |
|-------|-------------|-------|---------------------|
| 1     | 2 HIGH, 1 INFO | 2 HIGH fixed | 25/28 (89%) |
| 2     | 0 new | — | 28/28 (100%) |

**Key learning:** The self-critique loop caught both bugs before any manual testing. The timezone bug in particular is a silent, environment-specific crash that would have been very difficult to spot in code review without running the tests on SQLite specifically.
