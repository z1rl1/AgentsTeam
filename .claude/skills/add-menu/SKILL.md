---
name: add-menu
description: "Set up bot command menu visible in Telegram's UI. Use when the user wants to configure the commands list that appears when users type '/' in the bot chat."
---

# Add Bot Menu

Configure the bot's command menu that appears in Telegram's UI.

## Step 1: Analyze Existing Commands

Read all handlers in `src/commands/` to build the command list.
Read `src/bot/bot.ts` for current bot setup.

## Step 2: Create Menu Configuration

Create or update `src/bot/menu.ts`:

```typescript
import type { Bot } from "grammy";
import type { BotContext } from "../types/context.js";

export const setBotCommands = async (bot: Bot<BotContext>) => {
  await bot.api.setMyCommands([
    { command: "start", description: "Start the bot" },
    { command: "help", description: "Show help message" },
    // Add all public commands here
  ]);
};
```

Follow these patterns:
- Only include user-facing commands (not admin commands)
- Keep descriptions concise (under 256 characters)
- Order commands by importance/frequency of use
- Use `setMyCommands` with `scope` parameter for role-specific menus

## Step 3: Register on Bot Start

Call `setBotCommands(bot)` during bot initialization in `src/bot/bot.ts` or the entry point.

## Step 4: Validate

Run `pnpm typecheck && pnpm lint && pnpm test`.
