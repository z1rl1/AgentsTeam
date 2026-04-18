---
name: verify
description: Verify implementation against PRD acceptance criteria with evidence mapping. Maps each criterion to concrete test or code evidence.
argument-hint: [PRD-path]
disable-model-invocation: false
context: fork
---

# Verify: Goal-Backward Verification

Verify that the implementation satisfies ALL acceptance criteria from the PRD,
not just that it compiles and passes lint. Maps each criterion to concrete evidence.

## Step 1: Load PRD

Read the PRD at the given path (or search `docs/prds/` for a matching PRD).

## Step 2: Extract Acceptance Criteria

Parse every acceptance criterion from the PRD's user stories.
Look for GIVEN/WHEN/THEN blocks and any other testable criteria.

Build a list:
- **ID**: User story and criterion ID (e.g., US-1 AC-1)
- **Summary**: Brief description of what must be true
- **Full Text**: The complete GIVEN/WHEN/THEN block

## Step 3: Map Criteria to Evidence

For each acceptance criterion:

### a. Search for Tests
- Search the test suite for tests that validate this criterion
- Look for test names, descriptions, or comments that reference the criterion
- Check that the test actually exercises the described scenario

### b. Run Matching Tests
- If tests exist, run them and record pass/fail
- Note the test file and line number

### c. Search Implementation (if no test found)
- Search the implementation for code that addresses this criterion
- Verify the logic handles the described scenario
- Note the implementation file and line number

### d. Classify
- **VERIFIED**: Test exists and passes
- **IMPLEMENTED**: Code exists that addresses this, but no dedicated test
- **FAILING**: Test exists but fails
- **MISSING**: No test or implementation evidence found

## Step 4: Run Deterministic Validation

Run all validation commands from `PROJECT.md`:
- Lint
- Type check (if applicable)
- Full test suite
- Build (if applicable)

## Step 5: Generate Report

```markdown
# Verification Report: [Feature Name]

**PRD**: [path]
**Branch**: [current branch]
**Date**: [date]

## Acceptance Criteria Coverage

| ID | Criterion Summary | Status | Evidence |
|----|-------------------|--------|----------|
| US-1 AC-1 | [summary] | VERIFIED | `test/path:line` passes |
| US-1 AC-2 | [summary] | IMPLEMENTED | `src/path:line` (no test) |
| US-2 AC-1 | [summary] | MISSING | No evidence found |

## Coverage Summary
- **VERIFIED**: X criteria (test passes)
- **IMPLEMENTED**: X criteria (code exists, no test)
- **FAILING**: X criteria (test fails)
- **MISSING**: X criteria (no evidence)

## Deterministic Validation
- Lint: PASS / FAIL
- Type Check: PASS / FAIL / N/A
- Tests: X/Y passing
- Build: PASS / FAIL / N/A

## Gap Analysis

Criteria without tests:
1. **[ID]**: [summary] -- Recommended test: [description]
2. ...

## Overall Verdict
**[VERIFIED / PARTIALLY VERIFIED / NOT VERIFIED]**

- VERIFIED: All criteria have passing tests
- PARTIALLY VERIFIED: Some criteria lack tests or have only implementation evidence
- NOT VERIFIED: Critical criteria are missing or failing
```

Save report to `docs/plans/verification-[feature-name].md`.

## Step 6: Recommendations

If any criteria are MISSING or FAILING:
- List specific test cases that should be written
- Suggest using the **tester** agent to address gaps

---

PRD: $ARGUMENTS
