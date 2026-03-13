---
name: system-review
description: Meta-level analysis of plan vs execution to identify process improvements. Analyzes divergence patterns and suggests updates to CLAUDE.md, agents, and skills.
argument-hint: [plan-file] [execution-report-file]
disable-model-invocation: false
context: fork
---

# System Review

Perform a meta-level analysis of how well the implementation followed the plan and identify process improvements.

## Purpose

**System review is NOT code review.** You're not looking for bugs in the code -- you're looking for bugs in the *process*.

**Your job:**
- Analyze plan adherence and divergence patterns
- Identify which divergences were justified vs. problematic
- Surface process improvements that prevent future issues
- Suggest updates to CLAUDE.md, agent definitions, and skill definitions

## Inputs

**Plan file**: First argument from `$ARGUMENTS`
**Execution report**: Second argument from `$ARGUMENTS`

Read both files thoroughly.

## Analysis Workflow

### Step 1: Understand the Planned Approach

Extract from the plan:
- What features were planned?
- What architecture was specified?
- What validation steps were defined?
- What patterns were referenced?

### Step 2: Understand the Actual Implementation

Extract from the execution report:
- What was implemented?
- What diverged from the plan?
- What challenges were encountered?
- What was skipped and why?

### Step 3: Classify Each Divergence

For each divergence, classify as:

**Good Divergence** -- Justified:
- Plan assumed something that didn't exist in the codebase
- Better pattern discovered during implementation
- Performance optimization needed
- Security issue discovered requiring different approach

**Bad Divergence** -- Problematic:
- Ignored explicit constraints in plan
- Created new architecture instead of following existing patterns
- Took shortcuts that introduce tech debt
- Misunderstood requirements

### Step 4: Trace Root Causes

For each problematic divergence, identify the root cause:
- Was the plan unclear? Where, why?
- Was context missing? Where, why?
- Was validation missing? Where, why?

### Step 5: Generate Process Improvements

Based on patterns, suggest:
- **CLAUDE.md updates**: Universal patterns or anti-patterns to document
- **Agent definition updates**: Instructions that need clarification
- **Skill definition updates**: Missing steps or unclear instructions
- **New skills**: Manual processes that should be automated

## Output Format

### Overall Alignment Score: __/10

- 10: Perfect adherence, all divergences justified
- 7-9: Minor justified divergences
- 4-6: Mix of justified and problematic divergences
- 1-3: Major problematic divergences

### Divergence Analysis

For each divergence:
- **What changed**: [description]
- **Planned**: [what plan specified]
- **Actual**: [what was implemented]
- **Classification**: Good / Bad
- **Root cause**: [unclear plan | missing context | etc.]

### System Improvement Actions

**Update CLAUDE.md:**
- [ ] Document [pattern X] discovered during implementation
- [ ] Add anti-pattern warning for [Y]

**Update Agent Definitions:**
- [ ] Clarify [instruction] in [agent].md

**Update Skill Definitions:**
- [ ] Add [missing step] to /plan skill
- [ ] Improve [section] in /execute skill

**Create New Skill:**
- [ ] `/[skill-name]` for [repeated manual process]

### Key Learnings

**What worked well:**
- [specific things that went smoothly]

**What needs improvement:**
- [specific process gaps identified]

**For next implementation:**
- [concrete improvements to try]

---

Arguments: $ARGUMENTS
