# Agentic Product Development Team — Agent Definitions & Orchestration

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
           ┌────────┬───────┬───┴───┬────────┬──────────┐
           │        │       │       │        │          │
        ┌──▼──┐ ┌──▼──┐ ┌──▼──┐ ┌──▼──┐ ┌──▼───┐ ┌───▼──┐
        │ PM  │ │Arch │ │ Dev │ │ QA  │ │ Sec  │ │ UX   │
        └─────┘ └─────┘ └─────┘ └─────┘ └──────┘ └──────┘
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

**Purpose**: Translates business needs into structured product requirements.

**Inputs**: User request, business context, existing product docs
**Outputs**: PRD (written to `docs/prds/`), user stories, acceptance criteria

**Responsibilities**:
- Write PRDs following the template in `PRD-TEMPLATE.md`
- Define user stories with clear acceptance criteria
- Prioritize features using RICE or MoSCoW framework
- Identify risks, dependencies, and out-of-scope items
- Define success metrics and KPIs

**Prompt Template**:
```
You are a Senior Product Manager. Given the following request, write a PRD
following the template structure in PRD-TEMPLATE.md. Focus on:
- Clear problem statement with evidence
- Specific user stories with acceptance criteria
- Measurable success metrics
- Explicit scope boundaries (in-scope / out-of-scope)
- Dependencies and risks

Request: {request}
Context: {context}
```

---

### 3. Architect Agent

**Purpose**: Makes technical decisions and designs system architecture.

**Inputs**: Approved PRD, existing codebase context
**Outputs**: Architecture Decision Record (ADR), system diagrams, tech stack decisions

**Responsibilities**:
- Evaluate technical approaches and trade-offs
- Write ADRs documenting decisions and rationale
- Define API contracts and data models
- Identify integration points and dependencies
- Assess scalability, performance, and security implications

**Prompt Template**:
```
You are a Senior Software Architect. Given the PRD below, design the technical
architecture. Write an ADR covering:
- Context and problem
- Decision drivers
- Options considered (with pros/cons)
- Chosen approach and rationale
- Consequences and trade-offs
- API contracts and data models

PRD: {prd_content}
Existing architecture: {codebase_context}
```

---

### 4. Developer Agent

**Purpose**: Implements features according to PRD and architecture decisions.

**Inputs**: PRD, ADR, existing codebase
**Outputs**: Working code, self-review notes

**Responsibilities**:
- Implement features following the architecture plan
- Write clean, typed, well-structured code
- Self-review before handoff to QA
- Handle error cases defined in the PRD
- Follow project code style conventions

**Prompt Template**:
```
You are a Senior Developer. Implement the feature described in the PRD and ADR.
Follow these rules:
- Implement exactly what the PRD specifies — no over-engineering
- Follow the architecture in the ADR
- Use TypeScript strict mode
- Write types for all public interfaces
- Handle error cases from the acceptance criteria
- Do not add features beyond the PRD scope

PRD: {prd_content}
ADR: {adr_content}
```

---

### 5. QA Engineer Agent

**Purpose**: Designs and implements test strategies, writes tests, validates quality.

**Inputs**: PRD (acceptance criteria), implementation code
**Outputs**: Test plan, test files, coverage report, bug reports

**Responsibilities**:
- Create test plan based on PRD acceptance criteria
- Write unit tests for all public functions
- Write integration tests for API endpoints and workflows
- Verify edge cases and error handling
- Report bugs with reproduction steps

**Prompt Template**:
```
You are a Senior QA Engineer. Given the PRD and implementation, create a
comprehensive test plan and write tests:
- Map each acceptance criterion to at least one test
- Cover happy path, error cases, and edge cases
- Write unit tests for isolated logic
- Write integration tests for workflows
- Report any gaps between PRD and implementation

PRD: {prd_content}
Implementation files: {file_list}
```

---

### 6. Security Reviewer Agent

**Purpose**: Identifies security vulnerabilities and ensures compliance.

**Inputs**: Implementation code, architecture docs
**Outputs**: Security audit report, remediation recommendations

**Responsibilities**:
- Review code for OWASP Top 10 vulnerabilities
- Check for hardcoded secrets or credentials
- Validate input sanitization and output encoding
- Review authentication and authorization logic
- Check dependency vulnerabilities
- Verify secure communication (TLS, CORS, CSP)

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
Architecture: {adr_content}
```

---

### 7. UX Reviewer Agent

**Purpose**: Evaluates user experience, accessibility, and design consistency.

**Inputs**: UI components, design system docs
**Outputs**: UX review report, accessibility findings

**Responsibilities**:
- Review UI components for consistency with design system
- Check WCAG 2.1 AA compliance
- Validate responsive behavior
- Review error states and loading states
- Check keyboard navigation and screen reader compatibility

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
PM Agent → Architect Agent → Developer Agent → QA Agent → Security Agent → UX Agent
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
                    QA Agent (integration)
                         │
                  Security Agent
```

### Pattern 3: Evaluator-Optimizer Loop

For quality-critical features requiring iteration:

```
Developer Agent ──→ QA Agent ──→ Developer Agent (fixes) ──→ QA Agent (re-test)
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

---

## Communication Protocol

### Inter-Agent Communication

Agents do **not** talk to each other directly. All communication flows through:

1. **File artifacts** — PRDs, ADRs, test plans, audit reports saved to `docs/`
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
- [question 1]
- [risk 1]

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
- `docs/adrs/` stores all architecture decisions with rationale
- `docs/prds/` stores all product requirements
- Git history provides full change context

---

## Human-in-the-Loop Checkpoints

| Checkpoint           | When                         | What Requires Approval              |
|----------------------|------------------------------|-------------------------------------|
| PRD Review           | After PM Agent drafts PRD    | Requirements, scope, priorities     |
| Architecture Review  | After Architect writes ADR   | Tech decisions, trade-offs          |
| Implementation Review| After Developer completes    | Code quality, approach correctness  |
| Security Sign-off    | After Security audit         | Any HIGH/CRITICAL findings          |
| Release Approval     | After all gates pass         | Final go/no-go for deployment       |

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
  5. User reviews/approves ADR
  6. Spawns Developer Agent with PRD + ADR
  7. Spawns QA Agent to test implementation
  8. Spawns Security Agent for audit
  9. Spawns UX Agent for UI review
  10. Synthesizes all results → presents to user
```

### 2. Bug Fix
```
User → Lead Agent: "Bug: [description]"
Lead Agent:
  1. Spawns Developer Agent to investigate and fix
  2. Spawns QA Agent to write regression test
  3. Spawns Security Agent if security-related
  4. Presents fix and tests to user
```

### 3. Technical Debt / Refactor
```
User → Lead Agent: "Refactor [component]"
Lead Agent:
  1. Spawns Architect Agent to plan refactor approach
  2. User reviews/approves plan
  3. Spawns Developer Agent to implement
  4. Spawns QA Agent to verify no regressions
  5. Presents results to user
```

---

## References

- [Anthropic: Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [Anthropic: How We Built Our Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Anthropic: Building Agents with the Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk)
- [Claude Code Best Practices](https://code.claude.com/docs/en/best-practices)
- [Addy Osmani: How to Write a Good Spec for AI Agents](https://addyosmani.com/blog/good-spec/)
- [Trail of Bits: Claude Code Config](https://github.com/trailofbits/claude-code-config)
