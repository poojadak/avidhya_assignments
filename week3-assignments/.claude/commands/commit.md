# /commit — Smart Commit Message Generator

Analyse the staged diff and generate a proper commit message, then commit.

## What this does

1. Reads `git diff --staged` to understand what changed
2. Figures out the type of change (feat, fix, chore, etc.)
3. Writes a commit message following our conventional commits format
4. Shows you the message and asks for confirmation
5. Runs the commit

## Steps

```
Run: git diff --staged
Run: git diff --staged --stat
```

Based on the diff, determine:

- **Type**: `feat` (new feature), `fix` (bug fix), `chore` (tooling/deps), `docs` (docs only), `test` (tests only), `refactor` (no behaviour change)
- **Scope**: the part of the codebase affected (e.g. `auth`, `articles`, `users`, `middleware`)
- **Description**: one short sentence, present tense, lowercase, no period at end

## Commit message format

```
<type>(<scope>): <description>

<optional body — only if the change needs explanation>
```

Examples:
- `feat(articles): add pagination to article list endpoint`
- `fix(auth): return 401 instead of 500 on expired token`
- `test(users): add follow/unfollow endpoint tests`

## Rules

- Description must be under 72 characters
- No "updated", "changed", or "modified" — be specific about what it does
- If multiple things changed, describe the most important one and list the rest in the body

## Output

Show the proposed commit message, then ask: **"Commit with this message? (yes/no)"**

If yes: run `git commit -m "<message>"`
If no: ask what to change and regenerate.
