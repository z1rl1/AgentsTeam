# CLAUDE.md — Telegram Bot Development Team

## Project Overview

Agentic product development team for building **Telegram bots** with grammY framework.
Specialized AI agents handle the full lifecycle: requirements, architecture, implementation,
testing, review, debugging, and documentation.

> **Tech stack and commands** live in [`PROJECT.md`](PROJECT.md).

---

## Agent Team

Agents are defined in `.claude/agents/`. The main Claude Code session acts as team lead (orchestrator) and delegates to specialists.

| Agent             | Role                                     | Model   | When to Use                    |
|-------------------|------------------------------------------|---------|--------------------------------|
| `product-manager` | PRDs, user stories, acceptance criteria   | opus    | Planning new features          |
| `architect`       | System design, API contracts, ADRs        | opus    | Technical design decisions     |
| `implementer`     | Code writing, feature implementation      | inherit | Building features              |
| `code-reviewer`   | Quality, security, performance review     | inherit | After code changes             |
| `tester`          | Test writing, coverage, validation        | sonnet  | Verifying acceptance criteria  |
| `debugger`        | Root cause analysis, bug investigation    | inherit | Investigating bugs             |
| `docs-writer`     | API docs, architecture docs, changelogs   | sonnet  | Documentation tasks            |

---

## Skills

Custom skills in `.claude/skills/`:

### Core Workflows
- `/new-feature [description]` — Full pipeline: PRD → design → implement → test → review
- `/fix-bug [description]` — Bug pipeline: investigate → fix → test → review
- `/review-code` — Code review + test validation on current changes

### Plan/Execute
- `/plan [feature]` — Create implementation plan with codebase analysis
- `/execute [plan-path]` — Implement from a plan file, task by task
- `/prime` — Load project context (structure, docs, recent activity)
- `/commit` — Atomic commit with conventional prefix

### Validation
- `/validate` — Full project health check (lint, types, tests, build)
- `/execution-report [plan-path]` — Post-implementation analysis
- `/system-review [plan] [report]` — Meta-analysis: plan vs execution

### GitHub
- `/github-issue-rca [issue-id]` — Root cause analysis → `docs/rca/`

### Telegram Bot
- `/add-command [name]` — Create new bot command handler
- `/add-callback [name]` — Add callback query handler for inline buttons
- `/add-conversation [name]` — Create multi-step conversation dialog
- `/add-middleware [name]` — Add grammY middleware
- `/add-keyboard [name]` — Create inline or reply keyboard
- `/setup-webhook` — Configure webhook deployment
- `/add-menu` — Set up bot command menu via BotFather API

---

## Orchestration Patterns

### Sequential Pipeline (Default)
For well-defined features with clear dependencies:
```
PM → Architect → Implementer → Tester → Code Reviewer
```

### Parallel Specialization
For features with independent work streams:
```
              Architect
                  │
       ┌──────────┼──────────┐
    Frontend    Backend    Database
       │          │          │
       └──────────┼──────────┘
                  │
              Tester (integration)
```

### Evaluator-Optimizer Loop
For quality-critical features:
```
Implementer → Tester → Implementer (fixes) → Tester (re-test)
                              ↑                      │
                              └──────────────────────┘
```

### Research Spike
For exploratory work:
```
Lead spawns 3 Research Agents in parallel → synthesizes → Architect decides
```

---

## Development Workflow

### Feature Development
```
1. Human provides feature idea
2. product-manager → PRD in docs/prds/
3. Human reviews + approves
4. architect → design doc in docs/architecture/
5. Human reviews + approves
6. implementer → code on feature branch
7. tester → validates acceptance criteria
8. code-reviewer → reviews changes
9. Human merges
```

### Bug Fixing
```
1. Human describes bug (or GitHub issue ID)
2. debugger → root cause analysis
3. Human approves fix
4. implementer → applies fix
5. tester → regression test
6. code-reviewer → reviews
7. Human merges
```

---

## Directory Structure

```
.claude/
  agents/           # Agent definitions
  skills/           # Workflow skills (SKILL.md format)
  settings.json     # Shared team settings
  settings.local.json # Personal settings (gitignored)
docs/
  prds/             # Product Requirements Documents
  architecture/     # Technical design documents
  plans/            # Implementation plans
  rca/              # Root Cause Analysis documents
  templates/        # Document templates
src/
  bot/              # Bot setup and configuration
  commands/         # Bot command handlers (/start, /help, etc.)
  callbacks/        # Callback query handlers
  conversations/    # Multi-step conversation flows
  middleware/        # grammY middleware (auth, logging, etc.)
  keyboards/        # Keyboard builders (inline, reply)
  services/         # Business logic
  db/               # Database schema and queries (Drizzle)
  utils/            # Shared utilities
  types/            # TypeScript type definitions
tests/              # Test files mirroring src/ structure
CLAUDE.md           # This file
PROJECT.md          # Tech stack and commands
```

---

## Code Standards

- TypeScript strict mode, no `any` — use `unknown` and narrow
- `const` over `let`, never `var`
- Named exports, no default exports
- Functions under 30 lines; extract helpers when needed
- Error handling: never swallow errors silently
- All new business logic must have tests
- Functional patterns preferred over classes
- Run validation command from `PROJECT.md` before every commit

---

## Git Workflow

- Branch naming: `feat/`, `fix/`, `chore/`, `refactor/`, `docs/`, `test/`
- Commits: conventional format `<type>(<scope>): <description>`
- PRs require passing CI + human approval
- Squash merge to main

---

## Boundaries

### Always (agents can do freely)
- Read any file in the project
- Run tests, linters, type checks
- Create/edit source files and test files
- Create branches and commits

### Ask First (requires human approval)
- Adding new dependencies
- Changing database schema
- Modifying bot token or webhook configuration
- Changing shared interfaces or API contracts
- Architectural decisions affecting multiple modules

### Never
- Commit secrets, API keys, bot tokens, or credentials
- Bypass security checks or linting
- Push directly to main branch
- Delete or modify production data
- Modify existing migration files after they've been applied
- Disable tests to make them pass

---

## Agent Communication Protocol

Agents do not talk to each other directly. Communication flows through:

1. **File artifacts** — PRDs, design docs, test plans saved to `docs/`
2. **Shared task list** — TaskCreate/TaskUpdate for tracking work items
3. **Orchestrator summaries** — Lead passes relevant context when spawning workers

### Handoff Format

```markdown
## Handoff: [Agent Role] → [Next Agent Role]

### Status: [Complete | Blocked | Needs Review]

### Deliverables
- [file path 1]: [description]

### Key Decisions
- [decision]

### Open Questions / Risks
- [question or risk]

### Next Steps
- [what the next agent should focus on]
```

---

## Context Management

- Use `/clear` between unrelated tasks
- Delegate research-heavy work to subagents
- Keep the orchestrator session lean — plan and route, don't explore
- Store specs, plans, ADRs as files, not in conversation context
- Use Plan Mode for any task touching more than 2 files

---

## Quality Gates

| Gate              | Owner           | Criteria                                     |
|-------------------|-----------------|----------------------------------------------|
| Requirements      | Product Manager | PRD approved, stories defined                |
| Architecture      | Architect       | Design doc written, approach confirmed       |
| Implementation    | Developer       | Code complete, validation passing            |
| Testing           | QA Engineer     | All acceptance criteria tested, coverage ok  |
| Code Review       | Code Reviewer   | Quality, performance, security approved      |

## Human-in-the-Loop Checkpoints

| Checkpoint            | When                          | What Requires Approval               |
|-----------------------|-------------------------------|--------------------------------------|
| PRD Review            | After PM drafts PRD           | Requirements, scope, priorities      |
| Architecture Review   | After Architect writes design | Tech decisions, trade-offs           |
| Implementation Review | After Developer completes     | Code quality, approach correctness   |
| Release Approval      | After all gates pass          | Final go/no-go for deployment        |
