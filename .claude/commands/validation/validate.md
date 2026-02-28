---
description: Full project health check -- lint, types, tests, build, code quality
---

# Project Validation

Run a comprehensive health check across all layers.

## 1. Linting

Run the lint command from `PROJECT.md`.
**Expected**: No errors.

## 2. Type Checking

Run the type check command from `PROJECT.md` (skip if N/A).
**Expected**: No type errors.

## 3. Tests

Run the test command from `PROJECT.md`.
**Expected**: All tests pass.

If coverage command is available, run it.
**Expected**: 80%+ for new code.

## 4. Build

Run the build command from `PROJECT.md`.
**Expected**: Build succeeds.

## 5. Code Quality

Check for:
- **Hardcoded secrets**: API keys, tokens, passwords in source
- **Type safety violations**: any `any` types or unsafe casts
- **Dead code**: unused imports, commented-out blocks, unreachable code
- **Swallowed errors**: empty catch blocks or ignored error handlers

## 6. Dependencies

Run install command to verify lockfile is in sync.

## 7. Report

```markdown
### Passed
- [ ] Lint: clean
- [ ] Types: clean
- [ ] Tests: all passing
- [ ] Build: succeeds
- [ ] Code quality: no issues
- [ ] Dependencies: in sync

### Failed
For each failure:
1. **Category**: description
   - Expected: ...
   - Actual: ...
   - Fix: ...

### Overall: [PASS / FAIL]
```
