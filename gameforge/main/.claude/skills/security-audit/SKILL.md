---
name: security-audit
description: Security-focused review of the codebase. Checks for OWASP Top 10 vulnerabilities, secret exposure, dependency vulnerabilities, auth/authz issues, and injection risks.
argument-hint: "[optional: specific area to audit]"
disable-model-invocation: false
context: fork
---

# Security Audit

Comprehensive security-focused review of the codebase.

## Step 1: Read Context

- Read `PROJECT.md` for tech stack and security rules
- Read `CLAUDE.md` for security boundaries
- If `$ARGUMENTS` specifies an area, focus there; otherwise audit the full codebase

## Step 2: Audit Categories

Use the **code-reviewer** agent with a security focus to check:

### Secrets Exposure
- API keys, tokens, passwords, connection strings in source files
- Check `.gitignore` covers `.env`, `.env.local`, etc.
- Search for hardcoded credentials in config files
- Check for secrets in git history: `git log --all -p -S "password" -- "*.ts" "*.js" "*.env"` (sample)

### Injection Vulnerabilities
- **SQL Injection**: Raw queries with string concatenation, unsanitized user input in queries
- **XSS**: Unsanitized output, `dangerouslySetInnerHTML`, missing Content Security Policy
- **Command Injection**: `exec`, `spawn` with user-controlled input
- **Path Traversal**: File operations with user-controlled paths

### Authentication & Authorization
- Missing auth checks on protected routes
- Insecure session management
- JWT validation (algorithm, expiration, signing key)
- CORS configuration (overly permissive origins)
- Missing rate limiting on auth endpoints

### Data Exposure
- Sensitive data in logs (passwords, tokens, PII)
- Verbose error messages in production (stack traces)
- PII handling and storage
- Missing data sanitization in API responses

### Input Validation
- Missing validation on API endpoints
- File upload restrictions (type, size)
- Request size limits
- Missing CSRF protection on state-changing requests

### Cryptography
- Weak hashing algorithms (MD5, SHA1 for passwords)
- Hardcoded salts or IVs
- Insecure random number generation (`Math.random` for security)

### Configuration
- Debug mode in production config
- Permissive CORS (`*`)
- Missing security headers (HSTS, X-Frame-Options, etc.)
- Default credentials in config

### Dependencies
Run dependency vulnerability check:
- Node: `npm audit` / `pnpm audit`
- Python: `pip-audit`

## Step 3: Classify Findings

| Severity | Description |
|----------|-------------|
| **Critical** | Actively exploitable, data breach risk |
| **High** | Exploitable with moderate effort |
| **Medium** | Defense-in-depth issue, unlikely but possible |
| **Low** | Best practice violation, minimal risk |

## Step 4: Generate Report

Save to `docs/plans/security-audit-[date].md`:

```markdown
# Security Audit Report

**Date**: [date]
**Scope**: [full codebase or specific area]
**Audited by**: security-audit skill

## Executive Summary
- Critical: X findings
- High: X findings
- Medium: X findings
- Low: X findings

## Findings

### [CRITICAL] [Finding Title]
- **File**: `path/to/file:line`
- **Category**: [Injection / Auth / Secrets / etc.]
- **Description**: [what the vulnerability is]
- **Impact**: [what could happen if exploited]
- **Remediation**: [specific fix with code example]

[repeat for each finding, ordered by severity]

## Dependency Vulnerabilities
[output from audit command]

## Recommendations
1. [prioritized action items]
```

## Step 5: Present Summary

Show findings summary and top priority remediations.

---

Focus: $ARGUMENTS
