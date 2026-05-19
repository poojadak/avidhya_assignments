#!/usr/bin/env python3
"""
PreToolUse hook: check-secrets.py
Scans file writes for API keys, passwords, and tokens before saving.
"""

import json
import sys
import re

# Patterns that look like secrets
SECRET_PATTERNS = [
    (r'sk-[a-zA-Z0-9]{32,}', "OpenAI API key"),
    (r'AKIA[0-9A-Z]{16}', "AWS Access Key ID"),
    (r'aws_secret_access_key\s*=\s*["\']?[a-zA-Z0-9/+=]{40}', "AWS Secret Access Key"),
    (r'(?i)password\s*=\s*["\'][^"\']{6,}["\']', "Hardcoded password"),
    (r'(?i)passwd\s*=\s*["\'][^"\']{6,}["\']', "Hardcoded password (passwd)"),
    (r'(?i)secret\s*=\s*["\'][^"\']{8,}["\']', "Hardcoded secret"),
    (r'(?i)api_key\s*=\s*["\'][^"\']{8,}["\']', "Hardcoded API key"),
    (r'(?i)apikey\s*=\s*["\'][^"\']{8,}["\']', "Hardcoded API key"),
    (r'(?i)token\s*=\s*["\'][^"\']{16,}["\']', "Hardcoded token"),
    (r'ghp_[a-zA-Z0-9]{36}', "GitHub personal access token"),
    (r'gho_[a-zA-Z0-9]{36}', "GitHub OAuth token"),
    (r'xoxb-[0-9]+-[a-zA-Z0-9]+', "Slack bot token"),
    (r'xoxp-[0-9]+-[a-zA-Z0-9]+', "Slack user token"),
    (r'mongodb\+srv://[^:]+:[^@]+@', "MongoDB connection string with credentials"),
    (r'postgres://[^:]+:[^@]+@', "PostgreSQL connection string with credentials"),
    (r'mysql://[^:]+:[^@]+@', "MySQL connection string with credentials"),
    (r'-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----', "Private key"),
    (r'(?i)bearer\s+[a-zA-Z0-9._\-]{20,}', "Bearer token"),
]

# These are OK — they're placeholders, not real secrets
SAFE_EXCEPTIONS = [
    r'process\.env\.',
    r'\$\{.*\}',
    r'<your',
    r'YOUR_',
    r'example',
    r'placeholder',
    r'xxxxxxxx',
    r'<token>',
]

def looks_like_placeholder(value):
    for pattern in SAFE_EXCEPTIONS:
        if re.search(pattern, value, re.IGNORECASE):
            return True
    return False

def scan_for_secrets(content):
    """Scan text content for secret patterns. Returns list of (pattern_name, line_number)."""
    found = []
    lines = content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        # Skip comment lines
        if line.strip().startswith('#') or line.strip().startswith('//'):
            continue
        
        for pattern, name in SECRET_PATTERNS:
            match = re.search(pattern, line)
            if match:
                if not looks_like_placeholder(line):
                    found.append((name, line_num, line.strip()[:80]))
    
    return found

def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    
    # Check file write operations
    if tool_name in ("Write", "Edit", "MultiEdit", "str_replace_editor"):
        tool_input = data.get("tool_input", {})
        
        # Get the content being written
        content = tool_input.get("new_content") or tool_input.get("content") or ""
        if not content:
            # For edits, check the new_str
            content = tool_input.get("new_str", "")
        
        filename = tool_input.get("path", "unknown file")
        
        if content:
            secrets = scan_for_secrets(content)
            if secrets:
                issues = "\n".join(
                    f"  Line {line}: {name} — {preview}..."
                    for name, line, preview in secrets
                )
                print(json.dumps({
                    "decision": "block",
                    "reason": (
                        f"BLOCKED by check-secrets.py: Possible secrets found in {filename}\n\n"
                        f"{issues}\n\n"
                        f"Use environment variables (process.env.YOUR_KEY) instead of hardcoding secrets."
                    )
                }))
                sys.exit(2)
    
    sys.exit(0)

if __name__ == "__main__":
    main()
