#!/usr/bin/env python3
"""
Stop hook: session-summary.py
Runs when a Claude Code session ends. Reads the audit logs generated during
the session and writes a human-readable session summary report.

Hook type: Stop
"""

import json
import os
import sys
from datetime import datetime, timezone
from collections import Counter

AUDIT_DIR = ".claude/audit"
AUDIT_FILE = f"{AUDIT_DIR}/audit.jsonl"
PROMPTS_FILE = f"{AUDIT_DIR}/prompts.jsonl"
REPORTS_DIR = f"{AUDIT_DIR}/session-reports"


def load_jsonl(filepath: str) -> list[dict]:
    if not os.path.exists(filepath):
        return []
    entries = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def get_current_session_id() -> str:
    import hashlib
    pid = os.getpid()
    try:
        with open(f"/proc/{pid}/stat") as f:
            start_time = f.read().split()[21]
        raw = f"{pid}-{start_time}"
    except Exception:
        raw = str(pid)
    return "sess_" + hashlib.sha256(raw.encode()).hexdigest()[:8]


def main():
    session_id = get_current_session_id()

    # Load all audit records for this session
    all_actions = load_jsonl(AUDIT_FILE)
    all_prompts = load_jsonl(PROMPTS_FILE)

    session_actions = [a for a in all_actions if a.get("session_id") == session_id]
    session_prompts = [p for p in all_prompts if p.get("session_id") == session_id]

    if not session_actions and not session_prompts:
        # Nothing happened this session — skip report
        sys.exit(0)

    # ── Compute summary stats ─────────────────────────────────────────────────
    tool_counts = Counter(a["tool"] for a in session_actions)
    error_count = sum(1 for a in session_actions if a.get("status") == "error")
    files_written = [
        a["input_summary"].get("file", "")
        for a in session_actions
        if a["tool"] in ("Write", "Edit", "MultiEdit")
        and a["input_summary"].get("file")
    ]
    bash_commands = [
        a["input_summary"].get("command", "")
        for a in session_actions
        if a["tool"] == "Bash"
    ]
    slash_commands_used = [
        p["command"] for p in session_prompts if p.get("type") == "slash_command"
    ]

    # Load blocked actions
    blocked_file = f"{AUDIT_DIR}/blocked-commands.jsonl"
    blocked = load_jsonl(blocked_file)
    session_blocked = [b for b in blocked if b.get("session_id") == session_id
                       or True]  # blocked log doesn't always have session_id

    # Determine session time range
    timestamps = (
        [a["timestamp"] for a in session_actions] +
        [p["timestamp"] for p in session_prompts]
    )
    if timestamps:
        start_time = min(timestamps)
        end_time = max(timestamps)
    else:
        start_time = end_time = datetime.now(timezone.utc).isoformat()

    # ── Build report ──────────────────────────────────────────────────────────
    report_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report_time = datetime.now(timezone.utc).strftime("%H:%M UTC")

    report_lines = [
        f"# Claude Code Session Report",
        f"**Session ID:** {session_id}",
        f"**Date:** {report_date}  |  **End time:** {report_time}",
        f"**Session start:** {start_time}",
        f"**Session end:** {end_time}",
        "",
        "---",
        "",
        "## Prompts Summary",
        f"- Total prompts: **{len(session_prompts)}**",
        f"- Slash commands used: {', '.join(slash_commands_used) if slash_commands_used else 'none'}",
        f"- Prompt types: {dict(Counter(p.get('type','other') for p in session_prompts))}",
        "",
        "## Actions Summary",
        f"- Total tool calls: **{len(session_actions)}**",
        f"- Errors: {error_count}",
        f"- Tool breakdown: {dict(tool_counts)}",
        "",
        "## Files Modified",
    ]

    if files_written:
        seen = []
        for f in files_written:
            if f not in seen:
                seen.append(f)
                report_lines.append(f"  - `{f}`")
    else:
        report_lines.append("  - No files written this session")

    report_lines += [
        "",
        "## Bash Commands Run",
    ]
    if bash_commands:
        for cmd in bash_commands[:10]:  # cap at 10 for readability
            report_lines.append(f"  - `{cmd[:80]}`")
        if len(bash_commands) > 10:
            report_lines.append(f"  - ... and {len(bash_commands) - 10} more")
    else:
        report_lines.append("  - None")

    report_lines += [
        "",
        "## Security Events",
        f"- Blocked actions this session: {len(session_blocked)}",
    ]
    if session_blocked:
        for b in session_blocked[-5:]:  # last 5
            report_lines.append(
                f"  - [{b.get('hook','?')}] {b.get('action','?')}: {b.get('command', b.get('file',''))[:60]}"
            )

    report_lines += [
        "",
        "---",
        f"*Generated automatically by .claude/hooks/session-summary.py*",
    ]

    # ── Write report ──────────────────────────────────────────────────────────
    os.makedirs(REPORTS_DIR, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    report_path = f"{REPORTS_DIR}/session-{ts}-{session_id}.md"

    with open(report_path, "w") as f:
        f.write("\n".join(report_lines))

    print(f"📋 Session report saved: {report_path}", file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
