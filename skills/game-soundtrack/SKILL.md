---
name: game-soundtrack
description: Adds background music and sound effects to a game using MiniMax music_generation + Web Audio API. Use when user asks to add sounds, music, or audio effects.
---
# Game Soundtrack Skill
Добавляет фоновую музыку и звуковые эффекты через MiniMax music_generation + Web Audio API.

<!-- Auto-improved 2026-04-16 -->
## Improvement Notes
- Add example output containing: surge.sh
- Add example output containing: OK|ready|готова


## MiniMax Music Requirement
- Generate the main soundtrack through MiniMax `music_generation` as local `assets/theme.mp3`.
- Use Web Audio API for short SFX only.
- The final game must start music after a user gesture and must not rely on remote audio URLs.
