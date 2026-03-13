---
name: discuss
description: Capture implementation preferences and decisions before technical design. Prevents rework from misaligned assumptions by resolving gray areas upfront.
argument-hint: [PRD-path or feature-name]
disable-model-invocation: true
---

# Discuss: Capture Implementation Preferences

Gather implementation preferences and resolve gray areas BEFORE the architect begins
technical design. This prevents rework from misaligned assumptions.

## Step 1: Load Context

- Read the PRD at the given path, or search `docs/prds/` for a matching PRD
- Read `PROJECT.md` for tech stack and conventions
- Read relevant source code areas to understand existing patterns
- If `docs/state/STATE.md` exists, read it for prior context

## Step 2: Identify Discussion Topics

Based on the PRD's scope, identify which of these categories are relevant:

### Error Handling Strategy
- How should errors surface to users? (toast notifications, inline, error pages)
- Retry behavior for failed operations?
- Fallback approaches when services are unavailable?

### Authentication & Authorization
- Auth approach if the feature touches auth (OAuth, JWT, sessions, API keys)
- Permission model (RBAC, ABAC, simple roles)
- How to handle unauthorized access attempts?

### Data Flow & State
- Synchronous vs asynchronous processing?
- Caching strategy (what to cache, TTL, invalidation)
- Real-time updates vs polling vs on-demand?
- Client-side vs server-side state management?

### API Design
- REST conventions (resource naming, nesting depth)
- Pagination approach (cursor, offset, keyset)
- Response format and envelope structure?
- Versioning strategy?

### UI/UX Preferences (if applicable)
- Visual style and component library choices
- Layout approach (responsive strategy, breakpoints)
- Interaction patterns (optimistic updates, loading states)
- Accessibility requirements beyond defaults?

### Technology Choices
- Specific libraries for ambiguous parts of the implementation
- Database choices if new storage is needed
- Queue/messaging approach if async processing is needed

### Performance Tradeoffs
- Eager vs lazy loading?
- Denormalization decisions?
- Acceptable latency thresholds?

## Step 3: Structured Discussion

For each relevant category:
1. Present the options with brief pros/cons
2. Recommend an approach based on existing project patterns
3. Ask the user for their preference
4. Record the decision with rationale

Skip categories that are not relevant to this feature. Do not force discussion on irrelevant topics.

## Step 4: Save Decisions

Save the locked decisions to `docs/architecture/CONTEXT-[feature-name].md` using the
template from `docs/templates/CONTEXT-TEMPLATE.md`.

## Step 5: Update State

If `docs/state/STATE.md` exists, update:
- **phase** to `discussing`
- **updated** to current date

## Step 6: Summary

Present a summary of all locked decisions and tell the user:
"Implementation preferences are locked. These will feed into the architect's technical
design. Proceed with `/new-feature` to continue, or run the architect agent directly."

---

Feature: $ARGUMENTS
