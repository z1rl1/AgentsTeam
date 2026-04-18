---
name: database-patterns
description: Database schema design, migrations, query optimization, indexing strategy, and ORM patterns. Auto-loads when working with database queries, schemas, migrations, models, or data access code.
user-invocable: false
---

# Database Patterns & Conventions

Apply these patterns when working with database code.

## Schema Design

### Standard Fields
Every table should have:
- `id` — Primary key (prefer UUID for distributed systems, auto-increment for simplicity)
- `created_at` — Timestamp, set on creation, never modified
- `updated_at` — Timestamp, updated on every modification

### Soft Deletes
For data that should be recoverable:
- `deleted_at` — Nullable timestamp; `NULL` means active
- Filter soft-deleted records by default in all queries
- Create a partial index on `deleted_at IS NULL` for performance

### Naming Conventions
- Table names: plural, snake_case (`user_profiles`)
- Column names: snake_case (`first_name`)
- Foreign keys: `{singular_table}_id` (`user_id`)
- Indexes: `idx_{table}_{columns}` (`idx_users_email`)
- Unique constraints: `uniq_{table}_{columns}`

## Migrations

### Rules
- Migrations are **append-only** — never modify a migration after it's been applied
- Each migration must have an `up` and `down` function
- Test both directions: up → verify → down → verify → up
- Keep migrations small and focused (one logical change per migration)
- Destructive operations (drop column, drop table) should be separate migrations with clear naming

### Zero-Downtime Pattern
For column renames or type changes:
1. Add new column
2. Deploy code that writes to both columns
3. Backfill existing data
4. Deploy code that reads from new column
5. Drop old column

## Query Optimization

### N+1 Prevention
```typescript
// BAD: N+1 queries
const users = await db.users.findAll();
for (const user of users) {
  user.posts = await db.posts.findByUserId(user.id); // N queries!
}

// GOOD: Eager loading / join
const users = await db.users.findAll({
  include: [{ model: db.posts }],
});

// GOOD: Batch loading
const users = await db.users.findAll();
const userIds = users.map(u => u.id);
const posts = await db.posts.findAll({ where: { userId: userIds } });
```

### Indexing Strategy
- Always index foreign keys
- Index columns used in `WHERE`, `JOIN`, and `ORDER BY` clauses
- Use composite indexes for multi-column queries (order matters: most selective first)
- Use partial indexes for filtered queries (`WHERE deleted_at IS NULL`)
- Monitor query plans with `EXPLAIN ANALYZE`

### Pagination
- Use cursor-based pagination for large datasets (keyset pagination)
- Avoid `OFFSET` for deep pages — it scans and discards rows
```sql
-- Cursor-based (fast at any depth)
SELECT * FROM posts WHERE id > :cursor ORDER BY id ASC LIMIT 20;

-- Offset-based (slow at deep pages)
SELECT * FROM posts ORDER BY id ASC LIMIT 20 OFFSET 10000;
```

## Transaction Patterns

```typescript
// Wrap related operations in a transaction
await db.transaction(async (tx) => {
  const order = await tx.orders.create({ userId, total });
  await tx.orderItems.createMany(items.map(i => ({ orderId: order.id, ...i })));
  await tx.inventory.decrementMany(items);
  // If any step fails, everything rolls back
});
```

## Connection Pooling

- Use a connection pool (not individual connections)
- Size the pool based on: `pool_size = (num_cores * 2) + effective_spindle_count`
- Set connection timeout and idle timeout
- Monitor pool usage and waiting queries

## Anti-Patterns to Avoid

- Do NOT use `SELECT *` — specify columns explicitly
- Do NOT store computed values that can be derived from other columns
- Do NOT use `TEXT` for fields with a known max length — use `VARCHAR(n)`
- Do NOT create indexes on every column — they slow down writes
- Do NOT use ORM-generated queries blindly — check the SQL in development
- Do NOT mix business logic into raw SQL — keep queries in the data access layer
