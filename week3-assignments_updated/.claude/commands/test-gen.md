# /test-gen — Generate and Run Tests

Generate tests for recently changed files, then run them and report coverage.

## What this does

1. Finds which files changed recently (git diff)
2. Looks at each changed file and writes tests for any untested functions/routes
3. Runs the test suite
4. Reports coverage

## Steps

```
Run: git diff --name-only HEAD~1
```

For each `.js` file in `src/` that changed:

- Check if a corresponding test file exists in `tests/` or alongside the file
- If tests are missing or incomplete, generate them
- Tests should use Jest and follow our conventions in CLAUDE.md
- Focus on: happy path, error cases, edge cases (empty input, missing fields)

```
Run: npm test -- --coverage
```

## Test template to follow

```javascript
const request = require('supertest');
const app = require('../src/app');

describe('<feature name>', () => {
  describe('<function or route>', () => {
    it('should <expected behaviour>', async () => {
      // arrange
      // act
      // assert
    });

    it('should return error when <bad input>', async () => {
      // ...
    });
  });
});
```

## Output format

```
## Test Generation Report

**Files reviewed:** <list>
**Tests generated:** <count>
**Tests added to:** <filenames>

## Test Results
<paste npm test output summary>

## Coverage
- Statements: X%
- Branches: X%
- Functions: X%
- Lines: X%

## Status: PASS / FAIL
```
