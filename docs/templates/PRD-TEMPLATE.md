# PRD: [Feature Name]

**Status**: Draft | In Review | Approved | In Progress | Complete
**Author**: [name]
**Created**: [date]
**Priority**: P0 (critical) | P1 (high) | P2 (medium) | P3 (low)

---

## 1. Objective

[1-2 sentences: What are we building and why? What user problem does it solve?]

## 2. Mission

[Product mission statement for this feature. What principle does it serve?]

### Core Principles
1. [Principle 1]
2. [Principle 2]
3. [Principle 3]

## 3. Background

[Brief context: current state, motivation, relevant decisions. 2-3 sentences.]

## 4. Target Users

[Who benefits from this feature? What is their technical level? What are their key needs?]

## 5. User Stories

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

**Complexity**: S | M | L
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

## 6. Technical Context

### Relevant Files

| File | Purpose |
|------|---------|
| `[path from PROJECT.md]/[relevant]` | Logic to extend |
| `[path from PROJECT.md]/[relevant]` | Data model to modify |
| `[path from PROJECT.md]/[relevant]` | API/route layer |
| `[test path from PROJECT.md]/[relevant]` | Existing test patterns |

### Existing Patterns to Follow

```
// Example from codebase showing the pattern agents should replicate
// (paste a real code snippet here)
```

### Data Model Changes (if applicable)

```
-- Describe any schema changes needed for this feature
```

### API Changes (if applicable)

```
METHOD /endpoint
  Request:  { field: type }
  Response: { field: type }
  Errors:   [relevant error codes]
```

## 7. Non-Functional Requirements

| Requirement | Target | How to Validate |
|-------------|--------|----------------|
| API latency | < 200ms p95 | Load test |
| Test coverage | > 80% new code | Coverage command from `PROJECT.md` |
| Accessibility | WCAG 2.1 AA | Axe audit |

## 8. Implementation Phases

Follow the phase ordering from `PROJECT.md`. Customize phases below for this feature.

### Phase 1: [Name from PROJECT.md]

1. [Tasks for this phase]
2. [Write tests]

**Validation**: Run validation command from `PROJECT.md`

### Phase 2: [Name from PROJECT.md]

1. [Tasks for this phase]
2. [Write tests]

**Validation**: Run validation command from `PROJECT.md`

### Phase 3+: [Continue as needed]

Add or remove phases based on the project's architecture (see `PROJECT.md`).

## 9. Success Criteria

### Functional
- [ ] All acceptance criteria from user stories pass
- [ ] All API endpoints return correct status codes
- [ ] Error states handled and surfaced to user

### Quality
- [ ] Test coverage > 80% for new code
- [ ] Type safety rules from `PROJECT.md` followed
- [ ] All linting and type checks pass

### User Experience
- [ ] [Specific UX goals for this feature]

## 10. Out of Scope

- [Explicitly list what this PRD does NOT cover]
- [Prevents scope creep during implementation]

## 11. Boundaries

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
- Bypass type safety rules (see `PROJECT.md`)

## 12. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| [What could go wrong] | High/Med/Low | [Strategy] |

## 13. Future Considerations

- [Post-MVP enhancements]
- [Integration opportunities]
- [Advanced features for later phases]

## 14. Validation Checklist

- [ ] All acceptance criteria have passing tests
- [ ] Validation command from `PROJECT.md` passes (tests, type check, lint)
- [ ] Type safety rules from `PROJECT.md` followed
- [ ] No secrets in code
- [ ] Migration is reversible (if applicable)
- [ ] Success criteria all met
