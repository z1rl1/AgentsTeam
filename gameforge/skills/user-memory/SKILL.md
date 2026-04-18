---
name: user-memory
description: Remembers VK user preferences, favorite themes, past games, and personalizes game generation. Use before generating a game to get user context, and after to save the result.
---

# User Memory Skill

Сохраняй и читай предпочтения пользователей для персонализации игр.

## Хранилище
`/root/.openclaw/workspace/memory/users/{user_id}.json`

## Команды

### Прочитать профиль пользователя перед генерацией
```bash
python3 /root/.openclaw/workspace/skills/user-memory/scripts/memory.py get {user_id}
```
Вернёт: любимая тема, любимый тип игры, последние 5 игр.

### Сохранить результат после генерации
```bash
python3 /root/.openclaw/workspace/skills/user-memory/scripts/memory.py save {user_id} {slug} {game_type} {theme}
```

### Найти похожую игру в истории пользователя
```bash
python3 /root/.openclaw/workspace/skills/user-memory/scripts/memory.py find {user_id} {game_type}
```

## Как использовать

1. До генерации: `memory.py get {user_id}` — узнай предпочтения
2. Если у пользователя есть favorite_theme — используй его если он не указал другой
3. После генерации: `memory.py save ...` — обнови профиль
4. Если пользователь часто просит snake — предложи вариации: snake с боссами, snake RPG и т.д.
