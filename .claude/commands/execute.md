---
description: Implement from a plan file, task by task with validation
---

# Execute Plan: $ARGUMENTS

Implement the plan specified in `$ARGUMENTS`.

## Step 1: Load Plan

Read the entire plan file. Understand all tasks, dependencies, validation commands,
and mandatory context files.

## Step 2: Read Context

Study ALL files listed in the "Mandatory Reading" section.
Note existing patterns and conventions.

## Step 3: Implement

For each task in order:
1. Check that all dependencies are completed
2. Navigate to the target file
3. Implement according to the task specification
4. Maintain consistency with existing code patterns
5. Run the task's validation command
6. Fix any issues before moving to the next task

## Step 4: Test

Create all specified test files following the testing strategy.
Run the full test suite from `PROJECT.md`.

## Step 5: Validate

Run all validation commands:
- The project validation command from `PROJECT.md`
- Any additional validation commands from the plan
- Address all failures before proceeding

## Step 6: Report

Present a summary:
- Completed tasks with file paths
- Tests created and their results
- All validation outputs
- Any divergences from the plan
- Confirmation: ready for code review
