# /commit — Smart Commit Message Generator

Analyse staged changes and generate a Conventional Commits message, then commit.

## Steps

1. Run `git diff --staged` to get the full diff.
   If nothing is staged, tell the user: "Nothing is staged. Run `git add <files>` first."
   Stop here if nothing is staged.

2. Run `git diff --staged --stat` to get the file summary.

3. Analyse the diff to determine:
   - **Type:** What kind of change is this?
     - `feat` — new feature or endpoint
     - `fix` — bug fix
     - `test` — adding or fixing tests only
     - `refactor` — code restructure with no behaviour change
     - `docs` — documentation only
     - `chore` — dependency updates, config changes
     - `perf` — performance improvement
   - **Scope:** Which module was primarily changed?
     (`core`, `redirect`, `analytics`, `expiry`, `validation`, `api`, `hooks`, `ci`)
   - **Short description:** ≤ 72 chars, imperative mood, no full stop.
     Example: "add rate limiting to shorten endpoint"
   - **Body:** 2-3 sentences explaining *what* changed and *why* (not how).
   - **Refs:** If you can infer a ticket number from the branch name, include `Refs: #N`.

4. Show the proposed commit message to the user:
   ```
   Proposed commit message:
   ─────────────────────────────
   <type>(<scope>): <short description>

   <body>

   Refs: #<ticket> (if found)
   ─────────────────────────────
   ```

5. Ask: "Commit with this message? (yes / edit / cancel)"

6. If **yes**: run `git commit -m "<message>"` and confirm success.
   If **edit**: show the message in an editable block and wait for the user to provide the revised version, then commit.
   If **cancel**: stop without committing.

7. After a successful commit, print:
   "✅ Committed. Run /ship to open a PR, or push manually with `git push`."
