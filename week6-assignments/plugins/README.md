# HealthTrack Plugins

## run_skill.py — Skill Plugin Runner

> ⚠️ **Requires Anthropic API key** (`ANTHROPIC_API_KEY`) — does NOT work with Claude Pro subscription alone.
> 
> If you are using Claude Pro: use the slash commands inside Claude Code instead — `/security-audit`, `/pr-review`, `/test-coverage`. These work with your Pro subscription and need no setup.

---

## What the plugin adds (for API users only)

The slash commands run Skills cleanly but give you no visibility into what happened.
The plugin runner adds:

| Feature | Slash command | Plugin runner |
|---|---|---|
| Runs the Skill | ✅ | ✅ |
| Token count | ❌ | ✅ |
| Cost in USD | ❌ | ✅ |
| Output auto-saved to examples/ | ❌ | ✅ |
| Version + change type shown | ❌ | ✅ |
| Gmail alert on CRITICAL/MAJOR | ❌ | ✅ |
| Works in CI/CD pipelines | ❌ | ✅ |

---

## Setup (API users only)

```bash
pip install anthropic
export ANTHROPIC_API_KEY="sk-ant-..."   # from console.anthropic.com

# Optional — Gmail alerts on CRITICAL findings or MAJOR version changes:
export GMAIL_USER="you@gmail.com"
export GMAIL_APP_PASS="xxxx xxxx xxxx xxxx"   # Google App Password
```

---

## Commands

```bash
# List all Skills with version, status, release count
python plugins/run_skill.py --list

# Show full changelog for a Skill
python plugins/run_skill.py --changelog security-audit

# Run Security Audit
python plugins/run_skill.py security-audit --scope app/vitals.py --context CLAUDE.md

# Run PR Review
python plugins/run_skill.py pr-review --scope app/vitals.py --context CLAUDE.md

# Run Test Coverage Report
python plugins/run_skill.py test-coverage --module app/vitals.py --tests tests/test_vitals.py

# With email alert (fires on CRITICAL findings or MAJOR version)
python plugins/run_skill.py security-audit --scope app/vitals.py --context CLAUDE.md --notify you@gmail.com
```

---

## If you only have Claude Pro

Use slash commands inside a Claude Code session:

```
cd healthtrack-api
claude

/security-audit app/vitals.py
/pr-review app/vitals.py
/test-coverage app/vitals.py tests/test_vitals.py
```
