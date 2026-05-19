#!/bin/bash
# PostToolUse hook: audit-log.sh
# Logs every tool action Claude takes to .claude/audit/audit.jsonl

LOG_FILE=".claude/audit/audit.jsonl"
PROMPT_LOG=".claude/audit/prompts.jsonl"

# Make sure the audit directory exists
mkdir -p .claude/audit

# Read the full tool result from stdin
INPUT=$(cat)

# Extract fields using python (more reliable than bash JSON parsing)
python3 << EOF
import json
import sys
from datetime import datetime, timezone

input_data = '''$INPUT'''

try:
    data = json.loads(input_data)
except:
    # If we can't parse, log a raw entry
    data = {}

tool_name   = data.get("tool_name", "unknown")
tool_input  = data.get("tool_input", {})
tool_result = data.get("tool_result", {})
hook_event  = data.get("hook_event_name", "PostToolUse")

# Build a clean audit entry
entry = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "event": hook_event,
    "tool": tool_name,
    "input_summary": {},
    "result_summary": {},
    "session_id": data.get("session_id", "unknown"),
}

# Summarise input based on tool type
if tool_name == "Bash":
    entry["input_summary"]["command"] = tool_input.get("command", "")[:200]
elif tool_name in ("Write", "Edit", "str_replace_editor"):
    entry["input_summary"]["path"] = tool_input.get("path", "")
    entry["input_summary"]["operation"] = tool_name
elif tool_name == "Read":
    entry["input_summary"]["path"] = tool_input.get("path", "")
else:
    entry["input_summary"] = str(tool_input)[:200]

# Summarise result
if isinstance(tool_result, dict):
    entry["result_summary"]["exit_code"] = tool_result.get("exit_code")
    output = str(tool_result.get("output", ""))
    entry["result_summary"]["output_preview"] = output[:300]
else:
    entry["result_summary"]["raw"] = str(tool_result)[:300]

# Write to audit log
with open("$LOG_FILE", "a") as f:
    f.write(json.dumps(entry) + "\n")

EOF

exit 0
