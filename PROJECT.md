# PROJECT.md — Telegram Bot Configuration

> **Project-specific settings**: tech stack, commands, structure, conventions.
> All agents read this file automatically.

---

## Tech Stack

| Layer           | Technology                |
|-----------------|---------------------------|
| Language        | TypeScript 5.x            |
| Runtime         | Node.js 20 LTS            |
| Framework       | grammY 1.x                |
| Database        | SQLite (better-sqlite3)   |
| ORM / Query     | Drizzle ORM               |
| Test framework  | Vitest                    |
| E2E framework   | none                      |
| Linter          | ESLint + Prettier          |
| Type checker    | tsc (strict mode)          |
| Package manager | pnpm                      |

## Commands

| Task                  | Command                                |
|-----------------------|----------------------------------------|
| Install dependencies  | `pnpm install`                         |
| Dev (polling mode)    | `pnpm dev`                             |
| Build                 | `pnpm build`                           |
| Run all tests         | `pnpm test`                            |
| Run single test       | `pnpm test -- path/to/file.test.ts`    |
| Test with coverage    | `pnpm test:coverage`                   |
| Lint                  | `pnpm lint`                            |
| Lint with auto-fix    | `pnpm lint --fix`                      |
| Type check            | `pnpm typecheck`                       |
| DB migrate            | `pnpm db:migrate`                      |
| DB seed               | `pnpm db:seed`                         |
| DB studio             | `pnpm db:studio`                       |

### Validation Command (run before every commit)

```bash
pnpm typecheck && pnpm lint && pnpm test
```

## Directory Structure

```
src/
├── bot/              # Bot instance, session, config
│   ├── bot.ts        # Bot instance creation and plugin setup
│   ├── session.ts    # Session configuration
│   └── config.ts     # Environment variables and config
├── commands/         # Command handlers (/start, /help, etc.)
├── callbacks/        # Callback query handlers (inline buttons)
├── conversations/    # Multi-step conversation flows (grammY conversations plugin)
├── middleware/        # Custom middleware (auth, logging, rate-limit)
├── keyboards/        # Keyboard builders (InlineKeyboard, Keyboard)
├── services/         # Business logic (user service, etc.)
├── db/               # Drizzle schema, migrations, queries
│   ├── schema.ts     # Database schema definitions
│   ├── migrate.ts    # Migration runner
│   └── index.ts      # Database connection
├── utils/            # Pure utility functions
└── types/            # TypeScript type definitions
    └── context.ts    # Custom context type with session data
```

## File Conventions

| Convention             | Pattern                                    |
|------------------------|--------------------------------------------|
| Source file extension   | `.ts`                                      |
| Test file pattern       | `*.test.ts`                                |
| Test location           | `tests/` directory mirroring `src/`        |
| Module naming           | `kebab-case.ts`                            |
| Import ordering         | external → internal → relative             |

## Code Standards

- TypeScript strict mode, no `any` — use `unknown` and narrow
- `const` over `let`, never `var`
- Named exports, no default exports
- Functions under 30 lines; extract helpers when needed
- Error handling: never swallow errors silently
- Every public function needs a doc comment
- Use grammY's `Composer` for modular handler registration
- Bot handlers must be pure functions that receive `Context` and return `void`

## Architecture Pattern

```
Bot Entry Point → Middleware → Router (commands/callbacks/conversations) → Service → Database
```

## Security Considerations

- Bot token stored in `.env`, never committed
- Input validation on all user messages before processing
- Rate limiting middleware to prevent abuse
- SQL: parameterized queries only (Drizzle handles this)
- NEVER log bot tokens, user phone numbers, or PII
- Webhook mode: validate Telegram's secret token header

## Implementation Phases

```
Phase 1: Bot Setup — bot instance, config, session, basic /start and /help
Phase 2: Database — Drizzle schema, migrations, connection
Phase 3: Core Commands — main bot command handlers
Phase 4: Keyboards & Callbacks — inline keyboards and callback handlers
Phase 5: Conversations — multi-step dialog flows
Phase 6: Middleware — auth, logging, rate-limiting
Phase 7: Webhook — production webhook setup with Express
```

## Permissions Guidance

Bash commands that agents should be pre-approved for:

```json
"Bash(pnpm test*)",
"Bash(pnpm lint*)",
"Bash(pnpm typecheck*)",
"Bash(pnpm build*)",
"Bash(pnpm db:*)"
```
