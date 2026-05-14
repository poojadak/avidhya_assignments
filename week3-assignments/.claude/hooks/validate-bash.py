#!/usr/bin/env python3
"""
PreToolUse hook: validate-bash.py
Blocks dangerous shell commands before Claude executes them.

Claude Code passes tool input as JSON on stdin. This hook reads it,
checks the command against a blocklist of destructive patterns, and
exits non-zero to block execution if a match is found.

Hook type: PreToolUse
Applies to: Bash tool
"""

import json
import re
import sys
from datetime import datetime, timezone

# ── Blocklist patterns ────────────────────────────────────────────────────────
# Each entry: (pattern, reason_for_blocking)
BLOCKED_PATTERNS = [
    # Filesystem destruction
    (r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f\b",    "rm -rf is permanently destructive"),
    (r"\brm\s+-[a-zA-Z]*f[a-zA-Z]*r\b",    "rm -fr is permanently destructive"),
    (r"\brmdir\s+/",                          "Deleting root-level directories blocked"),

    # Database destruction
    (r"\bDROP\s+TABLE\b",                    "DROP TABLE blocked — use migrations"),
    (r"\bDROP\s+DATABASE\b",                 "DROP DATABASE blocked"),
    (r"\bTRUNCATE\s+TABLE\b",               "TRUNCATE blocked — too destructive in automation"),
    (r"\bDELETE\s+FROM\s+\w+\s*;",         "Unfiltered DELETE blocked (no WHERE clause)"),

    # Git danger operations
    (r"git\s+push\s+.*--force(?!-with-lease)", "git push --force blocked; use --force-with-lease"),
    (r"git\s+push\s+.*-f\b",                "git push -f blocked; use --force-with-lease"),
    (r"git\s+reset\s+--hard\s+HEAD",        "git reset --hard blocked — data loss risk"),
    (r"git\s+clean\s+-[a-zA-Z]*f",         "git clean -f blocked — untracked files loss"),

    # Privilege escalation
    (r"\bsudo\s+rm\b",                       "sudo rm blocked entirely"),
    (r"\bsudo\s+dd\b",                       "sudo dd blocked — disk overwrite risk"),
    (r"\bchmod\s+777\b",                     "chmod 777 blocked — insecure permissions"),
    (r"\bchmod\s+-R\s+777\b",              "chmod -R 777 blocked — insecure permissions"),

    # Network/exfiltration risks
    (r"\bcurl\b.*\|\s*bash\b",               "curl | bash blocked — remote code execution risk"),
    (r"\bwget\b.*\|\s*sh\b",                "wget | sh blocked — remote code execution risk"),

    # Secrets exposure
    (r"\benv\b.*\bpassword\b.*>",            "Redirecting env with passwords blocked"),
    (r"\bprintenv\b.*>\s*\S+",              "printenv redirect blocked — secrets leak risk"),

    # Overwriting critical files
    (r">\s*/etc/passwd",                      "Overwriting /etc/passwd blocked"),
    (r">\s*/etc/shadow",                      "Overwriting /etc/shadow blocked"),
]

# Commands that look scary but are fine in this project context
ALLOWLIST_PATTERNS = [
    r"git\s+push\s+.*--force-with-lease",   # Safe force push
    r"rm\s+-f\s+.*\.pyc",                   # Cleaning compiled Python files is fine
    r"rm\s+-rf\s+.*/__pycache__",           # Cleaning pycache is fine
    r"rm\s+-rf\s+.*\.pytest_cache",         # Cleaning pytest cache is fine
    r"rm\s+-rf\s+.*\.egg-info",             # Cleaning build artifacts is fine
]


def is_allowlisted(command: str) -> bool:
    return any(re.search(p, command, re.IGNORECASE) for p in ALLOWLIST_PATTERNS)


def check_command(command: str) -> tuple[bool, str]:
    """Returns (is_blocked, reason)."""
    if is_allowlisted(command):
        return False, ""
    for pattern, reason in BLOCKED_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True, reason
    return False, ""


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        # If we can't parse the input, fail open (allow) to avoid breaking legitimate use
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {})

    # Only intercept Bash tool calls
    if tool_name != "Bash":
        sys.exit(0)

    command = tool_input.get("command", "")
    is_blocked, reason = check_command(command)

    if is_blocked:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hook": "validate-bash",
            "action": "BLOCKED",
            "command": command[:200],  # truncate for log safety
            "reason": reason,
        }
        # Write to audit log
        try:
            import os
            os.makedirs(".claude/audit", exist_ok=True)
            with open(".claude/audit/blocked-commands.jsonl", "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception:
            pass  # Don't let logging failure prevent the block

        # Claude Code reads stderr as the block message shown to the user
        print(
            f"🚫 BLOCKED by validate-bash.py\n"
            f"Command: {command[:100]}\n"
            f"Reason:  {reason}\n"
            f"If you genuinely need this, run it manually in your terminal.",
            file=sys.stderr,
        )
        sys.exit(1)  # Non-zero exit = block the tool call

    sys.exit(0)  # Zero exit = allow


if __name__ == "__main__":
    main()
