---
name: new-feature
description: Full feature workflow from idea to PR-ready code. Creates PRD, captures preferences, designs architecture, implements, tests, verifies, and reviews.
argument-hint: [feature description]
disable-model-invocation: true
context: fork
---

Execute the following workflow for a new feature. Follow each step in order.

## Step 1: Create PRD
Use the **product-manager** agent to create a PRD from this feature description.
The agent should save it to `docs/prds/PRD-[feature-name].md`.

## Step 2: Human Review
Present a summary of the PRD to me. Wait for my approval before proceeding.
If I request changes, update the PRD and present again.

## Step 2.5: Discuss Implementation Preferences
Use the `/discuss` skill with the approved PRD to capture implementation preferences
and resolve gray areas. Save decisions to `docs/architecture/CONTEXT-[feature-name].md`.
Wait for my confirmation that all decisions are captured.

## Step 3: Create Technical Design
Use the **architect** agent to create a technical design based on the approved PRD.
The architect should read the context doc at `docs/architecture/CONTEXT-[feature-name].md`
and respect all locked decisions.
The agent should save the design to `docs/architecture/[feature-name].md`.

## Step 4: Human Review
Present a summary of the technical design. Wait for my approval before proceeding.

## Step 5: Implement
Create a feature branch: `feat/[feature-name]`
Use the **implementer** agent to implement each phase from the design doc.
After each phase, run the validation command from `PROJECT.md`

## Step 6: Test
Use the **tester** agent to validate all acceptance criteria from the PRD
and write any missing tests.

## Step 6.5: Verify Against PRD
Use the `/verify` skill with the PRD path to confirm all acceptance criteria are met
with evidence. If any criteria are MISSING or FAILING, use the **tester** agent to
address gaps before proceeding to review.

## Step 7: Review
Use the **code-reviewer** agent to review all changes on the feature branch.

## Step 8: Summary
Present a final summary:
- What was implemented
- Test results and coverage
- Review findings
- Any open items

Ask me if I want to create a PR.

---

Feature: $ARGUMENTS
