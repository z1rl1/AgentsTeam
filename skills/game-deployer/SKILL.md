---
name: game-deployer
description: Deploys an existing game to surge.sh without regenerating it. Use when user asks to redeploy, update the link, or fix deployment of an existing game.
argument-hint: "slug игры (например snake-cyberpunk)"
metadata:
  openclaw:
    requires:
      bins: [node]
---
# Game Deployer Skill

## Задача
Задеплоить уже существующую игру на surge.sh без повторной генерации.

## Алгоритм

### 1. Найди папку игры
```bash
ls /root/.openclaw/workspace/games/
```

### 2. Задеплой
```bash
bash /root/.openclaw/workspace/skills/game-generator/scripts/deploy.sh   /root/.openclaw/workspace/games/{slug} {slug}
```

### 3. Верни ссылку
```
✅ Игра задеплоена: https://{slug}.surge.sh
```

## Когда использовать
- Surge упал и игра недоступна
- Нужно обновить ссылку
- Игра была изменена и нужен ре-деплой
