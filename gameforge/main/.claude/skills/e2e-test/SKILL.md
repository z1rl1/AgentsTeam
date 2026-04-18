---
name: e2e-test
description: Design and implement end-to-end or integration tests. Identifies critical user journeys, writes E2E test scenarios, and validates they pass.
argument-hint: [feature or user journey to test]
disable-model-invocation: true
context: fork
agent: tester
---

# End-to-End Testing Workflow

Design and implement E2E tests for critical user journeys.

## Step 1: Understand Context

- Read `PROJECT.md` for E2E test framework (Playwright, Cypress, etc.) and test commands
- Search for existing E2E tests to understand patterns
- Read the relevant PRD (search `docs/prds/`) for user stories and acceptance criteria

## Step 2: Identify Test Scenarios

Map `$ARGUMENTS` to end-to-end flows:

For each user story:
- **Happy path**: The primary success flow
- **Error paths**: Key failure scenarios (invalid input, unauthorized, not found)
- **Edge cases**: Boundary conditions, empty states, concurrent actions

Document:
- **Scenario name**: Descriptive name
- **Preconditions**: Test data setup, auth state
- **Steps**: User actions in sequence
- **Expected result**: What should happen
- **External dependencies**: APIs, services to mock

## Step 3: Present Test Plan

Show the test scenarios for human review:

| # | Scenario | Type | Priority |
|---|----------|------|----------|
| 1 | [name] | Happy path | Critical |
| 2 | [name] | Error path | High |
| 3 | [name] | Edge case | Medium |

Wait for approval.

## Step 4: Implement Tests

Following the project's E2E test patterns:

- Set up test data and preconditions
- Implement each scenario as a test case
- Use page objects / test helpers if the project has them
- Add meaningful assertions at each critical step
- Include cleanup/teardown

## Step 5: Run Tests

Execute the E2E test suite:
- Run the E2E command from `PROJECT.md`
- Fix any failures
- Re-run until all pass

## Step 6: Report

Present results:

### Test Results
| Scenario | Status | Duration |
|----------|--------|----------|
| [name] | PASS/FAIL | [time] |

### Coverage
- User stories covered: X/Y
- Happy paths: X tests
- Error paths: X tests
- Edge cases: X tests

### Notes
- Any scenarios that couldn't be automated and why
- Suggested manual testing steps for those cases

---

Feature: $ARGUMENTS
