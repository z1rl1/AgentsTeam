---
name: refactor
description: Large multi-phase refactoring workflow. Analyzes impact, creates a migration plan, implements incrementally with validation at each step, and verifies no regressions.
argument-hint: [refactoring description]
disable-model-invocation: true
context: fork
---

# Refactor: Multi-Phase Refactoring Workflow

Structured approach for large refactoring tasks where the codebase must remain functional at every checkpoint.

## Step 1: Analyze Scope

- Read `PROJECT.md` and `CLAUDE.md` for conventions
- Use the **architect** agent to assess refactoring scope:
  - Identify all affected files and their dependencies
  - Map the blast radius of the change
  - Classify risk level: Low / Medium / High
  - Identify integration points that could break

## Step 2: Human Review

Present the impact assessment:
- Files affected (with line counts)
- Risk level and justification
- Proposed number of phases
- Rollback strategy (how to undo if something goes wrong)

Wait for approval before proceeding.

## Step 3: Create Phased Plan

Use the **architect** agent to produce a phased refactoring plan where:
- Each phase is independently testable
- The codebase compiles and tests pass after every phase
- Dependencies between phases are explicit
- Each phase has a clear validation checkpoint

## Step 4: Human Review

Present the phased plan. Wait for approval.

## Step 5: Execute Phases

Create branch: `refactor/[description]`

For EACH phase:
1. Use the **implementer** agent to apply the refactoring
2. Run the validation command from `PROJECT.md`
3. Run the full test suite
4. If any test fails, fix before proceeding
5. Create an atomic commit: `refactor: [phase description]`

**Critical**: Do NOT proceed to the next phase until the current phase passes all validation.

## Step 6: Final Validation

Use the **tester** agent to:
- Run the complete test suite
- Verify zero regressions
- Check that refactored code maintains the same behavior

## Step 7: Review

Use the **code-reviewer** agent to review all changes on the refactoring branch.
Focus areas: correctness, readability improvement, no behavioral changes.

## Step 8: Summary

Present:
- What was refactored and why
- Number of phases completed
- Before/after comparison (file count, complexity, line count)
- Test results
- Review findings
- Ask if the user wants to create a PR

---

Refactoring: $ARGUMENTS
