---
name: node-backend
description: Node.js backend patterns including middleware, error handling, logging, input validation, and async patterns. Auto-loads when working with server-side code, Express/Fastify routes, middleware, or backend services.
user-invocable: false
---

# Node.js Backend Conventions

Apply these patterns when working with server-side Node.js code.

## Project Structure

```
src/
├── routes/          # Route definitions (thin — delegate to services)
├── services/        # Business logic
├── models/          # Data models / entities
├── middleware/       # Express/Fastify middleware
├── lib/             # Shared utilities
├── config/          # Environment config, constants
└── types/           # TypeScript type definitions
```

## Error Handling

### Custom Error Classes
```typescript
class AppError extends Error {
  constructor(
    public statusCode: number,
    message: string,
    public code?: string,
  ) {
    super(message);
    this.name = "AppError";
  }
}

class NotFoundError extends AppError {
  constructor(resource: string) {
    super(404, `${resource} not found`, "NOT_FOUND");
  }
}
```

### Centralized Error Handler
```typescript
// Always the LAST middleware
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      error: { code: err.code, message: err.message },
    });
  }
  // Log unexpected errors, return generic message
  logger.error("Unhandled error", { error: err, path: req.path });
  res.status(500).json({ error: { code: "INTERNAL", message: "Internal server error" } });
});
```

### Async Error Wrapping
```typescript
// Wrap async route handlers to catch promise rejections
const asyncHandler = (fn: RequestHandler) => (req, res, next) =>
  Promise.resolve(fn(req, res, next)).catch(next);

router.get("/users/:id", asyncHandler(async (req, res) => {
  const user = await userService.findById(req.params.id);
  if (!user) throw new NotFoundError("User");
  res.json({ data: user });
}));
```

## Input Validation

Validate at the API boundary, trust internally:

```typescript
import { z } from "zod";

const CreateUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
  role: z.enum(["user", "admin"]).default("user"),
});

router.post("/users", asyncHandler(async (req, res) => {
  const data = CreateUserSchema.parse(req.body); // throws ZodError if invalid
  const user = await userService.create(data);
  res.status(201).json({ data: user });
}));
```

## Middleware Patterns

```typescript
// Authentication middleware
const authenticate = asyncHandler(async (req, res, next) => {
  const token = req.headers.authorization?.replace("Bearer ", "");
  if (!token) throw new AppError(401, "Missing token", "UNAUTHORIZED");
  req.user = await verifyToken(token);
  next();
});

// Authorization middleware
const authorize = (...roles: string[]) => (req, res, next) => {
  if (!roles.includes(req.user.role)) {
    throw new AppError(403, "Insufficient permissions", "FORBIDDEN");
  }
  next();
};
```

## Logging

- Use structured logging (JSON format in production)
- Include request ID for tracing
- Log at appropriate levels: error (failures), warn (degraded), info (operations), debug (development)
- Never log sensitive data (passwords, tokens, PII)

## Environment Configuration

```typescript
// config/env.ts — validate at startup, fail fast
const EnvSchema = z.object({
  NODE_ENV: z.enum(["development", "production", "test"]),
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
});

export const env = EnvSchema.parse(process.env);
```

## Anti-Patterns to Avoid

- Do NOT put business logic in route handlers — routes should be thin, delegate to services
- Do NOT use `try/catch` in every handler — use async wrapper + centralized error handler
- Do NOT return stack traces in production error responses
- Do NOT use `console.log` — use a structured logger
- Do NOT read `process.env` throughout the code — centralize in config
- Do NOT store state in module-level variables (breaks with multiple instances)
