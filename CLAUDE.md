# CLAUDE.md — Agentic Product Development Team

## Project Overview

This is an agentic product development team powered by Claude. The team operates as a
multi-agent system where specialized agents handle different aspects of the product lifecycle:
requirements, architecture, implementation, testing, security, and UX review.

## Team Structure

The team follows an **Orchestrator-Workers** pattern (Anthropic's recommended pattern for
complex tasks where subtasks can't be pre-defined). A Lead Agent coordinates while
specialized agents work in isolated context windows.

| Role               | Agent File                        | Responsibility                        |
|--------------------|-----------------------------------|---------------------------------------|
| Lead / Orchestrator| `agents/lead.md`                  | Planning, delegation, synthesis       |
| Product Manager    | `agents/product-manager.md`       | PRDs, user stories, prioritization    |
| Architect          | `agents/architect.md`             | System design, tech decisions, ADRs   |
| Developer          | `agents/developer.md`             | Implementation, code review           |
| QA Engineer        | `agents/qa.md`                    | Testing strategy, test implementation |
| Security Reviewer  | `agents/security.md`              | Threat modeling, OWASP compliance     |
| UX Reviewer        | `agents/ux.md`                    | UI/UX review, accessibility           |

## Workflow

### Standard Feature Flow (Pipeline)

```
PRD → Architecture → Implementation → Testing → Security Audit → UX Review → Done
```

### Parallel Work (when dependencies are low)

```
Lead Agent decomposes task
  ├── Frontend Agent (UI components)
  ├── Backend Agent (API endpoints)
  └── DB Agent (schema, migrations)
Lead Agent synthesizes results
```

## Development Conventions

### Commands
- Build: `npm run build`
- Test: `npm test`
- Lint: `npm run lint`
- Type check: `npx tsc --noEmit`

### Code Style
- TypeScript strict mode
- Functional components with hooks (React)
- Named exports over default exports
- Descriptive variable names; avoid abbreviations
- One component per file

### Git Workflow
- Branch naming: `feat/`, `fix/`, `refactor/`, `docs/`, `test/`
- Commit format: `<type>(<scope>): <description>`
- PRs require at least one review before merge
- Squash merge to main

### Project Structure
```
src/
  agents/         # Agent definition files (.md)
  components/     # UI components
  services/       # Business logic and API clients
  utils/          # Shared utilities
  types/          # TypeScript type definitions
tests/            # Test files mirroring src/ structure
docs/             # Architecture Decision Records, specs
  prds/           # Product Requirements Documents
  adrs/           # Architecture Decision Records
```

## Boundaries (Three-Tier System)

### Always Do
- Run tests before marking implementation complete
- Follow the code style conventions above
- Write types for all public interfaces
- Use environment variables for configuration
- Log errors with structured context

### Ask First
- Adding new dependencies
- Changing database schema
- Modifying authentication/authorization logic
- Changing CI/CD pipeline configuration
- Architectural decisions that affect multiple services

### Never Do
- Commit secrets, API keys, or credentials
- Bypass security checks or linting
- Push directly to main branch
- Delete or modify production data
- Disable tests to make them pass

## Context Management

- Use `/clear` between unrelated tasks to prevent context pollution
- Delegate research-heavy work to subagents via the Task tool
- Keep the main orchestrator session lean — it should plan and route, not explore
- Store intermediate artifacts (specs, plans, ADRs) as files, not in conversation context
- Use Plan Mode for any task touching more than 2 files

## Agent Communication Protocol

Agents communicate through:
1. **Shared task list** — TaskCreate/TaskUpdate for tracking work items
2. **File artifacts** — specs, PRDs, ADRs written to `docs/`
3. **Lightweight summaries** — subagents return concise results, not full context
4. **Structured handoffs** — each agent outputs a defined format the next agent expects

## Quality Gates

Every feature must pass through these gates before merge:

| Gate              | Owner          | Criteria                                    |
|-------------------|----------------|---------------------------------------------|
| Requirements      | Product Manager| PRD approved, user stories defined           |
| Architecture      | Architect      | ADR written, tech stack confirmed            |
| Implementation    | Developer      | Code complete, self-reviewed, types passing  |
| Testing           | QA Engineer    | Unit + integration tests passing, coverage ok|
| Security          | Security       | No OWASP top-10 issues, secrets scanned      |
| UX                | UX Reviewer    | Accessible, responsive, consistent with DS   |
