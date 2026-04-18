---
name: resume
description: Restore context from STATE.md and continue where the last session left off. Loads referenced documents and presents a summary of current state.
disable-model-invocation: false
---

# Resume: Restore Session Context

Pick up where the last session left off by loading saved state.

## Step 1: Load State

Read `docs/state/STATE.md` and parse the YAML frontmatter.

If the phase is `idle` and there is no active feature, tell the user:
"No saved session state found. Start a new task with `/new-feature`, `/fix-bug`, `/plan`, or `/quick`."

## Step 2: Load Referenced Documents

Read all files referenced in the STATE.md frontmatter:
- PRD file (if `prd` is set)
- Design doc (if `design` is set)
- Plan file (if `plan` is set)
- Context doc in `docs/architecture/CONTEXT-*.md` (if one exists for this feature)

## Step 3: Check Current Environment

- Run `git status` to check for uncommitted changes
- Run `git branch --show-current` to verify we're on the expected branch
- Run `git log -5 --oneline` to see recent commits
- If the branch doesn't match STATE.md, warn the user

## Step 4: Present Summary

```markdown
## Session Restored

**Feature**: [feature name]
**Phase**: [current phase]
**Branch**: [branch name]
**Last Updated**: [date]

### Completed
- [completed steps from STATE.md]

### Next Steps
- [next steps from STATE.md]

### Key Decisions
- [decisions from STATE.md]

### Blockers
- [blockers if any, or "None"]

### Context Notes
- [any important context]
```

## Step 5: Confirm

Ask: "Ready to continue with the next steps, or do you want to review any of the referenced documents first?"

## Step 6: Update State

Update `docs/state/STATE.md`:
- Set **status** to `active`
- Update **updated** to current date
