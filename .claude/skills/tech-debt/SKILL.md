---
name: tech-debt
description: Identify and address technical debt. Scans for code smells, outdated patterns, missing tests, TODO markers, and proposes a prioritized remediation plan.
argument-hint: "[optional: specific area or file path to focus on]"
disable-model-invocation: false
context: fork
---

# Technical Debt Assessment

Systematic scan and prioritized remediation of technical debt.

## Step 1: Read Standards

- Read `PROJECT.md` and `CLAUDE.md` for project standards
- Understand the expected code quality baseline

## Step 2: Scan for Debt Indicators

Search the codebase for:

### Code Quality
- `TODO`, `FIXME`, `HACK`, `XXX` comments
- Functions exceeding 50 lines
- Files exceeding 400 lines
- Duplicated code blocks (3+ similar blocks)
- Deeply nested conditionals (4+ levels)

### Testing Gaps
- Source files with no corresponding test file
- Test files with low assertion counts
- Run coverage report if available

### Dead Code
- Unused imports
- Commented-out code blocks (>5 lines)
- Unreachable branches
- Unused exports

### Error Handling
- Empty catch blocks
- Swallowed errors (catch without log/rethrow)
- Missing error boundaries (React)

### Dependencies
- Outdated packages (run outdated check)
- Unused dependencies

### Type Safety
- `any` type usage (TypeScript)
- Type assertions / casts
- Missing return types on exported functions

If `$ARGUMENTS` specifies an area, focus the scan there.

## Step 3: Categorize & Prioritize

Group findings by category. Score each item:

| Factor | Scoring |
|--------|---------|
| **Impact** | High (affects users/reliability), Medium (developer productivity), Low (cosmetic) |
| **Effort** | S (<30 min), M (1-3 hours), L (half day+) |
| **Risk** | High (could cause bugs), Medium (maintenance burden), Low (style only) |

## Step 4: Present Report

```markdown
## Technical Debt Report

### Summary
- Total items found: X
- Critical (High impact + High risk): X
- Quick wins (High impact + Small effort): X

### Top 5 Priority Items
1. [item] — Impact: High, Effort: S, Risk: High
   - File: `path/to/file:line`
   - Issue: [description]
   - Fix: [suggested approach]

### Full Findings by Category
[grouped tables]
```

## Step 5: Remediation (Optional)

If the user approves addressing items:
1. Create branch: `chore/tech-debt-[description]`
2. Use the **implementer** agent to fix approved items
3. Run validation after each fix
4. Use the **code-reviewer** agent to review changes
5. Commit: `chore: address technical debt -- [summary]`

---

Focus: $ARGUMENTS
