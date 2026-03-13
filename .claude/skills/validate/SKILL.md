---
name: validate
description: Run comprehensive project validation checks across all layers -- lint, type check, tests, build, code quality, and dependency sync.
disable-model-invocation: false
context: fork
---

# Project Validation

Run a comprehensive health check across all project layers.

## 1. Linting

Run the lint command from `PROJECT.md`.

**Expected**: No errors.

## 2. Type Checking

Run the type check command from `PROJECT.md` (skip if not applicable).

**Expected**: No type errors.

## 3. Tests

Run the test command from `PROJECT.md`.

**Expected**: All tests pass.

### Coverage (if available)

Run the coverage command from `PROJECT.md`.

**Expected**: Coverage meets project thresholds (80%+ for new code).

## 4. Build

Run the build command from `PROJECT.md`.

**Expected**: Build completes successfully.

## 5. Code Quality Checks

### No Hardcoded Secrets

Search for potential secrets in source code:
- API keys, tokens, passwords in string literals
- `.env` values committed to source

### Type Safety Violations

Check for violations of the type safety rules in `PROJECT.md`.

### No Dead Code

Check for:
- Unused imports
- Commented-out code blocks
- Unreachable code

### No Swallowed Errors

Check for empty catch blocks or error handlers that don't log/rethrow.

## 6. Dependency Check

Run the install command from `PROJECT.md` to verify dependencies are in sync.

## 7. Summary Report

After all checks, provide:

### Passed Checks
- [ ] Linting: no errors
- [ ] TypeScript: compiles clean
- [ ] Tests: all passing
- [ ] Build: succeeds
- [ ] Code quality: no issues found
- [ ] Dependencies: in sync

### Failed Checks

For each failure:
1. **Category**: Description of problem
   - Expected: ...
   - Actual: ...
   - Suggested fix: ...

### Overall Health

**[PASS / FAIL]** -- with brief explanation.

If FAIL, create a prioritized list of fixes to apply.
