---
name: backend-testing
description: API and integration test patterns, database test setup/teardown, mocking external services, fixture patterns, and test data factories. Auto-loads when writing backend or API tests.
user-invocable: false
---

# Backend Testing Conventions

Apply these patterns when writing tests for backend/API code.

## Test Organization

```
tests/
├── unit/              # Pure function tests (no I/O)
│   └── services/
├── integration/       # Tests with real DB / external deps
│   └── routes/
├── fixtures/          # Test data and factories
├── helpers/           # Test utilities
└── setup.ts           # Global test setup
```

### Unit vs Integration

| Test Type | What it Tests | Database | External Services | Speed |
|-----------|--------------|----------|------------------|-------|
| Unit | Pure logic, services | Mocked | Mocked | Fast |
| Integration | API routes, DB queries | Real (test DB) | Mocked | Medium |

## API Route Testing

```typescript
import { describe, it, expect } from "vitest"; // or jest
import request from "supertest";
import { app } from "../src/app";

describe("GET /api/users", () => {
  it("returns 200 with user list", async () => {
    const res = await request(app)
      .get("/api/users")
      .set("Authorization", `Bearer ${testToken}`)
      .expect(200);

    expect(res.body.data).toBeInstanceOf(Array);
    expect(res.body.data[0]).toHaveProperty("id");
    expect(res.body.data[0]).toHaveProperty("email");
  });

  it("returns 401 without auth", async () => {
    await request(app).get("/api/users").expect(401);
  });
});

describe("POST /api/users", () => {
  it("creates user and returns 201", async () => {
    const res = await request(app)
      .post("/api/users")
      .set("Authorization", `Bearer ${adminToken}`)
      .send({ email: "new@test.com", name: "New User" })
      .expect(201);

    expect(res.body.data.email).toBe("new@test.com");
  });

  it("returns 400 for invalid email", async () => {
    const res = await request(app)
      .post("/api/users")
      .set("Authorization", `Bearer ${adminToken}`)
      .send({ email: "invalid", name: "Test" })
      .expect(400);

    expect(res.body.error.code).toBe("VALIDATION_ERROR");
  });
});
```

## Database Test Setup

```typescript
// tests/setup.ts
import { db } from "../src/db";

beforeAll(async () => {
  await db.migrate.latest(); // ensure schema is up to date
});

beforeEach(async () => {
  await db.seed.run(); // reset test data
  // OR: truncate all tables
  // await db.raw("TRUNCATE TABLE users, posts CASCADE");
});

afterAll(async () => {
  await db.destroy(); // close connections
});
```

### Transaction Rollback Pattern (faster)
```typescript
let tx: Transaction;

beforeEach(async () => {
  tx = await db.transaction();
  // Patch the db instance to use the transaction
});

afterEach(async () => {
  await tx.rollback(); // instant cleanup, no data persists
});
```

## Test Data Factories

```typescript
// tests/fixtures/factories.ts
import { faker } from "@faker-js/faker";

export function buildUser(overrides: Partial<User> = {}): User {
  return {
    id: faker.string.uuid(),
    email: faker.internet.email(),
    name: faker.person.fullName(),
    role: "user",
    createdAt: new Date(),
    ...overrides,
  };
}

// Usage
const admin = buildUser({ role: "admin" });
const user = buildUser({ email: "specific@test.com" });
```

## Mocking External Services

```typescript
// Mock HTTP calls to external APIs
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";

const server = setupServer(
  http.post("https://api.stripe.com/v1/charges", () => {
    return HttpResponse.json({ id: "ch_test", status: "succeeded" });
  }),
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

## Testing Patterns

### Test Auth Middleware
```typescript
describe("authenticated routes", () => {
  it("rejects expired tokens", async () => {
    const expiredToken = createToken({ exp: Date.now() / 1000 - 3600 });
    await request(app)
      .get("/api/protected")
      .set("Authorization", `Bearer ${expiredToken}`)
      .expect(401);
  });
});
```

### Test Error Handling
```typescript
it("returns 500 on unexpected errors", async () => {
  // Mock the service to throw
  jest.spyOn(userService, "findAll").mockRejectedValueOnce(new Error("DB down"));

  const res = await request(app).get("/api/users").expect(500);
  expect(res.body.error.code).toBe("INTERNAL");
  // Verify the actual error message is NOT leaked
  expect(res.body.error.message).not.toContain("DB down");
});
```

## Anti-Patterns to Avoid

- Do NOT share mutable test state between tests — each test should be independent
- Do NOT test framework behavior (e.g., "Express returns 404 for unknown routes")
- Do NOT hardcode test data — use factories for maintainability
- Do NOT skip cleanup — leaked data causes flaky tests
- Do NOT mock the thing you're testing — mock its dependencies
- Do NOT write tests that pass when the feature is broken (test the negative case too)
