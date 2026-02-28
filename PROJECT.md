# PROJECT.md — Project Configuration

> **Project-specific settings**: tech stack, commands, structure, conventions.
> All agents read this file automatically. Update it when your project evolves.

---

## Tech Stack

| Layer           | Technology                                       |
|-----------------|--------------------------------------------------|
| Language        | `[e.g., TypeScript, Python, Go, Rust]`           |
| Runtime         | `[e.g., Node.js 20, Python 3.12, Go 1.22]`      |
| Framework       | `[e.g., Next.js, FastAPI, Gin, Actix-web]`       |
| Database        | `[e.g., PostgreSQL, MongoDB, SQLite, none]`      |
| ORM / Query     | `[e.g., Drizzle, Prisma, SQLAlchemy, none]`      |
| Test framework  | `[e.g., Vitest, pytest, go test, cargo test]`    |
| E2E framework   | `[e.g., Playwright, Cypress, none]`              |
| Linter          | `[e.g., ESLint, Ruff, golangci-lint, clippy]`    |
| Type checker    | `[e.g., tsc, mypy, built-in (Go/Rust), none]`   |
| Package manager | `[e.g., pnpm, npm, yarn, pip/uv, cargo]`        |

## Commands

| Task                  | Command                                    |
|-----------------------|--------------------------------------------|
| Install dependencies  | `[e.g., pnpm install]`                     |
| Dev server            | `[e.g., pnpm dev]`                         |
| Build                 | `[e.g., pnpm build]`                       |
| Run all tests         | `[e.g., pnpm test]`                        |
| Run single test       | `[e.g., pnpm test -- path/to/file.test.ts]`|
| Test with coverage    | `[e.g., pnpm test:coverage]`               |
| Lint                  | `[e.g., pnpm lint]`                        |
| Lint with auto-fix    | `[e.g., pnpm lint --fix]`                  |
| Type check            | `[e.g., pnpm typecheck]`                   |
| E2E tests             | `[e.g., pnpm test:e2e]`                    |
| DB migrate            | `[e.g., pnpm db:migrate]`                  |
| DB seed               | `[e.g., pnpm db:seed]`                     |

### Validation Command (run before every commit)

```bash
[e.g., pnpm test && pnpm typecheck && pnpm lint]
```

## Directory Structure

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

| Convention             | Pattern                                               |
|------------------------|-------------------------------------------------------|
| Source file extension   | `[e.g., .ts, .py, .go, .rs]`                         |
| Test file pattern       | `[e.g., *.test.ts, *_test.go, test_*.py]`            |
| Test location           | `[e.g., colocated, tests/ directory, same package]`  |
| Module naming           | `[e.g., kebab-case.ts, snake_case.py]`                |
| Component naming        | `[e.g., PascalCase.tsx, N/A]`                         |
| Import ordering         | `[e.g., external -> internal -> relative]`            |

## Code Standards

```
[e.g.,
- TypeScript strict mode, no `any` -- use `unknown` and narrow
- `const` over `let`, never `var`
- Named exports, no default exports
- Functions under 30 lines; extract helpers when needed
- Error handling: never swallow errors silently
- Every public function needs a doc comment
]
```

## Architecture Pattern

```
[e.g.,
Route -> Controller -> Service -> Repository -> Database
]
```

## Security Considerations

```
[e.g.,
- Auth: JWT tokens in httpOnly cookies
- Input validation: Zod schemas on all API endpoints
- SQL: parameterized queries only (ORM handles this)
- NEVER log tokens, passwords, or PII
]
```

## Implementation Phases

```
[e.g.,
Phase 1: Data Layer -- migrations, models, repository methods
Phase 2: Service Layer -- business logic, validation schemas
Phase 3: API Layer -- routes, controllers, middleware
Phase 4: UI -- components, hooks, pages
]
```

## Permissions Guidance

Bash commands that agents should be pre-approved for:

```json
[e.g.,
"Bash(pnpm test*)",
"Bash(pnpm lint*)",
"Bash(pnpm typecheck*)",
"Bash(pnpm build*)"
]
```
