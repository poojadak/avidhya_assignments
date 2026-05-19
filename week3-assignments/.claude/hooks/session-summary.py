#!/usr/bin/env python3
"""
Stop hook: session-summary.py
When Claude finishes a session, generate a summary report.
"""

import json
import sys
import os
from datetime import datetime, timezone
from collections import Counter

AUDIT_LOG = ".claude/audit/audit.jsonl"
PROMPT_LOG = ".claude/audit/prompts.jsonl"
SUMMARY_DIR = ".claude/audit/sessions"

def load_jsonl(path):
    entries = []
    if not os.path.exists(path):
        return entries
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except:
                    pass
    return entries

def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        data = {}

    session_id = data.get("session_id", "unknown")
    
    # Load logs
    actions = load_jsonl(AUDIT_LOG)
    prompts = load_jsonl(PROMPT_LOG)

    # Filter to this session if session_id is available
    if session_id != "unknown":
        session_actions = [a for a in actions if a.get("session_id") == session_id]
        session_prompts = [p for p in prompts if p.get("session_id") == session_id]
    else:
        # Just use everything logged (for demo purposes)
        session_actions = actions[-50:]  # last 50 entries
        session_prompts = prompts[-10:]

    # Build summary
    tool_counts = Counter(a.get("tool") for a in session_actions)
    
    files_edited = set()
    commands_run = []
    
    for action in session_actions:
        tool = action.get("tool", "")
        inp = action.get("input_summary", {})
        if tool in ("Write", "Edit", "str_replace_editor"):
            path = inp.get("path", "")
            if path:
                files_edited.add(path)
        elif tool == "Bash":
            cmd = inp.get("command", "")
            if cmd:
                commands_run.append(cmd[:100])

    summary = {
        "session_id": session_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stats": {
            "total_actions": len(session_actions),
            "total_prompts": len(session_prompts),
            "tools_used": dict(tool_counts),
            "files_edited": list(files_edited),
            "commands_run": commands_run[:20],  # cap at 20
        }
    }

    # Save session summary
    os.makedirs(SUMMARY_DIR, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    summary_file = f"{SUMMARY_DIR}/session_{ts}.json"
    
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)

    # Print a human-readable version
    print(f"\n{'='*50}")
    print(f"SESSION SUMMARY — {ts}")
    print(f"{'='*50}")
    print(f"Total actions: {summary['stats']['total_actions']}")
    print(f"Prompts sent:  {summary['stats']['total_prompts']}")
    print(f"\nTools used:")
    for tool, count in tool_counts.most_common():
        print(f"  {tool}: {count}x")
    if files_edited:
        print(f"\nFiles edited:")
        for f in sorted(files_edited):
            print(f"  {f}")
    print(f"\nSummary saved to: {summary_file}")
    print(f"{'='*50}\n")

    sys.exit(0)

if __name__ == "__main__":
    main()
