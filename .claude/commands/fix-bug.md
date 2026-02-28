---
description: Bug fix workflow -- investigate, fix, test, review
---

# Fix Bug: $ARGUMENTS

Execute the bug fix workflow. Follow each step in order.

**Note**: If `$ARGUMENTS` is a GitHub issue number (e.g., `42`), run `gh issue view $ARGUMENTS`
to fetch full context before starting.

## Step 1: Investigate

Use the **debugger** agent to investigate the root cause.

If this is a GitHub issue, also create an RCA document at `docs/rca/issue-$ARGUMENTS.md`.

## Step 2: Review Findings

Present the investigation results:
- Root cause analysis
- Proposed fix approach
- Confidence level
- Regression risk assessment

Wait for my approval before proceeding.

## Step 3: Apply Fix

Create a branch: `fix/[bug-description]`

Use the **implementer** agent to apply the approved fix.

## Step 4: Test

Use the **tester** agent to:
- Verify the bug is fixed
- Add a regression test that catches this specific bug
- Run the full test suite

## Step 5: Review

Use the **code-reviewer** agent to review the fix.

## Step 6: Summary

Present results and ask if I want to create a PR.

If this was a GitHub issue, suggest using `Fixes #$ARGUMENTS` in the commit message.
