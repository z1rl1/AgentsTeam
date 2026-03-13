# Product Requirements Document (PRD)

A template for collaborative work between product teams and autonomous development agents.  
Acceptance conditions use structured rules so they can be mapped directly to tests and automation.

---

## Document Metadata

| Field | Value |
|------|----------|
| **PRD** | [Feature / Capability Name] |
| **Stage** | Draft \| Review \| Approved \| Building \| Released |
| **Owner** | [Product Manager / Agent] |
| **Created** | YYYY-MM-DD |
| **Updated** | YYYY-MM-DD |
| **Priority** | P0 \| P1 \| P2 \| P3 |
| **Stakeholders** | [Names or teams] |

---

## 1. Overview

### Feature Summary

Describe briefly what this feature introduces and the main value it delivers to the user.

> **Example:** This feature allows users to create automated reports from analytics data and export them as scheduled emails.

### Strategic Goal

Explain how this feature supports the product strategy or roadmap.

---

## 2. Problem Description

### Current Situation

Describe how things work today.

### User Pain Points

Main difficulties users face:

- Pain point 1  
- Pain point 2  
- Pain point 3  

### Evidence

Supporting information such as:

- analytics data  
- support tickets  
- user interviews  
- competitive gaps  

### Impact if Ignored

What happens if the problem remains unsolved.

---

## 3. Target Audience

| Segment | Description | Needs |
|---------|-------------|--------|
| [Segment name] | [Who they are] | [Primary need] |

Include relevant characteristics:

- experience level  
- environment (mobile / desktop)  
- technical knowledge  

---

## 4. User Scenarios

Describe the core workflows supported by the feature.

### Scenario 1 — [Action Title]

**User role:** [persona]

**Goal:** The user wants to perform an action in order to achieve a specific outcome.

**Acceptance Conditions:**

```
GIVEN [initial state]
WHEN [user performs action]
THEN [system produces result]

GIVEN [state]
WHEN [action]
THEN [result]
AND [extra validation]
```

**Example Cases:**

| Request | Result |
|---------|--------|
| `{email:"test@test.com"}` | `{status:201, user_id:"abc123"}` |
| `{email:""}` | `{status:400, error:"email required"}` |

- **Estimated Effort:** Small \| Medium \| Large  
- **Blocked By:** [dependency]

---

### Scenario 2 — [Action Title]

**User role:** [persona]

**Goal:** The user performs another task enabled by the feature.

**Acceptance Conditions:**

```
GIVEN [condition]
WHEN [action]
THEN [expected outcome]
```

- **Estimated Effort:** Small \| Medium \| Large  
- **Blocked By:** Scenario 1  

---

## 5. Functional Scope

### Included

- Capability A  
- Capability B  
- Capability C  

### Excluded

| Item | Reason |
|------|--------|
| Feature X | Planned for future version |
| Feature Y | Out of project scope |

### Potential Extensions

Ideas that may be implemented later.

---

## 6. Technical Environment

### Relevant Components

| Location | Description |
|----------|-------------|
| `src/...` | Module to update |
| `api/...` | API layer |
| `tests/...` | Existing test reference |

### Coding Pattern Reference

Example snippet illustrating architecture or design pattern. Agents should replicate this style.

### Data Layer Updates

Describe database modifications or new tables.

> **Example:**  
> `table reports` — id, user_id, schedule, created_at  

### API Specification

**POST** `/reports`

**Request:**
```json
{
  "user_id": "string",
  "schedule": "string"
}
```

**Response:**
```json
{
  "id": "string",
  "created": true
}
```

**Possible errors:** 400 invalid request · 403 unauthorized · 500 internal error  

### Constraints

- Must integrate with existing authentication system  
- Response time target: &lt; 200ms (p95)  
- Browser compatibility: modern browsers  

---

## 7. UX / Interaction Design

### Flow Diagram

```
User action
    ↓
UI form submission
    ↓
Backend validation
    ↓
Database write
    ↓
Success confirmation
```

### Interface Notes

Describe layout or interaction logic if wireframes are unavailable.

### Error Handling

| Situation | Message | Recovery |
|-----------|---------|----------|
| Invalid input | "Please provide a valid value" | Correct form |
| Network error | "Connection failed" | Retry |

---

## 8. Quality Requirements

| Category | Requirement |
|----------|-------------|
| Performance | API response &lt; 200ms |
| Reliability | 99.9% uptime |
| Accessibility | WCAG 2.1 AA |
| Code Quality | &gt;80% test coverage |

**Validation methods:** load testing · automated tests · accessibility scanning  

---

## 9. Development Plan

Implementation should follow project architecture defined in **PROJECT.md**.

### Step 1 — Data Layer

**Tasks:**

- implement database changes  
- create migration  
- add unit tests  

**Validation:** run project validation pipeline.

### Step 2 — Business Logic

**Tasks:**

- implement service layer  
- add input validation  
- write tests  

**Validation:** run project validation pipeline.

### Step 3 — API / Interface

**Tasks:**

- implement endpoint  
- add integration tests  
- connect UI if applicable  

**Validation:** run project validation pipeline.

---

## 10. Deployment Strategy

| Stage | Users | Requirement |
|-------|--------|-------------|
| Internal | team only | no critical issues |
| Beta | limited users | positive metrics |
| Release | all users | stability confirmed |

### Feature Toggle

- **Feature flag name:** `[flag_name]`  
- **Default:** disabled  
- **Rollout:** incremental percentage  

---

## 11. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Dependency delay | Medium | High | fallback plan |
| Performance issue | Low | Medium | load testing |

---

## 12. Outstanding Questions

| # | Question | Responsible | Status |
|---|----------|--------------|--------|
| 1 | [topic] | [owner] | open |

---

## 13. Operating Rules for Agents

### Allowed

Agents may:

- run tests  
- update files related to this feature  
- reuse existing patterns  

### Requires Approval

Agents must ask before:

- introducing new dependencies  
- modifying shared interfaces  
- altering database schema beyond defined changes  

### Forbidden

Agents must never:

- commit secrets  
- remove tests  
- modify historical migrations  
- bypass type safety rules  

---

## 14. Completion Checklist

Before marking the feature complete:

- [ ] All acceptance conditions validated  
- [ ] Tests passing  
- [ ] Code coverage meets threshold  
- [ ] No security issues  
- [ ] Documentation updated  
- [ ] Code review completed  

---

## Appendix

### Terminology

| Term | Meaning |
|------|---------|
| [term] | definition |

### Related Resources

- design document  
- technical specification  
- related PRDs  
