---
description: Investigate a GitHub issue and create RCA document
---

# Root Cause Analysis: Issue #$ARGUMENTS

## Step 1: Fetch Issue

Run `gh issue view $ARGUMENTS` to get full issue context.
Extract: title, description, labels, reproduction steps.

## Step 2: Search Codebase

Locate relevant components:
- Search for error messages mentioned in the issue
- Find affected files and functions
- Check related test files

## Step 3: Review History

Run `git log --oneline -20 -- [affected files]` to check recent changes.
Look for commits that might have introduced the bug.

## Step 4: Investigate

Determine:
- Bug type (logic error, race condition, missing validation, etc.)
- Root cause vs. symptoms
- Why existing tests didn't catch it

## Step 5: Assess Impact

- Severity: Critical / High / Medium / Low
- Affected users / features
- Data integrity implications

## Step 6: Document

Save RCA to `docs/rca/issue-$ARGUMENTS.md`:

```markdown
# RCA: Issue #[number] -- [title]

**Severity**: [Critical/High/Medium/Low]
**Date**: [today]
**Status**: Investigating / Fix Proposed / Resolved

## Problem
- **Expected**: [behavior]
- **Actual**: [behavior]
- **Reproduction**: [steps]

## Root Cause
[Explanation with file:line references]

## Impact
- Affected: [users/features]
- Data: [any data implications]

## Proposed Fix
| File | Change |
|------|--------|
| `path:line` | [what to change] |

## Testing
- [ ] Regression test for this specific case
- [ ] Full test suite passes
- [ ] Edge cases covered

## Prevention
[How to prevent similar issues in the future]
```

## Next Steps

Suggest using the `/fix-bug` command to implement the fix.
Recommend `Fixes #$ARGUMENTS` in the commit message.
