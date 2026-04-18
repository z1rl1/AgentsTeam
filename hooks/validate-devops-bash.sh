#!/bin/bash
# ============================================================================
# validate-devops-bash.sh — PreToolUse hook for devops agent
# ============================================================================
# Allows infrastructure commands but blocks dangerous production operations
# without explicit confirmation context.
#
# Exit codes:
#   0 = allow command
#   2 = block command
# ============================================================================

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)

if [ -z "$COMMAND" ]; then
  exit 0
fi

# Block direct production deployments
if echo "$COMMAND" | grep -iE '\b(kubectl\s+delete|docker\s+system\s+prune|docker\s+rm\s+-f|docker\s+stop.*--all)\b' > /dev/null 2>&1; then
  echo "Blocked: Destructive production operations require human approval." >&2
  exit 2
fi

# Block force pushes
if echo "$COMMAND" | grep -iE 'git\s+push\s+.*(-f|--force)' > /dev/null 2>&1; then
  echo "Blocked: Force push is not allowed without human approval." >&2
  exit 2
fi

# Block dropping databases
if echo "$COMMAND" | grep -iE '\b(DROP\s+DATABASE|DROP\s+TABLE|dropdb)\b' > /dev/null 2>&1; then
  echo "Blocked: Database drop operations require human approval." >&2
  exit 2
fi

exit 0
