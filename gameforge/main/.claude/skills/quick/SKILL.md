---
name: quick
description: Fast implementation for small, well-defined changes that skip full planning. Maintains quality guarantees (tests, review, validation) but skips the PRD/design pipeline.
argument-hint: [description of change]
disable-model-invocation: true
context: fork
---

# Quick: Streamlined Implementation

Fast path for small, well-defined changes. Maintains quality guarantees (tests, review,
validation) but skips the full PRD/design pipeline.

## Guardrails

Before proceeding, verify ALL of the following. If ANY fail, tell the user:
"This change is too complex for quick mode. Use `/new-feature` or `/plan` instead."

- [ ] Small and well-defined (< ~100 lines of new/changed code)
- [ ] Scope is clear and bounded
- [ ] Does NOT require new dependencies
- [ ] Does NOT change shared interfaces or API contracts
- [ ] Does NOT modify database schemas

## Step 1: Assess

- Read `PROJECT.md` and `CLAUDE.md` for conventions
- Analyze what needs to change and which files are affected
- Present a brief plan (3-5 bullet points) to the user
- Wait for approval before proceeding

## Step 2: Branch

Create an appropriate branch:
- `feat/[description]` for new functionality
- `fix/[description]` for bug fixes
- `chore/[description]` for maintenance tasks
- `refactor/[description]` for refactoring

## Step 3: Implement

Use the **implementer** agent to:
- Make the code changes following project conventions
- Write tests for any new business logic

## Step 4: Validate

Run the validation command from `PROJECT.md`.
If any check fails, fix the issue and re-run.

## Step 5: Review

Use the **code-reviewer** agent to review all changes.
Address any critical findings before proceeding.

## Step 6: Commit

Create an atomic commit with a conventional commit prefix:
- `feat:`, `fix:`, `chore:`, `refactor:`, `test:`, `docs:`

## Step 7: Summary

Present:
- What was changed (files created/modified)
- Test results
- Review findings (if any)
- Ask if the user wants to create a PR

---

Change: $ARGUMENTS
