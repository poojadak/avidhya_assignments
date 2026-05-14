# /test-gen — Generate Tests for Changed Files

Auto-generate pytest tests for recently changed files, run them, and report coverage.

## Steps

1. Run `git diff --staged --name-only` to get the list of staged files.
   If nothing is staged, run `git diff HEAD~1 --name-only` instead.

2. Filter to only Python files inside `src/`. Ignore `__init__.py` and `extensions.py`.

3. For each changed `src/<module>.py` file:
   a. Read the file to understand what functions/classes changed.
   b. Check if `tests/test_<module>.py` already exists.
   c. If it exists, read it to understand existing coverage — do not duplicate tests.
   d. Generate new pytest test functions covering:
      - Happy path for every new/changed function
      - At least one error/edge case per function
      - Boundary value tests for any numeric or string-length inputs
   e. Every generated test must:
      - Follow naming: `test_should_<outcome>_when_<condition>`
      - Have a `# Tests: REQ-XXX-NNN` comment linking to a requirement
      - Use the `client` and `app` fixtures from `tests/conftest.py`
      - Not make real network or DB calls (use in-memory SQLite)

4. Write the new tests to the appropriate test file.
   - If the file exists, append only the new test functions to the correct class.
   - If the file doesn't exist, create it with a full module docstring and fixture imports.

5. Run the tests:
   ```
   python -m pytest tests/ -v --tb=short 2>&1
   ```

6. If any tests fail:
   - Show the failure output clearly.
   - Diagnose the root cause.
   - Fix either the test (if the test logic is wrong) or the source code (if there's a real bug).
   - Re-run until all tests pass.

7. Run coverage:
   ```
   python -m pytest tests/ --cov=src --cov-report=term-missing --tb=short 2>&1
   ```

8. Report summary:
   ```
   ## Test Generation Report
   **Files analysed:** <list>
   **Tests generated:** <N> new test functions
   **Test results:** X passed, Y failed
   **Coverage:** XX% overall
   **Uncovered lines:** <list any lines below 85% threshold>
   ```

9. If coverage on any changed file is below 85%, generate additional tests to close the gap.
