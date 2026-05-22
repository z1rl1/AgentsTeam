---
name: rate-limiter
description: Prevents generation spam by enforcing 60-second cooldown per VK user and max 5 concurrent generations. Use BEFORE starting game generation to check if user is allowed.
---

# Rate Limiter Skill

Защита от спама: один пользователь не может заказывать игры чаще чем раз в 60 секунд.

## Команды

### Проверить можно ли генерировать
```bash
python3 /root/.openclaw/workspace/skills/rate-limiter/scripts/rate_limit.py check {user_id}
```
Вернёт: `OK` (можно) или `BLOCKED`/`COOLDOWN` (нельзя).

### Заблокировать слот (перед генерацией)
```bash
python3 /root/.openclaw/workspace/skills/rate-limiter/scripts/rate_limit.py acquire {user_id}
```

### Освободить слот (после генерации)
```bash
python3 /root/.openclaw/workspace/skills/rate-limiter/scripts/rate_limit.py release {user_id}
```

### Статус всех активных блокировок
```bash
python3 /root/.openclaw/workspace/skills/rate-limiter/scripts/rate_limit.py status
```

## Лимиты

- Cooldown: 60 секунд между запросами от одного пользователя
- Max concurrent: 5 одновременных генераций
- Lock timeout: 300 секунд (авто-снятие если что-то зависло)

## Ответ при блокировке

Если пользователь заблокирован — ответь в VK:
```
Подожди немного! Я ещё генерирую твою предыдущую игру.
Попробуй через минуту.
```
