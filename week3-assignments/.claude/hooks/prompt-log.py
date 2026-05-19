#!/usr/bin/env python3
"""
UserPromptSubmit hook: prompt-log.py
Logs every user prompt before Claude processes it.
This gives us a full audit trail of what was asked, not just what was done.
"""

import json
import sys
from datetime import datetime, timezone

LOG_FILE = ".claude/audit/prompts.jsonl"

def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    prompt = data.get("prompt", "")
    session_id = data.get("session_id", "unknown")

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": "UserPromptSubmit",
        "session_id": session_id,
        "prompt_length": len(prompt),
        # Log the first 500 chars of prompt — enough for audit, not so much it's a data dump
        "prompt_preview": prompt[:500],
    }

    try:
        import os
        os.makedirs(".claude/audit", exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        # Never block a prompt because logging failed
        pass

    # Exit 0 = allow the prompt through
    sys.exit(0)

if __name__ == "__main__":
    main()
