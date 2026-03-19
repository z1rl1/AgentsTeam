---
name: skill-health
description: Dashboard showing quality health of all skills. Displays eval scores, trends, improvement history, and recommendations. Uses data from hooks metrics.
disable-model-invocation: false
context: fork
---

# Skill Health Dashboard

Display a comprehensive health report for all skills in the project.

## Data Sources

Read metrics from these locations:
- **Metrics**: `.claude/hooks/metrics/[skill-name].jsonl` — score history per skill
- **Eval logs**: `.claude/hooks/logs/eval-results-*.jsonl` — recent evaluation results
- **Execution logs**: `.claude/hooks/logs/skill-executions-*.jsonl` — usage stats
- **Session reports**: `.claude/hooks/logs/session-report-*.md` — past session summaries
- **Eval configs**: `.claude/skills/[skill]/eval/eval.json` — assertion definitions

## Step 1: Inventory All Skills

List every skill in `.claude/skills/` and classify:

| Status | Meaning |
|--------|---------|
| **Tracked** | Has eval.json AND metrics history |
| **Eval only** | Has eval.json but no metrics yet (never tested) |
| **Untracked** | No eval.json — quality not measured |

## Step 2: Score Dashboard

For each **tracked** skill, display:

```
╔══════════════════════════════════════════════════════════════╗
║                   SKILL HEALTH DASHBOARD                     ║
╠══════════════════════════════════════════════════════════════╣
║ Skill           │ Score │ Best │ Evals │ Trend │ Delta      ║
║─────────────────┼───────┼──────┼───────┼───────┼────────────║
║ review-code     │  92%  │ 95%  │   12  │  ↑    │ +15%       ║
║ commit          │ 100%  │ 100% │    8  │  =    │  +0%       ║
║ plan            │  78%  │ 85%  │    5  │  ↓    │  -7%       ║
║ validate        │  N/A  │ N/A  │    0  │  --   │  N/A       ║
╚══════════════════════════════════════════════════════════════╝
```

Where:
- **Score**: Latest eval score (% of passed binary assertions)
- **Best**: Highest score ever achieved
- **Evals**: Total number of evaluations recorded
- **Trend**: ↑ improving, ↓ declining, = stable, -- unknown
- **Delta**: Improvement since first evaluation

## Step 3: Detailed Breakdowns

For each tracked skill with failures, show:

```
### [skill-name] — 92% (23/25 assertions)

Failed assertions:
  ✗ [T2_A3] "Output must not end with a question" (forbidden)
  ✗ [T4_A1] "First line is standalone sentence" (structure)

Recent history: 85% → 88% → 90% → 92%
Last improved: 2026-03-18 (iteration 4 of self-improve)
```

## Step 4: Usage Statistics

From execution logs, show:

```
## Usage Stats (last 7 days)

| Skill         | Executions | Avg Score | Most Common Failure     |
|---------------|-----------|-----------|-------------------------|
| commit        |    23     |   100%    | —                       |
| review-code   |    15     |    91%    | Missing code blocks     |
| plan          |     8     |    82%    | Word count exceeded     |
```

## Step 5: Recommendations

Generate actionable recommendations:

1. **Critical** (score < 70%): "Run `/self-improve [skill]` immediately"
2. **Warning** (score 70-89%): "Schedule improvement with `/self-improve [skill]`"
3. **Untracked**: "Run `/generate-eval [skill]` to enable quality tracking"
4. **Declining trend**: "Investigate recent changes to [skill]"
5. **Perfect score**: "Consider adding more assertions to challenge the skill"

## Step 6: System Health Summary

```
## System Health

Total skills: 35
├── Tracked:    12 (34%)
├── Eval only:   3 (9%)
└── Untracked:  20 (57%)

Average score: 88%
Perfect scores: 4 skills
Below threshold: 2 skills
Improvement loop runs: 7 total

Suggestion: Generate evals for the 20 untracked skills to improve system coverage.
```

## Output Format

Present everything in clean markdown with the table/box formatting above.
If metrics directory is empty, state that no evaluations have been run yet
and suggest running `/generate-eval` on key skills first.
