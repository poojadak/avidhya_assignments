#!/usr/bin/env python3
"""
PostToolUse hook: audit-log.py
Logs every tool action Claude takes to .claude/audit/audit.jsonl.

Each line is a JSON record capturing: timestamp, session_id, tool_name,
tool_input summary, tool_result summary, and execution duration.

Hook type: PostToolUse
Applies to: All tools
"""

import json
import os
import sys
import hashlib
from datetime import datetime, timezone

AUDIT_DIR = ".claude/audit"
AUDIT_FILE = f"{AUDIT_DIR}/audit.jsonl"


def truncate(value, max_len=300):
    """Truncate long strings for log readability."""
    if isinstance(value, str) and len(value) > max_len:
        return value[:max_len] + f"... [truncated {len(value) - max_len} chars]"
    return value


def summarise_input(tool_name: str, tool_input: dict) -> dict:
    """Extract a meaningful, compact summary of the tool input."""
    if tool_name == "Bash":
        return {"command": truncate(tool_input.get("command", ""), 150)}
    elif tool_name in ("Write", "Edit"):
        return {
            "file": tool_input.get("file_path", tool_input.get("path", "unknown")),
            "content_length": len(tool_input.get("content", tool_input.get("new_string", ""))),
        }
    elif tool_name == "MultiEdit":
        return {
            "file": tool_input.get("file_path", "unknown"),
            "num_edits": len(tool_input.get("edits", [])),
        }
    elif tool_name == "Read":
        return {"file": tool_input.get("file_path", tool_input.get("path", "unknown"))}
    elif tool_name == "Glob":
        return {"pattern": tool_input.get("pattern", "")}
    else:
        # Generic: just include non-content keys
        return {k: truncate(str(v), 80) for k, v in tool_input.items()
                if k not in ("content", "new_string", "old_string")}


def summarise_output(tool_output) -> dict:
    """Extract a compact summary of the tool result."""
    if isinstance(tool_output, str):
        return {
            "type": "text",
            "length": len(tool_output),
            "preview": truncate(tool_output, 120),
        }
    elif isinstance(tool_output, dict):
        return {
            "type": "dict",
            "keys": list(tool_output.keys())[:10],
        }
    elif isinstance(tool_output, list):
        return {
            "type": "list",
            "count": len(tool_output),
        }
    return {"type": type(tool_output).__name__}


def get_session_id() -> str:
    """
    Derive a stable session ID for this process invocation.
    Uses PID + start time so each Claude session gets a unique ID.
    """
    pid = os.getpid()
    # Read process start time from /proc if available (Linux)
    try:
        with open(f"/proc/{pid}/stat") as f:
            start_time = f.read().split()[21]
        raw = f"{pid}-{start_time}"
    except Exception:
        raw = str(pid)
    return "sess_" + hashlib.sha256(raw.encode()).hexdigest()[:8]


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = payload.get("tool_name", "unknown")
    tool_input = payload.get("tool_input", {})
    tool_response = payload.get("tool_response", {})

    # Determine outcome
    output = tool_response.get("output", tool_response)
    is_error = tool_response.get("is_error", False)

    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": get_session_id(),
        "tool": tool_name,
        "status": "error" if is_error else "success",
        "input_summary": summarise_input(tool_name, tool_input),
        "output_summary": summarise_output(output),
    }

    os.makedirs(AUDIT_DIR, exist_ok=True)
    with open(AUDIT_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    sys.exit(0)


if __name__ == "__main__":
    main()
