---
description: Load project context -- structure, docs, recent activity
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
- `AGENTS.md`
- `README.md`
- Any docs in `docs/architecture/`
- Any docs in `docs/prds/`

## Step 3: Key Files

Identify and read:
- Entry points (main, index, app files)
- Configuration files (tsconfig, package.json, etc.)
- Core type definitions or schemas

## Step 4: Current State

- `git log --oneline -15` -- recent commits
- `git branch -a` -- all branches
- `git status` -- current working state

## Output

Present a concise summary:
- **Project**: what this is, what it does
- **Architecture**: key patterns and layers
- **Tech Stack**: languages, frameworks, tools
- **Team Agents**: available agents and their roles
- **Current State**: active branch, recent changes, anything in progress
