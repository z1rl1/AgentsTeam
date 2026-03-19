---
name: generate-eval
description: Generate an eval.json file with binary true/false assertions for a skill. Creates test cases with prompts and measurable assertions that enable the /self-improve loop.
argument-hint: [skill-name]
disable-model-invocation: false
context: fork
---

# Generate Eval for Skill

Create a comprehensive `eval.json` with binary assertions for the specified skill.

## Arguments

Parse `$ARGUMENTS`:
- First argument: skill name (required) — e.g. `review-code`, `commit`, `plan`

## Step 1: Analyze the Skill

Read `.claude/skills/[skill-name]/SKILL.md` thoroughly.

Identify:
- **Structural rules**: output format, sections, headings, ordering
- **Content rules**: what must/must not be included
- **Length constraints**: word counts, line limits
- **Format constraints**: markdown formatting, code blocks, lists
- **Forbidden patterns**: things the output should never contain
- **Required elements**: things that must always appear
- **Process rules**: steps that must be followed in order

Also read any reference files in the skill directory (if they exist).

## Step 2: Generate Test Cases

Create **5 test cases** that cover different usage scenarios of the skill.

Each test case needs:
- `name`: descriptive test name
- `prompt`: a realistic user prompt that would trigger this skill
- `expected_output_description`: brief description of what correct output looks like
- `assertions`: array of 5-7 binary (true/false) assertions

### Rules for Assertions

**MUST be binary** — answerable with true or false. No subjective judgments.

**Good assertions** (binary, measurable):
- "Output contains a markdown heading starting with ##"
- "Output does not contain em-dashes (—)"
- "Total word count is under 500"
- "Output includes at least one code block"
- "First line is not empty"
- "Output contains the word 'Summary' or 'Report'"
- "Output has at least 3 bullet points"
- "No line exceeds 120 characters"

**Bad assertions** (subjective, not automatable):
- "Output is well-written" ← subjective
- "The tone is professional" ← subjective
- "Code quality is high" ← not binary
- "Good use of examples" ← vague

### Coverage Guidelines

Across all 5 test cases, assertions should cover:
- [ ] Output structure and formatting
- [ ] Required sections/elements
- [ ] Forbidden patterns
- [ ] Length/size constraints
- [ ] Process adherence (correct ordering of steps)
- [ ] Edge cases specific to the skill

## Step 3: Write eval.json

Create the file at `.claude/skills/[skill-name]/eval/eval.json`:

```json
{
  "skill": "[skill-name]",
  "version": 1,
  "created": "YYYY-MM-DD",
  "description": "Binary assertions for [skill-name] skill self-improvement",
  "total_assertions": N,
  "tests": [
    {
      "name": "descriptive test name",
      "prompt": "realistic user prompt for this skill",
      "expected_output_description": "brief description of correct output",
      "assertions": [
        {
          "id": "T1_A1",
          "text": "Binary assertion text",
          "category": "structure|content|format|length|forbidden|process"
        }
      ]
    }
  ]
}
```

## Step 4: Validate

After generating, verify:
- [ ] Every assertion is truly binary (true/false)
- [ ] No duplicate assertions across test cases
- [ ] Assertions are specific enough to evaluate programmatically
- [ ] Test prompts are realistic and diverse
- [ ] Total assertions: 25-35 (5-7 per test case)

## Step 5: Report

Display:

```
✅ Generated eval.json for skill: [skill-name]

📊 Summary:
  Tests: 5
  Total assertions: N
  Categories:
    - structure: X
    - content: X
    - format: X
    - length: X
    - forbidden: X
    - process: X

📁 File: .claude/skills/[skill-name]/eval/eval.json

Next step: Run /self-improve [skill-name] to start the improvement loop.
```

---

Skill: $ARGUMENTS
