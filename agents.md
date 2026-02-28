# Agentic Product Development Team — Agent Definitions & Orchestration

> This file serves dual purpose: detailed agent definitions for Claude Code,
> and universal agent instructions for all AI coding tools (AGENTS.md standard).

---

## Universal Instructions (for all AI tools)

**Tech Stack, Commands, Conventions**: See `PROJECT.md`.

**Code Style**: Single-responsibility functions, clear naming, no abbreviations.
Follow import ordering and file naming from `PROJECT.md`.

**Testing**: Factories/fixtures over hardcoded data. Mock externals. Every acceptance
criterion needs a test. Follow patterns from `PROJECT.md`.

**Security**: Never log secrets/PII, never commit `.env`, never disable security middleware.

**Git**: `feat/`, `fix/`, `chore/` branches. Conventional commits. Squash merge to main.

**Agent Pipeline**: PRD → Design Doc → Implementation → Tests → Review → Human Merge.

---

## Architecture Overview

This system uses Anthropic's **Orchestrator-Workers** pattern — the recommended approach
for complex tasks where subtasks cannot be pre-defined. A Lead Agent dynamically decomposes
work, delegates to specialized worker agents, and synthesizes results.

```
                         ┌──────────────┐
                         │  Lead Agent  │
                         │ (Orchestrator)│
                         └──────┬───────┘
                                │
       ┌────────┬───────┬───────┼───────┬──────────┬──────────┐
       │        │       │       │       │          │          │
    ┌──▼──┐ ┌──▼──┐ ┌──▼──┐ ┌──▼──┐ ┌──▼───┐ ┌───▼──┐ ┌───▼────┐
    │ PM  │ │Arch │ │Impl │ │Test │ │Review│ │Debug │ │ Docs   │
    └─────┘ └─────┘ └─────┘ └─────┘ └──────┘ └──────┘ └────────┘
```

### Design Principles (from Anthropic's "Building Effective Agents")

1. **Simplicity** — start with simple patterns; add complexity only when it demonstrably
   improves outcomes
2. **Transparency** — explicitly show planning steps and reasoning
3. **One job per agent** — each subagent has a single goal with clear inputs/outputs
4. **Narrow permissions** — orchestrator reads and routes; workers execute within scope
5. **File-based artifacts** — agents write outputs to files, not conversation context

---

## Agent Roles

### 1. Lead Agent (Orchestrator)

**Purpose**: Receives user requests, decomposes them into tasks, delegates to specialists,
synthesizes results, and manages quality gates.

**Capabilities**:
- Analyze incoming requests and determine required agents
- Create and manage task lists (TaskCreate, TaskUpdate)
- Spawn subagents via Task tool with appropriate prompts
- Synthesize outputs from multiple agents into coherent deliverables
- Enforce quality gates before marking features complete

**Permissions**: Read, Glob, Grep, Task (spawn subagents), TaskCreate, TaskUpdate

**Does NOT**: Write code, make architecture decisions, or skip quality gates.

**Workflow**:
```
1. Receive request
2. Analyze scope and complexity
3. Determine which agents are needed
4. Create task list with dependencies
5. Delegate to agents (sequential or parallel based on dependencies)
6. Review outputs at each quality gate
7. Synthesize final deliverable
8. Present result to user
```

---

### 2. Product Manager Agent

**File**: `.claude/agents/product-manager.md`
**Model**: opus | **Mode**: acceptEdits

**Purpose**: Translates business needs into structured, agent-executable PRDs.

**Inputs**: User request, business context, existing product docs
**Outputs**: PRD (written to `docs/prds/`), user stories, acceptance criteria

**Key Behaviors**:
- Creates PRDs following `docs/templates/PRD-TEMPLATE.md`
- All acceptance criteria use GIVEN/WHEN/THEN predicate format
- Analyzes codebase before planning to reference real file paths
- Each user story sized to fit in a single agent session
- Includes explicit scope boundaries and agent permissions
- Conducts market/technical research via WebSearch when needed

**Prompt Template**:
```
You are a Senior Product Manager. Given the following request, write a PRD
following the template structure in docs/templates/PRD-TEMPLATE.md. Focus on:
- Clear problem statement with evidence
- Specific user stories with GIVEN/WHEN/THEN acceptance criteria
- Measurable success metrics
- Explicit scope boundaries (in-scope / out-of-scope)
- File paths referencing actual codebase locations
- Dependencies and risks

Request: {request}
Context: {context}
```

---

### 3. Architect Agent

**File**: `.claude/agents/architect.md`
**Model**: opus | **Mode**: plan (read-only)

**Purpose**: Makes technical decisions and designs system architecture.

**Inputs**: Approved PRD, existing codebase context
**Outputs**: Design document at `docs/architecture/[feature-name].md`

**Key Behaviors**:
- Evaluates technical approaches with pros/cons/trade-offs
- Creates design docs with API contracts, data models, file change lists
- Defines implementation phases matching `PROJECT.md` structure
- Each phase independently testable with validation command
- Checks existing patterns before proposing new ones
- Never writes implementation code

**Design Document Structure**:
```markdown
# Technical Design: [Feature Name]

## Context
## Decision
## Alternatives Considered
## API Changes
## Data Model Changes
## File Changes (table with paths)
## Implementation Order (phased)
## Risks and Mitigations
```

---

### 4. Implementer Agent (Developer)

**File**: `.claude/agents/implementer.md`
**Model**: inherit | **Mode**: acceptEdits

**Purpose**: Implements features according to PRD and architecture decisions.

**Inputs**: PRD, design doc, existing codebase
**Outputs**: Working code, tests for new business logic

**Key Behaviors**:
- Follows existing code patterns — no gratuitous new abstractions
- Implements phase by phase from design doc
- Writes tests for all new business logic
- Runs validation command from `PROJECT.md` after every phase
- Commits with conventional commit messages after each passing phase
- Functions under 30 lines, descriptive naming, no abbreviations

---

### 5. Code Reviewer Agent

**File**: `.claude/agents/code-reviewer.md`
**Model**: inherit | **Mode**: plan (read-only)

**Purpose**: Reviews code for quality, security, performance, and standards adherence.

**Inputs**: Git diff of changes
**Outputs**: Structured review with severity-classified findings

**Review Checklist**:
- **Correctness**: edge cases, error handling, race conditions
- **Security**: secrets, injection, auth, input validation
- **Quality**: naming, SRP, duplication, dead code, type safety
- **Testing**: coverage, determinism, happy + error paths
- **Performance**: N+1 queries, unnecessary recomputation, blocking ops

**Output**: Findings classified as Critical / Warning / Suggestion / Positive Pattern,
with verdict: APPROVE or REQUEST CHANGES.

---

### 6. Tester Agent (QA Engineer)

**File**: `.claude/agents/tester.md`
**Model**: sonnet | **Mode**: acceptEdits

**Purpose**: Validates acceptance criteria and writes missing tests.

**Inputs**: PRD (acceptance criteria), implementation code
**Outputs**: Test files, coverage report, validation report

**Key Behaviors**:
- Maps every GIVEN/WHEN/THEN criterion to at least one test
- Uses Arrange/Act/Assert pattern
- Covers edge cases: null, empty, boundary, concurrent, auth
- Uses factories and fixtures, never hardcoded data
- Mocks external services, never calls real APIs
- Reports coverage with acceptance criteria mapping table

---

### 7. Debugger Agent

**File**: `.claude/agents/debugger.md`
**Model**: inherit | **Mode**: plan (read-only)

**Purpose**: Investigates bugs and performs root cause analysis.

**Inputs**: Bug description or GitHub issue ID
**Outputs**: RCA document with proposed fix

**Investigation Methodology**:
1. **Reproduce** — confirm the issue exists
2. **Locate** — find error origin in codebase
3. **Trace** — follow call chain backward to root
4. **Hypothesize** — form theory about cause
5. **Verify** — test theory against code evidence
6. **Document** — write up with file:line references

**Does NOT implement fixes** — diagnoses and proposes only.
Outputs include confidence level, regression risk, and similar patterns elsewhere.

---

### 8. Documentation Agent

**File**: `.claude/agents/docs-writer.md`
**Model**: sonnet | **Mode**: acceptEdits

**Purpose**: Creates and maintains developer-facing documentation.

**Outputs**: API docs, architecture guides, changelogs, README updates

**Key Behaviors**:
- Writes for developers new to the project
- Includes runnable code examples
- Uses Mermaid diagrams for visual architecture
- Follows Keep a Changelog format
- Updates existing docs rather than creating duplicates

---

### 9. Security Reviewer Agent

**Purpose**: Identifies security vulnerabilities and ensures compliance.

**Inputs**: Implementation code, architecture docs
**Outputs**: Security audit report, remediation recommendations

**Review Scope**:
- OWASP Top 10 vulnerability scan
- Hardcoded secrets and credentials
- Input sanitization on all external boundaries
- Authentication and authorization bypass vectors
- Injection risks (SQL, XSS, command injection)
- Dependency vulnerability check (known CVEs)
- Secure communication (TLS, CORS, CSP)

**Prompt Template**:
```
You are a Senior Security Engineer. Audit the implementation for security issues:
- Check for OWASP Top 10 vulnerabilities
- Scan for hardcoded secrets or credentials
- Validate input sanitization on all external boundaries
- Review auth logic for bypass vulnerabilities
- Check for injection risks (SQL, XSS, command injection)
- Review dependency security (known CVEs)

Implementation files: {file_list}
Architecture: {design_doc_content}
```

---

### 10. UX Reviewer Agent

**Purpose**: Evaluates user experience, accessibility, and design consistency.

**Inputs**: UI components, design system docs
**Outputs**: UX review report, accessibility findings

**Review Scope**:
- Design system consistency (spacing, colors, typography)
- WCAG 2.1 AA accessibility compliance
- Keyboard navigation support
- Screen reader compatibility (ARIA labels, semantic HTML)
- Responsive behavior across breakpoints
- Error states, empty states, loading states

**Prompt Template**:
```
You are a Senior UX Engineer. Review the UI implementation for:
- Design system consistency (spacing, colors, typography)
- WCAG 2.1 AA accessibility compliance
- Keyboard navigation support
- Screen reader compatibility (ARIA labels, semantic HTML)
- Responsive behavior across breakpoints
- Error states, empty states, and loading states

UI Components: {component_list}
Design System: {design_system_docs}
```

---

## Orchestration Patterns

### Pattern 1: Sequential Pipeline (Default)

For well-defined features with clear dependencies:

```
PM Agent → Architect Agent → Implementer Agent → Tester Agent → Code Review → Security → UX
```

Each agent's output feeds the next. Quality gates between each step.

### Pattern 2: Parallel Specialization

For features with independent frontend/backend/data work:

```
                    Architect Agent
                         │
              ┌──────────┼──────────┐
              │          │          │
         Frontend    Backend    Database
          Agent       Agent      Agent
              │          │          │
              └──────────┼──────────┘
                         │
                    Tester Agent (integration)
                         │
                  Code Reviewer Agent
```

### Pattern 3: Evaluator-Optimizer Loop

For quality-critical features requiring iteration:

```
Implementer Agent → Tester Agent → Implementer Agent (fixes) → Tester Agent (re-test)
                                         ↑                          │
                                         └──────────────────────────┘
                                           (loop until tests pass)
```

### Pattern 4: Research Spike

For exploratory work before committing to a plan:

```
Lead Agent spawns 3 Research Subagents in parallel
  ├── Research Agent A (approach 1)
  ├── Research Agent B (approach 2)
  └── Research Agent C (approach 3)
Lead Agent synthesizes findings → Architect Agent decides
```

### Pattern 5: Plan/Execute Loop

For complex features requiring upfront analysis:

```
/plan → human reviews → /execute → /validation:execution-report → /validation:system-review
```

Iterative: system-review feeds improvements back into CLAUDE.md and agent definitions.

---

## Communication Protocol

### Inter-Agent Communication

Agents do **not** talk to each other directly. All communication flows through:

1. **File artifacts** — PRDs, design docs, test plans, audit reports saved to `docs/`
2. **Task list** — shared task tracking via TaskCreate/TaskUpdate
3. **Orchestrator summaries** — Lead Agent passes relevant context when spawning workers

### Handoff Format

Each agent outputs a structured handoff:

```markdown
## Handoff: [Agent Role] → [Next Agent Role]

### Status: [Complete | Blocked | Needs Review]

### Deliverables
- [file path 1]: [description]
- [file path 2]: [description]

### Key Decisions
- [decision 1]
- [decision 2]

### Open Questions / Risks
- [question or risk]

### Next Steps
- [what the next agent should focus on]
```

---

## Memory & Context Management

### Short-Term (Session Context)
- Each agent works in its own context window via subagent isolation
- Use `/clear` between unrelated tasks in the main session
- Orchestrator keeps a lean context — plans and routes, does not explore

### Medium-Term (File Artifacts)
- All decisions, specs, and plans are written to files in `docs/`
- Agents read relevant artifacts at the start of their task
- File artifacts persist across sessions and context window resets

### Long-Term (Project Knowledge)
- `CLAUDE.md` stores stable project conventions and architecture overview
- `PROJECT.md` stores tech stack, commands, and project-specific config
- `docs/architecture/` stores all technical design documents
- `docs/prds/` stores all product requirements
- `docs/rca/` stores root cause analyses for bugs
- Git history provides full change context

---

## Human-in-the-Loop Checkpoints

| Checkpoint           | When                         | What Requires Approval              |
|----------------------|------------------------------|-------------------------------------|
| PRD Review           | After PM Agent drafts PRD    | Requirements, scope, priorities     |
| Architecture Review  | After Architect writes design| Tech decisions, trade-offs          |
| Implementation Review| After Developer completes    | Code quality, approach correctness  |
| Security Sign-off    | After Security audit         | Any HIGH/CRITICAL findings          |
| Release Approval     | After all gates pass         | Final go/no-go for deployment       |

### When Humans Must Intervene

- Requirements are ambiguous or acceptance criteria are missing
- Architectural decisions affect multiple services
- New external dependencies are being introduced
- Tests fail with unclear root cause
- Security-sensitive changes (auth, crypto, payments)
- High blast-radius changes (shared interfaces, database schemas)

---

## Quality Verification Lattice

Five-layer verification ensures nothing slips through:

```
Layer 1: DETERMINISTIC   — build, unit tests, lint, typecheck
Layer 2: SEMANTIC         — contract tests, golden tests, snapshots
Layer 3: SECURITY         — SAST, dependency scan, secret scan
Layer 4: AGENTIC          — code-reviewer agent for style + spec adherence
Layer 5: HUMAN            — escalations and final acceptance
```

---

## Agent Teams (Experimental)

Enable in `.claude/settings.json`:
```json
{"env": {"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"}}
```

Agent teams allow multiple Claude Code instances to work in parallel:
- **Team Lead**: coordinates work, spawns teammates
- **Teammates**: independent context windows, claim tasks from shared list
- **Task List**: shared with pending/in_progress/completed states and dependencies
- **Mailbox**: direct inter-agent messaging

Best for: parallel implementation of independent modules, concurrent research,
competing approaches to the same problem.

---

## Quick Commands Reference

| Need | Command |
|------|---------|
| Full feature pipeline | `/new-feature [description]` |
| Fix a bug | `/fix-bug [description or #issue]` |
| Review current changes | `/review-code` |
| Plan implementation | `/plan [feature]` |
| Execute a plan | `/execute [plan-path]` |
| Load project context | `/prime` |
| Atomic commit | `/commit` |
| Health check | `/validation:validate` |
| Post-implementation report | `/validation:execution-report [plan]` |
| Process improvement analysis | `/validation:system-review [plan] [report]` |
| GitHub issue RCA | `/github-issue:rca [issue-id]` |

---

## Getting Started

### 1. New Feature Request
```
User → Lead Agent: "We need [feature description]"
Lead Agent:
  1. Creates task list
  2. Spawns PM Agent to write PRD
  3. User reviews/approves PRD
  4. Spawns Architect Agent with approved PRD
  5. User reviews/approves design doc
  6. Spawns Implementer Agent with PRD + design doc
  7. Spawns Tester Agent to test implementation
  8. Spawns Code Reviewer Agent for review
  9. Spawns Security Agent for audit (if applicable)
  10. Spawns UX Agent for UI review (if applicable)
  11. Synthesizes all results → presents to user
```

### 2. Bug Fix
```
User → Lead Agent: "Bug: [description]" or "Fix #42"
Lead Agent:
  1. Spawns Debugger Agent to investigate root cause
  2. User reviews/approves proposed fix
  3. Spawns Implementer Agent to apply fix
  4. Spawns Tester Agent to write regression test
  5. Spawns Code Reviewer Agent for review
  6. Presents fix and tests to user
```

### 3. Technical Debt / Refactor
```
User → Lead Agent: "Refactor [component]"
Lead Agent:
  1. Spawns Architect Agent to plan refactor approach
  2. User reviews/approves plan
  3. Spawns Implementer Agent to implement
  4. Spawns Tester Agent to verify no regressions
  5. Presents results to user
```

---

## References

- [Anthropic: Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [Anthropic: How We Built Our Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Anthropic: Building Agents with the Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk)
- [Claude Code Sub-Agents](https://code.claude.com/docs/en/sub-agents)
- [Claude Code Agent Teams](https://code.claude.com/docs/en/agent-teams)
- [Claude Code Best Practices](https://code.claude.com/docs/en/best-practices)
- [Using CLAUDE.md Files](https://claude.com/blog/using-claude-md-files)
- [AGENTS.md Specification](https://agents.md/)
- [Addy Osmani: How to Write a Good Spec for AI Agents](https://addyosmani.com/blog/good-spec/)
