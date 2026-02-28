---
description: Stage and create an atomic commit with conventional prefix
---

# Commit Current Changes

Run `git status` and `git diff HEAD` to see all uncommitted changes.

Stage the relevant files (avoid staging secrets, .env, credentials).

Create an atomic commit with a conventional commit message:
- Prefix: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`, `style:`, `perf:`
- Write a concise message describing the change
- If there are multiple logical changes, suggest separate commits

Do NOT push to remote unless explicitly asked.
