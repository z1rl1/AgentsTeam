---
name: nextjs-conventions
description: Next.js App Router conventions, Server vs Client Components, data fetching patterns, middleware, and routing. Auto-loads when working with Next.js routing, page.tsx, layout.tsx, API routes, or server components.
user-invocable: false
---

# Next.js Conventions

Apply these patterns when working with Next.js in this project.

## App Router Structure

```
app/
├── layout.tsx          # Root layout (wraps all pages)
├── page.tsx            # Home page (/)
├── loading.tsx         # Loading UI for this segment
├── error.tsx           # Error boundary for this segment
├── not-found.tsx       # 404 for this segment
├── (group)/            # Route group (no URL impact)
│   └── page.tsx
├── [slug]/             # Dynamic segment
│   └── page.tsx
└── api/
    └── route.ts        # API route handler
```

## Server vs Client Components

### Default to Server Components
- All components are Server Components by default
- They can directly `await` data, read from DB, access secrets
- They send zero JavaScript to the client

### Use `"use client"` Only When Needed
Add `"use client"` directive when the component uses:
- `useState`, `useReducer`, `useEffect`, `useContext`
- Browser APIs (`window`, `document`, `localStorage`)
- Event handlers (`onClick`, `onChange`, etc.)
- Third-party client libraries

### Boundary Pattern
```
ServerComponent (fetches data)
  └── ClientComponent (handles interactivity)
       └── ServerComponent (can be passed as children)
```

Push `"use client"` as far down the tree as possible.

## Data Fetching

### In Server Components (preferred)
```tsx
// Direct async/await in the component
export default async function Page() {
  const data = await fetchData();
  return <div>{data.title}</div>;
}
```

### Route Handlers (API endpoints)
```tsx
// app/api/resource/route.ts
export async function GET(request: Request) {
  const data = await db.query();
  return Response.json(data);
}

export async function POST(request: Request) {
  const body = await request.json();
  // validate, process, respond
}
```

### Server Actions (mutations)
```tsx
"use server";

export async function createItem(formData: FormData) {
  // validate input
  // mutate database
  // revalidate cache
  revalidatePath("/items");
}
```

## Caching & Revalidation

- `fetch` calls in Server Components are cached by default
- Use `{ next: { revalidate: 60 } }` for time-based revalidation
- Use `revalidatePath()` or `revalidateTag()` for on-demand revalidation
- Use `{ cache: "no-store" }` for data that must always be fresh

## Middleware

```tsx
// middleware.ts (root level)
export function middleware(request: NextRequest) {
  // auth checks, redirects, headers
}

export const config = {
  matcher: ["/dashboard/:path*", "/api/:path*"],
};
```

## Metadata

```tsx
// Static metadata
export const metadata: Metadata = {
  title: "Page Title",
  description: "Page description",
};

// Dynamic metadata
export async function generateMetadata({ params }): Promise<Metadata> {
  const data = await fetchData(params.id);
  return { title: data.title };
}
```

## Anti-Patterns to Avoid

- Do NOT use `"use client"` on data-fetching components — fetch on the server
- Do NOT pass serialization-unfriendly props (functions, classes) from Server to Client Components
- Do NOT use `getServerSideProps` or `getStaticProps` — those are Pages Router
- Do NOT read environment variables prefixed with `NEXT_PUBLIC_` on the server — use server-only env vars
- Do NOT create API routes just to fetch data for Server Components — fetch directly
