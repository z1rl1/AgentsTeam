---
name: frontend-testing
description: React Testing Library patterns, component test structure, mocking strategies (MSW, jest.mock), and accessibility testing. Auto-loads when writing tests for React components or frontend code.
user-invocable: false
---

# Frontend Testing Conventions

Apply these patterns when writing tests for React components.

## Testing Philosophy

- Test behavior, not implementation
- Test what the user sees and does, not internal state
- If a refactor doesn't change behavior, tests shouldn't break
- Prioritize: user flows > component behavior > edge cases > snapshots

## React Testing Library Query Priority

Use queries in this order (most preferred first):

1. **`getByRole`** — Accessible by everyone (screen readers, keyboard, mouse)
2. **`getByLabelText`** — Form fields
3. **`getByPlaceholderText`** — When no label exists
4. **`getByText`** — Non-interactive elements
5. **`getByDisplayValue`** — Filled form elements
6. **`getByAltText`** — Images
7. **`getByTestId`** — Last resort only

## Test Structure

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

describe("ComponentName", () => {
  it("should [expected behavior] when [condition]", async () => {
    // Arrange
    const user = userEvent.setup();
    render(<Component prop="value" />);

    // Act
    await user.click(screen.getByRole("button", { name: /submit/i }));

    // Assert
    expect(screen.getByText(/success/i)).toBeInTheDocument();
  });
});
```

## User Interaction

Always use `userEvent` over `fireEvent`:

```tsx
const user = userEvent.setup();

// Typing
await user.type(screen.getByRole("textbox"), "hello");

// Clicking
await user.click(screen.getByRole("button", { name: /save/i }));

// Selecting
await user.selectOptions(screen.getByRole("combobox"), "option-value");

// Keyboard
await user.keyboard("{Enter}");
```

## Async Testing

```tsx
// Wait for element to appear
expect(await screen.findByText(/loaded/i)).toBeInTheDocument();

// Wait for element to disappear
await waitForElementToBeRemoved(() => screen.queryByText(/loading/i));

// Assert element does NOT exist
expect(screen.queryByText(/error/i)).not.toBeInTheDocument();
```

## Mocking API Calls (MSW)

```tsx
import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";

const server = setupServer(
  http.get("/api/users", () => {
    return HttpResponse.json({ data: [{ id: 1, name: "Alice" }] });
  }),
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

it("shows users from API", async () => {
  render(<UserList />);
  expect(await screen.findByText("Alice")).toBeInTheDocument();
});

it("shows error on API failure", async () => {
  server.use(
    http.get("/api/users", () => {
      return HttpResponse.json({ error: "fail" }, { status: 500 });
    }),
  );
  render(<UserList />);
  expect(await screen.findByText(/error/i)).toBeInTheDocument();
});
```

## Accessibility Testing

```tsx
import { axe, toHaveNoViolations } from "jest-axe";
expect.extend(toHaveNoViolations);

it("should have no accessibility violations", async () => {
  const { container } = render(<Component />);
  expect(await axe(container)).toHaveNoViolations();
});
```

## What to Test

- User interactions (click, type, submit)
- Conditional rendering (loading, error, empty states)
- Form validation and submission
- Navigation and routing
- Accessibility (keyboard nav, screen reader)

## Anti-Patterns to Avoid

- Do NOT test implementation details (state values, method calls)
- Do NOT use `container.querySelector` — use RTL queries
- Do NOT test third-party library internals
- Do NOT write snapshot tests as the primary test strategy
- Do NOT mock everything — prefer MSW for API mocking over jest.mock
- Do NOT use `waitFor` when `findBy` queries work
