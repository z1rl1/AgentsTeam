---
name: observability
description: Tracks LLM token usage, generation costs, and system performance. Run to see daily/weekly spending and model efficiency stats.
---

# Observability Skill

Мониторинг токенов, стоимости и производительности GameForge.

## Команды

### Дневная статистика
```bash
python3 /root/.openclaw/workspace/skills/observability/scripts/stats.py today
```

### Статистика за неделю
```bash
python3 /root/.openclaw/workspace/skills/observability/scripts/stats.py week
```

### Топ дорогих генераций
```bash
python3 /root/.openclaw/workspace/skills/observability/scripts/stats.py top
```

## Что отслеживается
- Токены input/output на каждую генерацию
- Время генерации (секунды)
- Успех/провал каждого запроса к LLM
- Модель, которая использовалась
- Стоимость (по публичным ценам моделей)

<!-- Auto-improved 2026-04-16 -->

<!-- Auto-improved 2026-04-16 -->
## Improvement Notes
- Add example output containing: token|Token|tokens
- Add example output containing: \$|cost|Cost|USD|usd
- Fix: Contains numeric stats
- Add example output containing: ={3,}|-{3,}
- Add example output containing: model|Model|minimax|openrouter|gpt|claud
