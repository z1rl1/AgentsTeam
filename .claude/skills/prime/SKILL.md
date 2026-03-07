---
name: prime
description: "Load project context: structure, docs, recent activity. Use when starting a new session, switching context, or the user says 'prime' or 'load context'."
---

# Prime: Load Project Context

Build a comprehensive understanding of this project.

## Step 1: Project Structure

Run `git ls-files | head -80` to see the file tree.
Use Glob to map key directories.

## Step 2: Read Core Docs

Read these files (if they exist):
- `CLAUDE.md`
- `PROJECT.md`
- `README.md`
- Any docs in `docs/architecture/`
- Any docs in `docs/prds/`

## Step 3: Key Files

Identify and read:
- Entry points (src/bot/bot.ts, src/index.ts)
- Configuration files (tsconfig.json, package.json, drizzle.config.ts)
- Core type definitions (src/types/context.ts)
- Database schema (src/db/schema.ts)

## Step 4: Current State

- `git log --oneline -15` — recent commits
- `git branch -a` — all branches
- `git status` — current working state

## Output

Present a concise summary:
- **Project**: what this is, what it does
- **Architecture**: key patterns and layers
- **Tech Stack**: languages, frameworks, tools
- **Team Agents**: available agents and their roles
- **Current State**: active branch, recent changes, anything in progress
