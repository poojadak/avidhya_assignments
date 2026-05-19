#!/bin/bash
# PreToolUse hook: scope-guard.sh
# Only allows file edits inside approved directories.
# Blocks accidental writes to config files, system files, etc.

# Directories where Claude is allowed to make changes
ALLOWED_DIRS=(
    "src/"
    "tests/"
    "docs/"
    ".claude/"
    "scripts/"
)

# Read the JSON input from stdin
INPUT=$(cat)

# Get the tool name
TOOL_NAME=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_name',''))" 2>/dev/null)

# Only check file-writing tools
if [[ "$TOOL_NAME" != "Write" && "$TOOL_NAME" != "Edit" && "$TOOL_NAME" != "MultiEdit" && "$TOOL_NAME" != "str_replace_editor" ]]; then
    exit 0  # Not a write tool, allow it
fi

# Get the file path being written
FILE_PATH=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('path',''))" 2>/dev/null)

if [[ -z "$FILE_PATH" ]]; then
    exit 0  # No path, let it through
fi

# Check if the path starts with any allowed directory
ALLOWED=false
for dir in "${ALLOWED_DIRS[@]}"; do
    if [[ "$FILE_PATH" == "$dir"* || "$FILE_PATH" == "./$dir"* ]]; then
        ALLOWED=true
        break
    fi
done

# Also allow edits to root-level markdown and config files we explicitly manage
ROOT_ALLOWED_FILES=("CLAUDE.md" "README.md" "package.json" ".env.example" ".gitignore" "REPORT.md")
for f in "${ROOT_ALLOWED_FILES[@]}"; do
    if [[ "$FILE_PATH" == "$f" || "$FILE_PATH" == "./$f" ]]; then
        ALLOWED=true
        break
    fi
done

if [[ "$ALLOWED" == false ]]; then
    python3 -c "
import json
print(json.dumps({
    'decision': 'block',
    'reason': 'BLOCKED by scope-guard.sh: File path \"$FILE_PATH\" is outside allowed directories.\n\nAllowed: src/, tests/, docs/, .claude/, scripts/, and root markdown files.\n\nIf you need to edit something outside these folders, do it manually.'
}))
"
    exit 2
fi

exit 0
