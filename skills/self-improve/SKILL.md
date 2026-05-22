---
name: self-improve
description: Autonomously improves a skill using the Karpathy loop - runs eval assertions, scores output, patches SKILL.md, repeats until score >= 75%. Use when skill-health shows low scores or after adding new skills.
triggers:
  - "self-improve"
  - "улучши скилл"
  - "improve skill"
  - "overnight"
  - "karpathy"
---

# Self-Improve Skill — Karpathy Loop

Автономно улучшает скиллы: тестирует → оценивает → исправляет → повторяет.

## Алгоритм (Karpathy loop)

```
1. Загрузи eval.json скилла (binary assertions)
2. Запусти скилл / прочитай его output
3. Прогони все assertions через eval engine
4. Если score < 75% → сгенерируй fixes → примени к SKILL.md
5. Запиши метрику → повтори (max 3 раунда)
6. Залогируй в eval/improvement-log.json
```

## Команды

### Улучшить один скилл
```bash
python3 /root/.openclaw/workspace/skills/self-improve/scripts/self_improve.py game-generator
```

### Улучшить все скиллы ниже порога (75%)
```bash
python3 /root/.openclaw/workspace/skills/self-improve/scripts/self_improve.py all
```

### Статус всех скиллов
```bash
python3 /root/.openclaw/workspace/skills/self-improve/scripts/self_improve.py status
```

### Только запустить eval (без изменений)
```bash
python3 /root/.openclaw/workspace/skills/self-improve/scripts/self_improve.py run-eval game-generator
```

## Что меняется в SKILL.md

Скрипт добавляет в SKILL.md раздел `## Improvement Notes` с конкретными задачами:
- "Add code block with example" (если нет кода в документации)
- "Add ## headings to structure" (если нет заголовков)
- "Expand skill — too brief" (если слишком мало слов)

Это подсказки для следующего улучшения (ручного или автоматического).

## Метрики

Каждый запуск пишет в:
- `/root/.openclaw/workspace/hooks/metrics/{skill}.jsonl` — score + timestamp
- `/root/.openclaw/workspace/skills/{skill}/eval/improvement-log.json` — детали

## Overnight режим

Запускай раз в неделю для полного цикла:
```bash
python3 /root/.openclaw/workspace/skills/self-improve/scripts/self_improve.py all
```
Улучшит все скиллы с eval.json у которых score < 75%.
