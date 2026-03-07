# PRD: Telegram Bot Assistant

**Status**: Draft
**Author**: Product Manager Agent
**Created**: 2026-03-07
**Last Updated**: 2026-03-07
**Priority**: P1 (high)
**Reviewers**: [TBD]

---

## 1. Objective

Build a Telegram bot assistant that helps users manage tasks and get information through an intuitive conversational interface with inline keyboards and multi-step dialogs.

### Core Principles
1. Fast response time — bot replies within 1 second
2. Intuitive navigation — inline keyboards for all multi-option interactions
3. Persistent state — user data survives bot restarts via SQLite

---

## 2. Problem Statement

### What problem are we solving?
Users need a lightweight, always-available assistant accessible from Telegram — no app install, no login, no friction. The bot provides quick task management and information retrieval directly in the messenger they already use daily.

### Who has this problem?
Individual users who want a simple personal assistant in Telegram. Technical level: any. Context: mobile-first, on-the-go usage.

### How do we know this is real?
Telegram has 900M+ monthly active users. Bot ecosystem is a core platform feature. Task management bots consistently rank among top Telegram bots.

### What happens if we don't solve it?
Users continue using disconnected tools or heavier apps for simple task management.

---

## 3. User Stories

### US-1: Start Bot and See Welcome Message

**As a** new user
**I want to** send /start and see a welcome message with available commands
**So that** I understand what the bot can do

**Acceptance Criteria:**

```
GIVEN a user opens the bot for the first time
WHEN they send /start
THEN the bot replies with a welcome message
AND shows an inline keyboard with main actions (Tasks, Help, Settings)
AND creates a user record in the database
```

```
GIVEN a returning user
WHEN they send /start
THEN the bot replies with a welcome-back message
AND shows the same inline keyboard
AND does NOT create a duplicate user record
```

**Complexity**: S (hours)
**Dependencies**: None

---

### US-2: View Help Information

**As a** user
**I want to** see a list of all available commands with descriptions
**So that** I know how to interact with the bot

**Acceptance Criteria:**

```
GIVEN a user sends /help
WHEN the bot processes the command
THEN it replies with a formatted list of all commands and their descriptions
AND includes a "Back to Menu" inline button
```

**Complexity**: S (hours)
**Dependencies**: US-1

---

### US-3: Create a Task

**As a** user
**I want to** create a new task through a conversation flow
**So that** I can track things I need to do

**Acceptance Criteria:**

```
GIVEN a user clicks "Tasks" in the main menu
WHEN they select "Add Task"
THEN the bot starts a conversation asking for task title
AND then asks for optional description
AND then asks for priority (Low/Medium/High) via inline keyboard
AND saves the task to the database
AND confirms creation with task details
```

```
GIVEN a user is in the "Add Task" conversation
WHEN they send /cancel at any step
THEN the conversation is cancelled
AND the bot confirms cancellation
AND returns to the main menu
```

```
GIVEN a user tries to create a task with empty title
WHEN they send an empty message or only whitespace
THEN the bot asks them to provide a valid title
AND does NOT save an empty task
```

**Examples:**

| Input | Expected Output |
|-------|----------------|
| Title: "Buy groceries" | Task created with title "Buy groceries" |
| Title: "" (empty) | "Please provide a task title." |
| Title: "A".repeat(500) | Task created (long titles allowed up to 500 chars) |

**Complexity**: M (1-2 days)
**Dependencies**: US-1

---

### US-4: View Task List

**As a** user
**I want to** see all my tasks with their status
**So that** I can track my progress

**Acceptance Criteria:**

```
GIVEN a user clicks "Tasks" → "My Tasks"
WHEN the bot fetches their tasks
THEN it displays tasks grouped by status (Pending, Done)
AND each task shows title, priority, and creation date
AND each task has inline buttons: Complete, Delete
```

```
GIVEN a user has no tasks
WHEN they view "My Tasks"
THEN the bot shows "No tasks yet" message
AND offers an "Add Task" button
```

**Complexity**: M (1-2 days)
**Dependencies**: US-3

---

### US-5: Complete or Delete a Task

**As a** user
**I want to** mark tasks as done or delete them
**So that** I can manage my task list

**Acceptance Criteria:**

```
GIVEN a user views their task list
WHEN they click "Complete" on a task
THEN the task status changes to "Done"
AND the bot confirms with updated task list
```

```
GIVEN a user views their task list
WHEN they click "Delete" on a task
THEN the bot asks for confirmation via inline keyboard (Yes/No)
AND if confirmed, deletes the task and shows updated list
AND if denied, returns to task list unchanged
```

**Complexity**: S (hours)
**Dependencies**: US-4

---

### US-6: User Settings

**As a** user
**I want to** configure my preferences
**So that** the bot works the way I prefer

**Acceptance Criteria:**

```
GIVEN a user clicks "Settings" in the main menu
WHEN the settings panel opens
THEN they see options: Language, Notifications, Timezone
AND each option has inline keyboard choices
AND changes are saved to the database immediately
```

**Complexity**: M (1-2 days)
**Dependencies**: US-1

---

## 4. Scope

### In Scope
- Bot setup with grammY framework (polling mode for dev, webhook for prod)
- Command handlers: /start, /help, /tasks, /settings
- Inline keyboards for navigation and actions
- Multi-step conversation for task creation
- SQLite database with Drizzle ORM for persistence
- User and task data models
- Session management for conversation state
- Basic middleware: logging, error handling

### Out of Scope
- Group chat support — Reason: v1 is private chat only
- File/media handling — Reason: text-only for v1
- Payment integration — Reason: not needed for task management
- Multi-language i18n — Reason: English only for v1
- Admin panel or web dashboard — Reason: bot-only interface for v1
- Push notification scheduling — Reason: future enhancement

### Future Considerations
- Recurring tasks with cron-based reminders
- Task sharing between users
- Integration with external calendars (Google Calendar)
- Web mini-app for richer UI

> **Agent rule**: Do NOT implement anything under "Out of Scope" or "Future Considerations".

---

## 5. Technical Context

### Relevant Files

| File | Purpose |
|------|---------|
| `src/bot/bot.ts` | Bot instance and plugin setup |
| `src/bot/config.ts` | Environment configuration |
| `src/types/context.ts` | Custom context type with session |
| `src/db/schema.ts` | Drizzle database schema |
| `src/commands/` | Command handler directory |
| `src/callbacks/` | Callback query handlers |
| `src/conversations/` | Conversation flows |
| `src/keyboards/` | Keyboard builders |

### Data Model Changes

```sql
-- Users table
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  telegram_id INTEGER UNIQUE NOT NULL,
  username TEXT,
  first_name TEXT,
  language TEXT DEFAULT 'en',
  timezone TEXT DEFAULT 'UTC',
  notifications_enabled INTEGER DEFAULT 1,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Tasks table
CREATE TABLE tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL REFERENCES users(id),
  title TEXT NOT NULL,
  description TEXT,
  priority TEXT DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high')),
  status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'done')),
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  completed_at TEXT
);
```

### Constraints
- Bot token must be stored in `.env`, never in code
- SQLite database file stored locally (no external DB dependency)
- All Telegram API calls through grammY (no raw HTTP)
- Response time target: < 1 second for all commands

---

## 6. Design & UX

### User Flow
```
/start → Welcome + Main Menu
  ├── Tasks → [Add Task, My Tasks]
  │    ├── Add Task → Conversation: title → description → priority → saved
  │    └── My Tasks → List with [Complete, Delete] buttons per task
  ├── Help → Command list + Back button
  └── Settings → [Language, Notifications, Timezone] → saved
```

### Error States

| Error Condition | User-Facing Message | Recovery Action |
|----------------|---------------------|-----------------|
| Database error | "Something went wrong. Please try again." | Retry the action |
| Invalid input in conversation | "Please provide a valid [field]." | Re-ask the question |
| Task not found (deleted) | "This task no longer exists." | Show updated list |
| Rate limited | "Too many requests. Please wait a moment." | Auto-retry after delay |

---

## 7. Non-Functional Requirements

| Requirement | Target | How to Validate |
|-------------|--------|-----------------|
| Response time | < 1s for commands | Manual testing + logs |
| Test coverage | > 80% new code | `pnpm test:coverage` |
| Type safety | 0 TypeScript errors | `pnpm typecheck` |
| Lint | 0 ESLint errors | `pnpm lint` |

---

## 8. Success Metrics

### Primary Metrics
| Metric | Baseline | Target | How Measured |
|--------|----------|--------|-------------|
| Bot responds to /start | N/A | 100% | Automated test |
| Task CRUD works | N/A | All AC pass | Test suite |
| All commands handled | N/A | 6 commands | Command count |

### Guardrail Metrics
- No unhandled errors in production logs
- Database migrations are reversible
- Bot token never appears in logs or code

---

## 9. Implementation Phases

### Phase 1: Bot Setup
1. Initialize project with pnpm, TypeScript, grammY
2. Create bot instance, config, custom context type
3. Implement /start and /help commands
4. Write tests for Phase 1

**Validation**: `pnpm typecheck && pnpm lint && pnpm test`

### Phase 2: Database
1. Set up Drizzle with SQLite
2. Create users and tasks schema
3. Write migration runner
4. Write tests for DB operations

**Validation**: `pnpm typecheck && pnpm lint && pnpm test`

### Phase 3: Task Management
1. Create task service (CRUD operations)
2. Implement "Add Task" conversation flow
3. Implement "My Tasks" list with inline keyboards
4. Implement Complete/Delete callback handlers
5. Write tests for task flows

**Validation**: `pnpm typecheck && pnpm lint && pnpm test`

### Phase 4: Settings & Polish
1. Implement /settings command with inline keyboard
2. Add error handling middleware
3. Add logging middleware
4. Update bot menu commands
5. Write tests

**Validation**: `pnpm typecheck && pnpm lint && pnpm test`

### Phase 5: Webhook (Production)
1. Add Express server for webhook mode
2. Configure MODE switch (polling/webhook)
3. Add health check endpoint
4. Write tests

**Validation**: `pnpm typecheck && pnpm lint && pnpm test`

---

## 10. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Telegram API rate limits | Medium | Medium | Rate-limit middleware, exponential backoff |
| SQLite concurrent writes | Low | Medium | WAL mode, single-process architecture |
| Bot token leak | Low | Critical | .env only, .gitignore, pre-commit hook |
| Conversation state loss on restart | Medium | Low | grammY session plugin with DB storage |

---

## 11. Boundaries

### ALWAYS (agent can do freely)
- Run tests, linters, type checks
- Create/edit files within scope of this feature
- Follow grammY patterns from existing codebase

### ASK FIRST (requires human approval)
- Add new dependencies beyond grammY, Drizzle, Vitest, Express
- Modify database schema beyond what's specified above
- Change shared interfaces

### NEVER
- Commit bot token or any secrets
- Skip writing tests
- Bypass type safety
- Modify existing migration files

---

## 12. Validation Checklist

- [ ] All acceptance criteria have passing tests
- [ ] `pnpm typecheck && pnpm lint && pnpm test` passes
- [ ] No secrets in code
- [ ] Database migrations are reversible
- [ ] All 6 commands work (/start, /help, /tasks, /settings, /cancel + menu)
- [ ] Inline keyboards respond correctly
- [ ] Conversation flow handles cancellation
- [ ] Error states show user-friendly messages
- [ ] Code review approved

---

## Agent Processing Notes

### For Architect Agent
- Focus on Technical Context section and data model
- Use grammY's Composer pattern for modularity
- Plan for polling (dev) and webhook (prod) modes

### For Implementer Agent
- User Stories define WHAT to build
- Acceptance Criteria define WHEN it's done
- Implementation Phases define the ORDER
- Follow grammY conventions from `PROJECT.md`

### For Tester Agent
- Map every GIVEN/WHEN/THEN to at least one test
- Error States table requires negative test cases
- Mock Telegram API calls, never call real API

### For Code Reviewer Agent
- Check that bot token is not hardcoded
- Verify all callback queries call `answerCallbackQuery()`
- Ensure conversations handle cancellation
