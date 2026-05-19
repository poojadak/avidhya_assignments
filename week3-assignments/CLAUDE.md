# CLAUDE.md — Team Workflow Rules & Conventions

This file tells Claude how our team works. Read this before doing anything in this repo.

## Project Overview

We're working on a Node.js + Express REST API (based on the RealWorld spec). It has user auth, articles, comments, and tags. Tests are written with Jest.

## Architecture

```
src/
  routes/       # Express route handlers
  models/       # Mongoose models
  middleware/   # Auth, validation, error handling
  config/       # DB connection, env config
tests/
  unit/         # Unit tests for models and helpers
  integration/  # API endpoint tests
```

## Coding Conventions

- Use `async/await` instead of `.then()` chains
- Always handle errors with try/catch — never swallow exceptions silently
- Keep route handlers thin — business logic goes in a service layer if it gets complex
- Use `const` by default, `let` only when you need to reassign
- No `var`
- Indent with 2 spaces
- Single quotes for strings

## Naming

- Files: `kebab-case.js`
- Variables and functions: `camelCase`
- Classes and models: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Test files: `*.test.js` next to the file they test, or inside `tests/`

## Testing Standards

- Every new route needs at least one integration test
- Every utility function needs a unit test
- Aim for 70%+ coverage on new code (we check this in CI)
- Test file naming: `user.test.js` for `user.js`
- Use descriptive test names: `"should return 401 when token is missing"` not `"test auth"`

## Git Workflow

- Branch naming: `feature/short-description`, `fix/short-description`, `chore/short-description`
- Commit messages: follow conventional commits format (see below)
- Never commit directly to `main`
- PRs need at least one reviewer before merge
- Squash commits on merge

## Commit Message Format

```
<type>(<scope>): <short description>

<optional body>
```

Types: `feat`, `fix`, `chore`, `docs`, `test`, `refactor`

Examples:
- `feat(auth): add refresh token support`
- `fix(articles): return 404 when article not found`
- `test(users): add missing profile endpoint tests`

## Things Claude Should Never Do

- Never run `rm -rf` on anything
- Never push to `main` directly
- Never commit secrets, API keys, or passwords
- Never modify files outside `src/`, `tests/`, or `docs/` without asking first
- Never drop or truncate database tables

## Things to Always Do

- Run tests before committing (`npm test`)
- Add a comment if a piece of code is non-obvious
- Update the relevant test file when changing logic
- Check that the linter passes (`npm run lint`)
