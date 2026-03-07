---
name: add-conversation
description: "Create a multi-step conversation dialog using grammY conversations plugin. Use when the user needs a step-by-step interactive flow (e.g., registration, form filling, onboarding)."
---

# Add Conversation: $ARGUMENTS

Create a multi-step conversation flow using grammY's conversations plugin.

## Step 1: Analyze Existing Conversations

Read existing flows in `src/conversations/` to understand the pattern.
Read `src/types/context.ts` for context type and `src/bot/bot.ts` for plugin setup.

## Step 2: Create Conversation

Create `src/conversations/$ARGUMENTS.ts`:

```typescript
import type { BotContext } from "../types/context.js";
import type { Conversation } from "@grammyjs/conversations";

export const $ARGUMENTSConversation = async (
  conversation: Conversation<BotContext>,
  ctx: BotContext,
) => {
  // Step 1: Ask for input
  await ctx.reply("Please provide [first input]:");
  const step1 = await conversation.waitFor("message:text");
  const value1 = step1.message.text;

  // Step 2: Ask for confirmation
  await ctx.reply(`You entered: ${value1}. Is this correct?`);
  // ... continue with more steps

  // Final: Save and confirm
  await ctx.reply("Done! Your data has been saved.");
};
```

Follow these patterns:
- Each conversation is an async function with `conversation` and `ctx` params
- Use `conversation.waitFor()` to pause and wait for specific update types
- Use `conversation.external()` to call external APIs or database operations
- Handle cancellation gracefully
- Keep conversations focused — one flow per file

## Step 3: Register

Register the conversation in `src/bot/bot.ts`:
```typescript
import { $ARGUMENTSConversation } from "../conversations/$ARGUMENTS.js";
bot.use(createConversation($ARGUMENTSConversation, "$ARGUMENTS"));
```

Add a command or callback to enter the conversation:
```typescript
bot.command("$ARGUMENTS", async (ctx) => {
  await ctx.conversation.enter("$ARGUMENTS");
});
```

## Step 4: Write Test

Create `tests/conversations/$ARGUMENTS.test.ts`.

## Step 5: Validate

Run `pnpm typecheck && pnpm lint && pnpm test`.
