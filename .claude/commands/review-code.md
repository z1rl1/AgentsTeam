---
description: Run code review and test validation on current changes
---

# Code Review

## Step 1: Identify Changes

Run `git status` and `git diff` to see all current changes.

## Step 2: Code Review

Use the **code-reviewer** agent to review all modifications against project standards.

## Step 3: Test Validation

Use the **tester** agent to check if tests exist for changed code
and validate acceptance criteria coverage.

## Step 4: Report

Present combined findings from both review and testing.
Flag any critical issues that must be resolved before merge.
