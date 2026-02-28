---
description: Full feature workflow -- from idea to review-ready code
---

# New Feature: $ARGUMENTS

Execute the full feature development pipeline. Follow each step in order.

## Step 1: Requirements

Use the **product-manager** agent to create a PRD for this feature.
The agent should save it to `docs/prds/PRD-[feature-name].md`.

Feature description: $ARGUMENTS

## Step 2: Review PRD

Present a summary of the PRD including:
- Problem statement
- User stories count and priorities
- Key acceptance criteria
- Scope boundaries

Wait for my approval before proceeding. I may request revisions.

## Step 3: Technical Design

Use the **architect** agent to create a technical design based on the approved PRD.
The agent should save it to `docs/architecture/[feature-name].md`.

## Step 4: Review Design

Present design summary including:
- Chosen approach and rationale
- API/data model changes
- Implementation phases
- Identified risks

Wait for my approval before proceeding.

## Step 5: Implement

Create a feature branch: `feat/[feature-name]`

Use the **implementer** agent to build each phase from the design doc.
After each phase, run the validation command from `PROJECT.md`.

## Step 6: Test

Use the **tester** agent to validate all acceptance criteria from the PRD
and write any missing tests.

## Step 7: Code Review

Use the **code-reviewer** agent to review all changes on the feature branch.

## Step 8: Summary

Present the final implementation overview:
- What was built (files created/modified)
- Test results and coverage
- Review findings and their status
- Any outstanding items

Ask if I want to create a PR.
