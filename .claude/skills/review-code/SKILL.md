---
name: review-code
description: Review current code changes against project standards. Runs code review and test validation, then reports findings with critical issues highlighted.
disable-model-invocation: false
context: fork
---

Review the current code changes using the following workflow.

## Step 1: Identify Changes
Run `git status` and `git diff` to identify all current changes.

## Step 2: Code Review
Use the **code-reviewer** agent to review all changes against project standards.

## Step 3: Test Validation
Use the **tester** agent to check if tests exist for the changed code
and validate acceptance criteria coverage.

## Step 4: Report
Present the combined review and test findings.
Highlight any critical issues that must be fixed before merging.
