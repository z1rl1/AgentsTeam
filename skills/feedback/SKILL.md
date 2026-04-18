---
name: feedback
description: Saves and reads user feedback about games. Automatically detects when user says they dislike something and saves it as a constraint. Use to personalize future game generation per user.
triggers:
  - "не нравится"
  - "плохо"
  - "измени"
  - "хочу чтобы"
  - "сделай иначе"
  - "слишком"
  - "скучно"
---

# Feedback Skill

Когда пользователь говорит что ему не нравится — сохраняй это как ограничение.
Агент должен сам детектировать фидбек и сохранять без явной команды.

## Алгоритм детекции

После каждого сообщения пользователя проверь:
```bash
python3 /root/.openclaw/workspace/skills/feedback/scripts/feedback.py detect "{message}"
```
- Вернёт `negative` или `suggestion` → сохрани фидбек
- Вернёт `positive` → похвали и запиши
- Вернёт `neutral` → игнорируй

## Сохранить фидбек
```bash
python3 /root/.openclaw/workspace/skills/feedback/scripts/feedback.py add {user_id} {slug} negative "{что не понравилось}"
```

## Прочитать ограничения пользователя (до генерации)
```bash
python3 /root/.openclaw/workspace/skills/feedback/scripts/feedback.py get {user_id}
```
Передай результат в generate_game.py как user_id параметр — он сам подтянет ограничения.

## Важно
- НЕ жди явной команды "сохрани фидбек"
- АВТОМАТИЧЕСКИ детектируй негативные сообщения
- Отвечай в VK: "Понял! Запомнил что тебе не нравится [X]. Учту в следующей игре!"
