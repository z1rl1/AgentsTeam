---
name: add-callback
description: "Add a callback query handler for inline button interactions. Use when the user wants to handle inline keyboard button presses in the Telegram bot."
---

# Add Callback Handler: $ARGUMENTS

Create a callback query handler for inline button interactions.

## Step 1: Analyze Existing Callbacks

Read existing handlers in `src/callbacks/` to understand the pattern.
Read `src/types/context.ts` for the custom context type.

## Step 2: Create Handler

Create `src/callbacks/$ARGUMENTS.ts`:

```typescript
import { Composer } from "grammy";
import type { BotContext } from "../types/context.js";

export const $ARGUMENTSCallback = new Composer<BotContext>();

$ARGUMENTSCallback.callbackQuery(/^$ARGUMENTS:/, async (ctx) => {
  const data = ctx.callbackQuery.data;
  // Parse callback data after the prefix
  // Handle the action
  await ctx.answerCallbackQuery(); // Always answer to remove loading state
  await ctx.editMessageText("Updated text");
});
```

Follow these patterns:
- Use regex pattern matching for callback data prefixes
- Always call `ctx.answerCallbackQuery()` to dismiss the loading spinner
- Use `ctx.editMessageText()` or `ctx.editMessageReplyMarkup()` to update the message
- Handle the case where the message might have been deleted

## Step 3: Register

Add to the bot's composer chain in `src/bot/bot.ts`.

## Step 4: Write Test

Create `tests/callbacks/$ARGUMENTS.test.ts`.

## Step 5: Validate

Run `pnpm typecheck && pnpm lint && pnpm test`.
