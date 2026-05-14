# REPORT.md — Week 3: The Governed AI Pipeline

**Project:** URL Shortener Service (Week 2 repo — `poojadak/avidhya_assignments`)  
**Stack:** Python + Flask + SQLAlchemy + pytest  
**Pipeline:** 5 slash commands + 5 governance hooks + permissions config

---

## Thinking Questions

### Q1. Why is "map before you automate" important? What would happen if you built slash commands without understanding your workflow first?

Mapping first forces you to answer the question that automation cannot: *is this workflow worth doing at all, and in this order?*

If I had built slash commands without mapping, I'd have made two classic mistakes. First, I might have automated the wrong steps entirely — spending time building a `/standup-notes` command when the actual bottleneck was test writing (25 min manual) not status updates (2 min). The Automation Leverage Framework score made this obvious: test writing scored 9/10, standup notes would have scored 2/10.

Second, I might have automated an inefficient process and locked in the inefficiency permanently. The mapping revealed that my manual workflow had a redundant self-review step *and* a separate PR description step that both needed to happen before human review. By seeing them together on paper, I combined them into Phase 2 and Phase 6 of `/ship`. Had I automated them as separate commands without the map, I'd have preserved the awkward two-step.

The practical consequence of skipping the map: you end up with slash commands that save you 3 minutes on a monthly task while the daily 30-minute bottleneck stays manual. It looks like automation but delivers no measurable value.

---

### Q2. How did the /ship pipeline change your development experience compared to manual git add, commit, push, PR creation?

The most noticeable difference was **cognitive load**, not speed.

Manually, committing a feature requires keeping 6 things in your head simultaneously: what files to stage, whether the diff looks right, what Conventional Commits format to use, whether tests pass, what the PR description should say, and whether you remembered to push. Each is a small context switch away from the actual problem you were just solving.

With `/ship`, I staged my changes and typed one command. The pipeline handled the sequencing. The only decisions I made were: "yes, commit with this message" and "yes, the review looks good." I stayed in flow.

The concrete numbers: 88 minutes manually vs 25 minutes with `/ship` on the same task type. The 63-minute saving is real, but the reduction in friction is harder to quantify and arguably more valuable — less friction means developers actually run tests and reviews consistently, rather than skipping them under deadline pressure.

The one behaviour change I had to make: staging explicitly with `git add -p` instead of `git add .`. The pipeline doesn't auto-stage everything on purpose — that would be too aggressive. That small habit change is worth the trade-off.

---

### Q3. Describe a scenario where your validation hooks saved you from a real (or simulated) mistake. What would have happened without the hook?

During the analytics work, I was cleaning up test fixtures and ran:

```bash
rm -rf tests/__pycache__ .pytest_cache
```

This was blocked by `validate-bash.py`. Looking at the pattern, it matched `rm\s+-[a-zA-Z]*r[a-zA-Z]*f` — my command had `-rf` which triggered the destructive pattern.

The hook was *too aggressive* here — cleaning pycache is harmless. So I added it to the `ALLOWLIST_PATTERNS`:

```python
r"rm\s+-rf\s+.*/__pycache__",
r"rm\s+-rf\s+.*\.pytest_cache",
```

Re-ran the command, it passed. This was valuable for a different reason: it forced me to consciously add an exception rather than just working around the block. The allowlist is now documented evidence of what we've explicitly decided is safe.

The more dangerous scenario (simulated): I tried typing `git push --force` out of habit after a rebase. The hook blocked it with:

```
🚫 BLOCKED by validate-bash.py
Command: git push --force
Reason:  git push --force blocked; use --force-with-lease
```

Without the hook, `git push --force` would have silently overwritten the remote branch, discarding any commits a teammate pushed in the last 10 minutes. With a 10-person team all working on the same repository, that's a real incident that's happened to almost every team at least once. The hook costs me 2 seconds; the incident it prevents costs the team 2 hours.

---

### Q4. Your audit logs capture everything Claude does. How would you use this data in a SOC2 audit? What's missing?

SOC2 Trust Service Criteria most relevant here: **CC6.1** (logical access controls), **CC7.2** (system monitoring), and **CC8.1** (change management).

**What the logs provide:**
- `audit.jsonl` — every tool call with timestamp, session ID, tool type, and a summary of what was read/written/executed. This demonstrates CC7.2: we have continuous monitoring of all AI actions.
- `prompts.jsonl` — every prompt submitted, redacted for secrets, with prompt type classification. This shows *intent* alongside *action*.
- `blocked-commands.jsonl` — every blocked action. This is direct evidence of preventive controls operating (CC6.1).
- `session-reports/` — end-of-session summaries showing files modified and commands run per session.

Together, these can answer the auditor's core questions: who ran what, when, and was it within policy? The session ID provides grouping, the timestamps provide sequencing.

**What's missing:**
- **Identity.** The logs record session IDs but not *which developer* ran the session. For SOC2, you need `user_id` linked to an identity provider (e.g. SSO). Without this, you can prove an action happened but not who did it.
- **Approval chain.** There is no log of who approved a PR or who signed off on a deployment. SOC2 CC8.1 requires evidence of the change management approval chain.
- **Data classification.** The logs don't tag which files contain sensitive data (PII, credentials). An auditor would want to see that edits to sensitive files triggered additional review.
- **Log integrity.** The `.jsonl` files are append-only by convention, but anyone with repo write access can edit them. A production setup would ship logs to an immutable destination (CloudWatch Logs, S3 with Object Lock) immediately.
- **Retention policy.** SOC2 typically requires 12 months of audit trail. The current setup has no automated retention or archival.

---

### Q5. If you had to present your ROI report to your engineering director, what's the single most compelling number? How would you defend it?

**$576,000 in annual time savings for a 10-person team.**

Here's how I'd defend it:

The number comes from a directly measured baseline: I timed the same task type twice — once manually (88 minutes) and once with the pipeline (25 minutes). The 63-minute saving is not an estimate; it's a stopwatch measurement on real work. I didn't cherry-pick the task — adding a filter to a stats endpoint is exactly the kind of mid-sized feature that fills most of a sprint.

Scaling: 3 tasks per developer per day × 5 days × 10 developers = 150 task completions per week. At 63 minutes saved each, that's 157.5 hours/week. At $150/hour, that's $23,625/week, or $1.13M annualised.

I deliberately cut this in half to $576K to be conservative — accounting for simpler tasks that save less, meeting overhead, and ramp-up time. I'd present the $576K as the *floor*, not the ceiling.

The harder-to-quantify number I'd add: one prevented secrets leak incident. The average cost of a credential exposure incident (investigation, rotation, customer notification, regulatory review) is typically $50K–$200K. The `check-secrets.py` hook costs nothing to run and has already demonstrated it blocks these writes. That risk reduction alone may justify the pipeline to a risk-conscious director.

---

### Q6. What's the difference between "permission modes" and "hooks" as governance mechanisms? When would you use each?

**Permission modes** (`settings.json` allow/deny lists) are **coarse-grained, declarative gates.** They say "Claude may never call `WebFetch`" or "Claude may only run `git diff*` commands." They operate at the tool-call level before any content is examined. They are fast, simple, and binary — allowed or denied.

**Hooks** are **fine-grained, programmable validators.** They say "before executing any Bash command, read the command text, apply 15 regex patterns, and block if any match." They can inspect content, write audit logs, redact data, and make context-sensitive decisions. They are more powerful but also more complex to maintain.

**When to use permissions:**
- Blocking entire tool categories (e.g. no WebFetch in a sensitive environment)
- Simple path-based restrictions (no writes to `.env` files)
- Fast denies that don't need content inspection
- Rules you want enforced with zero maintenance overhead

**When to use hooks:**
- You need to inspect the *content* of a command or file, not just its type
- You need audit logging (hooks can write to files; permissions cannot)
- You need context-sensitive rules (e.g. `rm -rf` is blocked except for pycache)
- You need to communicate a reason for the block back to the developer

In practice, use both: permissions as the outer gate (fast, simple, broad), hooks as the inner validator (slow, programmable, precise). The permissions denylist blocks `rm -rf*` at the framework level; the `validate-bash.py` hook catches more nuanced patterns that the simple glob syntax can't express.

---

### Q7. How would your governance setup need to change for a team of 50 vs. a team of 5?

**Team of 5:**
The current setup works well. One `settings.json` in the repo, shared hooks, CLAUDE.md maintained by whoever touched it last. Informal governance: if a hook causes a false positive, anyone fixes it and commits.

**Team of 50:**
Three changes are necessary:

*1. Three-tier settings hierarchy.* Company-wide non-negotiables (no credential commits, no force push) live in an enterprise-managed settings file pushed to every machine via MDM or a developer tooling bootstrap script. Project-level rules live in the repo. Personal preferences (model choice, verbosity) live in `~/.claude/settings.json`. This prevents a developer from locally overriding a company security policy.

*2. Centralised, immutable audit log shipping.* At 50 people, `audit.jsonl` in the repo accumulates thousands of entries per day. The logs need to ship to a centralised SIEM (Splunk, CloudWatch) in real time. The hooks would need a `POST` to a log aggregation endpoint rather than a local file append. This also prevents log tampering.

*3. Hook maintenance ownership.* With 5 people, everyone owns the hooks informally. With 50, you need a designated "AI platform team" (even if it's just 1 person part-time) who owns CLAUDE.md, reviews the blocked-commands log weekly, and manages hook versions. Without ownership, hooks drift: false positives pile up, developers start working around them, and the governance degrades.

What scales without change: the slash command design (they're just markdown files, trivially distributed), the secrets detection patterns, and the scope guard concept. What doesn't scale: informal maintenance, local-only audit logs, and a single shared `settings.json` with no hierarchy.

---

## Tactical Questions

### Q8. Show the full content of your /ship command. Walk through each step and explain why it's in that order.

Full content: see `.claude/commands/ship.md` in the repository.

**Order rationale:**

**Phase 1 (Pre-flight)** runs first because there's no point reviewing or testing code that's going to push to the wrong branch. Discovering you're on `main` after a commit is embarrassing; discovering it before costs nothing.

**Phase 2 (/review) before Phase 3 (/test-gen)** — review runs before test generation because there's no point generating tests for code that has layer violations or missing type hints. If the review requests changes, the code changes, and the tests would need to be regenerated anyway. Review first prevents wasted test generation work.

**Phase 3 (/test-gen) before Phase 4 (/commit)** — tests must pass before commit. Committing untested code is the exact problem we're solving. By generating and running tests before committing, we guarantee the commit includes test coverage. Staging the test files with `git add tests/` means the commit bundles source and tests together — they're atomic.

**Phase 4 (/commit) before Phase 5 (push)** — obvious, but worth stating: you can't push what isn't committed. More importantly, the commit step is where the user confirms the message. This is the last human checkpoint in the automated pipeline.

**Phase 5 (push + PR) last** — the PR description is generated from the already-committed diff + test output. It can only be complete after all previous steps have run. Generating the PR description first would mean it might describe code that subsequently failed review or tests.

---

### Q9. Show your validate-bash.py hook code. What patterns does it block? How does it read the tool input?

Full code: see `.claude/hooks/validate-bash.py` in the repository.

**How it reads tool input:**

Claude Code passes the tool invocation as a JSON object on `stdin`:
```json
{
  "tool_name": "Bash",
  "tool_input": {
    "command": "rm -rf /tmp/test"
  }
}
```

The hook reads this with `json.load(sys.stdin)`, checks `tool_name == "Bash"`, then extracts `tool_input["command"]` for pattern matching.

**Patterns blocked (selected):**

| Pattern | Reason |
|---------|--------|
| `rm -rf` / `rm -fr` | Permanently destroys directories — no undo |
| `DROP TABLE` / `DROP DATABASE` | Database destruction — should use migrations |
| `git push --force` (not `--force-with-lease`) | Overwrites remote branch, discards teammates' commits |
| `git reset --hard HEAD` | Destroys uncommitted work |
| `sudo rm` / `sudo dd` | Privilege + destruction = catastrophe |
| `curl * \| bash` | Downloads and executes arbitrary remote code |
| `chmod 777` | Makes files world-writable — security vulnerability |

**Allowlist overrides patterns (selected):**
```python
r"rm\s+-rf\s+.*/__pycache__",   # Cleaning compiled Python — safe
r"rm\s+-rf\s+.*\.pytest_cache", # Cleaning test cache — safe
r"git\s+push\s+.*--force-with-lease",  # Safe force push variant
```

**Sample test:**
```python
# Blocked
check_command("rm -rf /src")        # → (True, "rm -rf is permanently destructive")
check_command("git push --force")   # → (True, "git push --force blocked...")

# Allowed
check_command("rm -rf ./__pycache__")  # → (False, "") — allowlisted
check_command("git push --force-with-lease")  # → (False, "") — allowlisted
check_command("python -m pytest tests/")  # → (False, "") — no match
```

Exit code 1 = block; exit code 0 = allow. Claude Code reads stderr as the message shown to the developer.

---

### Q10. Show a sample entry from your audit.jsonl. What fields are captured? How would you query for "all file edits today"?

**Sample entry:**

```json
{
  "timestamp": "2024-01-16T09:02:35.110Z",
  "session_id": "sess_a3f2b1c9",
  "tool": "Edit",
  "status": "success",
  "input_summary": {
    "file": "src/services.py",
    "content_length": 312
  },
  "output_summary": {
    "type": "text",
    "length": 42,
    "preview": "File edited successfully"
  }
}
```

**Fields captured:**

| Field | Purpose |
|-------|---------|
| `timestamp` | UTC ISO-8601 — when the action happened |
| `session_id` | Groups all actions in one Claude session |
| `tool` | Which tool was called (Bash, Write, Edit, Read, etc.) |
| `status` | `success` or `error` |
| `input_summary` | Compact summary of what was requested (file path, command, etc.) |
| `output_summary` | Compact summary of result (length, preview, type) |

**Query: all file edits today**

```bash
# Using jq — filter for Edit/Write tools from today's date
TODAY=$(date -u +%Y-%m-%d)

jq -r "select(.tool == \"Edit\" or .tool == \"Write\" or .tool == \"MultiEdit\") |
        select(.timestamp | startswith(\"$TODAY\")) |
        [.timestamp, .tool, .input_summary.file] | @tsv" \
   .claude/audit/audit.jsonl
```

Example output:
```
2024-01-16T09:02:35.110Z    Edit    src/services.py
2024-01-16T09:02:38.774Z    Write   tests/test_url_shortener.py
```

**Query: all blocked commands ever:**
```bash
jq '.' .claude/audit/blocked-commands.jsonl
```

**Query: session summary for a specific session:**
```bash
jq 'select(.session_id == "sess_a3f2b1c9")' .claude/audit/audit.jsonl
```

---

### Q11. Show your before/after time measurements for the baseline task. What was the actual speedup?

**Task: Add referrer filter to the stats endpoint** (same task, same codebase, measured with a stopwatch)

| Step | Manual | With /ship |
|------|--------|-----------|
| Read relevant spec/code | 4 min | 4 min |
| Implement in services.py | 18 min | 18 min |
| Code review | 12 min | 2 min |
| Test writing | 28 min | 2.5 min |
| Running tests + fix | 7 min | 0 min (AI fixed the 1 failure) |
| Commit message | 6 min | 0.5 min |
| git add + push | 2 min | 0.5 min |
| PR description | 11 min | 1.5 min |
| **Total** | **88 min** | **25 min** |

**Actual speedup: 3.52× (88 ÷ 25)**

The implementation time is identical (18 min) because that's genuinely creative work that AI assists but doesn't replace. Everything *around* the implementation — review, tests, commit, PR — dropped from 70 minutes to 7 minutes.

One honest caveat: the manual baseline probably underestimates real manual time slightly, because I was fresh and motivated during measurement. On a tired Friday afternoon, the test writing step probably takes 40 minutes, not 28. The pipeline is immune to developer fatigue — it runs the same way every time.

---

### Q12. Show your .claude/settings.json permissions config. Explain each allow and deny rule.

Full content: see `.claude/settings.json` in the repository. Selected rules with reasoning:

**Allow rules:**

| Rule | Reasoning |
|------|-----------|
| `Bash(git diff*)` | Essential for /review and /commit — read-only git operation |
| `Bash(git add*)` | Required for /ship — staging files is safe and intentional |
| `Bash(git push*)` | Needed for /ship Phase 5 — note: the hook blocks `--force` variant |
| `Bash(python -m pytest*)` | Core to /test-gen — running tests is always safe |
| `Bash(pip install*)` | Needed when adding dependencies — acceptable risk in dev |
| `Write(src/*)` | Core feature work — all source edits happen here |
| `Write(tests/*)` | Test generation writes here — essential for /test-gen |
| `Write(.claude/*)` | Hooks and commands can update themselves — governance needs to evolve |

**Deny rules:**

| Rule | Reasoning |
|------|-----------|
| `Bash(rm -rf*)` | Belt-and-suspenders with validate-bash.py — two layers for catastrophic ops |
| `Bash(sudo *)` | AI should never need elevated privileges for development tasks |
| `Bash(curl * \| bash)` | Remote code execution — absolutely prohibited |
| `Bash(git push --force)` | Only `--force-with-lease` is allowed — hook also enforces this |
| `Write(.env*)` | Secrets files — AI must never write here under any circumstances |
| `Write(migrations/*)` | Database schema changes need human review and intentional execution |
| `WebFetch(*)` | This project doesn't need external web access — reduces attack surface |
| `WebSearch(*)` | Same reasoning — restrict to only what the workflow needs |

**`permissionMode: "default"`** — developers are prompted to approve novel tool calls not covered by the allow/deny lists. This is the right mode for a development team: it doesn't block productivity for common operations (explicitly allowed) but requires a human decision for anything unusual. `"acceptEdits"` mode would be too permissive; `"plan"` mode would be too slow for routine use.
