---
name: pause
description: Save current work context to STATE.md for session continuity. Captures branch, phase, decisions, and next steps.
disable-model-invocation: true
---

# Pause: Save Session State

Save the current work context so it can be resumed later.

## Step 1: Gather Current State

- Run `git status` and `git branch --show-current` to capture branch and working tree state
- Read the existing `docs/state/STATE.md`
- Check for active PRDs in `docs/prds/`, design docs in `docs/architecture/`, and plans in `docs/plans/`

## Step 2: Update STATE.md

Update `docs/state/STATE.md` with:

### YAML Frontmatter
- **phase**: Current workflow phase (planning | discussing | designing | implementing | testing | reviewing | paused)
- **status**: Set to `paused`
- **feature**: Name of the feature or bug being worked on
- **branch**: Current git branch
- **prd**: Path to active PRD (if any)
- **design**: Path to active design doc (if any)
- **plan**: Path to active plan file (if any)
- **updated**: Current date (ISO format)
- **blockers**: Any known blockers

### Markdown Body
- **Current Focus**: What was being worked on when pausing
- **Decisions Made**: Key decisions made this session (append to existing, do not overwrite)
- **Completed Steps**: What has been done so far (checklist format)
- **Next Steps**: What should happen when resuming
- **Context Notes**: Any important context that would be lost between sessions (error messages, patterns discovered, things tried, etc.)

## Step 3: Commit

Stage and commit `docs/state/STATE.md`:

```
chore: save session state
```

## Step 4: Confirm

Tell the user:
- State has been saved
- Which branch they're on
- What the next steps are when they resume
- Remind them to use `/resume` to pick up where they left off
