# /review — AI Code Review

Review all staged changes against our team's conventions in CLAUDE.md.

## What this does

1. Runs `git diff --staged` to see what's about to be committed
2. Checks the changes against our coding standards
3. Flags any issues before they get committed

## Steps

```
Run: git diff --staged
```

Look at everything that changed and check for:

- **Code style**: Are we using async/await? Single quotes? 2-space indent?
- **Error handling**: Are there try/catch blocks where needed? Any silent failures?
- **Naming**: Do files, variables, and functions follow our naming conventions?
- **Test coverage**: If logic changed, is there a corresponding test change?
- **Security**: Any hardcoded secrets, API keys, or passwords?
- **Scope**: Are edits only inside `src/`, `tests/`, or `docs/`?

## Output format

Give a review in this format:

```
## Code Review Summary

**Files changed:** <list>
**Overall:** PASS / NEEDS CHANGES / FAIL

### Issues Found
- [CRITICAL] <issue> — must fix before commit
- [WARNING] <issue> — should fix, but won't block
- [SUGGESTION] <issue> — optional improvement

### What looks good
- <things done well>

### Verdict
Ready to commit / Fix these issues first
```

If there are no staged changes, say so and stop.
