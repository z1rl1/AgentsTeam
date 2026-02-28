---
description: Create a detailed implementation plan with codebase analysis
---

# Plan: $ARGUMENTS

Create a comprehensive implementation plan for this feature.

## Step 1: Analyze Project

1. Read `PROJECT.md` for tech stack, commands, directory structure
2. Read `CLAUDE.md` for project conventions
3. Map the codebase structure using Glob and Grep

## Step 2: Understand Context

1. Identify all files relevant to this feature
2. Read existing patterns in those files
3. Check for similar implementations in the codebase
4. Note any constraints or dependencies

## Step 3: Design the Plan

Create a step-by-step implementation plan including:

- **Mandatory context**: files to read before starting
- **Tasks**: ordered list with dependencies
  - Each task specifies: target file, change type, description
  - Each task has a validation command
- **Testing strategy**: what tests to write and where
- **Risks**: potential issues and mitigations

## Step 4: Save the Plan

Save to `docs/plans/plan-[feature-name].md` using this structure:

```markdown
# Implementation Plan: [Feature]

## Context
[What and why]

## Mandatory Reading
- `path/to/file` -- [why this file matters]

## Tasks

### Task 1: [title]
- **File**: `path/to/file`
- **Type**: Create / Modify
- **Description**: [what to do]
- **Validation**: [command to verify]
- **Depends on**: none

### Task 2: [title]
...

## Testing Strategy
[What tests, where, what patterns to follow]

## Risks
| Risk | Mitigation |
|------|-----------|
```

Present the plan summary and wait for approval.
