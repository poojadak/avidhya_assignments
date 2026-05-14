#!/usr/bin/env python3
"""
UserPromptSubmit hook: log-prompts.py
Logs every user prompt submitted to Claude to .claude/audit/prompts.jsonl.

This creates an immutable audit trail of what was asked and when,
supporting SOC2 CC6.1 (logical access) and CC7.2 (monitoring) controls.

Hook type: UserPromptSubmit
"""

import json
import os
import sys
import hashlib
from datetime import datetime, timezone

AUDIT_DIR = ".claude/audit"
PROMPTS_FILE = f"{AUDIT_DIR}/prompts.jsonl"

# Redact any obvious secrets that might appear in prompts
SECRET_REDACT_PATTERNS = [
    r"(?i)(password|passwd|secret|api[_-]?key|token)\s*[:=]\s*\S+",
]


def redact_secrets(text: str) -> str:
    """Replace obvious secret values with [REDACTED] for safe logging."""
    import re
    for pattern in SECRET_REDACT_PATTERNS:
        text = re.sub(pattern, r"\1=[REDACTED]", text)
    return text


def get_session_id() -> str:
    pid = os.getpid()
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

    prompt = payload.get("prompt", "")
    redacted_prompt = redact_secrets(prompt)

    # Classify the prompt type for easier querying later
    prompt_lower = prompt.lower().strip()
    if prompt_lower.startswith("/"):
        prompt_type = "slash_command"
        command = prompt_lower.split()[0]
    elif any(kw in prompt_lower for kw in ["fix", "bug", "error", "broken"]):
        prompt_type = "bugfix"
        command = None
    elif any(kw in prompt_lower for kw in ["add", "implement", "create", "build"]):
        prompt_type = "feature"
        command = None
    elif any(kw in prompt_lower for kw in ["explain", "what", "how", "why"]):
        prompt_type = "question"
        command = None
    else:
        prompt_type = "other"
        command = None

    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": get_session_id(),
        "type": prompt_type,
        "command": command,
        "prompt_length": len(prompt),
        "prompt_preview": redacted_prompt[:200],
    }

    os.makedirs(AUDIT_DIR, exist_ok=True)
    with open(PROMPTS_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    # Do NOT modify the prompt — just log and exit 0
    sys.exit(0)


if __name__ == "__main__":
    main()
