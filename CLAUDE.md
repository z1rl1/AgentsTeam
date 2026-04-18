# CLAUDE.md — GameForge

> **Для разработчика**: обзор архитектуры, структура файлов, как всё устроено.
> **Для агента (OpenClaw runtime)**: читай `SOUL.md` — там все инструкции.

## Что такое GameForge

AI-агент в VK: пользователь пишет "сделай змейку" → агент генерирует HTML5 игру через LLM → деплоит на surge.sh → отвечает живой ссылкой. Всё за < 60 секунд.

**Платформа**: OpenClaw 2026 (агентовый шлюз к VK User Long Poll)
**LLM**: MiniMax M1 (prod) / OpenRouter (fallback)
**Деплой**: surge.sh (статический хостинг)

## Архитектура

```
VK сообщение
     │
     ▼
GameForge (SOUL.md — главные инструкции агента)
     │
     ├── rate-limiter      ← 60с cooldown на пользователя
     ├── game-library      ← поиск в каталоге (не генерируем повторно)
     ├── user-memory       ← предпочтения пользователя (feedback)
     │
     ├── [простая игра] → пишет код сам → deploy.sh → VK
     │
     └── [сложная игра]:
          game-designer (план JSON)
               │
          ┌────┼────┐ параллельно
          │    │    │
       game  asset audio
       coder design design
          │
       game-tester (QA: READY/ISSUES/BROKEN)
          │
       game-deployer (surge.sh → URL → VK)
          │
       observability + prompt-optimizer
```

## Субагенты

| Агент | Роль | Mode | Файл |
|-------|------|------|------|
| `game-designer` | Планирует механику → JSON | plan | agents/game-designer.md |
| `game-coder` | Пишет HTML5/JS игру | acceptEdits | agents/game-coder.md |
| `game-asset-designer` | CSS/SVG ассеты (параллельно) | plan | agents/game-asset-designer.md |
| `game-audio-designer` | Web Audio API (параллельно) | plan | agents/game-audio-designer.md |
| `game-tester` | QA проверка перед деплоем | plan | agents/game-tester.md |
| `game-deployer` | Деплой на surge.sh → VK | acceptEdits | agents/game-deployer.md |

## Структура файлов

```
gameforge workspace/
├── SOUL.md              ← главный файл агента (читает OpenClaw)
├── CLAUDE.md            ← этот файл (читает разработчик / Claude Code)
│
├── agents/              ← определения субагентов
│   ├── game-designer.md
│   ├── game-coder.md
│   ├── game-asset-designer.md
│   ├── game-audio-designer.md
│   ├── game-tester.md
│   └── game-deployer.md
│
├── skills/              ← 40+ скиллов
│   └── [skill-name]/
│       ├── SKILL.md     ← инструкции скилла
│       ├── scripts/     ← Python скрипты
│       └── eval/
│           └── eval.json ← бинарные assertions для self-improve
│
├── hooks/               ← lifecycle хуки (автоматические)
│   ├── pre-skill-check.sh    ← перед скиллом: проверяет eval, инжектит score
│   ├── post-skill-eval.sh    ← после скилла: оценивает output, пишет метрики
│   ├── session-report.sh     ← при стопе: итоговый отчёт сессии
│   └── lib/
│       ├── eval-engine.sh    ← движок бинарных assertions
│       └── metrics.sh        ← трекинг scores по времени
│
├── docs/
│   └── PRD-gameforge.md ← полный Agentic PRD (GIVEN-WHEN-THEN)
│
└── setup/               ← одноразовые скрипты установки
    ├── setup_api.py     ← тестирует free модели, сохраняет рабочую
    └── save_config.py   ← записывает ключ и модель в openclaw.json
```

## Ключевые скиллы

| Скилл | Что делает |
|-------|-----------|
| `game-generator` | Основной: LLM генерирует HTML5 игру |
| `game-playtester` | QA: 7 чеков (canvas, gameloop, score, controls...) |
| `rate-limiter` | 60с cooldown + max 5 concurrent |
| `game-library` | Каталог игр, поиск по тегам |
| `user-memory` | Предпочтения пользователя |
| `feedback` | Детектирует негатив → сохраняет constraints |
| `prompt-optimizer` | Karpathy loop: scores → улучшает промпт |
| `observability` | Логирует токены + стоимость |
| `self-improve` | Автономное улучшение всех скиллов |

## Self-Improvement (Karpathy Loop)

```
Каждый запуск скилла:
  PostToolUse → post-skill-eval.sh
    → читает skills/*/eval/eval.json
    → проверяет assertions против output
    → пишет score в hooks/metrics/{skill}.jsonl
    → если score < 80% → предлагает улучшения

Ручной запуск:
  python3 skills/self-improve/scripts/self_improve.py status
  python3 skills/self-improve/scripts/self_improve.py all
  python3 skills/self-improve/scripts/self_improve.py game-generator
```

## LLM конфигурация

- **Prod**: MiniMax M1 (`MINIMAX_API_KEY`)
- **Fallback**: OpenRouter (`OPENROUTER_API_KEY`)
- **Рабочая free модель**: `nvidia/nemotron-3-super-120b-a12b:free`
- **Конфиг**: `skills/game-generator/scripts/generate_game.py`

## Установка

```bash
# Скопировать workspace на сервер
cp -r . /root/.openclaw/workspace/

# Настроить API ключи
python3 setup/setup_api.py    # тест free моделей → сохраняет рабочую
python3 setup/save_config.py  # записывает в openclaw.json

# Запустить OpenClaw
cd /root/.openclaw && npm start
```

## PRD

Полный Product Requirements Document с GIVEN-WHEN-THEN сценариями:
`docs/PRD-gameforge.md`
