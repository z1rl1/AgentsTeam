#!/bin/bash
# ============================================================================
# post-edit-validate.sh — PostToolUse hook for implementer agent
# ============================================================================
# After file edits, logs the change and reminds to run validation.
# Lightweight check — does not run full validation (that's the agent's job).
#
# Exit codes:
#   0 = success (message passed back as info)
# ============================================================================

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.filePath // empty' 2>/dev/null)

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Extract filename for logging
FILENAME=$(basename "$FILE_PATH" 2>/dev/null || echo "$FILE_PATH")

# Log the edit
HOOKS_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude/hooks"
LOGS_DIR="$HOOKS_DIR/logs"
mkdir -p "$LOGS_DIR"

DATE=$(date -u +"%Y-%m-%d")
LOG_FILE="$LOGS_DIR/agent-edits-${DATE}.jsonl"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "{\"timestamp\":\"$TIMESTAMP\",\"tool\":\"$TOOL_NAME\",\"file\":\"$FILE_PATH\"}" >> "$LOG_FILE" 2>/dev/null

echo "Edited: $FILENAME — remember to run validation before committing."

exit 0
