#!/bin/bash
# ============================================================================
# log-skill-result.sh — PostToolUse Logging Hook for Skill
# ============================================================================
# Fires AFTER every skill execution. Logs execution metadata:
#   - Skill name and arguments
#   - Timestamp and session ID
#   - Response size
#   - Execution context
#
# Logs are stored in JSONL format, one file per day.
# Meta-skills (self-improve, generate-eval, skill-health) are excluded.
#
# Hook event: PostToolUse
# Matcher: Skill
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/utils.sh"

ensure_dirs

# Read hook input from stdin
INPUT=$(read_stdin_json)

# Extract fields
SKILL_NAME=$(echo "$INPUT" | jq -r '.tool_input.skill // "unknown"')
SKILL_ARGS=$(echo "$INPUT" | jq -r '.tool_input.args // ""')
TOOL_RESPONSE=$(echo "$INPUT" | jq -r '.tool_response // ""')
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "unknown"')
CWD=$(echo "$INPUT" | jq -r '.cwd // "unknown"')

# Skip meta-skills
if is_meta_skill "$SKILL_NAME"; then
  exit 0
fi

# Calculate response metrics
RESPONSE_LENGTH=$(echo -n "$TOOL_RESPONSE" | wc -c | tr -d ' ')
RESPONSE_LINES=$(echo "$TOOL_RESPONSE" | wc -l | tr -d ' ')
RESPONSE_WORDS=$(echo "$TOOL_RESPONSE" | wc -w | tr -d ' ')

# Log file — one per day
LOG_FILE="$LOGS_DIR/skill-executions-$(timestamp_date).jsonl"

# Append log entry
jq -n \
  --arg timestamp "$(timestamp_utc)" \
  --arg session_id "$SESSION_ID" \
  --arg skill "$SKILL_NAME" \
  --arg args "$SKILL_ARGS" \
  --arg cwd "$CWD" \
  --argjson response_bytes "$RESPONSE_LENGTH" \
  --argjson response_lines "$RESPONSE_LINES" \
  --argjson response_words "$RESPONSE_WORDS" \
  '{
    timestamp: $timestamp,
    session_id: $session_id,
    event: "skill_execution",
    skill: $skill,
    args: $args,
    cwd: $cwd,
    response: {
      bytes: $response_bytes,
      lines: $response_lines,
      words: $response_words
    }
  }' >> "$LOG_FILE"

exit 0
