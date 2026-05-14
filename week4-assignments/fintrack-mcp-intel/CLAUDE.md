# CLAUDE.md — FinTrack MCP Engineering Intelligence Platform

## System Purpose

This system is a Claude Code-powered engineering intelligence tool built for FinTrack, a real-time financial monitoring SaaS. It connects Claude to live data sources — GitHub, PostgreSQL, and Jira — via MCP servers, and answers operational questions that would otherwise require engineers to switch between multiple tools manually. The primary users are FinTrack's 60-person engineering team, who use it during daily standups, incident response, and sprint reviews. Instead of spending 2+ hours a day stitching data together, engineers can ask natural language questions and get answers in under 60 seconds.

## MCP Server Registry

| Server      | URL                              | Access Level      | Owner               |
|-------------|----------------------------------|-------------------|---------------------|
| github-mcp  | https://api.github.com/mcp/sse   | Read-only (Issues, PRs, Contents, Metadata) | Platform Engineering |
| pg-mcp      | https://mcp.postgres.io/sse      | Read-only (analytics replica)               | Data Infrastructure  |

## Workflows

### WF-01: Morning Intelligence Brief

- **Trigger:** `python main.py --workflow morning-brief`
- **MCP tools called (in order):**
  1. `github_pull_requests` — fetches open, non-draft PRs older than 1 day
  2. `github_issues` — fetches open issues labelled P0 or P1
  3. `db_tools.get_overnight_alerts()` — returns services with elevated overnight error rates
- **Output:** A markdown string with four sections: `## PRs_NEEDING_REVIEW`, `## OPEN_P0_P1`, `## OVERNIGHT_DB_ALERTS`, `## ACTION_ITEMS` (exactly 3 bullet points, priority-ordered). If any data source returns empty, the section still appears with a "No data returned from [source]" message.

### WF-02: Incident Triage

- **Trigger:** `python main.py --workflow incident-triage --service <service_name>`
- **MCP tools called (in order):**
  1. `db_tools.get_error_rate(service, window_minutes=30)` — 30-minute baseline
  2. `github_commits` — recent commits to `services/<service>/` in the last 4 hours
  3. `github_issues` — open bugs tagged with the service name
  4. `db_tools.get_error_rate(service, window_minutes=5)` — current error rate snapshot
- **Output:** A JSON object matching the `IncidentReport` schema:
  ```json
  {
    "service": "string",
    "error_rate_now": 0.0,
    "error_rate_30min_avg": 0.0,
    "likely_cause": "string",
    "recent_deploys": ["sha: message"],
    "recommended_action": "string",
    "escalate": true
  }
  ```
  If Claude returns malformed JSON or a critical data call fails, returns `ESCALATE_FALLBACK` with `escalate: true`.

## Architecture Rules

1. **All tokens via environment variables only** — never hardcode credentials anywhere in the codebase. Use `.env` locally; use secrets manager in production. The `.env` file is in `.gitignore` and must never be committed.
2. **Every MCP tool call must be logged via `audit.log()`** — no exceptions. Logging failures must never crash the workflow; they should warn to stderr and continue.
3. **No PII flows through any prompt** — use aggregated metrics and anonymised data only. No customer names, no account IDs, no raw transaction data in prompts or responses.
4. **Error handling is mandatory in all tool wrappers** — every function in `mcp/github_tools.py` and `mcp/db_tools.py` must catch exceptions and return an empty list/dict rather than propagating the error to the caller. Workflows should degrade gracefully, not crash.
5. **Input data must be hashed before logging** — use SHA-256 on JSON-serialised tool inputs. Store the hex digest in audit entries, never the raw values.

## Prompt Templates

### morning_brief.txt

```
You are the FinTrack Engineering Intelligence System — a tool that helps the FinTrack engineering team start each day with a clear picture of what needs attention.

Below is live data pulled from GitHub and the production database. Summarise it into a structured engineering brief. Be concise and direct — engineers are reading this at standup, not a board meeting.

--- PULL REQUESTS NEEDING REVIEW ---
{{PR_DATA}}

--- OPEN P0/P1 ISSUES ---
{{ISSUE_DATA}}

--- OVERNIGHT DATABASE ALERTS ---
{{DB_ALERTS}}

---

Produce a markdown report with EXACTLY these four section headers in this order. Do not rename or reorder them:

## PRs_NEEDING_REVIEW
...

## OPEN_P0_P1
...

## OVERNIGHT_DB_ALERTS
...

## ACTION_ITEMS
(exactly 3 bullet points, most urgent first)

Rules: No PII, no customer names, no raw SQL. If any section has no data, still include the header with "No data returned from [source]".
```

### incident_triage.txt

```
You are the FinTrack Incident Triage System. Analyse the data below and return ONLY a JSON object matching the IncidentReport schema. No preamble, no explanation, no markdown fences.

Inputs: {{SERVICE_NAME}}, {{ERROR_RATE_30MIN}}, {{ERROR_RATE_NOW}}, {{RECENT_COMMITS}}, {{OPEN_BUGS}}

Set escalate=true if error_rate_now > 3x error_rate_30min_avg.

Return ONLY the JSON object.
```
