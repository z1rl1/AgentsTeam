# PRD Template — Agentic Product Development Team

> This template is designed to be consumed by both humans and AI agents.
> All acceptance criteria use GIVEN/WHEN/THEN predicates for direct test mapping.
> Based on patterns from Addy Osmani's agent spec guide, Anthropic's effective agent
> practices, and context-engineering research.

---

## Instructions for Use

1. Copy this template for each new feature
2. Save to `docs/prds/PRD-[feature-name].md`
3. Fill in all sections — mark unknowns with `[TBD]`
4. Have the product-manager agent (or human PM) complete the draft
5. Submit for review at the PRD Review checkpoint
6. Once approved, this becomes the source of truth for all downstream agents

---

# PRD: [Feature/Product Name]

**Status**: Draft | In Review | Approved | In Progress | Complete
**Author**: [Name or Agent]
**Created**: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD
**Priority**: P0 (critical) | P1 (high) | P2 (medium) | P3 (low)
**Reviewers**: [Names]

---

## 1. Objective

[1-2 sentences: What are we building and why? What user problem does it solve?]

### Core Principles
1. [Guiding principle 1]
2. [Guiding principle 2]
3. [Guiding principle 3]

---

## 2. Problem Statement

### What problem are we solving?
[Describe the user or business problem. Be specific. Include evidence — metrics,
user research quotes, support ticket volumes, competitive gaps.]

### Who has this problem?
[Target user segment. Persona, use case, technical level, context.]

### How do we know this is real?
[Data: user research, analytics, customer feedback, market analysis. Quantify impact.]

### What happens if we don't solve it?
[Business impact of inaction — churn, revenue loss, competitive disadvantage.]

---

## 3. User Stories

### US-1: [Imperative Title]

**As a** [persona]
**I want to** [action]
**So that** [benefit]

**Acceptance Criteria:**

```
GIVEN [precondition]
WHEN [action]
THEN [expected result]
AND [additional assertion]
```

```
GIVEN [precondition]
WHEN [action]
THEN [expected result]
```

**Examples:**

| Input | Expected Output |
|-------|----------------|
| `{"email": "valid@test.com"}` | `{"status": 201, "id": "usr_xxx"}` |
| `{"email": ""}` | `{"status": 400, "error": "Email required"}` |

**Complexity**: S (hours) | M (1-2 days) | L (3-5 days)
**Dependencies**: None

---

### US-2: [Imperative Title]

**As a** [persona]
**I want to** [action]
**So that** [benefit]

**Acceptance Criteria:**

```
GIVEN [precondition]
WHEN [action]
THEN [expected result]
```

**Complexity**: S | M | L
**Dependencies**: US-1

---

## 4. Scope

### In Scope
- [Feature/capability 1]
- [Feature/capability 2]

### Out of Scope
- [Excluded item 1] — Reason: [why excluded]
- [Excluded item 2] — Reason: [why excluded]

### Future Considerations
- [Potential future enhancement]

> **Agent rule**: Do NOT implement anything under "Out of Scope" or "Future Considerations".

---

## 5. Technical Context

### Relevant Files

| File | Purpose |
|------|---------|
| `[path from PROJECT.md]/[file]` | Logic to extend |
| `[path from PROJECT.md]/[file]` | Data model to modify |
| `[test path]/[file]` | Existing test patterns |

### Existing Patterns to Follow

```
// Paste a real code snippet from the codebase showing the pattern
// agents should replicate
```

### Data Model Changes (if applicable)

```
-- Describe any schema changes needed
```

### API Changes (if applicable)

```
METHOD /endpoint
  Request:  { field: type }
  Response: { field: type }
  Errors:   [relevant error codes]
```

### Constraints
- [Technical constraint — e.g., must work with existing auth system]
- [Performance constraint — e.g., response time < 200ms p95]
- [Compatibility constraint — e.g., must support Safari 14+]

### Dependencies

| Dependency            | Owner         | Status    | Risk if Delayed          |
|-----------------------|---------------|-----------|--------------------------|
| [API/service]         | [team]        | [status]  | [impact]                 |

---

## 6. Design & UX

### User Flow
```
[Step 1: User action] → [Step 2: System response] → [Step 3: ...] → Done
```

### Wireframes / Mockups
[Link to designs or describe layout]

### Accessibility Requirements
- WCAG 2.1 AA compliance
- Keyboard navigable
- Screen reader compatible
- Color contrast ratio >= 4.5:1

### Error States

| Error Condition       | User-Facing Message         | Recovery Action              |
|-----------------------|-----------------------------|------------------------------|
| [condition]           | [message]                   | [what user can do]           |

---

## 7. Non-Functional Requirements

| Requirement     | Target             | How to Validate              |
|-----------------|--------------------|------------------------------|
| API latency     | < 200ms p95        | Load test                    |
| Test coverage   | > 80% new code     | Coverage command             |
| Accessibility   | WCAG 2.1 AA        | Axe audit                    |
| Uptime          | 99.9%              | Monitoring                   |

---

## 8. Success Metrics

### Primary Metrics (must move)
| Metric          | Baseline    | Target       | How Measured             |
|-----------------|-------------|-------------- |--------------------------|
| [metric]        | [value]     | [target]     | [method]                 |

### Guardrail Metrics (must not regress)
- [Page load time stays under X ms]
- [Error rate stays below X%]
- [Existing feature Y continues working]

---

## 9. Implementation Phases

Follow the phase ordering from `PROJECT.md`. Customize phases for this feature.

### Phase 1: [Name — e.g., Data Layer]
1. [Specific task]
2. [Write tests for this phase]

**Validation**: Run validation command from `PROJECT.md`

### Phase 2: [Name — e.g., Service Layer]
1. [Specific task]
2. [Write tests]

**Validation**: Run validation command from `PROJECT.md`

### Phase 3+: [Continue as needed]

---

## 10. Rollout Plan

| Phase   | Audience         | Advance Criteria            | Rollback Trigger         |
|---------|------------------|-----------------------------|--------------------------|
| Alpha   | Internal team    | No P0 bugs                  | Any data loss            |
| Beta    | 10% of users     | Metrics trending positive   | Error rate > 5%          |
| GA      | 100% of users    | Beta targets met            | Per incident response    |

### Feature Flags
- Flag: `[feature_flag_name]`
- Default: off
- Rollout: gradual percentage

---

## 11. Risks & Mitigations

| Risk              | Likelihood  | Impact      | Mitigation                     |
|-------------------|-------------|-------------|--------------------------------|
| [risk]            | High/Med/Low| High/Med/Low| [strategy]                     |

---

## 12. Open Questions

| #  | Question                    | Owner         | Due Date   | Resolution |
|----|-----------------------------|---------------|------------|------------|
| 1  | [question]                  | [who decides] | [date]     | [TBD]      |

---

## 13. Boundaries

### ALWAYS (agent can do freely)
- Run tests, linters, type checks
- Create/edit files within scope of this feature
- Follow patterns from existing codebase

### ASK FIRST (requires human approval)
- Add new dependencies
- Modify database schemas beyond what's specified above
- Change shared interfaces

### NEVER
- Modify existing migration files
- Commit secrets or credentials
- Skip writing tests
- Bypass type safety rules from `PROJECT.md`

---

## 14. Validation Checklist

- [ ] All acceptance criteria have passing tests
- [ ] Validation command from `PROJECT.md` passes
- [ ] Type safety rules followed
- [ ] No secrets in code
- [ ] Migration is reversible (if applicable)
- [ ] Success criteria all met
- [ ] Code review approved

---

## Appendix

### Glossary
| Term      | Definition                                                   |
|-----------|--------------------------------------------------------------|
| [term]    | [definition]                                                 |

### Related Documents
- [Link to design doc]
- [Link to related PRDs]

### Revision History
| Date       | Author     | Changes                      |
|------------|------------|------------------------------|
| YYYY-MM-DD | [name]     | Initial draft                |

---

## Agent Processing Notes

> These notes help downstream agents parse and act on this PRD correctly.

### For Architect Agent
- Focus on Technical Context section and API/data model changes
- Use constraints to guide technology choices
- Dependencies determine integration sequencing

### For Implementer Agent
- User Stories define WHAT to build
- Acceptance Criteria define WHEN it's done
- Scope defines boundaries — respect "Out of Scope" strictly
- Implementation Phases define the ORDER of work

### For Tester Agent
- Map every GIVEN/WHEN/THEN to at least one test case
- Error States table requires negative test cases
- Non-Functional Requirements define performance targets
- Guardrail Metrics define regression test requirements

### For Security Agent
- Review data model changes for privacy/compliance risks
- API contracts need input validation and auth checks
- Feature flags: check for authorization bypass

### For UX Agent
- User Flow defines the interaction sequence
- Accessibility Requirements are non-negotiable
- Error States define all user-visible error experiences
