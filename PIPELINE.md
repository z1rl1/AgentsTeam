# PIPELINE.md — GameForge Минимальный Pipeline

> Этот файл загружается всегда. Если `SOUL.md` обрезан — выполняй эти инструкции.

## Полный Pipeline (субагенты)

1. Спаун `agents/game-designer.md` → получи JSON план
2. Параллельно спаун: `agents/game-coder.md` + `agents/game-asset-designer.md` + `agents/game-audio-designer.md`
3. Спаун `agents/game-tester.md` → QA
4. Спаун `agents/game-deployer.md` → деплой

## Fallback (если субагенты недоступны)

### Шаг 1: Генерация
```bash
python3 /root/.openclaw/workspace/skills/game-generator/scripts/make_game.py "{user_request}" "{user_id}"
```
(make_game.py сам генерирует slug, не нужны shell-переменные)

### Шаг 2: Деплой (только если exit code 0)
```bash
/root/.openclaw/workspace/skills/game-generator/scripts/deploy.sh "/root/.openclaw/workspace/games/{slug}" "{slug}"
```

## Правила

- Slug: `{game_type}-{theme}-{4digits}` — латиница, цифры, дефисы, lowercase.
- В VK отправляй только `https://{slug}.surge.sh`. Никогда локальный путь.
- QA не прошла (exit != 0) → не деплоить, запустить `fix_bugs.py {slug}`, повторить.
- Модель: `MiniMax-M2.7`. Не используй `MiniMax-Text-01`.
- Подробности: читай `SOUL.md`.
