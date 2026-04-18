---
name: self-improve
description: Run an autonomous self-improvement loop on a skill. Uses binary assertions from eval.json to test skill output, then iteratively improves skill.md until all assertions pass or max iterations reached. Based on Karpathy's auto-research pattern. Integrates with hooks for metrics tracking.
argument-hint: [skill-name] [--max-iterations N] [--target-score N]
disable-model-invocation: false
context: fork
---

# Self-Improve Skill (Karpathy Auto-Research Loop)

Run an autonomous improvement loop on a target skill using binary assertions.
This is the core engine of the skill self-improvement system.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SELF-IMPROVEMENT LOOP                      │
│                                                               │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│  │  Read     │───>│  Run     │───>│ Evaluate │               │
│  │ skill.md  │    │  Tests   │    │ Assertions│              │
│  └──────────┘    └──────────┘    └─────┬─────┘               │
│                                        │                      │
│                            ┌───────────┴───────────┐         │
│                            │    Score improved?     │         │
│                            └───────────┬───────────┘         │
│                                   ╱         ╲                 │
│                              YES ╱           ╲ NO             │
│                                ╱               ╲              │
│                    ┌──────────┐          ┌──────────┐        │
│                    │  Commit  │          │  Revert  │        │
│                    │  Change  │          │  Change  │        │
│                    └────┬─────┘          └────┬─────┘        │
│                         │                     │               │
│                         └──────────┬──────────┘               │
│                                    │                          │
│                         ┌──────────┴──────────┐              │
│                         │   Make ONE change    │              │
│                         │   to skill.md        │              │
│                         └──────────┬──────────┘              │
│                                    │                          │
│                              ┌─────┴─────┐                   │
│                              │   Loop    │                    │
│                              └───────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

## Integration with Hooks System

This skill works with the hooks infrastructure:

- **Reads from**: `.claude/hooks/metrics/[skill].jsonl` — previous scores
- **Writes to**: `.claude/hooks/metrics/[skill].jsonl` — new scores per iteration
- **Uses**: `.claude/skills/[skill]/eval/eval.json` — binary assertions
- **Generates**: `.claude/skills/[skill]/eval/improvement-log.json` — detailed log
- **Generates**: `.claude/skills/[skill]/eval/improvement-report.md` — final report

The PostToolUse hook (`post-skill-eval.sh`) also evaluates skills during normal
usage, so metrics accumulate passively even without running this loop.

## Arguments

Parse `$ARGUMENTS`:
- First argument: **skill name** (required) — e.g. `review-code`, `commit`, `plan`
- `--max-iterations N`: maximum loop iterations (default: 10)
- `--target-score N`: target pass rate percentage (default: 100)

## Prerequisites

The target skill MUST have `eval/eval.json`. If missing, tell the user:
> Run `/generate-eval [skill-name]` first to create binary assertions.

Then stop.

## Execution

### Step 0: Initialize

1. Read: `.claude/skills/[skill-name]/SKILL.md`
2. Read: `.claude/skills/[skill-name]/eval/eval.json`
3. Check/create: `.claude/skills/[skill-name]/eval/improvement-log.json`
4. Load previous metrics from `.claude/hooks/metrics/[skill-name].jsonl`
5. Save current skill.md content as `baseline_content`
6. Set: `iteration = 0`, `best_score = 0`, `best_content = baseline_content`
7. Set: `changes_made = []`, `reverted_approaches = []`

### Step 1: Run Tests

For EACH test case in `eval.json`:

1. Read the `prompt` field
2. Follow the SKILL.md instructions EXACTLY as if you were executing the skill with that prompt
3. Generate the expected output
4. For each `assertion`, evaluate strictly as TRUE or FALSE:
   - Word counts: count precisely
   - Pattern checks: search carefully
   - Structure checks: verify markdown structure
   - Be strict and honest — no rounding up

5. Record results:
```json
{
  "test": "test name",
  "passed": ["T1_A1", "T1_A2"],
  "failed": ["T1_A3"],
  "details": {"T1_A3": "Last line ends with '?' — violates assertion"}
}
```

### Step 2: Calculate Score

```
score = (total_passed / total_evaluable_assertions) * 100
```

Display clearly:
```
══════════════════════════════════════
  Iteration {N} — Score: {score}%
  Passed: {passed}/{total} assertions
══════════════════════════════════════
  ✓ T1_A1: "Contains heading ##"
  ✓ T1_A2: "Word count under 500"
  ✗ T1_A3: "Last line not a question"
    → Actual: "What do you think?"
  ...
══════════════════════════════════════
```

### Step 3: Record Metrics

Append to `.claude/hooks/metrics/[skill-name].jsonl`:
```json
{
  "timestamp": "ISO-8601",
  "skill": "skill-name",
  "score": 92,
  "total_assertions": 25,
  "passed": 23,
  "failed": 2,
  "needs_ai": 0,
  "iteration": 3,
  "source": "self-improve"
}
```

### Step 4: Decide

| Condition | Action |
|-----------|--------|
| `score >= target_score` | **STOP** — Perfect! Commit final changes. |
| `score > best_score` | **KEEP** — Commit, update best, continue. |
| `score == best_score` | **KEEP** — But try a different area next. |
| `score < best_score` | **REVERT** — Restore best version, try different approach. |
| `iteration >= max` | **STOP** — Report results, keep best version. |

On KEEP (commit):
```bash
git add .claude/skills/[skill-name]/SKILL.md
git commit -m "improve([skill-name]): score {old}% → {new}% (iteration {N})"
```

On REVERT:
- Restore `best_content` to skill.md
- Add the failed approach to `reverted_approaches` list
- Log: "Reverted: [description of change] — score dropped to {score}%"

### Step 5: Make ONE Targeted Change

Analyze failed assertions and make **exactly one** change to SKILL.md.

**Rules:**
1. **One change per iteration** — isolate what works
2. **Target the most impactful failure** — fix the assertion that fails across most tests
3. **Never remove working rules** — only add or clarify
4. **Don't repeat reverted approaches** — check `reverted_approaches` list
5. **Keep changes minimal** — add one line/rule, not a rewrite
6. **Be specific** — "Must not end with question mark" not "Improve ending"

**Change strategy (in order of preference):**
1. Add an explicit rule that directly addresses the failed assertion
2. Strengthen a vague instruction to be more specific
3. Add an example of correct behavior
4. Reorder instructions to emphasize the failing rule
5. Add a checklist item at the end of the skill

After making the change, log it and go back to **Step 1**.

### Step 6: Final Report

When the loop ends, generate:

```markdown
# Self-Improvement Report: [skill-name]

## Summary
| Metric | Value |
|--------|-------|
| Iterations | {N} |
| Initial score | {first}% |
| Final score | {last}% |
| Best score | {best}% |
| Assertions | {passed}/{total} |
| Changes kept | {kept_count} |
| Changes reverted | {reverted_count} |

## Improvement Timeline
| Iter | Score | Change | Result |
|------|-------|--------|--------|
| 1 | 80% | Added rule: "Must not end with question" | +8% |
| 2 | 88% | Clarified heading format | +4% |
| 3 | 85% | Added word count emphasis | REVERTED |
| 4 | 92% | Added checklist item for structure | +4% |

## Changes Applied to SKILL.md
1. Added: "LinkedIn posts must not end with a question mark..."
2. Clarified: "## heading must appear on its own line..."
3. Added checklist: "Before output, verify: [ ] No questions at end..."

## Remaining Failures
- [T3_A5] "Uses proof or founder stories" — requires creative judgment, not automatable

## Metrics Integration
- Scores recorded in: `.claude/hooks/metrics/[skill].jsonl`
- View dashboard: `/skill-health`
- Trend: 80% → 88% → 92% (improving)
```

Save to `.claude/skills/[skill-name]/eval/improvement-report.md`.

## Autonomy Rules

- **Never stop to ask permission.** The human may be asleep.
- **Never ask "should I continue?"** Just continue.
- **Log everything.** Every iteration, every change, every score.
- **One change at a time.** This is non-negotiable.
- **Revert failures immediately.** Don't stack bad changes.
- **Don't repeat yourself.** Track what was tried and reverted.
- **Stop at max iterations OR perfect score.** Nothing else stops you.

---

Skill to improve: $ARGUMENTS
