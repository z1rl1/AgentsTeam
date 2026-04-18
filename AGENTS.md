# AGENTS.md — GameForge Subagents Registry

Реестр всех субагентов GameForge VK.
Расположение файлов: /root/.openclaw/workspace/agents/

## Workflow

```
Простая игра:
  Пользователь → SOUL.md (пишет код сам) → deploy.sh → VK

Сложная игра:
  Пользователь
    └→ game-designer (план)
         └→ [game-coder + game-asset-designer + game-audio-designer] (параллельно)
              └→ game-tester (QA)
                   └→ game-deployer (деплой + VK)
```

## Агенты

### game-designer
- **Role:** Гейм-дизайнер — планирует механику, возвращает JSON план
- **Input:** Описание игры от пользователя
- **Output:** JSON: game_type, title, slug, theme, mechanics, controls, complexity
- **Mode:** plan (только читает, не пишет файлы)
- **File:** agents/game-designer.md

### game-coder
- **Role:** HTML5 developer — пишет полный код игры
- **Input:** JSON план от game-designer + output_path
- **Output:** /games/{slug}/index.html (300-800 строк)
- **Mode:** acceptEdits (создаёт файлы)
- **File:** agents/game-coder.md

### game-asset-designer *(параллельно с game-coder)*
- **Role:** CSS/SVG artist — создаёт визуальные ассеты
- **Input:** JSON план (visual_elements, theme)
- **Output:** Markdown с CSS/SVG сниппетами
- **Mode:** plan (возвращает текст, не пишет файлы)
- **File:** agents/game-asset-designer.md

### game-audio-designer *(параллельно с game-coder)*
- **Role:** Sound designer — создаёт Web Audio API звуки
- **Input:** JSON план (audio_elements, theme)
- **Output:** JavaScript AudioManager сниппет
- **Mode:** plan (возвращает текст, не пишет файлы)
- **File:** agents/game-audio-designer.md

### game-tester
- **Role:** QA engineer — валидирует игру перед деплоем
- **Input:** slug игры
- **Output:** Test Report: PASS/WARN/FAIL + конкретные проблемы
- **Mode:** plan (только читает и запускает тесты)
- **Threshold:** PASS >= 60%, WARN 40-59%, FAIL < 40%
- **File:** agents/game-tester.md

### game-deployer
- **Role:** DevOps — деплоит на surge.sh, возвращает URL для VK
- **Input:** game_dir, slug
- **Output:** GAME_URL + готовый текст для VK
- **Fallback:** Копирует на Desktop если surge недоступен
- **Mode:** acceptEdits (запускает deploy.sh)
- **File:** agents/game-deployer.md

## Параллельность

game-asset-designer и game-audio-designer работают ПАРАЛЛЕЛЬНО с game-coder.
Они не пишут файлы — возвращают сниппеты, которые game-coder интегрирует в HTML.

Или: game-coder интегрирует их результаты ПОСЛЕ своей работы (последовательно).

## PRD

Полный Product Requirements Document:
/root/.openclaw/workspace/docs/PRD-gameforge.md
