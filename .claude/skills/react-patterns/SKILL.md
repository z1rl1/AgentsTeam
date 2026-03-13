---
name: react-patterns
description: React component patterns, hooks best practices, state management, performance optimization, and accessibility standards. Auto-loads when working with React components, .tsx/.jsx files, hooks, or UI code.
user-invocable: false
---

# React Patterns & Conventions

Apply these patterns when working with React components in this project.

## Component Structure

### File Organization
- One component per file, named same as the component
- Co-locate styles, tests, and types with the component
- Use barrel exports (`index.ts`) for public API of a component directory

### Component Pattern
```tsx
// Prefer function components with explicit typing
interface Props {
  title: string;
  onAction: (id: string) => void;
  children?: React.ReactNode;
}

export function ComponentName({ title, onAction, children }: Props) {
  // hooks at top
  // derived state / computations
  // handlers
  // early returns for loading/error states
  // render
}
```

### Composition Over Configuration
- Prefer composable components over prop-heavy ones
- Use `children` and render props for flexibility
- Use compound components for complex UI (e.g., `<Tabs>`, `<Tabs.Panel>`)

## Hooks Best Practices

### Rules
- Only call hooks at the top level (never in conditions/loops)
- Custom hooks must start with `use`
- Extract repeated hook logic into custom hooks

### State Management Decision Tree
1. **Local UI state** (toggle, form input) → `useState`
2. **Complex local state** (form with many fields, state machine) → `useReducer`
3. **Shared state across siblings** → lift state up to common parent
4. **Shared state across distant components** → React Context or external store
5. **Server state** (API data, caching, revalidation) → React Query / SWR / server components

### Performance Hooks
- `useMemo`: Only for expensive computations. Do NOT wrap everything — React is fast by default
- `useCallback`: Only when passing callbacks to memoized children or dependency arrays
- `memo()`: Only when profiling shows unnecessary re-renders. Measure first

## Error Handling

- Use Error Boundaries for component-level error catching
- Place Error Boundaries at route/section level, not per-component
- Always provide a fallback UI

```tsx
<ErrorBoundary fallback={<ErrorFallback />}>
  <FeatureSection />
</ErrorBoundary>
```

## Suspense & Loading States

- Use `<Suspense>` with fallback for async boundaries
- Co-locate loading states with the components that need them
- Use skeleton UIs over spinners for better perceived performance

## Accessibility

- All interactive elements must be keyboard accessible
- Use semantic HTML elements (`button`, `nav`, `main`, `section`)
- Images must have `alt` text
- Form inputs must have associated labels
- Use ARIA attributes only when semantic HTML is insufficient
- Test with keyboard navigation

## Anti-Patterns to Avoid

- Do NOT use `useEffect` for derived state — compute during render instead
- Do NOT store props in state unless transforming them
- Do NOT use index as key for lists that reorder
- Do NOT reach for Context for high-frequency updates (use external store)
- Do NOT nest ternaries in JSX — extract to variables or early returns
