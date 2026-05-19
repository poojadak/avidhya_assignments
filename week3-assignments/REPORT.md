# REPORT.md — Week 3 Assignment: The Governed AI Pipeline

**Repository:** gothinkster/node-express-realworld (Node.js stack)
**Target:** `.claude/` governance infrastructure drop-in

---

## Thinking Questions

### Q1. Why is "map before you automate" important? What would happen if you built slash commands without understanding your workflow first?

If you start building automation without understanding your workflow, you end up automating the wrong things. Or worse, you automate a process that's already broken and just make the broken version faster.

For example, if I hadn't mapped the workflow first, I might have built a fancy `/deploy` command when the real pain point was that tests were inconsistent and slow to write. The deploy step is fine — it's automated by CI already. The test-writing step is where 30 minutes of every developer's day was disappearing.

Mapping forces you to see the workflow as it actually is, not how you think it is. It also surfaces the *pain points*, not just the *steps*. Two steps can take the same amount of time, but one is painful and error-prone while the other is just repetitive clicking. Those are different problems.

The other issue with skipping the map is that you might automate an inefficient process and lock it in. If your PR description workflow is bad, automating the bad version just makes bad PR descriptions get created faster and more consistently.

---

### Q2. How did the /ship pipeline change your development experience compared to manual git add, commit, push, PR creation?

The biggest change was cognitive load. When you're doing it manually, you're holding a checklist in your head: have I staged everything? Is the commit message right? Did I fill out the PR template? Did I run tests? It's not that any individual step is hard, it's that you're managing the whole sequence yourself.

With `/ship`, the pipeline manages the sequence. If review fails, it stops and tells you. If tests fail, it stops and tells you. You don't have to remember the order or worry about skipping a step because you were in a hurry.

Speed-wise, the 10–15 minutes of manual git + PR work becomes about 2 minutes. That doesn't sound like much, but it's actually a big deal because those 10–15 minutes happen multiple times a day, and they break your concentration at the worst possible moment — right when you're about to finish something.

The PR descriptions also got better. When I was writing them manually, I was tired from the implementation work and wrote minimal descriptions. The auto-generated ones from `/ship` are longer and more useful because they're created fresh from the diff, not from a fatigued brain.

---

### Q3. Describe a scenario where your validation hooks saved you from a real (or simulated) mistake. What would have happened without the hook?

During testing, I tried to clean up some old test fixture files and ran:

```bash
rm -rf ./tests/fixtures/*
```

This was blocked by `validate-bash.py` because the pattern matched `rm -rf` with a wildcard.

In this particular case, it wasn't actually dangerous — I was only removing fixture files I was about to regenerate. But here's the thing: the hook doesn't know that. And neither does a tired developer at 6pm on a Friday who thinks they're in a test directory but is actually one level higher than they think.

Without the hook, that command runs silently, deletes everything, and you only notice when the test suite fails with "cannot find module ./fixtures/user.json". Now you're spending 20 minutes figuring out what happened.

The hook created a moment of pause. I had to consciously think "yes, I actually want to delete these" and do it a different way (listed the files first, then deleted specifically). That's the right behavior.

---

### Q4. Your audit logs capture everything Claude does. How would you use this data in a SOC2 audit? What's missing?

The audit logs directly support a few SOC2 controls:

**CC6 (Logical Access Controls):** The logs show exactly which files were accessed and modified. If an auditor asks "did anyone touch the authentication middleware last month?", you can search the logs for `"path": "src/middleware/auth.js"` and get a complete answer.

**CC7 (System Operations):** The logs show every bash command that ran. This is useful for proving that dangerous operations were blocked and that the system behaved as configured.

**CC8 (Change Management):** Combined with git history, the audit logs can show the AI actions that led to each commit — what was reviewed, what tests were run, what the AI checked before the commit was made.

**What's missing:**

The current logs don't capture the developer's identity. They have a `session_id` but that doesn't map to a specific person without additional tooling. For a real SOC2 audit, you'd need to know *who* ran each command, not just *what* was run in a session.

There's also no approval chain. The logs show that a review happened, but they don't capture whether a human approved the review results before proceeding. That kind of human-in-the-loop confirmation would be important for high-risk changes.

And there's no tamper evidence. The current `audit.jsonl` file is just a text file — anyone with access to the repo can edit it. A proper audit trail needs to be write-once and stored somewhere that can't be modified after the fact.

---

### Q5. If you had to present your ROI report to your engineering director, what's the single most compelling number? How would you defend it?

**$288,000 in annual recovered engineering time for a 10-person team.**

Here's how I'd defend it:

The number comes from a concrete before/after measurement on a real task. Adding input validation to the user registration endpoint took 116 minutes manually and 37 minutes with the pipeline. That's a 68% reduction.

If a developer ships 3 tasks of similar size per week, that's 4 hours recovered per week per person. Across 10 developers over 48 working weeks: 1,920 hours saved. At $150/hour, that's $288,000.

The skeptical question will be: "Is that really replicable across all tasks?" Fair. Some tasks are bigger and more complex where the speedup is smaller. Some are tiny where the overhead of running the pipeline isn't worth it. So I'd say: "Even if this only applies to half our work, that's $144,000. And that's before counting the reduction in review cycles from better code quality, or the reduction in production incidents from the governance hooks."

The number is large enough to be interesting and the methodology is honest enough to survive scrutiny.

---

### Q6. What's the difference between "permission modes" and "hooks" as governance mechanisms? When would you use each?

**Permission modes** are blunt instruments. They say "this entire category of action is allowed or not allowed." They're enforced before anything else happens and they're binary. You either can call `Bash(rm -rf *)` or you can't.

**Hooks** are programmable. They can look at the specific command, check the context, examine the content, and make a nuanced decision. A hook can allow `rm -rf ./temp/*` while blocking `rm -rf ./src/*`. A permission rule would have to block all `rm -rf` or allow all of it.

**When to use permissions:**
Use them for things that should never happen in any context. "Never push directly to main" is a permission rule — there's no scenario where Claude should push to main directly from a developer workstation. It's a hard line.

**When to use hooks:**
Use them for things that need context to evaluate. "Don't delete important files" requires knowing what files are important, what the current directory is, whether the delete is inside a safe scope. That's hook territory.

In practice, you use both together. Permissions set the outer boundary (broad categories of allowed/denied actions). Hooks add fine-grained control within those boundaries.

---

### Q7. How would your governance setup need to change for a team of 50 vs. a team of 5? What scales and what doesn't?

**Team of 5 → current setup works fine.** Everyone knows the codebase. CLAUDE.md can be specific. One person can maintain the hooks. Audit logs are small enough to review manually.

**Team of 50 → several things break:**

*Hook maintenance becomes a job.* Right now one person owns the hooks and knows how they work. At 50 people across multiple repos, you need a dedicated security/tools team managing hook versions. The hooks need to live in a central place (maybe a shared package) instead of per-repo.

*CLAUDE.md can't be monolithic.* A single file with "team conventions" doesn't work when you have 5 teams with different conventions. You need a hierarchy: company-wide standards + team-specific standards + repo-specific standards.

*Audit log volume becomes a problem.* 10 developers generating logs is manageable. 50 developers will produce logs that need to be shipped to a real log management system (Splunk, Datadog, CloudWatch) with retention policies, search capability, and alerting.

*Settings.json needs central management.* You don't want 20 different repos with 20 different permission configs. You need a way to push policy updates from one place and have them propagate.

*What scales fine:* The `.claude/` directory concept, JSONL audit format, the slash command approach, the hook architecture. These are all good patterns — they just need tooling around them to work at scale.

---

## Tactical Questions

### Q8. Show the full content of your /ship command. Walk through each step and explain why it's in that order.

Full content is in `.claude/commands/ship.md`. Here's the logic behind the ordering:

**Step 1: /review first**

Review happens before tests because there's no point running tests on code that violates our conventions. If the code has a structural problem (wrong error handling pattern, wrong naming), I want to catch that first before generating tests that test the wrong implementation.

**Step 2: /test-gen second**

Tests come before committing because I want coverage data as part of the commit decision. If coverage drops below our threshold, I should know that before the commit, not after.

**Step 3: /commit third**

Commit happens after both review and tests have passed. The commit message is generated from the diff at this point, so it reflects exactly what's being committed — no drift between what changed and what the message says.

**Step 4: PR creation last**

The PR only gets created once everything is clean. This means reviewers get a PR that's already passed the automated pipeline. They can focus on logic and architecture, not style issues or missing tests.

The order isn't arbitrary — it's a quality gate cascade. Each step only runs if the previous one passed.

---

### Q9. Show your validate-bash.py hook code. What patterns does it block? How does it read the tool input?

Full code is in `.claude/hooks/validate-bash.py`.

**How it reads tool input:**

Claude Code passes a JSON object to stdin when a PreToolUse hook fires. The hook reads stdin, parses the JSON, checks the `tool_name` field, and then looks at `tool_input.command` for bash commands.

```python
data = json.load(sys.stdin)
tool_name = data.get("tool_name", "")
command = data.get("tool_input", {}).get("command", "")
```

If the tool isn't Bash, the hook exits 0 immediately (allow). If it is Bash, it runs the command through the pattern list.

**Patterns it blocks:**
- `rm -rf /`, `rm -rf *`, `rm -rf .` — filesystem destruction
- `DROP TABLE`, `DROP DATABASE`, `TRUNCATE TABLE` — database destruction
- `git push --force` and `git push -f` — force push
- `git push origin main/master` — direct push to protected branches
- `chmod 777` — overly permissive file permissions
- `curl | sh` and `wget | sh` — piping remote scripts to shell
- Fork bomb pattern
- `dd if=` — disk write commands
- `mkfs.` — filesystem formatting

**Sample test:**

```
$ python3 validate-bash.py --test

[PASS] 'rm -rf /'           expected=block, got=block
[PASS] 'git push origin --force'  expected=block, got=block
[PASS] 'npm test'           expected=allow, got=allow
[PASS] 'git push origin feature/my-branch'  expected=allow, got=allow
```

Exit code 2 = block. Exit code 0 = allow. The JSON `decision: block` message is printed to stdout so Claude Code can show it to the user.

---

### Q10. Show a sample entry from your audit.jsonl. What fields are captured? How would you query for "all file edits today"?

Sample entry:

```json
{
  "timestamp": "2025-05-15T09:13:10.002Z",
  "event": "PostToolUse",
  "tool": "Write",
  "input_summary": {
    "path": "tests/users.test.js",
    "operation": "Write"
  },
  "result_summary": {
    "exit_code": 0,
    "output_preview": "File written successfully"
  },
  "session_id": "sess_abc123"
}
```

**Fields captured:**
- `timestamp` — ISO 8601 UTC timestamp
- `event` — which hook fired (PostToolUse, UserPromptSubmit, etc.)
- `tool` — which Claude Code tool was used
- `input_summary` — what was passed to the tool (command, file path, etc.)
- `result_summary` — what came back (exit code, output preview)
- `session_id` — links all actions in a session together

**To query all file edits today:**

```bash
jq 'select(.timestamp | startswith("2025-05-15")) | select(.tool == "Write" or .tool == "Edit")' .claude/audit/audit.jsonl
```

To get just the file paths:

```bash
jq -r 'select(.timestamp | startswith("2025-05-15")) | select(.tool == "Write" or .tool == "Edit") | .input_summary.path' .claude/audit/audit.jsonl
```

---

### Q11. Show your before/after time measurements for the baseline task. What was the actual speedup?

**Task:** Add input validation (email format + password length) to the user registration endpoint.

**Without pipeline:**

| Step | Time |
|------|------|
| Read code, understand structure | 18 min |
| Write validation logic | 22 min |
| Write tests manually | 35 min |
| Run tests, fix failure | 12 min |
| Self-review diff | 14 min |
| Write commit message | 4 min |
| Push + fill PR template | 11 min |
| **Total** | **116 min** |

**With pipeline (/ship):**

| Step | Time |
|------|------|
| Write validation logic | 20 min |
| /review (caught one issue) | 3 min |
| Fix flagged issue | 5 min |
| /test-gen + run tests | 4 min |
| /commit + /ship | 2 min |
| **Total** | **34 min** |

**Actual speedup: 82 minutes saved (71% faster)**

To be transparent: the implementation time (writing the actual code) didn't change much. That's not what the pipeline helps with. The gains are almost entirely in the surrounding process — testing, reviewing, committing, and creating the PR. Those steps went from 62 minutes to 14 minutes.

---

### Q12. Show your .claude/settings.json permissions config. Explain each allow and deny rule.

Full config is in `.claude/settings.json`. Here's the reasoning:

**Allow rules:**

- `Bash(npm *)` — All npm commands are fine. Running tests, installing packages, running the dev server — these are all safe.
- `Bash(git add/commit/checkout/branch/status/diff/log/stash)` — Read-only and staging git operations. Safe to allow broadly.
- `Bash(git push origin feature/* and fix/*)` — Push is allowed, but only to feature and fix branches. Not to main or master.
- `Bash(gh pr *)` — GitHub CLI for PR operations. Safe.
- `Bash(cat/ls/find/echo/mkdir)` — Standard read and utility commands. No reason to block these.
- `Read(*)` — Reading any file is fine. You can't break anything by reading.
- `Write(src/*, tests/*, docs/*, .claude/*)` — Write access scoped to our working directories only.
- `Write(CLAUDE.md, README.md, REPORT.md)` — Root-level files we manage explicitly.

**Deny rules:**

- `Bash(rm -rf *)` — Never. The hook also catches this, but belt-and-suspenders.
- `Bash(sudo *)` — No elevated privileges, ever.
- `Bash(git push origin main/master)` — No direct pushes to protected branches.
- `Bash(git push --force, git push *-f *)` — No force pushes without explicit human action.
- `Bash(curl/wget | sh)` — Never pipe remote content directly to shell.
- `Bash(chmod 777 *)` — No world-writable permissions.
- `Bash(dd *)` — Disk operations.
- `Write(/etc/*, /usr/*, /home/*/.ssh/*)` — No writes to system or security directories.

The philosophy: allow what's needed for normal development work, deny what could cause irreversible damage or security problems. Hooks add nuance on top of this for cases that need context to evaluate.
