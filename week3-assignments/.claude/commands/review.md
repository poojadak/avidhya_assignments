# /review — AI-First Code Review

Review all staged changes against CLAUDE.md conventions and flag issues before commit.

## Steps

1. Run `git diff --staged` to get the full diff of staged changes.

2. If there are no staged changes, run `git diff HEAD~1` to review the last commit instead.
   Inform the user which diff you're reviewing.

3. Review the diff against **every rule in CLAUDE.md**. Check specifically:
   - **Layer violations** — business logic in routes, Flask imports in services, raw SQL anywhere
   - **Response envelope** — all JSON responses use `ok()` / `err()` helpers
   - **Type hints** — all new function signatures have type hints
   - **Docstrings** — all new public functions have Google-style docstrings
   - **Error handling** — no bare `except:` clauses
   - **Security** — no hardcoded secrets, no `shell=True`, no string interpolation in queries
   - **Test coverage** — are new functions covered by existing or new tests?
   - **Naming** — snake_case, Conventional Commits format for any commit messages present

4. Output your findings as a structured report:

```
## Code Review Report
**Files changed:** <list>
**Lines added / removed:** +X / -Y

### 🔴 CRITICAL (must fix before commit)
- <finding>

### 🟡 WARNING (should fix)
- <finding>

### 🟢 SUGGESTIONS (optional improvements)
- <finding>

### ✅ Looks Good
- <what was done well>

**Verdict:** APPROVED | CHANGES REQUESTED
```

5. If verdict is CHANGES REQUESTED, list the exact changes needed as a numbered action list.

6. If verdict is APPROVED, say: "✅ Ready to commit. Run /commit to generate your commit message."
