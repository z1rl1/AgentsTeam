#!/bin/bash
# ============================================================================
# log-test-result.sh — PostToolUse hook for tester agent
# ============================================================================
# After Bash commands, checks if the command was a test run and logs results.
#
# Exit codes:
#   0 = success
# ============================================================================

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)
EXIT_CODE=$(echo "$INPUT" | jq -r '.tool_result.exit_code // .tool_result.exitCode // "unknown"' 2>/dev/null)
STDOUT=$(echo "$INPUT" | jq -r '.tool_result.stdout // .tool_result.output // empty' 2>/dev/null)

if [ -z "$COMMAND" ]; then
  exit 0
fi

# Check if this was a test command
IS_TEST=false
if echo "$COMMAND" | grep -iE '\b(test|jest|vitest|pytest|mocha|cypress|playwright)\b' > /dev/null 2>&1; then
  IS_TEST=true
fi
if echo "$COMMAND" | grep -iE 'npm\s+(run\s+)?test|pnpm\s+(run\s+)?test|yarn\s+test' > /dev/null 2>&1; then
  IS_TEST=true
fi

if [ "$IS_TEST" = "false" ]; then
  exit 0
fi

# Log test execution
HOOKS_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude/hooks"
LOGS_DIR="$HOOKS_DIR/logs"
mkdir -p "$LOGS_DIR"

DATE=$(date -u +"%Y-%m-%d")
LOG_FILE="$LOGS_DIR/test-results-${DATE}.jsonl"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Truncate stdout to avoid huge log entries
STDOUT_SHORT=$(echo "$STDOUT" | tail -20 | head -c 2000)

echo "{\"timestamp\":\"$TIMESTAMP\",\"command\":\"$COMMAND\",\"exit_code\":\"$EXIT_CODE\",\"output_tail\":$(echo "$STDOUT_SHORT" | jq -Rs .)}" >> "$LOG_FILE" 2>/dev/null

if [ "$EXIT_CODE" = "0" ]; then
  echo "Tests PASSED"
else
  echo "Tests FAILED (exit code: $EXIT_CODE) — check output above."
fi

exit 0
