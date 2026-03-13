# CLAUDE.md

> Claude Code-specific configuration and universal agent instructions.
> For tech stack, commands, and directory layout see `PROJECT.md`.

## Project Overview

Agentic product development team workspace. Multi-agent architecture with specialized
roles handling requirements, architecture, implementation, testing, review, and documentation.

**Tech Stack**: See `PROJECT.md` for language, runtime, framework, database, and tooling.

## Agent Team Structure

This project uses Claude Code sub-agents defined in `.claude/agents/`. Each agent has a
specific role, tool access, and permission model. The team lead (your main Claude Code session)
delegates to specialists:

| Agent | Role | Model | When to Use |
|-------|------|-------|-------------|
| `product-manager` | PRDs, user stories, acceptance criteria | opus | Planning new features |
| `architect` | System design, API contracts, data models | opus | Technical design decisions |
| `implementer` | Code writing, feature implementation | inherit | Building features |
| `code-reviewer` | Quality, security, performance review | inherit | After code changes |
| `tester` | Test writing, coverage, validation | sonnet | Verifying acceptance criteria |
| `debugger` | Root cause analysis, bug fixing | inherit | Investigating bugs |
| `docs-writer` | API docs, architecture docs, changelogs | sonnet | Documentation tasks |

## Workflow Skills

Custom skills in `.claude/skills/`:

### Core Workflows
- `/bootstrap [project description]` -- Initialize a new project from scratch: gather requirements -> fill PROJECT.md -> scaffold -> validate
- `/new-feature [description]` -- Full feature workflow: PRD -> discuss -> design -> implement -> test -> verify -> review
- `/fix-bug [description]` -- Bug workflow: investigate -> fix -> test -> review (supports GitHub issue IDs)
- `/review-code` -- Run code review on current changes
- `/discuss [PRD-path]` -- Capture implementation preferences before technical design
- `/quick [description]` -- Fast implementation for small changes (skips PRD/design pipeline)
- `/refactor [description]` -- Large multi-phase refactoring with incremental validation
- `/release [version]` -- Generate release notes, changelog, and version bump

### Plan/Execute Loop
- `/plan [feature]` -- Create a detailed implementation plan with codebase analysis
- `/execute [plan-path]` -- Implement from a plan file, task by task with validation
- `/prime` -- Load project context (structure, docs, recent activity)
- `/commit` -- Stage and create an atomic commit with conventional prefix

### Validation & Process Improvement
- `/validate` -- Full project health check (lint, types, tests, build, code quality)
- `/execution-report [plan-path]` -- Post-implementation report: what was built, divergences from plan
- `/system-review [plan] [report]` -- Meta-analysis: plan vs. execution, process improvements
- `/verify [PRD-path]` -- Verify implementation against PRD acceptance criteria with evidence
- `/retro [feature]` -- Post-implementation retrospective that updates CLAUDE.md with learnings

### Testing & Security
- `/e2e-test [feature]` -- Design and implement end-to-end integration tests
- `/security-audit [area]` -- Security-focused review (OWASP Top 10, deps, auth)

### Maintenance
- `/update-deps [package]` -- Dependency updates with security audit and validation
- `/perf [area]` -- Performance profiling, optimization, and benchmarking
- `/migrate [description]` -- Database/API migration workflow with rollback plan
- `/tech-debt [area]` -- Identify and address technical debt

### Session Management
- `/pause` -- Save current work context to STATE.md for session continuity
- `/resume` -- Restore context from STATE.md and continue where you left off

### Documentation & Investigation
- `/onboard [area]` -- Generate onboarding docs from existing codebase
- `/rca [issue-id]` -- Investigate a GitHub issue, create RCA document at `docs/rca/`

### Domain Skills (auto-loaded by Claude when relevant)
- `react-patterns` -- React component patterns, hooks, state management, accessibility
- `nextjs-conventions` -- App Router, Server/Client Components, data fetching, middleware
- `node-backend` -- Middleware, error handling, validation, logging, async patterns
- `api-design` -- REST conventions, response formats, pagination, error responses
- `database-patterns` -- Schema design, migrations, query optimization, indexing
- `frontend-testing` -- React Testing Library, component tests, MSW mocking
- `backend-testing` -- API tests, database setup/teardown, fixtures, factories
- `auth-patterns` -- JWT flows, session management, RBAC, password hashing, CSRF

## Directory Structure

```
.claude/
  agents/           -- Agent definitions (role, tools, model, system prompt)
  skills/           -- Workflow skills and domain knowledge (SKILL.md format)
  reference/        -- Tech-stack best practices (populated per project)
  settings.json     -- Shared team settings (committed)
  settings.local.json -- Personal settings (gitignored)
docs/
  prds/             -- Product Requirements Documents
  architecture/     -- Technical design documents and CONTEXT-*.md decision docs
  plans/            -- Implementation plans and verification reports
  rca/              -- Root Cause Analysis documents and persistent debug sessions
  state/            -- Session state persistence (STATE.md)
  templates/        -- PRD, design doc, and context templates
CLAUDE.md           -- This file (Claude-specific project context + universal agent instructions)
PROJECT.md          -- Project-specific configuration (tech stack, commands, conventions)
```

## Setup

See `PROJECT.md` for install, environment setup, and database commands.

## Build & Test

See `PROJECT.md` for the full command table (dev, build, test, lint, typecheck, etc.).

## Architecture

See `PROJECT.md` for the project directory structure and architecture pattern.

```
docs/
├── prds/           # Product Requirements Documents
├── architecture/   # Technical design documents
└── templates/      # Document templates
```

## Code Style

- Functions should have a single responsibility and stay short
- Use clear, descriptive names; no abbreviations
- Functional patterns preferred over classes
- Error handling: never swallow errors silently
- Follow the import ordering convention defined in `PROJECT.md`
- Follow file naming conventions from `PROJECT.md`
- Run the validation command from `PROJECT.md` before every commit
- See `PROJECT.md` for language-specific coding rules

## Testing

- Use factories and fixtures, not hardcoded test data
- Mock external services, never call real APIs in tests
- Every acceptance criterion from the PRD must have at least one test
- Follow test file naming and location conventions from `PROJECT.md`

## Security

- NEVER log tokens, passwords, or PII
- NEVER commit `.env`, credentials, or API keys
- NEVER disable security middleware for convenience
- Injection prevention appropriate to the tech stack (see `PROJECT.md`)
- See `PROJECT.md` for project-specific security rules

## Git Workflow

- Branches: `feat/description`, `fix/description`, `chore/description`
- Commits: conventional commits (`feat:`, `fix:`, `chore:`, `docs:`)
- PRs: require CI pass + human approval
- Squash merge to main

## Development Workflow

### Feature Development (idea -> merge)

```
1. Human provides feature idea
2. product-manager agent -> creates PRD in docs/prds/
3. Human reviews + approves PRD
3.5. discuss skill -> captures preferences in CONTEXT-[feature].md
4. architect agent -> creates design doc in docs/architecture/
5. Human reviews + approves design
6. implementer agent -> writes code on feature branch
7. tester agent -> validates acceptance criteria, writes tests
7.5. verify skill -> maps acceptance criteria to evidence
8. code-reviewer agent -> reviews all changes
9. Human reviews PR and merges
```

### Bug Fixing

```
1. Human describes the bug
2. debugger agent -> investigates root cause
3. Human approves proposed fix
4. implementer agent -> applies fix
5. tester agent -> adds regression test
6. code-reviewer agent -> reviews fix
7. Human reviews and merges
```

## Boundaries

### ALWAYS (agents can do freely)
- Read any file in the project
- Run tests, linters, type checks
- Create/edit source files and test files
- Create branches and commits

### ASK FIRST (requires human approval)
- Add new dependencies
- Modify database schemas
- Change shared interfaces or API contracts
- Modify CI/CD configuration
- Delete files or directories

### NEVER
- Commit secrets, API keys, or credentials
- Modify existing migration files after they've been applied
- Push to main/master directly
- Bypass the project's type safety settings (see PROJECT.md)
- Skip writing tests for new logic

## Context Management

- For multi-phase implementations, spawn fresh sub-agents per phase to prevent
  context degradation (quality drops as context windows fill)
- The `/execute` skill should use the implementer agent per task, not accumulate
  all implementation work in a single agent session
- For complex debugging, save progress to `docs/rca/` and spawn fresh debugger
  agents for new hypotheses
- If you notice quality degradation (repetition, confusion, rushed output), save
  state with `/pause` and start a fresh session with `/resume`
