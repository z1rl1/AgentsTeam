---
name: execution-report
description: Generate a post-implementation report documenting what was built, challenges encountered, and divergences from the original plan.
argument-hint: [plan-file-path]
disable-model-invocation: false
context: fork
---

# Execution Report

Review and analyze the implementation you just completed.

## Context

You have just finished implementing a feature. Before moving on, reflect on what was built, how it aligns with the plan, and what challenges were encountered.

## Process

1. Read the plan file: `$ARGUMENTS`
2. Run `git diff main...HEAD --stat` (or appropriate base branch) to see all changes
3. Run `git log main...HEAD --oneline` to see all commits
4. Compare what was planned vs. what was implemented

## Generate Report

### Meta Information

- **Plan file**: [path to plan]
- **Files added**: [list with paths]
- **Files modified**: [list with paths]
- **Lines changed**: +X -Y

### Validation Results

Run and report results of:
- Linting: run the lint command from `PROJECT.md`
- Type checking: run the type check command from `PROJECT.md`
- Tests: run the test command from `PROJECT.md`

### What Went Well

List specific things that worked smoothly:
- [concrete examples]

### Challenges Encountered

List specific difficulties:
- [what was difficult and why]

### Divergences from Plan

For each divergence, document:

**[Divergence Title]**
- **Planned**: What the plan specified
- **Actual**: What was implemented instead
- **Reason**: Why this divergence occurred
- **Type**: Better approach found | Plan assumption wrong | Requirement changed | Other

### Skipped Items

List anything from the plan that was not implemented:
- [what was skipped]
- **Reason**: [why it was skipped]

### Recommendations

Based on this implementation, what should change for next time?
- Plan improvements: [suggestions]
- Process improvements: [suggestions]
- CLAUDE.md additions: [suggestions]

---

Plan: $ARGUMENTS
