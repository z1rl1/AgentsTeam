---
name: overnight
description: Launch autonomous overnight skill improvement. Scans all skills, identifies those below target score, and runs self-improvement loops on each one sequentially. Designed to run unattended — no human input needed.
argument-hint: [--target-score N] [--skills skill1,skill2,...] [--generate-missing]
disable-model-invocation: false
context: fork
---

# Overnight Skill Improvement

Launch a full autonomous improvement session across all skills.
Designed to run unattended while you sleep.

## Concept

```
  🌙 You go to sleep
  ┌──────────────────────────────────────────────────────────────┐
  │                                                              │
  │   ┌─────────┐    ┌────────────┐    ┌─────────────┐         │
  │   │  Scan   │───>│  Generate  │───>│  Improve    │         │
  │   │  Skills │    │  Missing   │    │  Loop per   │         │
  │   │         │    │  Evals     │    │  Skill      │         │
  │   └─────────┘    └────────────┘    └──────┬──────┘         │
  │                                           │                 │
  │                                    ┌──────┴──────┐         │
  │                                    │   Report    │         │
  │                                    │   Results   │         │
  │                                    └─────────────┘         │
  │                                                              │
  └──────────────────────────────────────────────────────────────┘
  ☀️ You wake up to better skills
```

## Arguments

Parse `$ARGUMENTS`:
- `--target-score N`: minimum acceptable score (default: 100)
- `--skills skill1,skill2,...`: only improve these specific skills (default: all)
- `--generate-missing`: auto-generate eval.json for skills that don't have one
- `--max-iterations N`: max iterations per skill (default: 10)

## Phase 1: Discovery

Scan all skills in `.claude/skills/` and classify each one:

```
══════════════════════════════════════════════════════════
  OVERNIGHT IMPROVEMENT — Discovery Phase
══════════════════════════════════════════════════════════

  Total skills found: 38

  ✓ Ready (has eval + below target):     5 skills
  ◐ No eval (needs generation):         28 skills
  ★ Already perfect (at target score):   2 skills
  ○ Meta-skills (skipped):               3 skills

  Skills queued for improvement:
  ┌──────────────────┬───────┬────────────────────────┐
  │ Skill            │ Score │ Status                 │
  ├──────────────────┼───────┼────────────────────────┤
  │ review-code      │  85%  │ Ready — will improve   │
  │ plan             │  72%  │ Ready — will improve   │
  │ commit           │  N/A  │ Will generate eval     │
  │ validate         │  N/A  │ Will generate eval     │
  │ ...              │       │                        │
  └──────────────────┴───────┴────────────────────────┘
══════════════════════════════════════════════════════════
```

Skip meta-skills: `self-improve`, `generate-eval`, `skill-health`, `overnight`.

If `--skills` flag is provided, only process the listed skills.

## Phase 2: Generate Missing Evals

If `--generate-missing` is set (or by default for overnight runs):

For each skill WITHOUT `eval/eval.json`:
1. Run the logic from `/generate-eval` to create binary assertions
2. Log: "Generated eval.json for [skill] — [N] assertions"

If `--generate-missing` is NOT set:
- Skip skills without eval.json
- Note them in the report

## Phase 3: Improvement Loops

For each skill below target score, run the self-improvement loop.

**Execution order**: Sort by score ascending (worst skills first — biggest gains).

For each skill:

```
──────────────────────────────────────────
  [3/5] Improving: review-code
  Current score: 85% | Target: 100%
──────────────────────────────────────────
```

1. Run the full `/self-improve` logic (from the self-improve SKILL.md):
   - Read skill.md and eval.json
   - Loop: test → score → change → commit/revert
   - Stop at target score or max iterations

2. After each skill completes, display progress:

```
  ✓ review-code:  85% → 100% (3 iterations, 2 changes kept)
  ✓ plan:         72% →  92% (10 iterations, 5 changes kept)
  ▸ commit:       running...
  ○ validate:     pending
  ○ execute:      pending
```

3. Move to next skill.

**Important**: Spawn a fresh context for each skill's improvement loop.
Use the implementer or a dedicated agent per skill to avoid context degradation.
Do NOT accumulate all skills in one context window.

## Phase 4: Final Report

When all skills are processed, generate:

```markdown
# Overnight Improvement Report

**Started**: 2026-03-20 23:00 UTC
**Finished**: 2026-03-21 06:30 UTC
**Duration**: 7h 30m

## Summary

| Metric | Value |
|--------|-------|
| Skills scanned | 38 |
| Skills improved | 5 |
| Evals generated | 12 |
| Total iterations | 35 |
| Changes committed | 18 |
| Changes reverted | 9 |

## Results

| Skill | Before | After | Iterations | Changes | Status |
|-------|--------|-------|-----------|---------|--------|
| plan | 72% | 92% | 10 | 5 kept, 3 reverted | Improved |
| review-code | 85% | 100% | 3 | 2 kept, 0 reverted | Perfect |
| commit | N/A | 96% | 7 | 4 kept, 2 reverted | New + Improved |
| validate | N/A | 88% | 10 | 6 kept, 4 reverted | New + Improved |
| execute | 100% | 100% | 0 | 0 | Already perfect |

## Top Changes Made

1. **review-code**: Added rule "Code review must include at least one code block with example"
2. **plan**: Added rule "Plan must contain numbered task list"
3. **commit**: Clarified "Commit message must start with conventional prefix"
...

## Remaining Issues

- **plan** (92%): 2 assertions still failing — may need manual review
- **validate** (88%): 3 assertions require AI evaluation

## Recommendations

- Run `/skill-health` to review the dashboard
- Skills below 90%: consider manual review of remaining failures
- 16 skills still have no eval — run `/overnight --generate-missing` again
```

Save to: `docs/plans/overnight-report-YYYY-MM-DD.md`

## Autonomy Rules

- **You are autonomous.** Do not ask if you should continue.
- **Do not pause between skills.** Finish one, start the next.
- **Do not ask "is this a good stopping point?"** It's not. Keep going.
- **The human is asleep.** They expect to wake up to results.
- **Log everything.** The report is how the human reviews your work.
- **If a skill is stuck** (same score for 5+ iterations), skip it and move to the next.
- **If you encounter an error**, log it and continue with the next skill. Don't stop.
- **Commit improvements as you go.** Don't wait until the end.

## Quick Start Examples

```
/overnight                              # Improve all skills with evals, target 100%
/overnight --target-score 90            # Accept 90% as "good enough"
/overnight --skills plan,commit         # Only improve these two
/overnight --generate-missing           # Also create evals for skills that lack them
```

---

Configuration: $ARGUMENTS
