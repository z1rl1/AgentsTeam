---
name: add-command
description: "Create a new bot command handler for grammY. Use when the user wants to add a new slash command to the Telegram bot (e.g., /start, /help, /settings, /tasks)."
---

# Add Bot Command: $ARGUMENTS

Create a new command handler for the `/$ARGUMENTS` bot command.

## Step 1: Analyze Existing Commands

Read existing handlers in `src/commands/` to understand the pattern.
Read `src/types/context.ts` for the custom context type.

## Step 2: Create Handler

Create `src/commands/$ARGUMENTS.ts`:

```typescript
import { Composer } from "grammy";
import type { BotContext } from "../types/context.js";

export const $ARGUMENTSCommand = new Composer<BotContext>();

$ARGUMENTSCommand.command("$ARGUMENTS", async (ctx) => {
  // Handler logic here
  await ctx.reply("Response text");
});
```

Follow these patterns:
- Use `Composer` for modular handler registration
- Type context with `BotContext` from `src/types/context.ts`
- Handle errors explicitly, never swallow
- Use session data when state is needed
- Export as named export

## Step 3: Register

Add the command to the bot's composer chain in `src/bot/bot.ts`:
```typescript
import { $ARGUMENTSCommand } from "../commands/$ARGUMENTS.js";
bot.use($ARGUMENTSCommand);
```

## Step 4: Write Test

Create `tests/commands/$ARGUMENTS.test.ts` following existing test patterns.
Test happy path and error cases.

## Step 5: Validate

Run `pnpm typecheck && pnpm lint && pnpm test`.
