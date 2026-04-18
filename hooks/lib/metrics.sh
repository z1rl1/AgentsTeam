#!/bin/bash
# ============================================================================
# metrics.sh — Skill Quality Metrics Tracker
# ============================================================================
# Tracks skill improvement scores over time. Stores per-skill JSONL files
# with timestamped score entries. Provides aggregation and trend functions.
#
# Usage:
#   source lib/metrics.sh
#   record_score "skill-name" 85 24 20 4 0
#   get_trend "skill-name"
#   get_all_skills_summary
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -z "${HOOKS_DIR:-}" ]]; then
  source "$SCRIPT_DIR/utils.sh"
fi

ensure_dirs

# --- Record a Score ----------------------------------------------------------

# Record a score entry for a skill
# Args: skill_name score total passed failed needs_ai [iteration] [source]
record_score() {
  local skill_name="$1"
  local score="$2"
  local total="${3:-0}"
  local passed="${4:-0}"
  local failed="${5:-0}"
  local needs_ai="${6:-0}"
  local iteration="${7:-0}"
  local source="${8:-hook}"  # hook | self-improve | manual

  local metrics_file="$METRICS_DIR/${skill_name}.jsonl"

  jq -n \
    --arg timestamp "$(timestamp_utc)" \
    --arg skill "$skill_name" \
    --argjson score "$score" \
    --argjson total "$total" \
    --argjson passed "$passed" \
    --argjson failed "$failed" \
    --argjson needs_ai "$needs_ai" \
    --argjson iteration "$iteration" \
    --arg source "$source" \
    '{
      timestamp: $timestamp,
      skill: $skill,
      score: $score,
      total_assertions: $total,
      passed: $passed,
      failed: $failed,
      needs_ai: $needs_ai,
      iteration: $iteration,
      source: $source
    }' >> "$metrics_file"
}

# --- Query Scores ------------------------------------------------------------

# Get the latest score for a skill
get_latest_score() {
  local skill_name="$1"
  local metrics_file="$METRICS_DIR/${skill_name}.jsonl"
  if [[ -f "$metrics_file" ]]; then
    tail -1 "$metrics_file" | jq -r '.score' 2>/dev/null || echo "N/A"
  else
    echo "N/A"
  fi
}

# Get the best score ever for a skill
get_best_score() {
  local skill_name="$1"
  local metrics_file="$METRICS_DIR/${skill_name}.jsonl"
  if [[ -f "$metrics_file" ]]; then
    jq -s 'map(.score) | max' "$metrics_file" 2>/dev/null || echo "0"
  else
    echo "N/A"
  fi
}

# Get number of evaluations for a skill
get_eval_count() {
  local skill_name="$1"
  local metrics_file="$METRICS_DIR/${skill_name}.jsonl"
  if [[ -f "$metrics_file" ]]; then
    wc -l < "$metrics_file" | tr -d ' '
  else
    echo "0"
  fi
}

# Get score trend (last 5 scores)
get_trend() {
  local skill_name="$1"
  local metrics_file="$METRICS_DIR/${skill_name}.jsonl"
  if [[ -f "$metrics_file" ]]; then
    tail -5 "$metrics_file" | jq -s 'map(.score)'
  else
    echo "[]"
  fi
}

# Get trend direction: improving, declining, stable, or unknown
get_trend_direction() {
  local skill_name="$1"
  local metrics_file="$METRICS_DIR/${skill_name}.jsonl"

  if [[ ! -f "$metrics_file" ]] || [[ $(wc -l < "$metrics_file") -lt 2 ]]; then
    echo "unknown"
    return
  fi

  local last_two
  last_two=$(tail -2 "$metrics_file" | jq -s 'map(.score)')
  local prev curr
  prev=$(echo "$last_two" | jq '.[0]')
  curr=$(echo "$last_two" | jq '.[1]')

  if [[ "$curr" -gt "$prev" ]]; then
    echo "improving"
  elif [[ "$curr" -lt "$prev" ]]; then
    echo "declining"
  else
    echo "stable"
  fi
}

# --- Aggregation -------------------------------------------------------------

# Get summary of all skills with evals
get_all_skills_summary() {
  local summary="[]"

  for metrics_file in "$METRICS_DIR"/*.jsonl; do
    [[ -f "$metrics_file" ]] || continue
    local skill_name
    skill_name=$(basename "$metrics_file" .jsonl)
    local latest_score best_score eval_count trend_dir
    latest_score=$(get_latest_score "$skill_name")
    best_score=$(get_best_score "$skill_name")
    eval_count=$(get_eval_count "$skill_name")
    trend_dir=$(get_trend_direction "$skill_name")
    local trend
    trend=$(get_trend "$skill_name")

    summary=$(echo "$summary" | jq \
      --arg skill "$skill_name" \
      --argjson latest "$latest_score" \
      --argjson best "$best_score" \
      --argjson count "$eval_count" \
      --arg direction "$trend_dir" \
      --argjson trend "$trend" \
      '. + [{
        skill: $skill,
        latest_score: $latest,
        best_score: $best,
        evaluations: $count,
        trend_direction: $direction,
        recent_scores: $trend
      }]')
  done

  echo "$summary" | jq 'sort_by(.latest_score)'
}

# --- Improvement Delta -------------------------------------------------------

# Calculate improvement since first evaluation
get_improvement_delta() {
  local skill_name="$1"
  local metrics_file="$METRICS_DIR/${skill_name}.jsonl"
  if [[ -f "$metrics_file" ]] && [[ $(wc -l < "$metrics_file") -ge 2 ]]; then
    local first last
    first=$(head -1 "$metrics_file" | jq '.score')
    last=$(tail -1 "$metrics_file" | jq '.score')
    echo $((last - first))
  else
    echo "0"
  fi
}
