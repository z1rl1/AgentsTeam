---
name: game-library
description: Searchable catalog of all generated games with tags, themes, and scores. Use BEFORE generating a new game to check if a similar game already exists and can be reused or modified.
---

# Game Library Skill

Каталог всех созданных игр с тегами и поиском.
Перед генерацией новой игры — проверь библиотеку, вдруг уже есть похожая!

## Команды

### Найти похожую игру
```bash
python3 /root/.openclaw/workspace/skills/game-library/scripts/library.py find "snake cyberpunk"
# или:
python3 /root/.openclaw/workspace/skills/game-library/scripts/library.py find snake --theme cyberpunk
```

### Добавить игру в каталог после генерации
```bash
python3 /root/.openclaw/workspace/skills/game-library/scripts/library.py add {slug} "{title}" {game_type} {theme} {score} "{url}"
```

### Показать весь каталог
```bash
python3 /root/.openclaw/workspace/skills/game-library/scripts/library.py list
```

### Топ игр по рейтингу
```bash
python3 /root/.openclaw/workspace/skills/game-library/scripts/library.py top
```

## Логика кеша

Если пользователь просит "змейку в стиле neон" и такая уже есть с score >= 80%:
→ Верни существующую ссылку (быстро, бесплатно)
→ Или предложи: "У меня уже есть такая! Хочешь новую или вот старая: [ссылка]?"

Если score < 60% — генерируй заново, кеш не использовать.
