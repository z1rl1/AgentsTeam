---
name: plan
description: Create a comprehensive implementation plan with deep codebase analysis. Produces a context-rich plan that enables one-pass implementation success.
argument-hint: [feature description]
disable-model-invocation: false
context: fork
agent: architect
---

# Plan a Feature

## Feature: $ARGUMENTS

## Mission

Transform a feature request into a comprehensive implementation plan through systematic codebase analysis and strategic planning.

**Core Principle**: Do NOT write code in this phase. Create a context-rich plan that enables one-pass implementation success.

**Key Philosophy**: Context is King. The plan must contain ALL information needed for implementation -- patterns, mandatory file reading, documentation, validation commands -- so the implementer agent succeeds on the first attempt.

## Planning Process

### Phase 1: Feature Understanding

**Deep Feature Analysis:**

- Extract the core problem being solved
- Identify user value and business impact
- Determine feature type: New Capability / Enhancement / Refactor / Bug Fix
- Assess complexity: Low / Medium / High
- Map affected systems and components

**Create User Story:**

```
As a <type of user>
I want to <action/goal>
So that <benefit/value>
```

### Phase 2: Codebase Intelligence Gathering

**1. Project Structure Analysis**

- Detect primary language(s), frameworks, and runtime versions
- Map directory structure and architectural patterns
- Identify service/component boundaries and integration points
- Locate configuration files (package.json, tsconfig.json, etc.)
- Find environment setup and build processes

**2. Pattern Recognition**

- Search for similar implementations in the codebase
- Identify coding conventions (naming, file organization, error handling, logging)
- Extract common patterns for the feature's domain
- Document anti-patterns to avoid
- Check `CLAUDE.md` and `AGENTS.md` for project-specific rules

**3. Dependency Analysis**

- Catalog external libraries relevant to feature
- Understand how libraries are integrated (check imports, configs)
- Find relevant documentation in `docs/`, `.claude/reference/` if available
- Note library versions and compatibility requirements

**4. Testing Patterns**

- Identify test framework and structure
- Find similar test examples for reference
- Understand test organization (unit vs integration)
- Note coverage requirements and testing standards

**5. Integration Points**

- Identify existing files that need updates
- Determine new files that need creation and their locations
- Map router/API registration patterns
- Understand database/model patterns if applicable
- Identify authentication/authorization patterns if relevant

**Clarify Ambiguities:**

- If requirements are unclear, ask the user to clarify before continuing
- Get specific implementation preferences (libraries, approaches, patterns)
- Resolve architectural decisions before proceeding

### Phase 3: Strategic Thinking

**Think Deeply About:**

- How does this feature fit into the existing architecture?
- What are the critical dependencies and order of operations?
- What could go wrong? (Edge cases, race conditions, errors)
- How will this be tested comprehensively?
- What performance implications exist?
- Are there security considerations?
- How maintainable is this approach?

**Design Decisions:**

- Choose between alternative approaches with clear rationale
- Design for extensibility and future modifications
- Plan for backward compatibility if needed

### Phase 4: Plan Generation

Create the plan using this structure:

```markdown
# Feature: <feature-name>

## Feature Description
<Detailed description, purpose, and value to users>

## User Story
As a <type of user>
I want to <action/goal>
So that <benefit/value>

## Feature Metadata
**Type**: [New Capability / Enhancement / Refactor / Bug Fix]
**Complexity**: [Low / Medium / High]
**Primary Systems Affected**: [List of main components/services]
**Dependencies**: [External libraries or services required]

---

## CONTEXT REFERENCES

### Files to Read Before Implementing (MANDATORY)
- `path/to/file` (lines X-Y) -- Why: Contains pattern for X
- `path/to/model` (lines X-Y) -- Why: Data model structure to follow

### New Files to Create
- `path/to/new_module` -- Purpose
- `path/to/new_module_test` -- Tests for new module

### Patterns to Follow
<Actual code examples extracted from the codebase>

---

## IMPLEMENTATION PLAN

### Phase 1: [Foundation]
Tasks and validation command

### Phase 2: [Core Implementation]
Tasks and validation command

### Phase 3: [Integration]
Tasks and validation command

### Phase 4: [Testing & Validation]
Tasks and validation command

---

## STEP-BY-STEP TASKS

Execute every task in order. Each task is atomic and independently testable.

### 1. {ACTION} {target_file}
- **IMPLEMENT**: Specific implementation detail
- **PATTERN**: Reference to existing pattern -- file:line
- **IMPORTS**: Required imports and dependencies
- **GOTCHA**: Known issues or constraints to avoid
- **VALIDATE**: `executable validation command`

(Continue with all tasks in dependency order...)

---

## VALIDATION COMMANDS

Run the commands from `PROJECT.md` for each level:

### Level 1: Lint
[Lint command from PROJECT.md]

### Level 2: Type Check (if applicable)
[Type check command from PROJECT.md]

### Level 3: Tests
[Test command from PROJECT.md]

### Level 4: Manual Validation
<Feature-specific manual testing steps>

---

## ACCEPTANCE CRITERIA
- [ ] Feature implements all specified functionality
- [ ] All validation commands pass with zero errors
- [ ] Unit test coverage meets requirements (80%+)
- [ ] Code follows project conventions and patterns
- [ ] No regressions in existing functionality

---

## COMPLETION CHECKLIST
- [ ] All tasks completed in order
- [ ] All validation commands pass
- [ ] Full test suite passes
- [ ] No linting or type checking errors
- [ ] Acceptance criteria all met
```

## Output

Save the plan to: `docs/plans/{kebab-case-feature-name}.md`

Create the `docs/plans/` directory if it doesn't exist.

## Quality Criteria

- [ ] All necessary patterns identified and documented with file:line references
- [ ] Tasks ordered by dependency (can execute top-to-bottom)
- [ ] Each task is atomic and has a validation command
- [ ] Another developer could implement without additional context
- [ ] No reinvention of existing patterns or utilities

---

Feature: $ARGUMENTS
