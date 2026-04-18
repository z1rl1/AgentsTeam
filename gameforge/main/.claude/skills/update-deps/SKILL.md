---
name: update-deps
description: Check for outdated and vulnerable dependencies, propose updates, and apply them with validation. Runs security audit and ensures no regressions.
argument-hint: "[optional: specific package name]"
disable-model-invocation: true
context: fork
---

# Update Dependencies

Structured workflow for updating project dependencies safely.

## Step 1: Read Project Config

- Read `PROJECT.md` for package manager and commands
- Identify the dependency management tool (npm, pnpm, yarn, pip, go mod, etc.)

## Step 2: Check Outdated

Run the appropriate command:
- Node: `pnpm outdated` / `npm outdated` / `yarn outdated`
- Python: `pip list --outdated`
- Go: `go list -m -u all`

If `$ARGUMENTS` specifies a package, focus on that package only.

## Step 3: Security Audit

Run the appropriate security check:
- Node: `npm audit` / `pnpm audit`
- Python: `pip-audit` (if available)
- Go: `govulncheck ./...` (if available)

## Step 4: Present Findings

Show two tables:

### Outdated Dependencies
| Package | Current | Latest | Update Type |
|---------|---------|--------|-------------|
| [name]  | [ver]   | [ver]  | major/minor/patch |

### Vulnerabilities
| Package | Severity | Description | Fix Version |
|---------|----------|-------------|-------------|
| [name]  | [level]  | [desc]      | [ver]       |

## Step 5: Human Selection

Ask which updates to apply:
- All security fixes (recommended)
- All patch updates
- All minor updates
- Specific packages
- All updates (including major -- higher risk)

Wait for approval.

## Step 6: Apply Updates

Create branch: `chore/update-deps`

Use the **implementer** agent to:
- Update dependency files
- Run install command
- Run full validation from `PROJECT.md`

## Step 7: Test

Run the full test suite. If any test fails:
- Use the **debugger** agent to investigate
- Present findings: is the failure from a breaking change or a pre-existing issue?

## Step 8: Review

Use the **code-reviewer** agent to review dependency changes.
Focus: check changelogs of major/minor updates for breaking changes.

## Step 9: Commit

```bash
git commit -m "chore: update dependencies"
```

Present summary and ask about PR creation.

---

Package: $ARGUMENTS
