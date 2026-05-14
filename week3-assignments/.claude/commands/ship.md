# /ship — Full Deployment Pipeline

End-to-end pipeline: review → generate tests → commit → push → open PR.
This is the command you run when a feature is ready.

## Steps

### Phase 1 — Pre-flight Check
1. Run `git status` to confirm we're on a feature branch (not `main` or `master`).
   If on main/master, STOP and tell the user:
   "⛔ You're on the main branch. Create a feature branch first:
   `git checkout -b feature/<description>`"

2. Run `git diff --staged --stat`. If nothing is staged, run `git add -p` guidance:
   "ℹ️ Nothing staged. Showing unstaged changes — stage the files you want to ship:"
   Then run `git diff --stat` and ask the user to confirm which files to stage.
   Do NOT auto-stage everything with `git add .` — always be explicit.

### Phase 2 — Code Review (/review)
3. Run the full /review pipeline on staged changes.
   - If verdict is **CHANGES REQUESTED**: stop and list required fixes.
     Do NOT continue to test generation until review passes.
   - If verdict is **APPROVED**: continue.

### Phase 3 — Test Generation & Validation (/test-gen)
4. Run the full /test-gen pipeline.
   - Generate tests for all changed src/ files.
   - Run `python -m pytest tests/ -v --tb=short`.
   - If any tests FAIL: diagnose and fix before continuing.
   - Run coverage — if any changed file is below 85%, generate more tests.
   - Stage the new test files: `git add tests/`.

### Phase 4 — Commit (/commit)
5. Run the full /commit pipeline on all staged changes (src + tests together).
   Wait for user confirmation before committing.

### Phase 5 — Push & PR
6. After successful commit, run:
   ```
   git push -u origin <current-branch>
   ```

7. Generate a PR description using this template:
   ```
   ## What changed
   <2-3 sentences from the commit body>

   ## Why
   <business/technical reason>

   ## Test evidence
   <paste the pytest output summary — X passed, coverage %>

   ## Checklist
   - [x] Tests written and passing
   - [x] Coverage ≥ 85% on changed files
   - [x] /review approved (no CRITICAL/HIGH findings)
   - [x] Follows CLAUDE.md conventions
   - [ ] Reviewed by teammate
   ```

8. Print the PR description and say:
   "📋 PR description ready. Open a PR at:
   https://github.com/poojadak/avidhya_assignments/compare/<branch>
   and paste the description above."

### Phase 6 — Summary
9. Print a ship summary:
   ```
   🚀 Ship complete!
   ─────────────────────────────────
   Branch:    <branch>
   Commit:    <sha> — <message>
   Tests:     X passed, Y% coverage
   Review:    APPROVED
   PR:        Link above
   ─────────────────────────────────
   ```
