#!/usr/bin/env python3
"""
PreToolUse hook: check-secrets.py
Scans file content being written by Claude for leaked credentials,
API keys, tokens, and passwords before the write is executed.

Hook type: PreToolUse
Applies to: Write, Edit, MultiEdit tools
"""

import json
import re
import sys
from datetime import datetime, timezone

# ── Secret patterns ───────────────────────────────────────────────────────────
# Format: (name, regex_pattern)
SECRET_PATTERNS = [
    # Generic high-entropy strings that look like keys/tokens
    ("AWS Access Key",        r"AKIA[0-9A-Z]{16}"),
    ("AWS Secret Key",        r"(?i)aws[_\-\s]?secret[_\-\s]?(?:access[_\-\s]?)?key['\"]?\s*[:=]\s*['\"]?[A-Za-z0-9/+=]{40}"),
    ("GitHub Token",          r"ghp_[A-Za-z0-9]{36}"),
    ("GitHub OAuth Token",    r"gho_[A-Za-z0-9]{36}"),
    ("Slack Token",           r"xox[baprs]-[0-9A-Za-z\-]{10,48}"),
    ("Stripe Live Key",       r"sk_live_[0-9a-zA-Z]{24,}"),
    ("Stripe Test Key",       r"sk_test_[0-9a-zA-Z]{24,}"),
    ("SendGrid API Key",      r"SG\.[A-Za-z0-9_\-]{22}\.[A-Za-z0-9_\-]{43}"),
    ("Twilio Account SID",    r"AC[a-zA-Z0-9]{32}"),
    ("Heroku API Key",        r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"),
    ("Private Key Header",    r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"),
    ("JWT Token",             r"eyJ[A-Za-z0-9_\-]+\.eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+"),

    # Hardcoded password assignments
    ("Hardcoded Password",    r"""(?i)password\s*=\s*['"][^'"]{4,}['"]"""),
    ("Hardcoded Secret Key",  r"""(?i)secret[_\-]?key\s*=\s*['"][^'"]{6,}['"]"""),
    ("Hardcoded DB Password", r"""(?i)db[_\-]?pass(?:word)?\s*=\s*['"][^'"]{4,}['"]"""),
    ("Hardcoded API Key",     r"""(?i)api[_\-]?key\s*=\s*['"][^'"]{8,}['"]"""),
]

# Safe patterns that look like secrets but aren't
SAFE_EXCEPTIONS = [
    r"change-me-in-production",   # Explicit placeholder in config
    r"your[_\-]?api[_\-]?key",    # Placeholder text
    r"<your[_\-]?\w+>",           # Template placeholders
    r"example\.com",               # Example values
    r"test[_\-]?password",        # Obvious test values
    r"\${[A-Z_]+}",               # Environment variable references  ${VAR}
    r"os\.environ",                # os.environ lookups (fine — reading from env)
    r"os\.getenv",                 # os.getenv() calls (fine)
    r"dotenv",                     # dotenv loading code
]

# File types to skip entirely (binary, compiled, etc.)
SKIP_EXTENSIONS = {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".pdf",
                   ".zip", ".tar", ".gz", ".whl", ".egg"}


def is_safe_exception(matched_text: str) -> bool:
    return any(re.search(p, matched_text, re.IGNORECASE) for p in SAFE_EXCEPTIONS)


def scan_content(content: str, filepath: str) -> list[dict]:
    """Returns list of findings: [{name, pattern_matched, line_number, excerpt}]"""
    # Skip binary/compiled files
    ext = "." + filepath.rsplit(".", 1)[-1] if "." in filepath else ""
    if ext.lower() in SKIP_EXTENSIONS:
        return []

    # Skip .env files themselves (they're allowed to contain real values — just not committed)
    # But DO scan if it's being written to a non-.env path
    findings = []
    lines = content.splitlines()

    for line_num, line in enumerate(lines, start=1):
        # Skip comment lines
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("//"):
            continue

        for name, pattern in SECRET_PATTERNS:
            match = re.search(pattern, line)
            if match:
                matched_text = match.group(0)
                if not is_safe_exception(line):
                    findings.append({
                        "name": name,
                        "line": line_num,
                        "excerpt": line.strip()[:80],  # truncated for safety
                        "matched": matched_text[:30] + "..." if len(matched_text) > 30 else matched_text,
                    })
                    break  # one finding per line is enough

    return findings


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {})

    # Only intercept file-writing tools
    if tool_name not in ("Write", "Edit", "MultiEdit"):
        sys.exit(0)

    # Extract content depending on tool type
    filepath = tool_input.get("file_path", tool_input.get("path", "unknown"))
    if tool_name == "Write":
        content = tool_input.get("content", "")
    elif tool_name == "Edit":
        content = tool_input.get("new_content", tool_input.get("new_string", ""))
    elif tool_name == "MultiEdit":
        # Combine all edits
        content = " ".join(
            e.get("new_string", "") for e in tool_input.get("edits", [])
        )
    else:
        content = ""

    findings = scan_content(content, filepath)

    if findings:
        report_lines = [
            f"🔐 SECRET DETECTED by check-secrets.py — write BLOCKED",
            f"File: {filepath}",
            "",
        ]
        for f in findings:
            report_lines.append(
                f"  Line {f['line']}: [{f['name']}] — {f['excerpt']}"
            )
        report_lines += [
            "",
            "Fix: Use environment variables instead.",
            "  1. Add the value to your .env file",
            "  2. Load it with: os.getenv('MY_VAR')",
            "  3. Never commit .env to git",
        ]

        # Audit log the detection
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hook": "check-secrets",
            "action": "BLOCKED",
            "file": filepath,
            "findings": [{"name": f["name"], "line": f["line"]} for f in findings],
        }
        try:
            import os
            os.makedirs(".claude/audit", exist_ok=True)
            with open(".claude/audit/blocked-commands.jsonl", "a") as log:
                log.write(json.dumps(log_entry) + "\n")
        except Exception:
            pass

        print("\n".join(report_lines), file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
