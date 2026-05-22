---
name: game-generator
description: Generates ANY HTML5 game from user description using MiniMax/OpenRouter LLM API. Deploys to surge.sh and sends live link to VK. Use when user asks to create, make, or generate any game.
triggers:
  - "сделай игру"
  - "создай игру"
  - "хочу игру"
  - "змейку"
  - "тетрис"
  - "понг"
  - "кликер"
  - "платформер"
  - "make a game"
  - "create game"
---

# Game Generator Skill

Создаёт ЛЮБУЮ HTML5-игру по описанию. AI пишет код сам через MiniMax API — никаких шаблонов.

## Алгоритм (выполняй строго по шагам)

### Шаг 1 — Определи параметры

Из сообщения пользователя:
- **slug**: короткое имя латиницей (snake-cyberpunk-1234, space-rpg, platformer-cat)
- **title**: название на русском ("Змейка: Неон", "Космический RPG")
- **theme**: cyberpunk | space | retro | neon | minimal
- **description**: полное описание для LLM (что за игра, механика, особенности)

### Шаг 2 — Проверь rate limit

```bash
python3 /root/.openclaw/workspace/skills/rate-limiter/scripts/rate_limit.py check {user_id}
```
Если BLOCKED — ответь пользователю: "Подожди минуту, ещё генерирую!"

### Шаг 3 — Найди в каталоге (может уже есть)

```bash
python3 /root/.openclaw/workspace/skills/game-library/scripts/library.py find "{description}"
```
Если найдено с score >= 80% — предложи готовую ссылку.

### Шаг 4 — Сгенерируй игру через LLM

```bash
export MINIMAX_API_KEY="ваш_ключ"
python3 /root/.openclaw/workspace/skills/game-generator/scripts/generate_game.py \
  "{description}" "{title}" "{theme}" \
  "/root/.openclaw/workspace/games/{slug}" \
  "{user_id}"
```

Скрипт вызывает MiniMax API, получает HTML5 код, сохраняет index.html.
Автоматически читает feedback пользователя и добавляет в промпт.
Автоматически запускает playtester и логирует в observability.

### Шаг 5 — Задеплой на surge.sh

```bash
bash /root/.openclaw/workspace/skills/game-generator/scripts/deploy.sh \
  "/root/.openclaw/workspace/games/{slug}" "{slug}"
```

Ищи строку: `GAME_URL:https://{slug}.surge.sh`

### Шаг 6 — Сохрани в каталог и память

```bash
python3 /root/.openclaw/workspace/skills/game-library/scripts/library.py add \
  {slug} "{title}" {game_type} {theme} {score} "https://{slug}.surge.sh"

python3 /root/.openclaw/workspace/skills/user-memory/scripts/memory.py save \
  {user_id} {slug} {game_type} {theme}

python3 /root/.openclaw/workspace/skills/rate-limiter/scripts/rate_limit.py release {user_id}
```

### Шаг 7 — Ответь в VK

```
Игра готова!

{title}

Играть: https://{slug}.surge.sh

Управление: Enter/Space — старт, стрелки — движение
```

## Темы оформления

| Тема | Стиль | Цвета |
|------|-------|-------|
| cyberpunk | Неон, тёмный фон | #ff00ff, #00ffff на #0a0010 |
| space | Космос, звёзды | #4488ff, #ffcc00 на #000820 |
| retro | Пиксели, ретро | #ff6600, #cc4400 на #1a0a00 |
| neon | Зелёный неон | #00ff41, #00cc33 на #000000 |
| minimal | Минимализм | #ff4444, #cc0000 на #0d1117 |

## Требования к генерируемой игре

Каждая игра ОБЯЗАНА содержать:
- `<!DOCTYPE html>` + весь код в одном файле
- `<canvas>` элемент для рендеринга
- `requestAnimationFrame` game loop
- Экран старта: "Press Enter to start"
- Экран game over со счётом
- Управление клавиатурой (стрелки / WASD)
- Отображение счёта во время игры
- Без внешних библиотек, без CDN

## Правила

- ВСЕГДА используй MiniMax или OpenRouter — не пиши HTML вручную
- ВСЕГДА деплой через surge.sh
- Если surge не работает — скопируй в /mnt/c/Users/kiril/Desktop/ и сообщи
- Читай feedback пользователя через feedback.py get {user_id}
- Логируй стоимость через observability автоматически

## Самоулучшение

generate_game.py автоматически:
- Читает user constraints из feedback.py
- Читает prompt improvements из prompt_optimizer.py
- Записывает score в prompt_optimizer.py после playtester
- Логирует токены и стоимость в hooks/logs/
