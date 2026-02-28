---
description: Post-implementation report -- what was built, divergences from plan
---

# Execution Report for: $ARGUMENTS

Generate a post-implementation analysis.

## Step 1: Review Plan

Read the plan file: `$ARGUMENTS`

## Step 2: Review Changes

Run `git diff main...HEAD --stat` to see all file changes.
Run `git log main...HEAD --oneline` to see commit history.

## Step 3: Compare Plan vs Reality

For each planned task, check:
- Was it implemented as specified?
- Were there any divergences?
- Were additional changes needed?

## Step 4: Validate

Run all validation commands from `PROJECT.md`:
- Lint
- Type check
- Tests

## Step 5: Generate Report

```markdown
## Execution Report

### Summary
- Plan file: [path]
- Files added: [list]
- Files modified: [list]
- Lines changed: +X -Y

### Validation Results
- Lint: PASS/FAIL
- Types: PASS/FAIL
- Tests: PASS/FAIL (X/Y passing)

### What Went Well
- [specific wins]

### Challenges
- [difficulties and why]

### Divergences from Plan
| Planned | Actual | Reason | Type |
|---------|--------|--------|------|

### Skipped Items
- [what and why]

### Recommendations
- [process improvements]
- [CLAUDE.md updates to consider]
```
