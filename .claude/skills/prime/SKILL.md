---
name: prime
description: Load project context and build comprehensive codebase understanding. Analyzes structure, documentation, and key files, then presents a scannable summary.
disable-model-invocation: false
---

# Prime: Load Project Context

## Objective

Build comprehensive understanding of the codebase by analyzing structure, documentation, and key files.

## Process

### 1. Analyze Project Structure

List all tracked files:
Run: `git ls-files`

Show directory structure:
Run: `find . -type f -not -path './.git/*' -not -path './node_modules/*' -not -path './dist/*' | head -100`

### 2. Read Core Documentation

- Read `CLAUDE.md` for project rules and conventions
- Read `AGENTS.md` for universal agent instructions
- Read any README files at project root and major directories
- Read architecture docs in `docs/architecture/`
- Read reference docs in `.claude/reference/` if they exist

### 3. Identify Key Files

Based on the structure, identify and read:
- Main entry points (index.ts, app.ts, main.ts, etc.)
- Core configuration files (package.json, tsconfig.json)
- Key model/schema definitions
- Important service or controller files

### 4. Understand Current State

Check recent activity:
Run: `git log -10 --oneline`

Check current branch and status:
Run: `git status`

Check for open PRDs and design docs:
Run: `ls docs/prds/ docs/architecture/ 2>/dev/null`

## Output Report

Provide a concise summary covering:

### Project Overview
- Purpose and type of application
- Primary technologies and frameworks
- Current version/state

### Architecture
- Overall structure and organization
- Key architectural patterns identified
- Important directories and their purposes

### Tech Stack
- Languages and versions
- Frameworks and major libraries
- Build tools and package managers
- Testing frameworks

### Agent Team
- Available agents and their roles
- Available workflow skills
- Existing PRDs and design docs

### Current State
- Active branch
- Recent changes or development focus
- Any immediate observations or concerns

**Keep this summary scannable -- use bullet points and clear headers.**
