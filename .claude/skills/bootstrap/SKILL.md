---
name: bootstrap
description: Initialize a new project from scratch. Gathers requirements through discussion, scaffolds the project, fills in PROJECT.md, sets up domain skills, and creates initial boilerplate.
argument-hint: [project description]
disable-model-invocation: true
---

Bootstrap a new project from scratch. This is an interactive workflow -- ask questions
and wait for answers before proceeding.

## Step 1: Gather Requirements

Parse the project idea from `$ARGUMENTS`. Then ask the user the following questions
(skip any that are already clear from the description):

1. **Language & runtime** -- TypeScript/Python/Go/Rust/other? Which version?
2. **Framework** -- e.g., Next.js, Express, FastAPI, grammY, Gin, Actix-web, none
3. **Database** -- PostgreSQL, SQLite, MongoDB, none
4. **Package manager** -- pnpm, npm, yarn, pip/uv, cargo, go modules
5. **Any known requirements or constraints** -- monorepo, specific APIs, deployment target, etc.

Wait for the user to answer before proceeding. Confirm the choices back to them.

## Step 2: Fill in PROJECT.md

Using the project idea and confirmed tech stack, auto-populate every section of `PROJECT.md`:

- **Product Overview** -- product name, one-line description, target users, core problem, key domain concepts, deployment target, external integrations, and product goals
- **Tech Stack** table -- fill in all rows based on chosen stack
- **Commands** table -- install, dev, build, test, lint, typecheck (use real commands for the chosen tools)
- **Validation Command** -- composite command that runs tests + lint + typecheck
- **Directory Structure** -- standard layout for the chosen framework/language
- **File Conventions** -- extensions, test patterns, naming conventions for the stack
- **Code Standards** -- language-specific best practices
- **Architecture Pattern** -- data flow for the chosen architecture
- **Security Considerations** -- stack-specific security rules
- **Implementation Phases** -- default phase ordering for the architecture
- **Permissions Guidance** -- Bash permission patterns for `.claude/settings.json`

## Step 3: Scaffold Project

Use the **implementer** agent to set up the project:

1. Initialize the project (e.g., `pnpm init`, `go mod init`, `cargo init`, etc.)
2. Install core dependencies (framework, test framework, linter, etc.)
3. Create the directory structure defined in PROJECT.md
4. Set up config files (tsconfig.json, .eslintrc, .gitignore, pyproject.toml, etc.)
5. Create a minimal entry point with hello-world boilerplate
6. Set up test configuration with one passing example test

Present a summary of what was created and ask the user to confirm before continuing.

## Step 4: Domain Skills Review

Based on the chosen tech stack, review the domain skills in `.claude/skills/` and
present recommendations:

- **Relevant** -- skills that match the stack (e.g., `react-patterns` for React projects)
- **Not relevant** -- skills that don't apply (e.g., `database-patterns` for a project with no database)

Present these recommendations and let the user decide whether to remove irrelevant
skills. Do NOT auto-delete anything -- just suggest.

## Step 5: Update Permissions

Read `.claude/settings.json` and add Bash permission entries for the project's
validation commands (from the Permissions Guidance section in PROJECT.md).
Show the user the proposed changes and ask for confirmation before writing.

## Step 6: Validate

Run the validation command from PROJECT.md to confirm everything compiles and passes.
If anything fails, fix it before proceeding.

## Step 7: Initial Commit

Stage all new and modified files and create an initial commit:
```
chore: initial project setup
```

## Step 8: Next Steps

Tell the user:
- "Project is ready. Use `/new-feature` to build your first feature."
- "Use `/plan` if you want to plan before implementing."
- "Use `/prime` to review the full project context."

---

Project idea: $ARGUMENTS
