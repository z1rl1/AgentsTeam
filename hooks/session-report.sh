#!/bin/bash
# ============================================================================
# session-report.sh — Stop Hook (Session End)
# ============================================================================
# Fires when Claude finishes responding (Stop event). Generates a session
# summary of skill health metrics:
#   - Skills used in this session
#   - Quality scores from evaluations
#   - Trends and improvement suggestions
#   - Overall system health
#
# Hook event: Stop
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/utils.sh"
source "$SCRIPT_DIR/lib/metrics.sh"

ensure_dirs

# Read hook input from stdin
INPUT=$(read_stdin_json)
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "unknown"')

# Check if any skills were used today (check execution log)
TODAY=$(timestamp_date)
EXEC_LOG="$LOGS_DIR/skill-executions-${TODAY}.jsonl"
EVAL_LOG="$LOGS_DIR/eval-results-${TODAY}.jsonl"

# Count today's skill executions
SKILLS_USED=0
EVALS_RUN=0

if [[ -f "$EXEC_LOG" ]]; then
  SKILLS_USED=$(wc -l < "$EXEC_LOG" | tr -d ' ')
fi

if [[ -f "$EVAL_LOG" ]]; then
  EVALS_RUN=$(wc -l < "$EVAL_LOG" | tr -d ' ')
fi

# Skip report if no skills were used
if [[ "$SKILLS_USED" -eq 0 ]]; then
  exit 0
fi

# Count skills with evals
SKILLS_WITH_EVAL=0
SKILLS_WITHOUT_EVAL=0
SKILLS_BELOW_THRESHOLD=0
THRESHOLD=80

for skill_dir in "$SKILLS_DIR"/*/; do
  [[ -d "$skill_dir" ]] || continue
  skill_name=$(basename "$skill_dir")
  is_meta_skill "$skill_name" && continue

  if skill_has_eval "$skill_name"; then
    SKILLS_WITH_EVAL=$((SKILLS_WITH_EVAL + 1))
    local_score=$(get_latest_score "$skill_name")
    if [[ "$local_score" != "N/A" ]] && [[ "$local_score" -lt "$THRESHOLD" ]]; then
      SKILLS_BELOW_THRESHOLD=$((SKILLS_BELOW_THRESHOLD + 1))
    fi
  else
    SKILLS_WITHOUT_EVAL=$((SKILLS_WITHOUT_EVAL + 1))
  fi
done

# Generate session report file
REPORT_FILE="$LOGS_DIR/session-report-${TODAY}-${SESSION_ID:0:8}.md"

{
  echo "# Session Skill Health Report"
  echo ""
  echo "**Date**: $TODAY"
  echo "**Session**: ${SESSION_ID:0:8}"
  echo ""
  echo "## Session Activity"
  echo ""
  echo "| Metric | Value |"
  echo "|--------|-------|"
  echo "| Skills executed | $SKILLS_USED |"
  echo "| Evaluations run | $EVALS_RUN |"
  echo "| Skills with eval | $SKILLS_WITH_EVAL |"
  echo "| Skills without eval | $SKILLS_WITHOUT_EVAL |"
  echo "| Skills below ${THRESHOLD}% | $SKILLS_BELOW_THRESHOLD |"
  echo ""

  # Per-skill breakdown
  if [[ -f "$EVAL_LOG" ]]; then
    echo "## Evaluation Results"
    echo ""
    echo "| Skill | Score | Passed | Failed | Trend |"
    echo "|-------|-------|--------|--------|-------|"

    # Get unique skills evaluated today
    jq -r '.skill' "$EVAL_LOG" 2>/dev/null | sort -u | while read -r skill; do
      latest=$(get_latest_score "$skill")
      best=$(get_best_score "$skill")
      trend=$(get_trend_direction "$skill")

      # Get today's latest eval for this skill
      local_passed=$(jq -r "select(.skill == \"$skill\") | .passed" "$EVAL_LOG" | tail -1)
      local_failed=$(jq -r "select(.skill == \"$skill\") | .failed" "$EVAL_LOG" | tail -1)

      trend_icon="--"
      case "$trend" in
        improving) trend_icon="^" ;;
        declining) trend_icon="v" ;;
        stable)    trend_icon="=" ;;
      esac

      echo "| $skill | ${latest}% | $local_passed | $local_failed | $trend_icon |"
    done

    echo ""
  fi

  # Recommendations
  echo "## Recommendations"
  echo ""

  if [[ "$SKILLS_WITHOUT_EVAL" -gt 0 ]]; then
    echo "- **${SKILLS_WITHOUT_EVAL} skills** lack eval.json — run \`/generate-eval [skill]\` to enable quality tracking"
  fi

  if [[ "$SKILLS_BELOW_THRESHOLD" -gt 0 ]]; then
    echo "- **${SKILLS_BELOW_THRESHOLD} skills** below ${THRESHOLD}% — run \`/self-improve [skill]\` to improve"
  fi

  if [[ "$SKILLS_WITHOUT_EVAL" -eq 0 ]] && [[ "$SKILLS_BELOW_THRESHOLD" -eq 0 ]]; then
    echo "- All tracked skills are healthy!"
  fi

} > "$REPORT_FILE"

# Return summary to Claude
jq -n \
  --argjson skills_used "$SKILLS_USED" \
  --argjson evals_run "$EVALS_RUN" \
  --argjson with_eval "$SKILLS_WITH_EVAL" \
  --argjson without_eval "$SKILLS_WITHOUT_EVAL" \
  --argjson below_threshold "$SKILLS_BELOW_THRESHOLD" \
  --arg report_path "$REPORT_FILE" \
  '{
    hookSpecificOutput: {
      session_skill_health: {
        skills_used_today: $skills_used,
        evaluations_run: $evals_run,
        skills_with_eval: $with_eval,
        skills_without_eval: $without_eval,
        skills_below_threshold: $below_threshold,
        report: $report_path
      }
    }
  }'

exit 0
