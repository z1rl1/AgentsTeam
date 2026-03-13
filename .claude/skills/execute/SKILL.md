---
name: execute
description: Execute an implementation plan created by /plan. Implements each task in order with validation at every step.
argument-hint: [path-to-plan]
disable-model-invocation: true
context: fork
---

# Execute: Implement from Plan

## Plan to Execute

Read the plan file: `$ARGUMENTS`

## Execution Instructions

### 1. Read and Understand

- Read the ENTIRE plan carefully
- Understand all tasks and their dependencies
- Note the validation commands to run
- Review the context references and mandatory files to read
- Review the testing strategy

### 2. Read Mandatory Context

Read every file listed in "Files to Read Before Implementing (MANDATORY)".
Understand the patterns, naming conventions, and code structure before writing anything.

### 3. Execute Tasks in Order

For EACH task in "Step-by-Step Tasks":

#### a. Navigate to the task
- Identify the file and action required
- Read existing related files if modifying

#### b. Implement the task
- Follow the detailed specifications exactly
- Maintain consistency with existing code patterns
- Include proper type hints and documentation
- Add structured error handling where appropriate

#### c. Verify as you go
- After each file change, check syntax
- Ensure imports are correct
- Verify types are properly defined
- Run the task's VALIDATE command

### 4. Implement Testing Strategy

After completing implementation tasks:

- Create all test files specified in the plan
- Implement all test cases mentioned
- Follow the testing approach outlined
- Ensure tests cover edge cases

### 5. Run Validation Commands

Execute ALL validation commands from the plan in order:

Run the validation commands from `PROJECT.md` (lint, type check, tests).

Plus any feature-specific validation commands from the plan.

If any command fails:
- Fix the issue
- Re-run the command
- Continue only when it passes

### 6. Final Verification

Before completing:

- [ ] All tasks from plan completed
- [ ] All tests created and passing
- [ ] All validation commands pass
- [ ] Code follows project conventions
- [ ] Documentation added/updated as needed

## Output Report

Provide summary:

### Completed Tasks
- List of all tasks completed
- Files created (with paths)
- Files modified (with paths)

### Tests Added
- Test files created
- Test cases implemented
- Test results

### Validation Results
```
Output from each validation command
```

### Divergences from Plan
If you deviated from the plan:
- What changed and why
- Whether the divergence was an improvement or a workaround

### Ready for Review
- Confirm all changes are complete
- Confirm all validations pass
- Ready for `/review-code` skill

---

Plan: $ARGUMENTS
