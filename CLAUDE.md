# CLAUDE.md — GameForge

> **For Claude Code agents**: architecture overview, file structure, conventions, and rules for this project.
> **For the OpenClaw runtime agent**: read `SOUL.md` — that file contains all runtime instructions.
> These two files serve different purposes and must never be merged.

---

## 1. Project Overview

**GameForge** is an AI agent deployed inside VK (Russia's largest social network) that generates
HTML5 browser games on demand. A user sends a message like "make me a snake game" — the agent
generates a complete, playable HTML5/JS game via an LLM call, deploys it to surge.sh, and replies
with a live link. End-to-end latency target: under 60 seconds.

### End-to-End Flow

```
VK User sends message
       │
       ▼
OpenClaw 2026 (agent gateway, Long Poll)
       │  reads SOUL.md as system prompt
       ▼
GameForge Agent
       │
       ├── feedback.py detect    ← auto-detect negative sentiment
       ├── rate_limit.py check   ← 60s cooldown guard
       ├── library.py find       ← cache hit? return existing link
       ├── memory.py get         ← load user preferences
       │
       ├── [SIMPLE game]         ← agent writes HTML5 code itself
       │      └── deploy.sh → GAME_URL → VK reply
       │
       └── [COMPLEX game]        ← 6-agent subagent pipeline (see Section 2)
              └── GAME_URL → VK reply
```

### Platform and Infrastructure

| Component | Technology |
|-----------|-----------|
| Agent gateway | OpenClaw 2026 (VK User Long Poll) |
| Primary LLM | MiniMax M1 (`MINIMAX_API_KEY`) |
| Fallback LLM | OpenRouter (`OPENROUTER_API_KEY`) |
| Free working model | `nvidia/nemotron-3-super-120b-a12b:free` |
| Static hosting | surge.sh (every game gets `{slug}.surge.sh`) |
| Game format | Single self-contained HTML5 file (no CDN, no external deps) |
| Runtime config | `/root/.openclaw/workspace/skills/game-generator/scripts/generate_game.py` |
| Server deploy path | `/root/.openclaw/workspace/` |

---

## 2. Architecture — Two Modes

### Mode 1: Simple Game (< 30 seconds)

Used for well-known templates: snake, tetris, pong, clicker.

The agent writes the HTML5 code directly inline without spawning subagents. Steps:
1. Determine slug, title, and theme from user message
2. Write complete `index.html` to `games/{slug}/`
3. Run `deploy.sh` to publish on surge.sh
4. Send live link to VK

### Mode 2: Complex Game (< 60 seconds)

Used for custom game types, RPGs, platformers, multiplayer, or any request with unusual mechanics.
A 6-agent pipeline runs sequentially (with two parallel branches in the middle).

```
VK message (complex game request)
        │
        ▼
  game-designer          ← plan mode, 10 turns
  Produces: JSON plan with game_type, mechanics, controls,
            win/lose conditions, visual style, slug, complexity
        │
        ├────────────────────┐
        │                    │
        ▼                    ▼
  game-coder           game-asset-designer    ← parallel
  (writes index.html)  (CSS/SVG snippets)
        │
        │  (waits for asset-designer output, merges visuals)
        │
        ▼
  game-audio-designer        ← plan mode, 10 turns (can run parallel with coder)
  (Web Audio API JS snippets)
        │
        ▼
  game-tester                ← runs 7 QA checks
  Returns: READY | ISSUES | BROKEN + score (X/7)
        │
        ▼ (only if READY or score >= 60%)
  game-deployer              ← surge.sh deploy
  Returns: public URL + VK response template
        │
        ▼
  observability + prompt-optimizer   ← passive logging after every run
```

---

## 3. Subagents

All subagent definitions live in `agents/`. Each is a Markdown file with YAML frontmatter
that Claude Code reads when spawning the agent.

| Agent | Role | permissionMode | maxTurns | When to Use |
|-------|------|----------------|----------|-------------|
| `game-designer` | Analyzes user request and produces a structured JSON plan: game_type, mechanics list, controls, win/lose conditions, visual style, slug, complexity | `plan` | 10 | Start of every COMPLEX game pipeline |
| `game-coder` | Receives JSON plan from game-designer and writes a complete, self-contained `index.html` HTML5 game. Minimum 200 lines for templates, 300+ for custom games | `acceptEdits` | 20 | After game-designer, main code generation step |
| `game-asset-designer` | Creates CSS animations, SVG sprites, and Canvas drawing recipes for each visual element in the plan. Runs in parallel with game-coder | `plan` | 10 | Parallel to game-coder for visual polish |
| `game-audio-designer` | Produces Web Audio API JavaScript snippets for sound effects and background music. All code is inline-ready | `plan` | 10 | Parallel to game-coder for audio polish |
| `game-tester` | Runs `game_playtester.py` against the generated file plus manual file-size/line-count checks. Returns structured Test Report with PASS/FAIL verdict | `plan` | 10 | Before every deploy; gate for game-deployer |
| `game-deployer` | Executes `deploy.sh` to push the game to surge.sh. Falls back to Desktop copy if surge is unavailable. Returns the VK response message | `acceptEdits` | 10 | Final step, only after game-tester PASS |

### game-designer Output Format

```json
{
  "game_type": "snake|tetris|pong|clicker|custom",
  "title": "Game title in Russian",
  "slug": "short-latin-slug-1234",
  "theme": "cyberpunk|space|retro|neon|minimal",
  "mechanics": ["..."],
  "controls": { "start": "Enter or Space", "move": "Arrow keys" },
  "win_condition": "...",
  "lose_condition": "...",
  "visual_elements": ["..."],
  "audio_elements": ["..."],
  "complexity": "simple|medium|complex"
}
```

### game-tester QA Checklist (7 checks)

| Check | What it verifies |
|-------|-----------------|
| Start screen | Press Enter/Space to start is present |
| Canvas/DOM element | `<canvas>` or valid DOM game container exists |
| Game loop | `requestAnimationFrame` or `setInterval` found |
| Game over condition | `gameOver` flag or equivalent detected |
| Score display | Score variable shown on screen |
| Keyboard controls | Arrow keys or WASD handlers present |
| No blocking alert | No `alert()` calls |

Thresholds: PASS >= 60% (4/7), WARN 40-59%, FAIL < 40%.

### HTML5 Game Requirements (enforced by game-coder and game-tester)

Every generated game must satisfy all of the following:

- `<!DOCTYPE html>` — single self-contained file, no external dependencies
- `<canvas>` element for rendering (or valid DOM alternative)
- `requestAnimationFrame` game loop (not `setInterval`)
- Start screen with "Press Enter or Space to start"
- Game over screen with final score and "Press Enter to restart"
- Live score display during gameplay
- Keyboard controls (arrow keys or WASD as appropriate)
- No `alert()` calls — all UI via canvas
- No CDN URLs, no ES6 modules — everything inline
- Minimum 300 lines of actual game code

---

## 4. File Structure

```
AgentsTeam/                          ← project root (git repo)
├── SOUL.md                          ← OpenClaw runtime system prompt (DO NOT edit without care)
├── CLAUDE.md                        ← this file (Claude Code agent instructions)
├── AGENTS.md                        ← agent team overview (summary table)
│
├── agents/                          ← subagent definitions (YAML frontmatter + system prompt)
│   ├── game-designer.md             ← planning agent, plan mode, 10 turns
│   ├── game-coder.md                ← HTML5 writer, acceptEdits, 20 turns
│   ├── game-asset-designer.md       ← CSS/SVG visuals, plan mode, 10 turns
│   ├── game-audio-designer.md       ← Web Audio API, plan mode, 10 turns
│   ├── game-tester.md               ← QA gate, plan mode, 10 turns
│   └── game-deployer.md             ← surge.sh deploy, acceptEdits, 10 turns
│
├── skills/                          ← 40+ skills, each in its own directory
│   ├── [skill-name]/
│   │   ├── SKILL.md                 ← skill instructions (triggers, algorithm, commands)
│   │   ├── scripts/                 ← Python implementation scripts
│   │   │   └── *.py
│   │   └── eval/
│   │       ├── eval.json            ← binary assertions for self-improvement scoring
│   │       ├── improvement-log.json ← history of autonomous improvement runs
│   │       └── improvement-report.md← human-readable improvement summary
│   │
│   ├── game-generator/              ← core: LLM call → HTML5 → surge.sh
│   │   └── scripts/
│   │       ├── generate_game.py     ← main generator (MiniMax + OpenRouter)
│   │       └── deploy.sh            ← surge.sh deploy script
│   ├── game-playtester/             ← 7-check QA validator
│   ├── rate-limiter/                ← 60s cooldown, max 5 concurrent
│   ├── game-library/                ← searchable catalog of generated games
│   ├── user-memory/                 ← per-user preferences (theme, game type, history)
│   ├── feedback/                    ← detect negative sentiment → save constraints
│   ├── prompt-optimizer/            ← track scores → improve base prompt
│   ├── observability/               ← token usage, cost, latency logging
│   ├── self-improve/                ← Karpathy loop: eval → patch SKILL.md → repeat
│   ├── game-enhancer/               ← post-generation enhancement pass
│   ├── game-balancer/               ← difficulty tuning for generated games
│   ├── game-bug-fixer/              ← automated JS bug detection and fix
│   ├── game-catalog/                ← catalog UI and search features
│   ├── game-clone/                  ← clone an existing game with modifications
│   ├── game-difficulty/             ← adjust difficulty settings
│   ├── game-randomizer/             ← random game idea generator
│   ├── game-soundtrack/             ← audio generation for games
│   ├── game-tutorial/               ← in-game tutorial generation
│   ├── generate-eval/               ← create eval.json for a skill
│   ├── idea-generator/              ← suggest game ideas to users
│   ├── mobile-optimizer/            ← add touch controls, responsive layout
│   ├── multiplayer-adapter/         ← add 2-player local multiplayer support
│   ├── performance-optimizer/       ← optimize game rendering performance
│   ├── skill-health/                ← dashboard: scores and trends across skills
│   ├── theme-switcher/              ← switch visual theme of existing game
│   ├── achievement-system/          ← add achievements to generated games
│   ├── code-auditor/                ← audit generated code for quality issues
│   ├── game-asset-generator/        ← standalone asset generation
│   ├── game-leaderboard/            ← add leaderboard functionality
│   └── jpeng-data-analyzer/         ← data analysis utilities
│
├── hooks/                           ← lifecycle hooks (fire automatically)
│   ├── pre-skill-check.sh           ← PreToolUse: check eval exists, inject score + trend
│   ├── post-skill-eval.sh           ← PostToolUse: run assertions, record metrics
│   ├── log-skill-result.sh          ← PostToolUse: log execution metadata (JSONL)
│   ├── log-test-result.sh           ← PostToolUse: log test run pass/fail
│   ├── post-edit-validate.sh        ← PostToolUse: remind to validate after edits
│   ├── session-report.sh            ← Stop: generate session health summary
│   ├── validate-readonly-bash.sh    ← PreToolUse: block destructive bash commands
│   ├── validate-devops-bash.sh      ← PreToolUse: block dangerous prod ops
│   ├── lib/
│   │   ├── eval-engine.sh           ← binary assertion evaluation engine
│   │   ├── metrics.sh               ← score tracking, trend analysis
│   │   └── utils.sh                 ← path resolution, JSON helpers, logging
│   ├── logs/                        ← execution logs (JSONL + Markdown, daily rotation)
│   │   ├── skill-executions-YYYY-MM-DD.jsonl
│   │   ├── eval-results-YYYY-MM-DD.jsonl
│   │   ├── pre-checks-YYYY-MM-DD.jsonl
│   │   └── session-report-DATE-SESSION.md
│   └── metrics/                     ← per-skill score history
│       └── {skill-name}.jsonl       ← one score entry per eval run
│
├── docs/
│   ├── PRD-gameforge.md             ← full Agentic PRD (GIVEN-WHEN-THEN scenarios)
│   ├── rca/                         ← Root Cause Analysis documents
│   ├── state/                       ← session state (pause/resume)
│   └── templates/                   ← PRD, design doc templates
│
├── setup/                           ← one-time install scripts (run once on server)
│   ├── setup_api.py                 ← tests free models, saves working model name
│   ├── save_config.py               ← writes API key + model to openclaw.json
│   ├── build_full_system.py         ← scaffold full skills directory from scratch
│   ├── build_feedback_system.py     ← scaffold feedback + user-memory skills
│   ├── build_self_improve.py        ← scaffold self-improve + eval infrastructure
│   ├── create_gameforge_infra.py    ← create hooks, logs, metrics directories
│   ├── fix_evals.py                 ← repair malformed eval.json files
│   ├── fix_skill_mds.py             ← repair malformed SKILL.md frontmatter
│   └── self_improve.py              ← standalone self-improvement runner
│
├── games/                           ← [gitignored] generated game files
│   └── {slug}/
│       └── index.html
│
└── memory/                          ← [gitignored] user preference storage
    └── users/
        └── {user_id}.json
```

---

## 5. Skills Overview

### Core Skills (always used in game generation)

| Skill | What it does | Key script |
|-------|-------------|-----------|
| `game-generator` | Main pipeline: calls LLM API (MiniMax or OpenRouter), extracts HTML5 code, saves `index.html`. Auto-reads user feedback constraints and prompt optimizer improvements | `generate_game.py` |
| `game-playtester` | 7-check QA validator: start screen, canvas, game loop, game over, score, controls, no alert. Returns X/7 score | `game_playtester.py` |
| `rate-limiter` | Enforces 60s cooldown per VK user ID. Max 5 concurrent generations. Auto-release after 300s if stuck | `rate_limit.py` |
| `game-library` | Searchable catalog of all generated games. Cache hit if score >= 80% avoids regeneration | `library.py` |
| `user-memory` | Stores and retrieves per-user preferences: favorite theme, favorite game type, last 5 games | `memory.py` |
| `feedback` | Detects negative sentiment in user messages (`detect` command). Saves dislikes as constraints injected into future generation prompts | `feedback.py` |
| `observability` | Logs tokens (input/output), generation time, LLM model used, cost estimate, success/fail per request | `stats.py` |
| `prompt-optimizer` | After every game records slug + QA score. After 10+ games runs pattern analysis and suggests prompt improvements. Improvements auto-injected into next generation | `prompt_optimizer.py` |
| `self-improve` | Karpathy loop: loads `eval.json`, runs assertions against skill output, patches `SKILL.md` with improvement notes, repeats up to 3 rounds | `self_improve.py` |

### Enhancement Skills (optional, invoked on demand)

| Skill | What it does |
|-------|-------------|
| `game-enhancer` | Post-generation polish pass: better animations, smoother physics |
| `game-balancer` | Adjusts difficulty curve after playtesting feedback |
| `game-bug-fixer` | Auto-detects and patches common JS game bugs |
| `mobile-optimizer` | Adds touch event handlers and responsive canvas scaling |
| `multiplayer-adapter` | Adds local 2-player keyboard support |
| `theme-switcher` | Re-skins existing game to a different visual theme |
| `achievement-system` | Injects achievement unlock logic into existing game |
| `game-tutorial` | Generates in-game tutorial overlay |
| `game-soundtrack` | Adds Web Audio API background music and SFX |
| `game-randomizer` | Generates a surprising random game idea for bored users |
| `idea-generator` | Suggests 5 game ideas based on user's history |
| `game-clone` | Clones an existing game (by slug) with user-specified modifications |
| `game-difficulty` | Standalone difficulty parameter adjustment |
| `performance-optimizer` | Diagnoses and fixes rendering bottlenecks |

### Infrastructure Skills

| Skill | What it does |
|-------|-------------|
| `skill-health` | Dashboard: shows latest score, trend (up/flat/down), eval coverage for every skill |
| `generate-eval` | Creates `eval/eval.json` with 25-35 binary assertions for a skill that lacks one |
| `code-auditor` | Static analysis of generated code quality |
| `game-leaderboard` | Adds persistent score leaderboard (localStorage) to a game |
| `game-catalog` | Manages the public-facing game catalog and tag taxonomy |

---

## 6. LLM Configuration

### Model Priority

Generation attempts in this order:

1. **MiniMax M1** (primary) — set `MINIMAX_API_KEY` environment variable.
   Model ID: `minimax/minimax-text-01` or as set by `GAMEFORGE_MODEL` env var.

2. **OpenRouter** (fallback) — set `OPENROUTER_API_KEY` environment variable.
   Used when MiniMax returns an error or is unavailable.

3. **Free model** — during setup or when no paid key is available:
   `nvidia/nemotron-3-super-120b-a12b:free` (verified working as of 2026-04-16)

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `MINIMAX_API_KEY` | MiniMax M1 primary access | (required for prod) |
| `OPENROUTER_API_KEY` | OpenRouter fallback access | (required for fallback) |
| `GAMEFORGE_MODEL` | Override LLM model ID | `minimax/minimax-text-01` |
| `SKILL_EVAL_THRESHOLD` | Score below this triggers improvement suggestion | `80` |
| `CLAUDE_PROJECT_DIR` | Project root (set by Claude Code automatically) | `.` |

### generate_game.py Behavior

- Reads `MINIMAX_API_KEY` → tries MiniMax first
- Reads `OPENROUTER_API_KEY` → fallback if MiniMax fails
- Reads user constraints via `feedback.py get {user_id}` and injects into prompt
- Reads prompt improvements via `prompt_optimizer.py best-prompt` and appends to prompt
- After generation: runs `game_playtester.py` automatically and records score
- Logs tokens + cost to `hooks/logs/` via observability pipeline

### Visual Themes (used by all generation paths)

| Theme | Background | Primary | Secondary | Style |
|-------|-----------|---------|-----------|-------|
| `cyberpunk` | `#0a0010` | `#ff00ff` | `#00ffff` | Neon glow, scan lines, glitch |
| `space` | `#000820` | `#4488ff` | `#ffcc00` | Stars, gradient, glow |
| `retro` | `#1a0a00` | `#ff6600` | `#cc4400` | Pixel borders, CRT effect |
| `neon` | `#000000` | `#00ff41` | `#00cc33` | Bright outlines, pulse animations |
| `minimal` | `#0d1117` | `#ff4444` | `#cc0000` | Clean shapes, flat design |

---

## 7. Hooks System

Hooks fire automatically at lifecycle events. They require no manual invocation.

### Hook Event Map

| Event | Script | Purpose | Timeout |
|-------|--------|---------|---------|
| `PreToolUse → Skill` | `pre-skill-check.sh` | Check if skill has eval.json; inject latest score and trend into conversation context | 10s |
| `PostToolUse → Skill` | `log-skill-result.sh` | Write execution metadata (skill name, args, response size) to JSONL log | 10s |
| `PostToolUse → Skill` | `post-skill-eval.sh` | Run binary assertions from eval.json against output; record score in metrics/{skill}.jsonl | 30s |
| `Stop` | `session-report.sh` | Generate session-level health summary with score table and improvement recommendations | 15s |

### Hook Data Flow

```
Skill executes
    │
    ├─► pre-skill-check.sh
    │     reads  hooks/metrics/{skill}.jsonl
    │     injects { latest_score, trend, has_eval } into conversation
    │
    ├─► log-skill-result.sh
    │     writes hooks/logs/skill-executions-YYYY-MM-DD.jsonl
    │
    ├─► post-skill-eval.sh
    │     reads  skills/{skill}/eval/eval.json
    │     runs   eval-engine.sh against output text
    │     writes hooks/metrics/{skill}.jsonl  (score + timestamp)
    │     writes hooks/logs/eval-results-YYYY-MM-DD.jsonl
    │     returns { score, failures, suggestion } into conversation
    │
    └─► session-report.sh (on Stop)
          reads  all metrics + logs
          writes hooks/logs/session-report-DATE-SESSION.md
```

### Eval Engine Assertion Types

The eval engine (`hooks/lib/eval-engine.sh`) evaluates binary assertions programmatically:

| Assertion type | Example | What it checks |
|----------------|---------|---------------|
| `contains` | `"token\|Token\|tokens"` | Case-insensitive pattern match in output |
| `not_contains` | `"alert\(\)"` | Pattern must NOT appear |
| `word_count_over` | `100` | Output has more than N words |
| `word_count_under` | `500` | Output has fewer than N words |
| `has_heading` | `"##"` | Markdown heading present |
| `has_code_block` | — | At least one fenced code block |
| `has_numbered_list` | — | Numbered list present |
| `has_bullet_list` | — | Bullet list present |
| `line_count_over` | `50` | More than N lines |
| `no_empty_first_line` | — | Output does not start blank |
| `no_trailing_question` | — | Does not end with a question mark |
| `has_numbers` | — | Contains at least one numeric value |
| `no_em_dash` | — | No em-dash characters (formatting) |
| `non_empty` | — | Output is not empty |
| `needs_ai` | — | Cannot be checked programmatically; skipped in automated score |

Assertions in `eval.json` must be binary (true/false), never subjective.

### Shared Libraries

| Library | Purpose |
|---------|---------|
| `hooks/lib/utils.sh` | Path resolution, JSON helpers (`jq` wrappers), logging utilities, skill detection |
| `hooks/lib/eval-engine.sh` | Core assertion evaluation engine; sourced by post-skill-eval.sh |
| `hooks/lib/metrics.sh` | Score persistence: `get_latest_score`, `get_best_score`, `get_trend_direction`, `get_eval_count` |

---

## 8. Self-Improvement (Karpathy Loop)

GameForge improves its own skill instructions autonomously without human intervention.

### Two-Layer Improvement

1. **Passive monitoring** (automatic): every skill execution is scored by `post-skill-eval.sh`.
   Scores accumulate in `hooks/metrics/{skill}.jsonl`.

2. **Active improvement** (on-demand or scheduled): `self-improve` skill runs the Karpathy loop
   to patch failing assertions in `SKILL.md`.

### Karpathy Loop Algorithm

```
1. Load eval.json for the target skill (binary assertions)
2. Read the current SKILL.md content as simulated output
3. Run all assertions through eval-engine.sh
4. If score < 75%:
     a. Identify failing assertions
     b. Generate specific fixes (add heading, add code block, expand text, etc.)
     c. Append "## Improvement Notes" section to SKILL.md
     d. Record score in improvement-log.json
5. Repeat up to 3 rounds
6. Write final score to hooks/metrics/{skill}.jsonl
```

### Commands

```bash
# Status dashboard — scores for all skills
python3 /root/.openclaw/workspace/skills/self-improve/scripts/self_improve.py status

# Improve one specific skill
python3 /root/.openclaw/workspace/skills/self-improve/scripts/self_improve.py game-generator

# Improve all skills with score < 75% (run weekly)
python3 /root/.openclaw/workspace/skills/self-improve/scripts/self_improve.py all

# Run eval without making changes (dry-run)
python3 /root/.openclaw/workspace/skills/self-improve/scripts/self_improve.py run-eval game-generator
```

### Prompt Optimizer Loop (separate from skill improvement)

The prompt optimizer improves the LLM prompt used in `generate_game.py`:

```bash
# After 10+ games: analyze patterns of failures
python3 /root/.openclaw/workspace/skills/prompt-optimizer/scripts/prompt_optimizer.py analyze

# Generate and save prompt improvements
python3 /root/.openclaw/workspace/skills/prompt-optimizer/scripts/prompt_optimizer.py improve

# View current active improvements
python3 /root/.openclaw/workspace/skills/prompt-optimizer/scripts/prompt_optimizer.py best-prompt
```

Improvements are auto-injected into every subsequent generation by `generate_game.py`.

### How to Create eval.json for a New Skill

```bash
# Manually: create skills/{skill-name}/eval/eval.json
# Use the generate-eval skill to draft it:
# Run the generate-eval SKILL.md instructions, targeting the new skill
```

Each `eval.json` should contain 25-35 binary assertions across 5 representative test cases.
Every assertion must be checkable by the eval engine without AI judgment.

---

## 9. Development Workflow

### Adding a New Skill

1. Create directory: `skills/{skill-name}/`
2. Write `skills/{skill-name}/SKILL.md` with YAML frontmatter:
   ```yaml
   ---
   name: skill-name
   description: One-line description (used for auto-selection)
   triggers:
     - "trigger phrase"
   ---
   ```
3. Add Python scripts to `skills/{skill-name}/scripts/`
4. Create `skills/{skill-name}/eval/eval.json` with binary assertions
5. Run `python3 skills/self-improve/scripts/self_improve.py run-eval skill-name` to verify eval works
6. Test manually with the skill's commands

### Improving Game Generation Quality

```
1. Run observability to find low-quality generations:
   python3 skills/observability/scripts/stats.py today

2. Run playtester manually on a suspect game:
   python3 skills/game-playtester/scripts/game_playtester.py {slug}

3. Run prompt optimizer:
   python3 skills/prompt-optimizer/scripts/prompt_optimizer.py analyze
   python3 skills/prompt-optimizer/scripts/prompt_optimizer.py improve

4. Run self-improve on game-generator skill:
   python3 skills/self-improve/scripts/self_improve.py game-generator

5. Verify score improved:
   python3 skills/self-improve/scripts/self_improve.py status
```

### Checking System Status

```bash
# All skill scores and trends
python3 /root/.openclaw/workspace/skills/self-improve/scripts/self_improve.py status

# Today's token usage and costs
python3 /root/.openclaw/workspace/skills/observability/scripts/stats.py today

# Weekly generation report
python3 /root/.openclaw/workspace/skills/observability/scripts/stats.py week

# Top costly generations
python3 /root/.openclaw/workspace/skills/observability/scripts/stats.py top

# Rate limiter status (who is in cooldown)
python3 /root/.openclaw/workspace/skills/rate-limiter/scripts/rate_limit.py status

# Game library catalog
python3 /root/.openclaw/workspace/skills/game-library/scripts/library.py list

# Prompt optimizer current state
python3 /root/.openclaw/workspace/skills/prompt-optimizer/scripts/prompt_optimizer.py analyze
```

### Modifying game-designer or game-coder Agents

When editing agent definitions in `agents/*.md`:
- The YAML frontmatter fields (`permissionMode`, `maxTurns`, `effort`) are enforced by OpenClaw
- The system prompt body is what the subagent sees as its instructions
- Always test with a simple game request after editing game-coder.md
- Never reduce `maxTurns` below what the agent needs to complete a full HTML5 file

### Adding a New Visual Theme

1. Add theme colors to `THEME_COLORS` dict in `generate_game.py`
2. Add theme colors to `THEMES` const in `agents/game-coder.md`
3. Add theme description to `agents/game-asset-designer.md` under "Theme Styles"
4. Add theme to `SOUL.md` theme selection logic (requires human approval — see Section 10)

---

## 10. Agent Rules

### ALWAYS (agents can do freely)

- Read any file in the workspace
- Run skill Python scripts (`python3 skills/*/scripts/*.py`)
- Edit `SKILL.md` files to improve instructions
- Create or update `eval/eval.json` assertion files
- Create new skills in `skills/`
- Run `deploy.sh` for testing
- Run the self-improve loop on any skill
- Write to `games/` and `memory/` (gitignored)
- Check logs in `hooks/logs/`
- Run observability and prompt-optimizer commands

### ASK FIRST (requires human approval before making changes)

- Modify `skills/game-generator/scripts/generate_game.py` (core generation logic)
- Modify `skills/game-generator/scripts/deploy.sh` (deployment script)
- Change API keys or update environment variable values
- Delete any skill directory
- Modify `SOUL.md` (the OpenClaw runtime system prompt)
- Change `agents/` frontmatter fields that affect permissions or turn limits
- Add new Python dependencies (pip install)
- Modify hooks in `hooks/*.sh`
- Change `setup/` scripts

### NEVER

- Commit API keys, tokens, or credentials to git
- Commit the `games/` directory (gitignored)
- Commit the `memory/` directory (gitignored)
- Push to main/master branch directly
- Disable type safety or skip error handling in Python scripts
- Call real LLM APIs in tests (mock them)
- Swallow exceptions silently
- Use external CDN URLs in generated game HTML

---

## 11. Installation

### Deploy to Server (one-time setup)

```bash
# 1. Copy workspace to OpenClaw working directory
cp -r /path/to/AgentsTeam /root/.openclaw/workspace/

# 2. Install Python dependencies (if needed)
pip3 install requests

# 3. Test API connectivity and find a working free model
python3 /root/.openclaw/workspace/setup/setup_api.py

# 4. Save API keys and model to OpenClaw config
python3 /root/.openclaw/workspace/setup/save_config.py

# 5. Verify hooks directory structure exists
ls /root/.openclaw/workspace/hooks/logs/
ls /root/.openclaw/workspace/hooks/metrics/
# If missing: python3 /root/.openclaw/workspace/setup/create_gameforge_infra.py

# 6. Install surge CLI (for deployment)
npm install -g surge

# 7. Authenticate surge (one-time, saves token)
surge login

# 8. Verify deploy script works with a test game
mkdir -p /root/.openclaw/workspace/games/test-deploy-123
echo '<!DOCTYPE html><html><body><h1>Test</h1></body></html>' \
  > /root/.openclaw/workspace/games/test-deploy-123/index.html
bash /root/.openclaw/workspace/skills/game-generator/scripts/deploy.sh \
  /root/.openclaw/workspace/games/test-deploy-123 test-deploy-123

# 9. Start OpenClaw agent runtime
cd /root/.openclaw && npm start
```

### Verify Installation

```bash
# Check skill system is working
python3 /root/.openclaw/workspace/skills/self-improve/scripts/self_improve.py status

# Check rate limiter
python3 /root/.openclaw/workspace/skills/rate-limiter/scripts/rate_limit.py status

# Check game library
python3 /root/.openclaw/workspace/skills/game-library/scripts/library.py list

# Test generation end-to-end (will call LLM and deploy)
python3 /root/.openclaw/workspace/skills/game-generator/scripts/generate_game.py \
  "simple snake game" "Test Snake" "neon" \
  "/root/.openclaw/workspace/games/test-snake-001" \
  "test_user"
```

### Environment Variables (set in server environment or openclaw.json)

```bash
export MINIMAX_API_KEY="your_minimax_key_here"
export OPENROUTER_API_KEY="your_openrouter_key_here"
export GAMEFORGE_MODEL="minimax/minimax-text-01"   # optional override
export SKILL_EVAL_THRESHOLD="80"                    # optional, default 80
```

---

## 12. Code Style and Conventions

### Python Scripts

- All scripts in `skills/*/scripts/` use `#!/usr/bin/env python3` shebang
- Argument parsing via `sys.argv` (no argparse required for simple scripts)
- Exit codes: `0` for success, `1` for error
- Print human-readable output to stdout; errors to stderr
- Every script must handle the case where its data file does not exist yet (first run)
- Use `json.dumps(data, ensure_ascii=False, indent=2)` for JSON files (supports Russian text)
- No silent exception swallowing: at minimum `print(f"ERROR: {e}", file=sys.stderr)`

### SKILL.md Format

```yaml
---
name: skill-name
description: One-line description used for agent auto-selection
triggers:
  - "trigger phrase in Russian"
  - "trigger phrase in English"
---

# Skill Title

Brief one-paragraph description of what this skill does.

## Algorithm

Step-by-step instructions with bash commands.

### Step 1 — Action name
```bash
python3 /root/.openclaw/workspace/skills/skill-name/scripts/script.py args
```

## Rules
- Bullet list of hard constraints
```

### Agent Definition Format (agents/*.md)

```yaml
---
name: agent-name
description: What this agent does and when to use it (visible to parent agent)
model: inherit
permissionMode: plan|acceptEdits|default
maxTurns: N
effort: high|medium|low
---

# Agent Title

## Role
One paragraph describing the agent's job.

## Input
What the agent expects to receive.

## Output
What the agent returns (format, structure).

## Process
Numbered steps.

## Rules
- Hard constraints
```

### Shell Scripts (hooks/*.sh)

- `set -euo pipefail` at the top of every hook script
- Source `lib/utils.sh` and `lib/metrics.sh` as needed
- Read hook input from stdin via `read_stdin_json` (from utils.sh)
- Return JSON via `jq -n` to stdout
- Log to `$LOGS_DIR/` using timestamped filenames
- Maximum 10 second timeout for pre/post hooks; 30 seconds for eval hooks

---

## 13. Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Single self-contained HTML5 file | Works at `file://` URL without a server; surge.sh hosts it for free; no build step |
| `requestAnimationFrame` over `setInterval` | Smoother animation, browser-throttled when tab inactive, industry standard |
| No external libraries or CDN | Games must work offline and be fully inspectable; CDN reliability risk eliminated |
| 60s cooldown per user | Prevents LLM cost spikes; one user cannot DoS the system |
| game-library cache at 80% score | High-quality games are reused; low-quality games (< 60%) are always regenerated |
| Simple vs complex routing in SOUL.md | Agent writes code directly for snake/tetris/pong/clicker (faster, cheaper); subagent pipeline for custom games (better quality) |
| Binary assertions only in eval.json | Programmatically checkable; no AI needed to run eval; deterministic scores |
| Karpathy loop max 3 rounds | Prevents infinite improvement loops; most gains come in rounds 1-2 |

---

## 14. PRD Reference

Full Product Requirements Document with GIVEN-WHEN-THEN acceptance scenarios:
`docs/PRD-gameforge.md`

The PRD covers:
- User stories for all game generation paths
- Rate limiting and cache behavior specifications
- QA thresholds and deploy conditions
- Feedback and personalization requirements
- Observability and cost management requirements
