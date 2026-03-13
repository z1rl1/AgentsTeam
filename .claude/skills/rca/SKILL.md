---
name: rca
description: Investigate a GitHub issue and create a Root Cause Analysis document with evidence-based findings and proposed fix strategy.
argument-hint: [github-issue-id]
disable-model-invocation: true
context: fork
agent: debugger
---

# Root Cause Analysis: GitHub Issue #$ARGUMENTS

## Objective

Investigate GitHub issue #$ARGUMENTS, identify the root cause, and document findings for implementation.

**Prerequisites:**
- Working in a Git repository with GitHub remote
- GitHub CLI installed and authenticated (`gh auth status`)

## Investigation Process

### 1. Fetch GitHub Issue Details

```bash
gh issue view $ARGUMENTS
```

Extract: title, description, labels, comments, reproduction steps.

### 2. Search Codebase

- Search for components, functions, and error messages mentioned in the issue
- Find related code paths
- Check similar implementations
- Look for recent changes to affected areas

### 3. Review Recent History

```bash
git log --oneline -20 -- [relevant-paths]
```

Look for:
- Recent modifications to affected code
- Related bug fixes
- Refactorings that might have introduced the issue

### 4. Investigate Root Cause

Analyze the code to determine:
- What is the actual bug or issue?
- Why is it happening?
- What was the original intent?
- Is this a logic error, edge case, or missing validation?
- Are there related issues or symptoms?

### 5. Assess Impact

- How widespread is this issue?
- What features are affected?
- Are there workarounds?
- Severity: Critical / High / Medium / Low
- Could this cause data corruption or security issues?

### 6. Propose Fix Approach

- What needs to be changed?
- Which files will be modified?
- What is the fix strategy?
- What testing is needed?
- Are there risks or side effects?

## Output: RCA Document

Save analysis to: `docs/rca/issue-$ARGUMENTS.md`

Use this structure:

```markdown
# Root Cause Analysis: GitHub Issue #$ARGUMENTS

## Issue Summary
- **Issue**: #$ARGUMENTS
- **Title**: [title from GitHub]
- **Severity**: Critical / High / Medium / Low

## Problem Description
[Clear description]

**Expected**: [what should happen]
**Actual**: [what actually happens]

## Root Cause

### Affected Files
- `path/to/file:line` -- [description]

### Analysis
[Detailed explanation of why this happens]

### Code Location
[Relevant code snippet showing the bug]

## Impact Assessment
- **Scope**: [how widespread]
- **Affected features**: [list]

## Proposed Fix

### Strategy
[High-level approach]

### Files to Modify
1. `path/to/file` -- [what to change and why]

### Testing Requirements
1. [Test case to verify fix]
2. [Regression test]

### Risks
- [Any risks with this fix]

## Next Steps
1. Review this RCA
2. Use the **implementer** agent to apply the fix
3. Use the **tester** agent to add regression tests
4. Commit with message: `fix: resolve #$ARGUMENTS -- [description]`
```

The `Fixes #$ARGUMENTS` pattern in the commit message will auto-close the GitHub issue when merged.

---

Issue: $ARGUMENTS
