---
name: game-playtester
description: Tests HTML5 game quality before deployment. Checks for start screen, canvas, game loop, game over, score display, controls, and no blocking alerts. Returns READY/ISSUES/BROKEN verdict.
---

# Game Playtester Skill

QA-проверка HTML5 игры перед деплоем на surge.sh.

## Команды

### Протестировать конкретную игру
```bash
python3 /root/.openclaw/workspace/skills/game-playtester/scripts/game_playtester.py {slug}
```

### Протестировать все игры
```bash
python3 /root/.openclaw/workspace/skills/game-playtester/scripts/game_playtester.py
```

## Что проверяется (7 чеков)

| Чек | Что ищет | Тип |
|-----|----------|-----|
| Start screen | `Enter|Space` в коде | Required |
| Canvas or DOM | `<canvas` или `getElementById` | Required |
| Game loop | `setInterval` или `requestAnimationFrame` | Required |
| Game over | `game.?over` или `running.*false` | Required |
| Score/points | `score|Score|points` | Optional |
| Arrow key controls | `ArrowUp|ArrowLeft` | Optional |
| No blocking alert() | Отсутствие `alert(` | Invert |

## Вердикты

- **READY** — score >= 80% (6-7 из 7) — можно деплоить
- **ISSUES** — score 60-79% (4-5 из 7) — деплоить с предупреждением
- **BROKEN** — score < 60% (< 4 из 7) — НЕ деплоить, регенерировать

## Пример вывода

```
Testing: snake-cyberpunk-1234
=============================================
  [OK] Start screen (Enter/Space)
  [OK] Canvas or DOM element
  [OK] Game loop (interval/RAF)
  [OK] Game over condition
  [OK] Score/points
  [WARN] Arrow key controls
  [OK] No blocking alert()
---------------------------------------------
  Result: 6/7 (85%) — READY
=============================================
```

## Когда использовать

1. Автоматически — generate_game.py запускает playtester после генерации
2. Вручную — перед деплоем если хочешь проверить
3. После исправлений — убедиться что score улучшился

## Пороги деплоя

```python
score >= 80%  # READY  — деплой разрешён
score >= 60%  # ISSUES — деплой с предупреждением
score < 60%   # BROKEN — запрети деплой, скажи пользователю
```
