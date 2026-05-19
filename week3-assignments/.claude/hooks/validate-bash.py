#!/usr/bin/env python3
"""
PreToolUse hook: validate-bash.py
Blocks dangerous bash commands before Claude runs them.
"""

import json
import sys
import re

# Patterns we never want to run
BLOCKED_PATTERNS = [
    (r'rm\s+-rf\s+/', "rm -rf on root or absolute path is too risky"),
    (r'rm\s+-rf\s+\*', "rm -rf with wildcard — this would delete everything"),
    (r'rm\s+-rf\s+\.', "rm -rf on current directory — not allowed"),
    (r'DROP\s+TABLE', "SQL DROP TABLE is not allowed"),
    (r'DROP\s+DATABASE', "SQL DROP DATABASE is not allowed"),
    (r'TRUNCATE\s+TABLE', "SQL TRUNCATE is not allowed without explicit approval"),
    (r'git\s+push\s+.*--force', "Force push is blocked — use --force-with-lease and get approval"),
    (r'git\s+push\s+.*-f\b', "Force push (-f) is blocked"),
    (r'git\s+push\s+origin\s+main', "Direct push to main is not allowed — use a PR"),
    (r'git\s+push\s+origin\s+master', "Direct push to master is not allowed — use a PR"),
    (r'chmod\s+777', "chmod 777 is a security risk — be more specific with permissions"),
    (r'curl\s+.*\|\s*sh', "Piping curl into sh is not allowed — review scripts before running"),
    (r'wget\s+.*\|\s*sh', "Piping wget into sh is not allowed"),
    (r':\(\)\{.*\}', "Fork bomb pattern detected"),
    (r'dd\s+if=', "dd command is blocked — can overwrite disks"),
    (r'mkfs\.', "Filesystem formatting command blocked"),
    (r'>\s*/dev/sd', "Writing directly to disk device is blocked"),
]

def check_command(command):
    """Check if a command matches any blocked pattern."""
    for pattern, reason in BLOCKED_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return False, reason
    return True, None

def main():
    # Claude Code passes tool input as JSON on stdin
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        # If we can't parse input, let it through and let Claude handle it
        sys.exit(0)

    # We only care about Bash tool calls
    tool_name = data.get("tool_name", "")
    if tool_name != "Bash":
        sys.exit(0)  # Not a bash call, allow it

    command = data.get("tool_input", {}).get("command", "")
    if not command:
        sys.exit(0)  # No command, allow it

    allowed, reason = check_command(command)

    if not allowed:
        # Exit code 2 tells Claude Code to block the action
        print(json.dumps({
            "decision": "block",
            "reason": f"BLOCKED by validate-bash.py: {reason}\n\nCommand was: {command}"
        }))
        sys.exit(2)
    else:
        # Exit code 0 = allow
        sys.exit(0)

if __name__ == "__main__":
    main()


# --- TEST CASES (run this file directly to test) ---
# python3 validate-bash.py --test
if len(sys.argv) > 1 and sys.argv[1] == "--test":
    test_cases = [
        ("rm -rf /", False),
        ("rm -rf *", False),
        ("git push origin --force", False),
        ("git push origin main", False),
        ("DROP TABLE users;", False),
        ("npm test", True),
        ("git add .", True),
        ("git push origin feature/my-branch", True),
        ("ls -la", True),
        ("cat package.json", True),
    ]
    print("Running test cases...\n")
    all_passed = True
    for cmd, should_allow in test_cases:
        allowed, reason = check_command(cmd)
        status = "PASS" if (allowed == should_allow) else "FAIL"
        if status == "FAIL":
            all_passed = False
        expected = "allow" if should_allow else "block"
        actual = "allow" if allowed else "block"
        print(f"[{status}] '{cmd}'")
        print(f"       expected={expected}, got={actual}")
        if reason:
            print(f"       reason: {reason}")
        print()
    print("All tests passed!" if all_passed else "Some tests FAILED.")
