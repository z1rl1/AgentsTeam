#!/bin/bash
# ============================================================================
# eval-engine.sh — Binary Assertion Evaluation Engine
# ============================================================================
# Core engine that evaluates skill output against binary assertions
# from eval.json. Each assertion is checked programmatically where possible
# (word count, pattern matching, structure), or flagged for AI evaluation.
#
# Usage:
#   source lib/eval-engine.sh
#   evaluate_output "$skill_name" "$output_text"
#
# Returns JSON with per-assertion results and aggregate score.
# ============================================================================

# Source utils if not already loaded
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -z "${HOOKS_DIR:-}" ]]; then
  source "$SCRIPT_DIR/utils.sh"
fi

# --- Assertion Checkers ------------------------------------------------------

# Check if text contains a pattern (case-insensitive)
check_contains() {
  local text="$1"
  local pattern="$2"
  echo "$text" | grep -qi "$pattern" && echo "true" || echo "false"
}

# Check if text does NOT contain a pattern
check_not_contains() {
  local text="$1"
  local pattern="$2"
  echo "$text" | grep -qi "$pattern" && echo "false" || echo "true"
}

# Check word count is under N
check_word_count_under() {
  local text="$1"
  local limit="$2"
  local count
  count=$(echo "$text" | wc -w | tr -d ' ')
  [[ "$count" -lt "$limit" ]] && echo "true" || echo "false"
}

# Check word count is over N
check_word_count_over() {
  local text="$1"
  local limit="$2"
  local count
  count=$(echo "$text" | wc -w | tr -d ' ')
  [[ "$count" -gt "$limit" ]] && echo "true" || echo "false"
}

# Check line count
check_line_count_under() {
  local text="$1"
  local limit="$2"
  local count
  count=$(echo "$text" | wc -l | tr -d ' ')
  [[ "$count" -lt "$limit" ]] && echo "true" || echo "false"
}

# Check if text contains markdown heading (## level)
check_has_heading() {
  local text="$1"
  local level="${2:-#}"
  echo "$text" | grep -q "^${level} " && echo "true" || echo "false"
}

# Check if text contains at least N bullet points
check_min_bullets() {
  local text="$1"
  local min="$2"
  local count
  count=$(echo "$text" | grep -c '^\s*[-*•]' || true)
  [[ "$count" -ge "$min" ]] && echo "true" || echo "false"
}

# Check if text contains at least N code blocks
check_min_code_blocks() {
  local text="$1"
  local min="$2"
  local count
  count=$(echo "$text" | grep -c '```' || true)
  local blocks=$((count / 2))
  [[ "$blocks" -ge "$min" ]] && echo "true" || echo "false"
}

# Check if first line is not empty
check_first_line_not_empty() {
  local text="$1"
  local first_line
  first_line=$(echo "$text" | head -1)
  [[ -n "$first_line" ]] && echo "true" || echo "false"
}

# Check if last line is/isn't a question
check_last_line_not_question() {
  local text="$1"
  local last_line
  last_line=$(echo "$text" | tail -1 | tr -d '[:space:]')
  [[ "$last_line" != *"?" ]] && echo "true" || echo "false"
}

# Check if no line exceeds N characters
check_max_line_length() {
  local text="$1"
  local max="$2"
  local longest
  longest=$(echo "$text" | awk '{ print length }' | sort -rn | head -1)
  [[ "$longest" -le "$max" ]] && echo "true" || echo "false"
}

# Check if text contains at least one number/statistic
check_has_number() {
  local text="$1"
  echo "$text" | grep -qE '[0-9]+' && echo "true" || echo "false"
}

# Check if output contains a numbered list
check_has_numbered_list() {
  local text="$1"
  echo "$text" | grep -qE '^\s*[0-9]+[\.\)]' && echo "true" || echo "false"
}

# Check if text contains em-dash
check_no_em_dash() {
  local text="$1"
  echo "$text" | grep -qP '\x{2014}' 2>/dev/null && echo "false" || echo "true"
}

# --- Smart Assertion Router --------------------------------------------------

# Try to evaluate an assertion programmatically.
# Returns "true", "false", or "needs_ai" if can't be determined.
evaluate_assertion() {
  local assertion_text="$1"
  local output_text="$2"
  local lower_assertion
  lower_assertion=$(echo "$assertion_text" | tr '[:upper:]' '[:lower:]')

  # --- Word count checks ---
  if echo "$lower_assertion" | grep -qE '(word count|words).*(under|less than|fewer than|below|maximum|max|не более|менее)'; then
    local limit
    limit=$(echo "$assertion_text" | grep -oE '[0-9]+' | head -1)
    if [[ -n "$limit" ]]; then
      check_word_count_under "$output_text" "$limit"
      return
    fi
  fi

  if echo "$lower_assertion" | grep -qE '(word count|words).*(over|more than|greater than|above|minimum|min|at least|не менее|более)'; then
    local limit
    limit=$(echo "$assertion_text" | grep -oE '[0-9]+' | head -1)
    if [[ -n "$limit" ]]; then
      check_word_count_over "$output_text" "$limit"
      return
    fi
  fi

  # --- Contains / not contains ---
  if echo "$lower_assertion" | grep -qE '^(output )?(does not|doesn.t|must not|should not|не содержит|не должен) contain'; then
    local pattern
    pattern=$(echo "$assertion_text" | sed -E "s/.*contain[s]? //i" | tr -d '"'"'"')
    check_not_contains "$output_text" "$pattern"
    return
  fi

  if echo "$lower_assertion" | grep -qE '^(output )?(contains|includes|has|must contain|should contain|содержит|должен содержать)'; then
    local pattern
    pattern=$(echo "$assertion_text" | sed -E "s/.*(contains|includes|has|contain|содержит) //i" | tr -d '"'"'"')
    check_contains "$output_text" "$pattern"
    return
  fi

  # --- Heading checks ---
  if echo "$lower_assertion" | grep -qE '(heading|заголовок).*##'; then
    check_has_heading "$output_text" "##"
    return
  fi
  if echo "$lower_assertion" | grep -qE '(heading|заголовок).*#'; then
    check_has_heading "$output_text" "#"
    return
  fi

  # --- Bullet points ---
  if echo "$lower_assertion" | grep -qE '(at least|minimum|минимум) [0-9]+ (bullet|пункт)'; then
    local min
    min=$(echo "$assertion_text" | grep -oE '[0-9]+' | head -1)
    check_min_bullets "$output_text" "$min"
    return
  fi

  # --- Code blocks ---
  if echo "$lower_assertion" | grep -qE '(code block|блок кода)'; then
    local min
    min=$(echo "$assertion_text" | grep -oE '[0-9]+' | head -1)
    min=${min:-1}
    check_min_code_blocks "$output_text" "$min"
    return
  fi

  # --- Line length ---
  if echo "$lower_assertion" | grep -qE '(line|строка).*(exceed|длиннее|более).*[0-9]+ (char|символ)'; then
    local max
    max=$(echo "$assertion_text" | grep -oE '[0-9]+' | head -1)
    check_max_line_length "$output_text" "$max"
    return
  fi

  # --- First/last line ---
  if echo "$lower_assertion" | grep -qE '(first line|первая строка).*(not empty|не пуст)'; then
    check_first_line_not_empty "$output_text"
    return
  fi

  if echo "$lower_assertion" | grep -qE '(last|final|последняя).*(line|строка).*(not.*question|не.*вопрос)'; then
    check_last_line_not_question "$output_text"
    return
  fi

  # --- Numbers/statistics ---
  if echo "$lower_assertion" | grep -qE '(number|statistic|цифр|статистик)'; then
    check_has_number "$output_text"
    return
  fi

  # --- Numbered list ---
  if echo "$lower_assertion" | grep -qE '(numbered list|numbered sequentially|нумерованн)'; then
    check_has_numbered_list "$output_text"
    return
  fi

  # --- Em-dash ---
  if echo "$lower_assertion" | grep -qE '(em.?dash|м.?тире|—)'; then
    check_no_em_dash "$output_text"
    return
  fi

  # --- Not empty ---
  if echo "$lower_assertion" | grep -qE '(not empty|non.?empty|не пуст)'; then
    [[ -n "$(echo "$output_text" | tr -d '[:space:]')" ]] && echo "true" || echo "false"
    return
  fi

  # Can't evaluate programmatically
  echo "needs_ai"
}

# --- Main Evaluation Function ------------------------------------------------

# Evaluate all assertions for a skill against output text.
# Prints JSON result to stdout.
#
# Usage: evaluate_output "skill-name" "output text"
evaluate_output() {
  local skill_name="$1"
  local output_text="$2"
  local eval_file
  eval_file=$(skill_eval_path "$skill_name")

  if [[ ! -f "$eval_file" ]]; then
    jq -n '{error: "no eval.json found", skill: $skill}' --arg skill "$skill_name"
    return 1
  fi

  local total_assertions=0
  local passed=0
  local failed=0
  local needs_ai=0
  local results="[]"
  local failed_list="[]"

  # Iterate over tests and assertions
  local num_tests
  num_tests=$(jq '.tests | length' "$eval_file")

  for ((t=0; t<num_tests; t++)); do
    local test_name
    test_name=$(jq -r ".tests[$t].name" "$eval_file")

    local num_assertions
    num_assertions=$(jq ".tests[$t].assertions | length" "$eval_file")

    for ((a=0; a<num_assertions; a++)); do
      local assertion_id assertion_text assertion_category
      assertion_id=$(jq -r ".tests[$t].assertions[$a].id" "$eval_file")
      assertion_text=$(jq -r ".tests[$t].assertions[$a].text" "$eval_file")
      assertion_category=$(jq -r ".tests[$t].assertions[$a].category" "$eval_file")

      local result
      result=$(evaluate_assertion "$assertion_text" "$output_text")

      total_assertions=$((total_assertions + 1))

      case "$result" in
        true)    passed=$((passed + 1)) ;;
        false)
          failed=$((failed + 1))
          failed_list=$(echo "$failed_list" | jq \
            --arg id "$assertion_id" \
            --arg text "$assertion_text" \
            --arg test "$test_name" \
            --arg cat "$assertion_category" \
            '. + [{id: $id, text: $text, test: $test, category: $cat}]')
          ;;
        needs_ai)
          needs_ai=$((needs_ai + 1))
          ;;
      esac

      results=$(echo "$results" | jq \
        --arg id "$assertion_id" \
        --arg text "$assertion_text" \
        --arg result "$result" \
        --arg test "$test_name" \
        '. + [{id: $id, assertion: $text, result: $result, test: $test}]')
    done
  done

  # Calculate score (excluding needs_ai from denominator)
  local evaluable=$((total_assertions - needs_ai))
  local score=0
  if [[ "$evaluable" -gt 0 ]]; then
    score=$((passed * 100 / evaluable))
  fi

  # Build final result
  jq -n \
    --arg skill "$skill_name" \
    --arg timestamp "$(timestamp_utc)" \
    --argjson total "$total_assertions" \
    --argjson passed "$passed" \
    --argjson failed "$failed" \
    --argjson needs_ai "$needs_ai" \
    --argjson score "$score" \
    --argjson results "$results" \
    --argjson failed_list "$failed_list" \
    '{
      skill: $skill,
      timestamp: $timestamp,
      score: $score,
      total_assertions: $total,
      passed: $passed,
      failed: $failed,
      needs_ai_evaluation: $needs_ai,
      results: $results,
      failed_assertions: $failed_list
    }'
}
