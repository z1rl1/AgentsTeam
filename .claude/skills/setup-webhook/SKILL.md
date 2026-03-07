---
name: setup-webhook
description: "Configure webhook deployment for the Telegram bot with Express. Use when moving from polling to webhook mode for production deployment."
disable-model-invocation: true
---

# Setup Webhook

Configure the bot for production webhook deployment.

## Step 1: Analyze Current Setup

Read `src/bot/bot.ts` and `src/bot/config.ts` to understand current bot setup.
Check if Express is already a dependency in `package.json`.

## Step 2: Add Express Server

Create or update `src/webhook.ts`:

```typescript
import express from "express";
import { webhookCallback } from "grammy";
import { bot } from "./bot/bot.js";
import { config } from "./bot/config.js";

const app = express();

app.use(express.json());

// Health check endpoint
app.get("/health", (_req, res) => {
  res.json({ status: "ok" });
});

// Webhook endpoint
app.use(`/webhook/${config.WEBHOOK_SECRET}`, webhookCallback(bot, "express"));

app.listen(config.PORT, () => {
  console.log(`Webhook server listening on port ${config.PORT}`);
});
```

## Step 3: Update Config

Add webhook-related environment variables to `src/bot/config.ts`:
- `WEBHOOK_URL` — public URL for the webhook
- `WEBHOOK_SECRET` — secret path segment for security
- `PORT` — server port (default 3000)
- `MODE` — "polling" or "webhook"

## Step 4: Update Entry Point

Modify the main entry point to support both modes:
- `MODE=polling` → use `bot.start()` (development)
- `MODE=webhook` → use Express server (production)

## Step 5: Add Scripts

Update `package.json`:
```json
{
  "scripts": {
    "start:webhook": "node dist/webhook.js",
    "webhook:set": "tsx scripts/set-webhook.ts"
  }
}
```

## Step 6: Write Test

Test webhook endpoint responds correctly.

## Step 7: Validate

Run `pnpm typecheck && pnpm lint && pnpm test`.
