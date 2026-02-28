---
description: Meta-analysis -- plan vs execution, process improvements
---

# System Review

Analyze how well the implementation followed the plan and identify process improvements.

**This is NOT code review.** You are looking for bugs in the *process*, not the code.

## Inputs

- **Plan file**: first argument from `$ARGUMENTS`
- **Execution report**: second argument from `$ARGUMENTS`

Read both files thoroughly.

## Step 1: Understand the Plan

Extract: features planned, architecture specified, validation steps, patterns referenced.

## Step 2: Understand the Execution

Extract: what was implemented, divergences, challenges, skipped items.

## Step 3: Classify Divergences

**Justified divergences:**
- Plan assumed something that didn't exist in codebase
- Better pattern discovered during implementation
- Performance or security issue required different approach

**Problematic divergences:**
- Explicit plan constraints were ignored
- New architecture created instead of following existing patterns
- Shortcuts that introduce technical debt
- Misunderstood requirements

## Step 4: Trace Root Causes

For each problematic divergence: was the plan unclear? Was context missing? Was validation missing?

## Step 5: Output

```markdown
## System Review

### Alignment Score: __/10

### Divergence Analysis
| What Changed | Planned | Actual | Good/Bad | Root Cause |
|-------------|---------|--------|----------|-----------|

### Process Improvements

**CLAUDE.md updates:**
- [ ] [what to add or change]

**Agent definition updates:**
- [ ] [what to clarify]

**Command template updates:**
- [ ] [what to improve]

### Key Learnings
- What worked well: [specifics]
- What needs improvement: [specifics]
- For next time: [concrete actions]
```
