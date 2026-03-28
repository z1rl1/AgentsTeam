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
delegates to specialists.

### How Subagents Work

Subagents are **isolated instances** with their own context window. Key principles:

1. **Context isolation** — each subagent gets a clean context, not polluted by the parent's history
2. **Automatic selection** — the parent agent picks the right subagent based on `description`
3. **One task, one lifecycle** — subagent is created, executes its task, returns a summary, and is destroyed
4. **Economy** — only `name` and `description` are loaded into the parent's context; full instructions stay in the subagent
5. **Model flexibility** — expensive models (opus) for complex reasoning, cheap models (sonnet) for routine tasks

### Core Team (Development Workflow)

| Agent | Role | Model | Mode | Skills | Denied Tools | maxTurns | Effort | Background | Isolation |
|-------|------|-------|------|--------|-------------|----------|--------|------------|-----------|
| `product-manager` | PRDs, user stories, acceptance criteria | opus | plan | new-feature, discuss, bootstrap | Edit, Bash | 30 | high | no | — |
| `architect` | System design, API contracts, data models | opus | plan | plan | Edit | 30 | high | no | — |
| `implementer` | Code writing, feature implementation | inherit | acceptEdits | execute, quick, refactor, fix-bug, migrate | — | 50 | high | no | worktree |
| `code-reviewer` | Quality, performance, standards review | inherit | plan | review-code | Write, Edit | 20 | high | yes | — |
| `tester` | Test writing, coverage, validation | sonnet | acceptEdits | e2e-test, validate, verify | — | 40 | medium | no | — |
| `debugger` | Root cause analysis, bug investigation | inherit | plan | fix-bug, rca | Write, Edit | 30 | high | no | — |
| `docs-writer` | API docs, architecture docs, changelogs | sonnet | acceptEdits | onboard, release | Bash, Edit | 20 | medium | yes | — |

### Utility Agents (Specialized Tasks)

| Agent | Role | Model | Mode | Skills | Denied Tools | maxTurns | Effort | Background | Memory |
|-------|------|-------|------|--------|-------------|----------|--------|------------|--------|
| `researcher` | Web/codebase search, information gathering | sonnet | plan | prime, onboard | Write, Edit, Bash | 15 | medium | yes | user |
| `security-reviewer` | OWASP Top 10, secrets, injection, auth audit | inherit | plan | security-audit | Write, Edit | 25 | high | yes | project |
| `devops` | Docker, CI/CD, deployment, infrastructure | inherit | plan | update-deps, migrate, release | WebSearch, WebFetch | 30 | medium | no | project |
| `performance-analyst` | Profiling, bottleneck identification | sonnet | plan | perf | Write, Edit | 20 | medium | yes | project |

### Agent Interaction Map

```
                    ┌─────────────────┐
                    │   Team Lead     │
                    │ (main session)  │
                    └────────┬────────┘
                             │ delegates
            ┌────────────────┼────────────────┐
            │                │                │
     ┌──────▼──────┐  ┌─────▼──────┐  ┌──────▼──────┐
     │   product-   │  │  architect  │  │  researcher  │
     │   manager    │  │            │  │  (isolated)  │
     │  (PRD)       │  │ (design)   │  │  (web/code)  │
     └──────┬──────┘  └─────┬──────┘  └─────────────┘
            │               │
            ▼               ▼
     ┌─────────────────────────────┐
     │       implementer           │
     │  (code, per-phase fresh)    │
     └──────────┬──────────────────┘
                │
       ┌────────┼────────┐
       │        │        │
  ┌────▼───┐ ┌──▼───┐ ┌──▼──────────┐
  │ tester │ │ code-│ │ security-   │
  │        │ │review│ │ reviewer    │
  └────────┘ └──────┘ └─────────────┘
                │
          ┌─────▼──────┐
          │ docs-writer │
          └────────────┘
```

### Permission Modes Explained

| Mode | Can Read | Can Edit | Can Execute | Use Case |
|------|----------|----------|-------------|----------|
| `plan` | Yes | No | Limited | Review, design, investigation — propose only |
| `acceptEdits` | Yes | Yes | Yes | Implementation, testing, documentation |
| `default` | Yes | Ask | Ask | Research, general tasks |

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

### Self-Improvement (Karpathy Loop + Hooks)
- `/generate-eval [skill-name]` -- Generate eval.json with binary assertions for a skill
- `/self-improve [skill-name]` -- Run autonomous improvement loop on one skill (Karpathy pattern)
- `/overnight [--target-score N]` -- Launch overnight improvement across ALL skills (sleep → wake up to better skills)
- `/skill-health` -- Dashboard: quality scores, trends, and recommendations for all skills

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
  agents/              -- Agent definitions (role, tools, model, system prompt)
  skills/              -- Workflow skills and domain knowledge (SKILL.md format)
    [skill]/eval/      -- Eval files: eval.json, improvement-log.json, improvement-report.md
  hooks/               -- Hook lifecycle scripts
    lib/               -- Shared libraries (eval-engine.sh, metrics.sh, utils.sh)
    logs/              -- Execution logs, eval results, session reports (JSONL + MD)
    metrics/           -- Per-skill score history ([skill].jsonl)
    pre-skill-check.sh   -- PreToolUse: pre-flight health check
    log-skill-result.sh  -- PostToolUse: execution logging
    post-skill-eval.sh   -- PostToolUse: assertion evaluation + metrics
    session-report.sh    -- Stop: session health summary
  reference/           -- Tech-stack best practices (populated per project)
  settings.json        -- Shared team settings (committed, includes hooks config)
  settings.local.json  -- Personal settings (gitignored)
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

## Hooks System

Automated lifecycle hooks for skill quality monitoring and self-improvement.
Configured in `.claude/settings.json` under `hooks`. All scripts in `.claude/hooks/`.

### Hook Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     HOOK LIFECYCLE                                    │
│                                                                       │
│  PreToolUse                PostToolUse                    Stop        │
│  ┌──────────────┐         ┌──────────────────┐      ┌────────────┐  │
│  │ pre-skill-   │         │ log-skill-       │      │ session-   │  │
│  │ check.sh     │         │ result.sh        │      │ report.sh  │  │
│  │              │         │                  │      │            │  │
│  │ • Eval exist?│         │ • Log execution  │      │ • Daily    │  │
│  │ • Last score │         │ • JSONL format   │      │   summary  │  │
│  │ • Trend info │         │ • Response stats │      │ • Scores   │  │
│  │ • Inject ctx │         └──────────────────┘      │ • Suggest  │  │
│  └──────────────┘         ┌──────────────────┐      │   improve  │  │
│                           │ post-skill-      │      └────────────┘  │
│                           │ eval.sh          │                       │
│                           │                  │                       │
│                           │ • Run assertions │                       │
│                           │ • Score output   │                       │
│                           │ • Record metrics │                       │
│                           │ • Suggest fixes  │                       │
│                           └──────────────────┘                       │
└─────────────────────────────────────────────────────────────────────┘
```

### Hook Event Map

#### Project-Level Hooks (settings.json — always active)

| Event | Script | Purpose | Timeout |
|-------|--------|---------|---------|
| `PreToolUse → Skill` | `pre-skill-check.sh` | Pre-flight: check eval exists, inject last score & trend | 10s |
| `PostToolUse → Skill` | `log-skill-result.sh` | Log execution metadata (skill, args, response size) | 10s |
| `PostToolUse → Skill` | `post-skill-eval.sh` | Evaluate output against binary assertions, record metrics | 30s |
| `Stop` | `session-report.sh` | Generate session health summary with recommendations | 15s |

#### Agent-Level Hooks (frontmatter — active only while agent runs)

| Agent | Event | Script | Purpose | Timeout |
|-------|-------|--------|---------|---------|
| `code-reviewer` | `PreToolUse → Bash` | `validate-readonly-bash.sh` | Block destructive commands | 10s |
| `security-reviewer` | `PreToolUse → Bash` | `validate-readonly-bash.sh` | Block destructive commands | 10s |
| `debugger` | `PreToolUse → Bash` | `validate-readonly-bash.sh` | Block destructive commands | 10s |
| `performance-analyst` | `PreToolUse → Bash` | `validate-readonly-bash.sh` | Block destructive commands | 10s |
| `implementer` | `PostToolUse → Edit\|Write` | `post-edit-validate.sh` | Log edits, remind to validate | 10s |
| `tester` | `PostToolUse → Bash` | `log-test-result.sh` | Log test execution results | 10s |
| `devops` | `PreToolUse → Bash` | `validate-devops-bash.sh` | Block dangerous production ops | 10s |

#### Hook Scripts for Agents

| Script | Type | Used by | What it does |
|--------|------|---------|-------------|
| `validate-readonly-bash.sh` | PreToolUse | code-reviewer, security-reviewer, debugger, performance-analyst | Blocks `rm`, `git push`, `npm install`, file redirects — enforces read-only |
| `post-edit-validate.sh` | PostToolUse | implementer | Logs file edits, reminds to run validation |
| `log-test-result.sh` | PostToolUse | tester | Detects test commands, logs pass/fail results |
| `validate-devops-bash.sh` | PreToolUse | devops | Blocks `kubectl delete`, `docker prune`, force push, `DROP DATABASE` |

### Shared Libraries (`.claude/hooks/lib/`)

| Library | Purpose |
|---------|---------|
| `utils.sh` | Path resolution, JSON helpers, logging, skill detection |
| `eval-engine.sh` | Binary assertion evaluation engine — programmatically checks word count, patterns, structure, headings, code blocks, forbidden content |
| `metrics.sh` | Score tracking over time — record, query, trend analysis, aggregation across all skills |

### Data Flow

```
Skill executes
  │
  ├─→ pre-skill-check.sh reads metrics/[skill].jsonl
  │     └─→ injects {latest_score, trend, has_eval} into conversation
  │
  ├─→ log-skill-result.sh writes logs/skill-executions-YYYY-MM-DD.jsonl
  │
  ├─→ post-skill-eval.sh:
  │     ├─→ reads skills/[skill]/eval/eval.json (assertions)
  │     ├─→ runs eval-engine.sh against output
  │     ├─→ writes metrics/[skill].jsonl (score entry)
  │     ├─→ writes logs/eval-results-YYYY-MM-DD.jsonl
  │     └─→ returns {score, failures, suggestion} to conversation
  │
  └─→ session-report.sh (on Stop):
        ├─→ reads all metrics and logs
        └─→ writes logs/session-report-DATE-SESSION.md
```

### Eval Engine Capabilities

The eval engine (`lib/eval-engine.sh`) can programmatically check:

- **Word count**: under/over N words
- **Contains/not contains**: pattern matching (case-insensitive)
- **Markdown structure**: headings (##, ###), bullet points, numbered lists
- **Code blocks**: presence and count
- **Line length**: max characters per line
- **First/last line**: empty check, question mark check
- **Numbers/statistics**: presence of numeric data
- **Forbidden characters**: em-dashes, specific symbols
- **Non-empty output**: basic sanity check

Assertions that can't be evaluated programmatically are flagged as `needs_ai`
and excluded from the automated score (handled by the AI in `/self-improve`).

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `SKILL_EVAL_THRESHOLD` | `80` | Score below this triggers improvement suggestion |
| `CLAUDE_PROJECT_DIR` | `.` | Project root (set by Claude Code) |

## Skill Self-Improvement

Autonomous skill quality improvement based on the Karpathy auto-research pattern.

### Overview

Two-layer system:
1. **Passive monitoring** — hooks automatically evaluate every skill call and track metrics
2. **Active improvement** — `/self-improve` runs the Karpathy loop to fix failing assertions

### Workflow

```
/generate-eval [skill]     ← Step 1: Create eval.json with binary assertions
                             (25-35 assertions across 5 test cases)

[normal usage]             ← Step 2: Hooks passively evaluate and track scores
                             (PostToolUse → post-skill-eval.sh)

/skill-health              ← Step 3: Review dashboard, identify weak skills

/self-improve [skill]      ← Step 4: Run autonomous improvement loop
                             (Karpathy pattern: change → test → commit/revert → repeat)

/skill-health              ← Step 5: Verify improvement
```

### Binary Assertions

Assertions in `eval.json` must be **binary (true/false)**, not subjective:

| Good (binary) | Bad (subjective) |
|---------------|-----------------|
| "Output contains heading ##" | "Output is well-structured" |
| "Word count under 300" | "Appropriate length" |
| "Does not end with question" | "Has good ending" |
| "Contains at least 1 code block" | "Good code examples" |
| "No em-dashes in output" | "Professional formatting" |

### Skills

- `/generate-eval [skill]` — Generate eval.json with binary assertions
- `/self-improve [skill]` — Run the Karpathy improvement loop (autonomous, no human input needed)
- `/skill-health` — Dashboard: scores, trends, recommendations for all skills

### Two Layers of Improvement

1. **Activation accuracy** — use Anthropic's built-in skill-creator for YAML description tuning
2. **Output quality** — use `/self-improve` with binary assertions (Karpathy loop + hooks)

## Context Management

- For multi-phase implementations, spawn fresh sub-agents per phase to prevent
  context degradation (quality drops as context windows fill)
- The `/execute` skill should use the implementer agent per task, not accumulate
  all implementation work in a single agent session
- For complex debugging, save progress to `docs/rca/` and spawn fresh debugger
  agents for new hypotheses
- If you notice quality degradation (repetition, confusion, rushed output), save
  state with `/pause` and start a fresh session with `/resume`

## Subagent Architecture

### Design Principles

1. **Context isolation is the primary value** — subagents protect the parent's context
   window from noise. A researcher agent fetches 50 web pages but returns 200 words.
2. **One task per subagent** — created, executes, returns summary, destroyed. No reuse.
3. **Fresh eyes catch more** — code-reviewer and security-reviewer work better with
   clean context because they see the code without development assumptions.
4. **Model economy** — use sonnet for routine tasks (research, testing, docs),
   opus for complex reasoning (PRD, architecture), inherit for tasks that need
   the same capability as the parent.
5. **Parallel where possible** — code-reviewer + security-reviewer + tester can
   run in parallel during `/review-code` since they don't depend on each other.

### Agent Definition Format

Each agent is a Markdown file in `.claude/agents/` with YAML frontmatter:

```yaml
---
name: agent-name           # Unique identifier, used in Agent() calls
description: ...           # What it does — ONLY this is visible to parent agent
tools: Read, Glob, ...     # Which tools this agent can use
disallowedTools: Write, Edit  # Tools explicitly DENIED (safety boundary)
model: opus|sonnet|inherit # LLM model to use
permissionMode: plan|acceptEdits|default  # What actions are allowed
memory: user|project|local # Persistent memory scope (cross-session learning)
maxTurns: 30               # Max agentic turns (prevents infinite loops)
effort: high               # Reasoning effort: low|medium|high
background: false          # Run in background (true) or foreground (false)
isolation: worktree        # Git worktree isolation for safe parallel work
skills:                    # Skills injected into subagent context at startup
  - review-code
  - security-audit
---
```

**Key fields:**
- `tools` — whitelist of tools the agent CAN use
- `disallowedTools` — explicit blacklist of tools the agent MUST NOT use (overrides tools)
- `skills` — list of project skills (from `.claude/skills/`) injected into context at startup
- `permissionMode` — controls whether the agent can write files or only propose
- `maxTurns` — safety limit to prevent runaway agents
- `effort` — controls reasoning depth (high for complex tasks, medium for routine)
- `background` — true = runs concurrently while main conversation continues
- `isolation` — `worktree` gives the agent an isolated git copy for safe changes
- `memory` — `user` (all projects), `project` (shared via git), `local` (gitignored)

The body contains the system prompt: role, process, output format, rules, and
coordination notes explaining how this agent interacts with others.

### Agent Capabilities Matrix

| Agent | skills | disallowedTools | maxTurns | effort | background | isolation | Rationale |
|-------|--------|-----------------|----------|--------|------------|-----------|-----------|
| `product-manager` | new-feature, discuss, bootstrap | Edit, Bash | 30 | high | no | — | Creates PRDs, no code editing needed |
| `architect` | plan | Edit | 30 | high | no | — | Designs systems, writes docs, no code editing |
| `implementer` | execute, quick, refactor, fix-bug, migrate | — | 50 | high | no | worktree | Full access, isolated git copy for safe changes |
| `code-reviewer` | review-code | Write, Edit | 20 | high | yes | — | Reviews in background, must not modify code |
| `tester` | e2e-test, validate, verify | — | 40 | medium | no | — | Needs Write/Edit to create test files |
| `debugger` | fix-bug, rca | Write, Edit | 30 | high | no | — | Investigates only, proposes fixes without applying |
| `docs-writer` | onboard, release | Bash, Edit | 20 | medium | yes | — | Writes docs in background, no shell needed |
| `researcher` | prime, onboard | Write, Edit, Bash | 15 | medium | yes | — | Read-only research, runs in background |
| `security-reviewer` | security-audit | Write, Edit | 25 | high | yes | — | Audits in background, must not change code |
| `performance-analyst` | perf | Write, Edit | 20 | medium | yes | — | Analyzes in background, does not apply optimizations |
| `devops` | update-deps, migrate, release | WebSearch, WebFetch | 30 | medium | no | — | Infrastructure tasks, needs human approval |

### When to Use Which Agent

| Situation | Agent | Why |
|-----------|-------|-----|
| Need info from the web | `researcher` | Isolates web noise from your context |
| Planning a new feature | `product-manager` | Creates structured, agent-executable PRDs |
| Designing architecture | `architect` | Technical decisions, API contracts |
| Writing code | `implementer` | Per-phase, fresh context each time |
| Code changes need review | `code-reviewer` | Clean eyes, unbiased perspective |
| Security concerns | `security-reviewer` | Dedicated OWASP checklist |
| Tests needed | `tester` | Maps PRD criteria to test cases |
| Something is broken | `debugger` | Methodical RCA, proposes fixes |
| Need documentation | `docs-writer` | API docs, changelogs, READMEs |
| Deployment tasks | `devops` | Docker, CI/CD, server config |
| Performance issues | `performance-analyst` | Profiling, bottleneck analysis |

### Subagent Communication Pattern

```
Parent Agent                    Subagent
     │                              │
     │  1. Create with task prompt  │
     ├─────────────────────────────►│
     │                              │
     │     (subagent reads files,   │
     │      searches, analyzes —    │
     │      all in isolated ctx)    │
     │                              │
     │  2. Return concise summary   │
     │◄─────────────────────────────┤
     │                              │
     │  3. Subagent destroyed       │
     │                              ✕
     │
     │  Parent continues with
     │  clean context + summary
```

### Key Differences: Subagents vs Agent Teams

| Aspect | Subagents | Agent Teams |
|--------|-----------|-------------|
| Context | Isolated, one-way | Shared scratchpad |
| Communication | Only with parent | Between each other |
| Lifecycle | Single task, then destroyed | Persist during project |
| Capability | Defined subset of tools | Full Claude Code capability |
| Model | Can be cheaper (sonnet) | Each has own model |
| Best for | Focused tasks, context isolation | Complex multi-role collaboration |

This project primarily uses **subagents** for the development workflow, with
`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` enabled for future team capabilities.
