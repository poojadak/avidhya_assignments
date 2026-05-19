# ROI Report — AI-Augmented Development Pipeline

## Workflow Map

See [docs/workflow-map.md](./workflow-map.md) for the full annotated Mermaid diagram.

Quick version:
```
Ticket → Understand → Branch → Implement → Test → Review → Commit → PR → Review → Merge → Deploy
```

---

## Before/After Time Comparison

**Baseline task used for measurement:**
Add input validation to the user registration endpoint (check that email format is valid and password is at least 8 characters). This is a realistic, medium-sized task that touches a route, maybe a helper, and needs tests.

### Manual approach (WITHOUT pipeline)

| Step | Time Taken | Notes |
|------|-----------|-------|
| Read existing code and understand structure | 18 min | Had to trace through middleware manually |
| Write the validation logic | 22 min | Looked up regex for email validation |
| Write tests manually | 35 min | Figured out test structure, wrote edge cases slowly |
| Run tests, fix one failure | 12 min | Had a typo in the test assertion |
| Read diff, self-review | 14 min | Missed one convention issue (caught later in PR review) |
| Write commit message | 4 min | Had to look up our format doc |
| Push + manually fill out PR template | 11 min | Copy-paste from previous PR, edit |
| **Total** | **116 min** | |

### With full pipeline (/ship)

| Step | Time Taken | Notes |
|------|-----------|-------|
| Write the validation logic | 20 min | Same implementation time — AI doesn't write the code for me here |
| Run /review | 3 min | Caught one missing error handling case I hadn't noticed |
| Fix the issue flagged by review | 5 min | |
| Run /test-gen | 4 min | Generated 6 tests covering happy path + 4 edge cases |
| Checked and ran tests | 3 min | All passed, coverage went from 68% to 79% |
| Run /ship (commit + PR) | 2 min | Commit message generated, confirmed, pushed, PR opened |
| **Total** | **37 min** | |

### Result

- **Before: 116 minutes**
- **After: 37 minutes**
- **Time saved per task: ~79 minutes (68% reduction)**

The biggest gains were in testing (35 min → 4 min) and the review/commit/PR steps (29 min → 10 min combined).

---

## Estimated Weekly Time Savings Per Developer

Assuming a developer ships roughly 3 features or bug fixes per week of this size:

- Time saved per task: 79 minutes
- Tasks per week: 3
- **Weekly savings per developer: ~237 minutes (≈ 4 hours)**

---

## Projected Annual Savings for a 10-Person Team

| Metric | Value |
|--------|-------|
| Weekly savings per dev | 4 hours |
| Team size | 10 developers |
| Weekly team savings | 40 hours |
| Working weeks per year | 48 |
| **Annual hours saved** | **1,920 hours** |
| Hourly rate | $150 |
| **Projected annual savings** | **$288,000** |

Even if we're being conservative and cut that in half (say developers are only 50% as efficient with the tools as this test suggests), you're still looking at $144,000/year in recovered engineering time.

---

## Quality Improvements

| Area | Before | After |
|------|--------|-------|
| Test coverage (new code) | ~60–65% average | 74–80% with /test-gen |
| Review consistency | Varies by person and mood | Consistent checklist every time |
| Commit message quality | "fix stuff", "update route" | Proper conventional commits format |
| PR descriptions | Often blank or copy-pasted | Auto-generated with context |
| Secret leaks caught | 0 (caught in GitHub scanning later) | At write time, before commit |
| Dangerous command runs | Possible (trust developer memory) | Blocked by hook before execution |

---

## Governance Controls Deployed

| Control | Type | What It Does |
|---------|------|--------------|
| validate-bash.py | PreToolUse hook | Blocks rm -rf, force push, push to main, DROP TABLE |
| check-secrets.py | PreToolUse hook | Scans file writes for API keys, tokens, passwords |
| scope-guard.sh | PreToolUse hook | Blocks writes outside src/, tests/, docs/ |
| audit-log.sh | PostToolUse hook | Logs every tool action to audit.jsonl |
| prompt-log.py | UserPromptSubmit hook | Logs all user prompts |
| session-summary.py | Stop hook | Generates end-of-session report |
| settings.json allowlist | Permission config | Explicit allow/deny rules for all tool calls |
