#!/bin/bash
# ============================================================================
# utils.sh — Shared utilities for skill self-improvement hooks
# ============================================================================
# Provides common functions used across all hook scripts:
#   - Path resolution
#   - JSON helpers
#   - Logging
#   - Skill detection
# ============================================================================

set -euo pipefail

# --- Paths -------------------------------------------------------------------

HOOKS_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude/hooks"
SKILLS_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude/skills"
LOGS_DIR="$HOOKS_DIR/logs"
METRICS_DIR="$HOOKS_DIR/metrics"

# Ensure directories exist
ensure_dirs() {
  mkdir -p "$LOGS_DIR" "$METRICS_DIR"
}

# --- Timestamps --------------------------------------------------------------

timestamp_utc() {
  date -u +"%Y-%m-%dT%H:%M:%SZ"
}

timestamp_date() {
  date +"%Y-%m-%d"
}

# --- JSON helpers ------------------------------------------------------------

# Safely extract a field from JSON on stdin
json_field() {
  local field="$1"
  jq -r "$field // empty" 2>/dev/null || echo ""
}

# Read JSON from stdin and store it
read_stdin_json() {
  cat
}

# --- Skill helpers -----------------------------------------------------------

# Check if a skill has eval/eval.json
skill_has_eval() {
  local skill_name="$1"
  [[ -f "$SKILLS_DIR/$skill_name/eval/eval.json" ]]
}

# Get the eval.json path for a skill
skill_eval_path() {
  local skill_name="$1"
  echo "$SKILLS_DIR/$skill_name/eval/eval.json"
}

# Get the SKILL.md path
skill_md_path() {
  local skill_name="$1"
  echo "$SKILLS_DIR/$skill_name/SKILL.md"
}

# Get latest score for a skill from metrics
skill_latest_score() {
  local skill_name="$1"
  local metrics_file="$METRICS_DIR/${skill_name}.jsonl"
  if [[ -f "$metrics_file" ]]; then
    tail -1 "$metrics_file" | jq -r '.score // 0' 2>/dev/null || echo "0"
  else
    echo "N/A"
  fi
}

# List of meta-skills to skip in hooks
is_meta_skill() {
  local skill_name="$1"
  case "$skill_name" in
    self-improve|generate-eval|skill-health) return 0 ;;
    *) return 1 ;;
  esac
}

# --- Logging -----------------------------------------------------------------

log_info() {
  echo "[$(timestamp_utc)] [INFO] $*" >&2
}

log_warn() {
  echo "[$(timestamp_utc)] [WARN] $*" >&2
}

log_error() {
  echo "[$(timestamp_utc)] [ERROR] $*" >&2
}
