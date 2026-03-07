---
name: add-keyboard
description: "Create an inline or reply keyboard for the Telegram bot. Use when the user wants to add buttons, menus, or interactive keyboards to bot messages."
---

# Add Keyboard: $ARGUMENTS

Create a keyboard builder for the bot.

## Step 1: Determine Keyboard Type

- **InlineKeyboard**: Buttons attached to a message (callback queries)
- **Keyboard** (Reply): Persistent buttons replacing the user's keyboard

## Step 2: Create Keyboard Builder

Create `src/keyboards/$ARGUMENTS.ts`:

### For Inline Keyboard:
```typescript
import { InlineKeyboard } from "grammy";

export const build$ARGUMENTSKeyboard = (data?: unknown): InlineKeyboard => {
  return new InlineKeyboard()
    .text("Button 1", "callback_prefix:action1")
    .text("Button 2", "callback_prefix:action2")
    .row()
    .text("Button 3", "callback_prefix:action3");
};
```

### For Reply Keyboard:
```typescript
import { Keyboard } from "grammy";

export const build$ARGUMENTSKeyboard = (): Keyboard => {
  return new Keyboard()
    .text("Option 1").text("Option 2")
    .row()
    .text("Option 3")
    .resized()
    .oneTime();
};
```

Follow these patterns:
- Keyboard builders are pure functions that return keyboard instances
- Use `.row()` to start a new row of buttons
- For inline keyboards, use structured callback data: `prefix:action:id`
- Keep callback data under 64 bytes (Telegram limit)
- Use `.resized()` for reply keyboards to fit button text

## Step 3: Use in Handler

Import and use in the relevant command or callback handler:
```typescript
import { build$ARGUMENTSKeyboard } from "../keyboards/$ARGUMENTS.js";

await ctx.reply("Choose an option:", {
  reply_markup: build$ARGUMENTSKeyboard(),
});
```

## Step 4: Write Test

Create `tests/keyboards/$ARGUMENTS.test.ts`.

## Step 5: Validate

Run `pnpm typecheck && pnpm lint && pnpm test`.
