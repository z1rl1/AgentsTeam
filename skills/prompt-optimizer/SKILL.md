---
name: prompt-optimizer
description: Tracks game generation quality over time and automatically improves the base prompt. Runs after every game (records score) and periodically analyzes patterns to suggest prompt improvements.
---

# Prompt Optimizer Skill

Самообучение системы: отслеживает что работает, улучшает промпты.

## Как работает (автоматически)

1. После каждой генерации → запускается через generate_game.py (авто)
2. Записывает: slug, score, theme, game_type
3. После 10+ игр → `improve` анализирует паттерны провалов
4. Улучшения сохраняются → следующие генерации используют их

## Ручные команды

### Аналитика
```bash
python3 /root/.openclaw/workspace/skills/prompt-optimizer/scripts/prompt_optimizer.py analyze
```

### Запустить улучшение промпта
```bash
python3 /root/.openclaw/workspace/skills/prompt-optimizer/scripts/prompt_optimizer.py improve
```

### Посмотреть текущие улучшения
```bash
python3 /root/.openclaw/workspace/skills/prompt-optimizer/scripts/prompt_optimizer.py best-prompt
```

## Self-Improvement Loop (Karpathy pattern)

Запускай раз в неделю или после 20+ игр:
```bash
python3 prompt_optimizer.py analyze
python3 prompt_optimizer.py improve
# → улучшения автоматически применяются к следующим генерациям
```
