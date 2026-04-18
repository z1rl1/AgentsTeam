---
name: migrate
description: Database or API migration workflow. Designs migration strategy, generates migration files, validates data integrity, and provides rollback plan.
argument-hint: [migration description]
disable-model-invocation: true
context: fork
---

# Migration Workflow

Structured process for database schema changes, API migrations, or data transformations.

## Step 1: Read Context

- Read `PROJECT.md` for database, ORM, and migration commands
- Identify the migration framework (Prisma, Drizzle, Knex, Alembic, etc.)
- Review existing migrations for patterns

## Step 2: Design Migration

Use the **architect** agent to design the migration:
- What changes are needed and why
- Data transformation logic (if migrating existing data)
- Rollback strategy (explicit steps to undo)
- Zero-downtime considerations (if applicable)

## Step 3: Human Review

Present the migration plan. Explicitly highlight:
- **Destructive operations** (column drops, table deletions, data loss)
- **Data transformations** (what happens to existing rows)
- **Rollback procedure** (step-by-step undo)
- **Estimated risk level**: Low / Medium / High

Wait for approval before proceeding.

## Step 4: Create Migration Files

Create branch: `chore/migrate-[description]`

Use the **implementer** agent to generate migration files following existing patterns:
- Up migration (apply changes)
- Down migration (rollback changes)
- Seed data updates (if needed)

## Step 5: Test Migration

- Run migration up: verify schema matches expectations
- Run migration down: verify clean rollback
- Run migration up again: verify idempotency
- Check that no data is lost or corrupted

## Step 6: Update Application Code

Use the **implementer** agent to update:
- Models / entity definitions
- Repository / data access layer
- Services that depend on changed schema
- API response shapes (if schema change affects API)
- TypeScript types / interfaces

## Step 7: Validate

Run full validation from `PROJECT.md`:
- Lint, type check, tests, build
- Verify data integrity assertions

## Step 8: Review

Use the **code-reviewer** agent with focus on:
- Data safety (no silent data loss)
- Rollback completeness
- Migration idempotency

## Step 9: Summary

Present:
- Migration files created
- Application code updated
- Test results
- Rollback procedure documented
- Ask about PR creation

---

Migration: $ARGUMENTS
