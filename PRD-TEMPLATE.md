# PRD Template — Agentic Product Development Team

> This template is designed to be consumed by both humans and AI agents.
> It follows structured formatting so agents can parse sections reliably.
> Based on patterns from OpenAI's AI PRD template, Addy Osmani's agent spec guide,
> and Anthropic's effective agent practices.

---

## Instructions for Use

1. Copy this template for each new feature/product
2. Save to `docs/prds/PRD-[feature-name].md`
3. Fill in all sections — mark any unknowns with `[TBD]`
4. Have the PM Agent (or human PM) complete the draft
5. Submit for review at the PRD Review checkpoint
6. Once approved, this becomes the source of truth for all downstream agents

---

# PRD: [Feature/Product Name]

**Author**: [Name or Agent]
**Status**: Draft | In Review | Approved | Deprecated
**Created**: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD
**Reviewers**: [Names]
**Approvers**: [Names]

---

## 1. Problem Statement

### What problem are we solving?
[Describe the user or business problem. Be specific. Include evidence — metrics,
user research quotes, support ticket volumes, competitive gaps.]

### Who has this problem?
[Identify the target user segment. Be specific about persona, use case, and context.]

### How do we know this is a real problem?
[Data points: user research findings, analytics, customer feedback, market analysis.
Quantify the impact where possible.]

### What happens if we don't solve it?
[Business impact of inaction — churn risk, revenue loss, competitive disadvantage.]

---

## 2. Proposed Solution

### High-Level Approach
[1-3 paragraph description of what we're building and why this approach was chosen
over alternatives.]

### Key User Stories

| ID    | As a...        | I want to...              | So that...                  | Priority |
|-------|----------------|---------------------------|-----------------------------|----------|
| US-01 | [user type]    | [action]                  | [benefit]                   | P0       |
| US-02 | [user type]    | [action]                  | [benefit]                   | P1       |
| US-03 | [user type]    | [action]                  | [benefit]                   | P2       |

### Acceptance Criteria

For each user story, define testable acceptance criteria:

**US-01: [Story Title]**
- [ ] Given [context], when [action], then [expected result]
- [ ] Given [context], when [action], then [expected result]
- [ ] Given [error condition], then [error handling behavior]

**US-02: [Story Title]**
- [ ] Given [context], when [action], then [expected result]
- [ ] ...

---

## 3. Scope

### In Scope
- [Feature/capability 1]
- [Feature/capability 2]
- [Feature/capability 3]

### Out of Scope
- [Explicitly excluded item 1] — Reason: [why excluded]
- [Explicitly excluded item 2] — Reason: [why excluded]

### Future Considerations
- [Potential future enhancement 1]
- [Potential future enhancement 2]

> **Note for agents**: Do NOT implement anything listed under "Out of Scope" or
> "Future Considerations". These are documented for context only.

---

## 4. Technical Considerations

### Constraints
- [Technical constraint 1 — e.g., must work with existing auth system]
- [Performance constraint — e.g., page load < 2s on 3G]
- [Compatibility constraint — e.g., must support IE11 / Safari 14+]

### Dependencies
| Dependency            | Owner         | Status    | Risk if Delayed          |
|-----------------------|---------------|-----------|--------------------------|
| [API endpoint]        | [team/person] | [status]  | [impact]                 |
| [Third-party service] | [vendor]      | [status]  | [impact]                 |

### Data Requirements
- [What data is needed]
- [Data sources]
- [Data privacy/compliance considerations (GDPR, CCPA, etc.)]

### API Contracts (if applicable)
```
POST /api/v1/[resource]
Request:
  { "field": "type", "field2": "type" }
Response:
  { "id": "string", "status": "string" }
Errors:
  400: { "error": "validation_error", "details": [...] }
  401: { "error": "unauthorized" }
  404: { "error": "not_found" }
```

---

## 5. Design & UX

### User Flow
```
[Step 1: User action] → [Step 2: System response] → [Step 3: User action] → ...
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
| [condition]           | [message]                   | [what user can do]           |

---

## 6. Success Metrics

### Primary Metrics (must move)
| Metric                | Current Baseline | Target        | Measurement Method       |
|-----------------------|------------------|---------------|--------------------------|
| [metric 1]            | [value]          | [target]      | [how measured]           |
| [metric 2]            | [value]          | [target]      | [how measured]           |

### Secondary Metrics (should not degrade)
| Metric                | Current Baseline | Acceptable Range | Alert Threshold        |
|-----------------------|------------------|------------------|------------------------|
| [metric 1]            | [value]          | [range]          | [threshold]            |

### Guardrail Metrics (must not regress)
- [Page load time must stay under X ms]
- [Error rate must stay below X%]
- [Existing feature Y must not break]

---

## 7. Rollout Plan

### Phases
| Phase     | Audience           | Criteria to Advance           | Rollback Trigger         |
|-----------|--------------------|-------------------------------|--------------------------|
| Alpha     | Internal team      | No P0 bugs                    | Any data loss            |
| Beta      | 10% of users       | Success metric trending up    | Error rate > 5%          |
| GA        | 100% of users      | Beta targets met              | Per incident response    |

### Feature Flags
- Flag name: `[feature_flag_name]`
- Default: off
- Rollout: gradual percentage

### Monitoring & Alerting
- [What dashboards to watch]
- [What alerts to set up]
- [On-call expectations during rollout]

---

## 8. Risks & Mitigations

| Risk                  | Likelihood | Impact   | Mitigation                          |
|-----------------------|------------|----------|-------------------------------------|
| [risk 1]              | High/Med/Low| High/Med/Low | [mitigation strategy]          |
| [risk 2]              | High/Med/Low| High/Med/Low | [mitigation strategy]          |

---

## 9. Open Questions

| #  | Question                              | Owner         | Due Date   | Resolution |
|----|---------------------------------------|---------------|------------|------------|
| 1  | [question]                            | [who decides] | [date]     | [TBD]      |
| 2  | [question]                            | [who decides] | [date]     | [TBD]      |

---

## 10. Appendix

### Glossary
| Term           | Definition                                                      |
|----------------|-----------------------------------------------------------------|
| [term]         | [definition]                                                    |

### Related Documents
- [Link to architecture ADR]
- [Link to design specs]
- [Link to competitive analysis]
- [Link to user research findings]

### Revision History
| Date       | Author     | Changes                                                    |
|------------|------------|------------------------------------------------------------|
| YYYY-MM-DD | [name]     | Initial draft                                              |

---

## Agent Processing Notes

> These notes help downstream agents parse and act on this PRD correctly.

### For Architect Agent
- Focus on sections 4 (Technical Considerations) and the API Contracts
- Use constraints to guide technology choices
- Dependencies determine integration sequencing

### For Developer Agent
- User Stories (section 2) define WHAT to build
- Acceptance Criteria define WHEN it's done
- Scope section defines boundaries — respect "Out of Scope" strictly
- API Contracts define the interface contract

### For QA Agent
- Map every Acceptance Criterion to at least one test case
- Error States table (section 5) requires negative test cases
- Success Metrics (section 6) define performance test targets
- Guardrail Metrics define regression test requirements

### For Security Agent
- Review Data Requirements for privacy/compliance risks
- API Contracts need input validation and auth checks
- Check Feature Flags for authorization bypass risks

### For UX Agent
- User Flow (section 5) defines the interaction sequence
- Accessibility Requirements are non-negotiable
- Error States define all user-visible error experiences
