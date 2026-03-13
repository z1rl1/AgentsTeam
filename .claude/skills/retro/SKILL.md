---
name: retro
description: Post-implementation retrospective that analyzes what went well, what went poorly, and updates CLAUDE.md with learnings. Improves the team's process over time.
argument-hint: "[optional: feature name or branch to review]"
disable-model-invocation: true
---

# Retrospective: Learn and Improve

Analyze the last implementation cycle and permanently capture learnings.

## Step 1: Gather Context

- `git log -20 --oneline` to review recent history
- Read execution reports in `docs/plans/` if they exist
- Read any system review outputs
- Read `docs/state/STATE.md` for session history
- If `$ARGUMENTS` specifies a feature/branch, focus on that

## Step 2: Analyze the Lifecycle

- Time from first commit to merge (commit timestamps)
- Number of iterations/rework cycles
- Divergences from plan (from execution reports)
- Review findings (from code review artifacts)
- Test coverage achieved
- Validation failures encountered

## Step 3: Interactive Discussion

Ask the user structured questions:

### What went well?
- Planning quality (was the plan accurate?)
- Agent accuracy (did agents produce good output?)
- Test coverage (were tests sufficient?)
- Speed (was the workflow efficient?)

### What went poorly?
- Rework needed (what had to be redone?)
- Misunderstood requirements?
- Agent errors or unhelpful output?
- Context loss between sessions?
- Missing skills or tooling?

### What should change?
- Process adjustments?
- Agent instruction improvements?
- New CLAUDE.md rules?
- New or modified skills?

## Step 4: Generate Retro Document

Save to `docs/plans/retro-[feature-name].md`:

```markdown
# Retrospective: [Feature Name]
**Date**: [date]
**Branch**: [branch]

## Summary
[brief overview]

## What Went Well
- [items]

## What Went Poorly
- [items]

## Root Causes
- [why things went poorly]

## Action Items
- [ ] [specific improvement with owner]
```

## Step 5: Propose CLAUDE.md Updates

Based on learnings, draft specific additions/modifications to CLAUDE.md:
- New rules or conventions discovered
- Anti-patterns to avoid
- Process improvements

Present each proposed change for approval.

## Step 6: Apply Approved Changes

Update CLAUDE.md with approved changes only.

## Step 7: Commit

```bash
git add docs/plans/retro-*.md CLAUDE.md
git commit -m "docs: retrospective for [feature]"
```

---

Feature: $ARGUMENTS
