---
name: add-middleware
description: "Add grammY middleware for cross-cutting concerns. Use when the user wants to add logging, authentication, rate limiting, or other middleware to the Telegram bot."
---

# Add Middleware: $ARGUMENTS

Create a custom grammY middleware.

## Step 1: Analyze Existing Middleware

Read existing middleware in `src/middleware/` to understand the pattern.

## Step 2: Create Middleware

Create `src/middleware/$ARGUMENTS.ts`:

```typescript
import type { BotContext } from "../types/context.js";
import type { MiddlewareFn } from "grammy";

export const $ARGUMENTSMiddleware: MiddlewareFn<BotContext> = async (ctx, next) => {
  // Pre-processing (before handler)
  // ... your logic here

  // Pass to next middleware/handler
  await next();

  // Post-processing (after handler, optional)
};
```

Follow these patterns:
- Always call `await next()` unless intentionally blocking the chain
- Use typed `MiddlewareFn<BotContext>` for proper typing
- Keep middleware focused on a single concern
- Log errors but don't swallow them — rethrow after logging
- Place order-sensitive middleware early in the chain

## Step 3: Register

Add to `src/bot/bot.ts` — middleware order matters:
```typescript
import { $ARGUMENTSMiddleware } from "../middleware/$ARGUMENTS.js";
bot.use($ARGUMENTSMiddleware); // Before command handlers
```

## Step 4: Write Test

Create `tests/middleware/$ARGUMENTS.test.ts`.

## Step 5: Validate

Run `pnpm typecheck && pnpm lint && pnpm test`.
