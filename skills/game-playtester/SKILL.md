---
name: game-playtester
description: Strict quality gate for generated HTML5 games. Rejects tiny prototypes, weak visuals, missing genre mechanics, hanging dialogs, and non-responsive canvas layouts. Returns READY/ISSUES/BROKEN.
---

# Game Playtester Skill

QA gate before any public deploy.

## Commands

```bash
python3 /root/.openclaw/workspace/skills/game-playtester/scripts/game_playtester.py {slug}
```

## What Is Checked

The checker now validates both technical and product quality:

- complete single-file HTML document
- canvas renderer
- large or responsive canvas, not a tiny boxed prototype
- requestAnimationFrame loop with frame timing
- start/restart, game over/win state, score/objective UI
- keyboard controls
- substantial code size
- rich canvas drawing density
- animation/effects
- no alert/prompt/confirm
- no external dependencies
- genre-specific mechanics from `gameforge.json` and slug

For platformer / beat-em-up games it additionally requires physics, jump/velocity, scrolling camera or wider level, enemies, combat/hit detection, health/lives, and city/platform scenery.

## Verdicts

- **READY**: score >= 85% and no required failures. Public deploy is allowed.
- **ISSUES**: score 65-84% or any required failure. Do not deploy; regenerate or fix.
- **BROKEN**: score < 65%. Do not deploy; regenerate.

## Rules

- Never deploy an ISSUES/BROKEN game to a user.
- A game being technically playable is not enough; it must look and feel presentable.
- If an old game now fails, that is expected. The gate is intentionally stricter.
