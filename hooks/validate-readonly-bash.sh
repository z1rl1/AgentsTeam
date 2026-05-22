#!/bin/bash
# ============================================================================
# validate-readonly-bash.sh — PreToolUse hook for read-only agents
# ============================================================================
# Blocks destructive bash commands for agents that should only read/analyze.
# Used by: code-reviewer, security-reviewer, debugger, performance-analyst
#
# Exit codes:
#   0 = allow command
#   2 = block command (feeds error message back to agent)
# ============================================================================

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)

if [ -z "$COMMAND" ]; then
  exit 0
fi

# Block destructive file operations
if echo "$COMMAND" | grep -iE '\b(rm|rmdir|mv|cp|chmod|chown|truncate|shred)\b' > /dev/null 2>&1; then
  echo "Blocked: Destructive file operations are not allowed for read-only agents." >&2
  exit 2
fi

# Block git write operations
if echo "$COMMAND" | grep -iE '\bgit\s+(push|commit|merge|rebase|reset|checkout\s+--|restore|clean|branch\s+-[dD]|tag\s+-d|stash\s+drop)' > /dev/null 2>&1; then
  echo "Blocked: Git write operations are not allowed for read-only agents." >&2
  exit 2
fi

# Block package manager installs
if echo "$COMMAND" | grep -iE '\b(npm\s+install|npm\s+uninstall|pnpm\s+add|pnpm\s+remove|yarn\s+add|yarn\s+remove|pip\s+install|pip\s+uninstall)\b' > /dev/null 2>&1; then
  echo "Blocked: Package manager write operations are not allowed for read-only agents." >&2
  exit 2
fi

# Block file creation/write redirects
if echo "$COMMAND" | grep -E '>\s*[^&]|>>' > /dev/null 2>&1; then
  echo "Blocked: File write redirects are not allowed for read-only agents." >&2
  exit 2
fi

exit 0
