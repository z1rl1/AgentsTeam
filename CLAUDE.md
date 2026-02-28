# CLAUDE.md — Agentic Product Development Team

## Project Overview

This is an **agentic product development team** workspace. It uses specialized AI agents
to handle the full software development lifecycle: requirements, architecture, implementation,
testing, review, debugging, and documentation.

> **Project-specific configuration** (tech stack, commands, directory layout) lives in
> [`PROJECT.md`](PROJECT.md). All agents read it automatically.

## Agent Team Structure

Agents are defined in `.claude/agents/`. Each has a specific role, tool access, and permission
model. The main Claude Code session acts as team lead and delegates to specialists.

| Agent             | Role                                     | Model   | When to Use                    |
|-------------------|------------------------------------------|---------|--------------------------------|
| `product-manager` | PRDs, user stories, acceptance criteria   | opus    | Planning new features          |
| `architect`       | System design, API contracts, ADRs        | opus    | Technical design decisions     |
| `implementer`     | Code writing, feature implementation      | inherit | Building features              |
| `code-reviewer`   | Quality, security, performance review     | inherit | After code changes             |
| `tester`          | Test writing, coverage, validation        | sonnet  | Verifying acceptance criteria  |
| `debugger`        | Root cause analysis, bug investigation    | inherit | Investigating bugs             |
| `docs-writer`     | API docs, architecture docs, changelogs   | sonnet  | Documentation tasks            |
| `security`        | Threat modeling, OWASP compliance         | inherit | Security audits                |
| `ux`              | UI/UX review, accessibility              | inherit | UI review                     |

## Workflow Commands

Custom slash commands in `.claude/commands/`:

### Core Workflows
- `/new-feature [description]` — Full pipeline: PRD → design → implement → test → review
- `/fix-bug [description]` — Bug pipeline: investigate → fix → test → review
- `/review-code` — Run code review + test validation on current changes

### Plan/Execute Loop
- `/plan [feature]` — Create implementation plan with codebase analysis
- `/execute [plan-path]` — Implement from a plan file, task by task
- `/prime` — Load project context (structure, docs, recent activity)
- `/commit` — Stage and create atomic commit with conventional prefix

### Validation & Process Improvement
- `/validation:validate` — Full project health check (lint, types, tests, build, quality)
- `/validation:execution-report [plan-path]` — Post-implementation analysis: what was built, divergences
- `/validation:system-review [plan] [report]` — Meta-analysis: plan vs execution, process improvements

### GitHub Issue Integration
- `/github-issue:rca [issue-id]` — Root cause analysis, creates document at `docs/rca/`

## Development Workflow

### Feature Development (idea → merge)

```
1. Human provides feature idea
2. product-manager agent → creates PRD in docs/prds/
3. Human reviews + approves PRD
4. architect agent → creates design doc in docs/architecture/
5. Human reviews + approves design
6. implementer agent → writes code on feature branch
7. tester agent → validates acceptance criteria, writes tests
8. code-reviewer agent → reviews all changes
9. Human reviews and merges
```

### Bug Fixing

```
1. Human describes bug (or provides GitHub issue ID)
2. debugger agent → investigates root cause
3. Human approves proposed fix
4. implementer agent → applies fix
5. tester agent → adds regression test
6. code-reviewer agent → reviews changes
7. Human reviews and merges
```

## Directory Structure

```
.claude/
  agents/           # Agent definitions (role, tools, model, system prompt)
  commands/         # Workflow slash commands
    validation/     # Validation and process improvement commands
    github-issue/   # GitHub issue workflows (RCA)
  reference/        # Tech-stack best practices (populated per project)
  settings.json     # Shared team settings (committed)
  settings.local.json # Personal settings (gitignored)
docs/
  prds/             # Product Requirements Documents
  architecture/     # Technical design documents
  adrs/             # Architecture Decision Records
  plans/            # Implementation plans (from /plan command)
  rca/              # Root Cause Analysis documents
  templates/        # Document templates
src/
  components/       # UI components
  services/         # Business logic and API clients
  utils/            # Shared utilities
  types/            # TypeScript type definitions
tests/              # Test files mirroring src/ structure
CLAUDE.md           # This file
AGENTS.md           # Universal agent instructions (all AI tools)
PROJECT.md          # Project-specific configuration
```

## Code Standards

- Error handling: never swallow errors silently
- All new business logic must have tests
- Functional patterns preferred over classes
- Run the validation command from `PROJECT.md` before every commit
- Follow language-specific rules from `PROJECT.md`

## Git Workflow

- Branch naming: `feat/`, `fix/`, `chore/`, `refactor/`, `docs/`, `test/`
- Commits: conventional format `<type>(<scope>): <description>`
- PRs require passing CI + human approval
- Squash merge to main

## Boundaries (Three-Tier System)

### Always (agents can do freely)
- Read any file in the project
- Run tests, linters, type checks
- Create/edit source files and test files
- Create branches and commits

### Ask First (requires human approval)
- Adding new dependencies
- Changing database schema
- Modifying authentication/authorization logic
- Changing CI/CD pipeline configuration
- Changing shared interfaces or API contracts
- Architectural decisions affecting multiple services

### Never
- Commit secrets, API keys, or credentials
- Bypass security checks or linting
- Push directly to main branch
- Delete or modify production data
- Modify existing migration files after they've been applied
- Disable tests to make them pass

## Context Management

- Use `/clear` between unrelated tasks to prevent context pollution
- Delegate research-heavy work to subagents via the Task tool
- Keep the main orchestrator session lean — plan and route, don't explore
- Store intermediate artifacts (specs, plans, ADRs) as files, not in conversation context
- Use Plan Mode for any task touching more than 2 files

## Agent Communication Protocol

Agents do not talk to each other directly. All communication flows through:

1. **File artifacts** — PRDs, ADRs, design docs, test plans saved to `docs/`
2. **Shared task list** — TaskCreate/TaskUpdate for tracking work items
3. **Orchestrator summaries** — Lead passes relevant context when spawning workers
4. **Structured handoffs** — each agent outputs a defined format the next agent expects

## Quality Verification Lattice

```
Layer 1: DETERMINISTIC   — build, unit tests, lint, typecheck
Layer 2: SEMANTIC         — contract tests, golden tests, snapshots
Layer 3: SECURITY         — SAST, dependency scan, secret scan
Layer 4: AGENTIC          — code-reviewer agent for style + spec adherence
Layer 5: HUMAN            — escalations and final acceptance
```

## Quality Gates

Every feature must pass these gates before merge:

| Gate              | Owner           | Criteria                                     |
|-------------------|-----------------|----------------------------------------------|
| Requirements      | Product Manager | PRD approved, stories defined                |
| Architecture      | Architect       | Design doc written, approach confirmed       |
| Implementation    | Developer       | Code complete, validation passing            |
| Testing           | QA Engineer     | All acceptance criteria tested, coverage ok  |
| Security          | Security        | No OWASP top-10 issues, secrets scanned      |
| UX                | UX Reviewer     | Accessible, responsive, design-consistent    |
| Code Review       | Code Reviewer   | Quality, performance, security approved      |

## Human-in-the-Loop Checkpoints

| Checkpoint            | When                          | What Requires Approval               |
|-----------------------|-------------------------------|--------------------------------------|
| PRD Review            | After PM drafts PRD           | Requirements, scope, priorities      |
| Architecture Review   | After Architect writes design | Tech decisions, trade-offs           |
| Implementation Review | After Developer completes     | Code quality, approach correctness   |
| Security Sign-off     | After Security audit          | Any HIGH/CRITICAL findings           |
| Release Approval      | After all gates pass          | Final go/no-go for deployment        |
