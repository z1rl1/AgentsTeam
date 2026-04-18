---
name: onboard
description: Generate comprehensive onboarding documentation from an existing codebase. Analyzes architecture, conventions, key files, and produces a developer guide.
argument-hint: "[optional: specific area to document]"
disable-model-invocation: false
context: fork
agent: docs-writer
---

# Onboard: Generate Developer Guide

Create onboarding documentation by analyzing the actual codebase.

## Step 1: Full Codebase Scan

- `git ls-files` to list all tracked files
- Analyze directory structure and organization
- Identify languages, frameworks, and build tools

## Step 2: Read Core Files

- `PROJECT.md` and `CLAUDE.md` for project configuration
- `AGENTS.md` for team instructions
- All README files
- All docs in `docs/architecture/`
- Configuration files (package.json, tsconfig.json, etc.)

## Step 3: Analyze Architecture

- Identify entry points and application flow
- Map routing patterns (pages, API routes)
- Document data flow (client → API → DB)
- Identify service boundaries and key abstractions
- Find shared utilities and helpers

## Step 4: Extract Conventions

From actual code, identify and document:
- Import patterns and module organization
- Naming conventions (files, functions, components, variables)
- Test patterns and structure
- Error handling approach
- State management patterns
- Authentication/authorization patterns

Include **real examples** from the codebase, not generic advice.

## Step 5: Generate Onboarding Doc

If `$ARGUMENTS` specifies an area, focus on that area. Otherwise generate a comprehensive guide.

Save to `docs/ONBOARDING.md`:

```markdown
# Developer Onboarding Guide

## Project Overview
- What this project does
- Key technologies
- Architecture diagram (ASCII)

## Getting Started
- Prerequisites
- Setup steps (from PROJECT.md)
- Running locally
- Running tests

## Architecture Overview
- Directory structure with descriptions
- Key architectural patterns
- Data flow overview
- Service boundaries

## Common Tasks
### Adding a new API endpoint
[step-by-step with file paths from actual codebase]

### Adding a new page/component
[step-by-step with file paths]

### Adding a new database model
[step-by-step with file paths]

### Writing tests
[patterns from actual test files]

## Code Conventions
- [conventions with real examples]

## Agent Workflows
- Available skills and when to use them
- Common workflows (new feature, bug fix, etc.)

## Troubleshooting
- Common issues and solutions
```

## Step 6: Summary

Present the generated doc for human review.

---

Focus: $ARGUMENTS
