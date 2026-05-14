#!/usr/bin/env bash
# PreToolUse hook: scope-guard.sh
# Enforces that Claude Code only edits files in allowed directories.
# Any attempt to write/edit outside the allowed scope is blocked.
#
# Hook type: PreToolUse
# Applies to: Write, Edit, MultiEdit tools

set -euo pipefail

# ── Allowed directories (relative to repo root) ───────────────────────────────
ALLOWED_DIRS=(
    "src/"
    "tests/"
    "docs/"
    ".claude/"
    "url-shortener/src/"
    "url-shortener/tests/"
    "url-shortener/docs/"
    "url-shortener/.claude/"
)

# ── Files that are always allowed regardless of directory ─────────────────────
ALWAYS_ALLOWED=(
    "CLAUDE.md"
    "README.md"
    "run.py"
    "conftest.py"
)

# ── Directories that are always blocked ───────────────────────────────────────
BLOCKED_DIRS=(
    ".env"
    "migrations/"
    ".git/"
    "node_modules/"
    "__pycache__/"
)

# Read JSON from stdin
INPUT=$(cat)

TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_name',''))" 2>/dev/null || echo "")

# Only intercept file-writing tools
if [[ "$TOOL_NAME" != "Write" && "$TOOL_NAME" != "Edit" && "$TOOL_NAME" != "MultiEdit" ]]; then
    exit 0
fi

# Extract file path
FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
inp = d.get('tool_input', {})
print(inp.get('file_path', inp.get('path', '')))
" 2>/dev/null || echo "")

if [[ -z "$FILE_PATH" ]]; then
    exit 0  # Can't determine path — fail open
fi

# Normalise path (remove leading ./ if present)
FILE_PATH="${FILE_PATH#./}"

# Check always-allowed filenames
for allowed in "${ALWAYS_ALLOWED[@]}"; do
    if [[ "$(basename "$FILE_PATH")" == "$allowed" ]]; then
        exit 0
    fi
done

# Check blocked directories first
for blocked in "${BLOCKED_DIRS[@]}"; do
    if [[ "$FILE_PATH" == "$blocked"* ]]; then
        echo "🚫 BLOCKED by scope-guard.sh" >&2
        echo "File: $FILE_PATH" >&2
        echo "Reason: '$blocked' is a protected path. AI edits are not allowed here." >&2
        echo "If you need to edit this file, do it manually in your terminal." >&2

        # Audit log
        python3 -c "
import json, os
from datetime import datetime, timezone
os.makedirs('.claude/audit', exist_ok=True)
entry = {
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'hook': 'scope-guard',
    'action': 'BLOCKED',
    'file': '$FILE_PATH',
    'reason': 'blocked directory: $blocked',
}
with open('.claude/audit/blocked-commands.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
" 2>/dev/null || true

        exit 1
    fi
done

# Check if path is inside an allowed directory
ALLOWED=false
for dir in "${ALLOWED_DIRS[@]}"; do
    if [[ "$FILE_PATH" == "$dir"* ]]; then
        ALLOWED=true
        break
    fi
done

if [[ "$ALLOWED" == "false" ]]; then
    echo "🚫 BLOCKED by scope-guard.sh" >&2
    echo "File: $FILE_PATH" >&2
    echo "Reason: Outside allowed directories." >&2
    echo "" >&2
    echo "Allowed directories:" >&2
    for dir in "${ALLOWED_DIRS[@]}"; do
        echo "  ✅ $dir" >&2
    done
    echo "" >&2
    echo "To edit this file, either:" >&2
    echo "  1. Add the directory to ALLOWED_DIRS in .claude/hooks/scope-guard.sh" >&2
    echo "  2. Edit the file manually in your terminal" >&2

    # Audit log
    python3 -c "
import json, os
from datetime import datetime, timezone
os.makedirs('.claude/audit', exist_ok=True)
entry = {
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'hook': 'scope-guard',
    'action': 'BLOCKED',
    'file': '$FILE_PATH',
    'reason': 'outside allowed directories',
}
with open('.claude/audit/blocked-commands.jsonl', 'a') as f:
    f.write(json.dumps(entry) + '\n')
" 2>/dev/null || true

    exit 1
fi

exit 0
