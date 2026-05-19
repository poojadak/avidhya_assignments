# Governance Playbook — 6-Week Team Rollout

## Goal

Get the full AI pipeline running safely across a 10-person engineering team, without disrupting existing workflows or causing frustration.

The approach is gradual. We start with the people who want to try it, show wins, then expand. We don't mandate it until people trust it.

---

## Week 1: Foundation (Admin only)

**Who:** Engineering lead + 1 volunteer developer

**What to do:**
- Clone the `.claude/` directory into the main repo
- Test all hooks manually to confirm they work on your machine
- Run `/review`, `/test-gen`, `/commit` on a real but low-stakes change
- Check that audit logs are generating correctly
- Fix any issues with paths or permissions

**Checklist:**
- [ ] `.claude/` directory merged to main branch
- [ ] All 5 hooks execute without errors
- [ ] Audit logs writing to `.claude/audit/audit.jsonl`
- [ ] `/ship` runs end-to-end at least once
- [ ] `settings.json` permissions tested (try a blocked command, confirm it's blocked)

**Gotchas to watch for:**
- Hook scripts need execute permissions (`chmod +x`)
- Python 3 needs to be in PATH on everyone's machine
- GitHub CLI (`gh`) needs to be installed for the PR step in `/ship`

---

## Week 2: Pilot with 3 Developers

**Who:** Engineering lead picks 3 developers (ideally a mix of experience levels)

**What to do:**
- Share a short doc explaining what each command does (max 1 page)
- Have each person use `/review` and `/commit` on their next real PR
- No pressure to use `/ship` yet — just get them comfortable with the basics
- Daily quick check-in (5 min): what worked, what was annoying?

**Goal:** Collect honest feedback. Don't defend the tools, just listen.

**Metrics to track:**
- Did they actually use the commands?
- Any false positives from hooks (blocked something they shouldn't have)?
- Commit message quality before vs. after?

---

## Week 3: Expand to Full Team + Address Feedback

**Who:** All 10 developers

**What to do:**
- Fix the issues from week 2 (update blocked patterns, adjust hook thresholds)
- Run a 30-min team session: show `/ship` end-to-end live, take questions
- Set the expectation: use `/review` before every PR from now on
- `/test-gen` and `/ship` are optional but encouraged

**What to tell the team:**
> "This isn't about replacing your judgment — it's about automating the repetitive checks so you can focus on the actual thinking. The hooks are there to catch mistakes, not to distrust you."

---

## Week 4: Measure and Tune

**Who:** Engineering lead, with input from the team

**What to do:**
- Pull 2 weeks of audit logs and summarize: how many actions, which tools used most, any blocks triggered?
- Look at commit history: is message quality improving?
- Run a test coverage comparison: week before vs. week after
- Update `CLAUDE.md` if any conventions need clarifying

**Adjust based on what you find:**
- If hooks are firing false positives often → tighten the pattern list
- If nobody is using `/test-gen` → find out why (too slow? output not useful?)
- If `/ship` is breaking on PR creation → check `gh` auth setup

---

## Week 5: Governance Review

**Who:** Engineering lead + any compliance/security stakeholder

**What to do:**
- Review the audit logs format — is it capturing enough for compliance?
- Check: can we answer "who ran what command when" from the logs? (You should be able to)
- Add any company-specific blocked patterns to `validate-bash.py`
- Document the permission rationale in `settings.json` (already started there)

**If you're heading toward SOC2:**
- Make sure session IDs are consistent and traceable
- Add user identity to log entries (Claude Code session → developer name mapping)
- Set up log retention (rotate or archive logs older than 90 days)

---

## Week 6: Make It the Default

**Who:** Full team

**What to do:**
- Add a CI check that requires audit log entries to exist for PRs (optional but powerful)
- Update the team onboarding docs to include Claude Code setup
- Run `/onboard` on the main repo and commit the output as `docs/onboarding-guide.md`
- Celebrate: you now have a governed AI pipeline that's actually being used

**What "success" looks like:**
- Developers are using `/ship` for most PRs without being asked
- Audit logs are clean and searchable
- No production incidents caused by Claude Code doing something it shouldn't
- At least one story of a hook catching a real mistake

---

## What Scales and What Doesn't

**Scales well:**
- The `.claude/` directory structure — just drop it in any repo
- Audit logging — JSONL is easy to stream to a central log aggregator later
- Permission configs — can be templated across repos

**Doesn't scale as well (needs attention at 50+ people):**
- Manual hook maintenance — you need someone owning the hook codebase
- Audit log volume — at 50 devs, you'll need to ship logs to something like Splunk or Datadog
- Per-repo CLAUDE.md — consider a shared "company standards" document that gets pulled in
- Onboarding — the `/onboard` command is great but doesn't replace a real onboarding process at scale
