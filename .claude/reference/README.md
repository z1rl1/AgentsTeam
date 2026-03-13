# Reference Documents

Store tech-stack-specific best practices here. Agents read these when working on specific areas.

## Structure

Create one file per technology or domain. Examples:

- `[framework]-best-practices.md` -- Framework patterns, component structure, idioms
- `[backend]-best-practices.md` -- Backend/API patterns, routing, error handling
- `[database]-best-practices.md` -- Database patterns, queries, migrations
- `testing-best-practices.md` -- Testing patterns, fixtures, coverage

## When to Create

Add reference docs when you choose your tech stack and start building.
These files provide consistent guidance to agents without bloating CLAUDE.md.

## How Agents Use These

Agents are instructed to check `.claude/reference/` when working on specific areas.
The **product-manager** and **architect** agents reference these during planning.
The **implementer** agent follows patterns documented here during coding.
