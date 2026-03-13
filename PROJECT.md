# PROJECT.md

> **Project-specific configuration for the agentic development team.**
> Fill in every section below before running workflows. Agents read this file to understand
> your product, tech stack, commands, directory layout, and conventions.

---

## Product Overview

> What is this project? Agents use this section to understand the business context,
> make better design decisions, and write code that fits the product domain.

| Field | Description |
|-------|-------------|
| Product name | `[e.g., RemindBot, Acme Dashboard]` |
| One-line description | `[e.g., A Telegram bot that sends daily reminders]` |
| Target users | `[e.g., busy professionals, small teams, developers]` |
| Core problem | `[e.g., users forget recurring tasks and miss deadlines]` |
| Key domain concepts | `[e.g., reminders, schedules, notifications, users]` |
| Deployment target | `[e.g., Vercel, AWS Lambda, Docker on VPS, App Store]` |
| External integrations | `[e.g., Telegram Bot API, Stripe, SendGrid, none]` |

### Product Goals

```
[e.g.,
1. Users can create, edit, and delete daily reminders via chat commands
2. Reminders fire at the user's local time with timezone support
3. Free tier: 5 reminders, paid tier: unlimited
]
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | `[e.g., TypeScript, Python, Go, Rust, Swift]` |
| Runtime | `[e.g., Node.js 20, Python 3.12, Go 1.22]` |
| Framework | `[e.g., Next.js, FastAPI, Gin, Actix-web]` |
| Database | `[e.g., PostgreSQL, MongoDB, SQLite, none]` |
| ORM / Query | `[e.g., Drizzle, Prisma, SQLAlchemy, GORM, none]` |
| Test framework | `[e.g., Vitest, pytest, go test, cargo test]` |
| E2E framework | `[e.g., Playwright, Cypress, none]` |
| Linter | `[e.g., ESLint, Ruff, golangci-lint, clippy]` |
| Type checker | `[e.g., tsc, mypy, built-in (Go/Rust), none]` |
| Package manager | `[e.g., pnpm, npm, yarn, pip/uv, cargo, go modules]` |

## Commands

> Replace every `[placeholder]` with the actual command for your project.
> Delete rows that don't apply (e.g., "Type check" for Go where the compiler handles it).

| Task | Command |
|------|---------|
| Install dependencies | `[e.g., pnpm install]` |
| Dev server | `[e.g., pnpm dev]` |
| Build | `[e.g., pnpm build]` |
| Run all tests | `[e.g., pnpm test]` |
| Run single test file | `[e.g., pnpm test -- path/to/file.test.ts]` |
| Test with coverage | `[e.g., pnpm test:coverage]` |
| Lint | `[e.g., pnpm lint]` |
| Lint with auto-fix | `[e.g., pnpm lint --fix]` |
| Type check | `[e.g., pnpm typecheck]` |
| E2E tests | `[e.g., pnpm test:e2e]` |
| DB migrate | `[e.g., pnpm db:migrate]` |
| DB seed | `[e.g., pnpm db:seed]` |

### Validation Command

> The single composite command that agents run before every commit.
> Must exit non-zero on any failure.

```bash
[e.g., pnpm test && pnpm typecheck && pnpm lint]
```

## Directory Structure

> Map your project's source layout. Agents use this to know where files go.

```
[e.g.,
src/
├── api/            # HTTP layer (routes, controllers, middleware)
├── services/       # Business logic
├── repositories/   # Data access
├── models/         # Type definitions and schemas
├── utils/          # Pure utility functions
├── config/         # Environment and app configuration
└── ui/             # Frontend components
    ├── components/
    ├── pages/
    ├── hooks/
    └── stores/
]
```

## File Conventions

| Convention | Pattern |
|-----------|---------|
| Source file extension | `[e.g., .ts, .py, .go, .rs]` |
| Test file pattern | `[e.g., *.test.ts, *_test.go, test_*.py, *_test.rs]` |
| Test location | `[e.g., colocated next to source, tests/ directory, same package]` |
| Module naming | `[e.g., kebab-case.ts, snake_case.py, snake_case.go]` |
| Component naming | `[e.g., PascalCase.tsx, N/A]` |
| Import ordering | `[e.g., external → internal → relative, separated by blank lines]` |

## Code Standards

> Project-specific coding rules that agents must follow.
> Include only rules specific to your language/framework -- universal rules
> (no swallowed errors, no committed secrets, tests required) are in CLAUDE.md.

```
[e.g.,
- TypeScript strict mode, no `any` -- use `unknown` and narrow
- `const` over `let`, never `var`
- Named exports, no default exports
- Barrel files (`index.ts`) for module public APIs
- Functions under 30 lines; extract helpers when needed
- Error handling: use `Result<T, E>` pattern, never throw from services
- Every public function needs a doc comment
]
```

## Architecture Pattern

> Describe the data flow / layering pattern for your project.

```
[e.g.,
Route → Controller → Service → Repository → Database
]
```

## Security Considerations

> Project-specific security rules. Universal rules (never commit secrets,
> never disable security middleware) are in CLAUDE.md.

```
[e.g.,
- Auth: JWT tokens in httpOnly cookies
- Input validation: Zod schemas on all API endpoints
- SQL: parameterized queries only (ORM handles this)
- NEVER log tokens, passwords, or PII
]
```

## Implementation Phases

> Default ordering for multi-phase implementations (PRDs, design docs, /plan).
> Customize for your architecture. Each phase should be independently testable.

```
[e.g.,
Phase 1: Data Layer -- migrations, models, repository methods
Phase 2: Service Layer -- business logic, validation schemas
Phase 3: API Layer -- routes, controllers, middleware
Phase 4: UI -- components, hooks, pages
]
```

## Permissions Guidance

> Commands to add to `.claude/settings.json` for your project's tools.
> These let agents run validation without prompting for permission.

```json
[e.g.,
"Bash(pnpm test*)",
"Bash(pnpm lint*)",
"Bash(pnpm typecheck*)",
"Bash(pnpm build*)"
]
```
