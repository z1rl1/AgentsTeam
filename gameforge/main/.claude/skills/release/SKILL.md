---
name: release
description: Generate release notes, update changelog, and prepare a version bump. Analyzes commits since last tag, categorizes changes, and produces formatted output.
argument-hint: [version number, e.g. v1.2.0]
disable-model-invocation: true
---

# Release: Prepare a New Release

## Step 1: Detect Current Version

- Read package.json / Cargo.toml / pyproject.toml (whichever exists per `PROJECT.md`)
- Get the latest git tag: `git describe --tags --abbrev=0 2>/dev/null`
- If no tags exist, treat all commits as new changes

## Step 2: Gather Changes

```bash
git log [last-tag]..HEAD --oneline --no-merges
```

Parse conventional commit prefixes to categorize.

## Step 3: Categorize Changes

Use the **docs-writer** agent to generate human-readable release notes grouped by:
- **Added** (`feat:` commits)
- **Changed** (`refactor:` commits)
- **Fixed** (`fix:` commits)
- **Performance** (`perf:` commits)
- **Documentation** (`docs:` commits)
- **Other** (`chore:`, `test:`, `style:` commits)

Omit empty categories.

## Step 4: Update CHANGELOG.md

Prepend a new section following [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [version] - YYYY-MM-DD

### Added
- Description of new feature (#PR)

### Fixed
- Description of bug fix (#PR)
```

Create CHANGELOG.md if it doesn't exist.

## Step 5: Version Bump

Update the version in the project's manifest file(s):
- package.json: `"version": "X.Y.Z"`
- Other manifests as appropriate

If `$ARGUMENTS` is provided, use that version. Otherwise suggest based on changes:
- Breaking changes → major bump
- New features → minor bump
- Only fixes → patch bump

## Step 6: Human Review

Present:
- The new changelog entry
- Version bump details
- List of all changes included
- Ask for approval

## Step 7: Commit

```bash
git add CHANGELOG.md [manifest files]
git commit -m "chore: release $ARGUMENTS"
```

## Step 8: Tag (Optional)

Ask the user if they want to create a git tag:

```bash
git tag -a [version] -m "Release [version]"
```

Do NOT push unless explicitly asked.

---

Version: $ARGUMENTS
