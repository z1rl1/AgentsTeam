# GameForge — AI HTML5 Game Generator for VK

> OpenClaw agent workspace. Generates any HTML5 game on demand via VK messages using LLM API.

## Agent Identity

**Name**: GameForge (Игрокузница)
**Platform**: VK via OpenClaw 2026
**Core skill**: Generate → Deploy → Send link — all in one message

## Architecture

```
VK User message
      │
      ▼
 GameForge Agent (SOUL.md)
      │
      ├── rate-limiter        check cooldown (60s per user)
      ├── game-library        search catalog (skip generation if exists)
      ├── user-memory         load user preferences
      │
      ├── game-designer       plan: slug, theme, mechanics (JSON)
      │
      ├── game-coder          write HTML5/JS (acceptEdits)
      ├── game-asset-designer CSS/SVG snippets (parallel)
      ├── game-audio-designer Web Audio API (parallel)
      │
      ├── game-tester         QA: READY/ISSUES/BROKEN verdict
      ├── game-deployer       deploy to surge.sh, return URL
      │
      ├── observability       log tokens + cost
      └── prompt-optimizer    record score, improve prompt
```

## Key Files

| File | Purpose |
|------|---------|
| `SOUL.md` | Agent identity, personality, core instructions |
| `AGENTS.md` | Registry of all 6 subagents |
| `agents/` | Subagent definitions (role, tools, mode) |
| `skills/` | 40+ skills with SKILL.md + eval.json + scripts/ |
| `hooks/` | Lifecycle hooks (pre-check, post-eval, session-report) |
| `docs/PRD-gameforge.md` | Full Agentic PRD with GIVEN-WHEN-THEN |
| `setup/` | One-time installation scripts |

## Subagents

| Agent | Role | Mode |
|-------|------|------|
| `game-designer` | Plan: slug, theme, mechanics | plan |
| `game-coder` | Write complete HTML5/JS game | acceptEdits |
| `game-asset-designer` | CSS/SVG visual assets (parallel) | plan |
| `game-audio-designer` | Web Audio API sounds (parallel) | plan |
| `game-tester` | QA check: READY/ISSUES/BROKEN | plan |
| `game-deployer` | Deploy to surge.sh, return link | acceptEdits |

## LLM Integration

- **Primary**: MiniMax M1 (paid, production)
- **Fallback**: OpenRouter free models
- **Working free model**: `nvidia/nemotron-3-super-120b-a12b:free`
- Config: `skills/game-generator/scripts/generate_game.py`

## Self-Improvement (Karpathy Loop)

Runs automatically via hooks:

```
PostToolUse -> post-skill-eval.sh -> scores output -> records to hooks/metrics/
/self-improve [skill] -> reads failures -> fixes SKILL.md -> re-evals
```

All 40+ skills have binary assertions in `skills/*/eval/eval.json`.

## Setup

```bash
# 1. Install OpenClaw
# 2. Copy this workspace to /root/.openclaw/workspace/
# 3. Set API keys
python3 setup/setup_api.py    # finds working free model
python3 setup/save_config.py  # saves to openclaw.json
# 4. Start OpenClaw and connect to VK
```
