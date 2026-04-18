---
id: PRD-001
version: 1.0.0
stage: approved
owner: GameForge VK Agent
priority: critical
created: 2026-04-16
---

# PRD-001 — GameForge VK: AI-генератор HTML5-игр

## 1. Overview

**Feature:** AI-агент принимает текстовое описание игры в VK, генерирует рабочую HTML5-игру, деплоит на surge.sh и отвечает живой ссылкой — за < 60 секунд.

**Strategic Goal:** Democratize game creation — любой VK-пользователь получает персонализированную браузерную игру без знания программирования.

---

## 2. Problem Description

**Current State:** Создание браузерной игры требует 2–8 часов и знания HTML5/Canvas/JS/CSS.

**Pain Points:**
- Нет инструмента "опиши — получи игру" для массового пользователя
- AI-кодогенераторы дают код, но не дают ссылку (нужен деплой)
- Персонализация игр недоступна без разработчика

---

## 3. Target Audience

| Persona | Needs | Success |
|---------|-------|---------|
| VK-геймер (14–25) | Уникальная игра про свой интерес | Получил ссылку, поиграл |
| VK-автор | Мини-игра для вовлечения аудитории | Поделился с подписчиками |
| Студент | Игра для демо/портфолио | Показал преподавателю |

---

## 4. User Scenarios (GIVEN-WHEN-THEN)

### Scenario 1 — Базовая генерация

```
GIVEN пользователь написал в VK: "сделай змейку в стиле киберпанк"
WHEN агент получает сообщение
THEN:
  - определяет: game_type=snake, theme=cyberpunk, slug=snake-cyberpunk-{timestamp}
  - запускает generate_game.py → создаёт index.html
  - запускает game_playtester.py → проверяет: score >= 80%
  - запускает deploy.sh → получает GAME_URL
  - отвечает в VK: ссылка + управление
  - игра открывается в браузере, Enter начинает, стрелки управляют
```

**Input/Output Table:**

| User Message | game_type | theme | URL |
|---|---|---|---|
| "змейку в стиле киберпанк" | snake | cyberpunk | snake-cyberpunk-XXX.surge.sh |
| "хочу тетрис космический" | tetris | space | tetris-space-XXX.surge.sh |
| "понг для двух игроков ретро" | pong | retro | pong-retro-XXX.surge.sh |
| "кликер с улучшениями неон" | clicker | neon | clicker-neon-XXX.surge.sh |
| "платформер где кот прыгает" | custom | minimal | platformer-cat-XXX.surge.sh |

### Scenario 2 — Нестандартная игра

```
GIVEN пользователь написал: "самолёт уворачивается от ракет"
WHEN тип игры не совпадает с шаблоном
THEN:
  - game_type = "custom"
  - AI генерирует уникальный HTML5/JS код с нуля
  - код содержит: canvas, requestAnimationFrame, collision detection, score, game over
  - проверка game_playtester.py >= 60%
  - деплой и ссылка в VK
```

### Scenario 3 — Параллельные субагенты

```
GIVEN сложная игра требует кастомные ассеты
WHEN game-designer определил структуру
THEN ПАРАЛЛЕЛЬНО запускаются:
  - game-coder      → пишет HTML5/JS механику
  - game-asset-designer → создаёт CSS/SVG спрайты
  - game-audio-designer → добавляет Web Audio API звуки
AFTER все завершены:
  - game-tester     → валидация (start, loop, gameover, score)
  - game-deployer   → surge.sh деплой
  - ответ в VK < 120 сек
```

### Scenario 4 — Fallback при ошибке деплоя

```
GIVEN surge.sh вернул ошибку
WHEN deploy.sh exit != 0
THEN:
  - копирует index.html в /mnt/c/Users/kiril/Desktop/games/{slug}/
  - сообщает в VK: "игра готова! surge недоступен, файл сохранён на рабочий стол"
```

---

## 5. Functional Scope

### In Scope
- snake, tetris, pong, clicker — шаблонная генерация + 5 тем
- custom — AI-генерация любой игры с нуля
- Деплой на surge.sh, fallback на Desktop
- Каталог игр `/game-catalog`
- Тестирование `/game-playtester`
- Параллельные субагенты для сложных игр
- Self-improvement через eval + hooks

### Out of Scope
- WebSocket мультиплеер
- Сохранение рекордов в БД
- Мобильные нативные приложения
- Монетизация

---

## 6. Technical Environment

### File Paths
```
/root/.openclaw/workspace/
  SOUL.md                          — идентичность агента
  agents/
    game-designer.md               — планирует механику
    game-coder.md                  — пишет HTML5/JS
    game-asset-designer.md         — CSS/SVG спрайты (параллельно)
    game-audio-designer.md         — Web Audio API (параллельно)
    game-tester.md                 — валидирует игру
    game-deployer.md               — деплоит на surge.sh
  skills/
    game-generator/scripts/
      generate_game.py             — создаёт index.html
      deploy.sh                    — деплоит на surge.sh
    game-playtester/scripts/game_playtester.py
    game-catalog/scripts/game_catalog.py
  games/{slug}/index.html          — готовые игры
```

### API Contracts

**generate_game.py:**
```
Input:  game_type title theme output_dir
Output: creates output_dir/index.html
Exit 0: success | Exit 1: error
```

**deploy.sh:**
```
Input:  game_dir slug
Output: prints "GAME_URL:https://{slug}.surge.sh"
Exit 0: deployed | Exit 1: surge failed
```

### HTML5 Game Binary Requirements
- MUST contain: `<canvas` OR `getElementById`
- MUST contain: `setInterval` OR `requestAnimationFrame`
- MUST contain: `Enter|Space` для старта
- MUST contain: `game.?over|running.*false` для конца
- MUST contain: `score|Score|points`
- MUST NOT contain: `alert(`

---

## 7. Quality Requirements

| Metric | Target | Tool |
|--------|--------|------|
| Time to link | < 60 сек | deploy.sh timing |
| Game playability | >= 80% | game_playtester.py |
| Deploy success | >= 95% | surge.sh response |
| VK response after deploy | < 2 сек | timestamp diff |

---

## 8. Development Plan

### Phase 1 — Core Generator (no dependencies)
**Tasks:**
1. Восстановить generate_game.py: snake, tetris, pong, clicker шаблоны
2. Исправить Python/JS конфликт: `.replace()` вместо `.format()`
3. Добавить apply_theme() для 5 тем

**Validation:**
```bash
python3 /root/.openclaw/workspace/skills/game-generator/scripts/generate_game.py snake "Test Snake" cyberpunk /tmp/test-snake
python3 /root/.openclaw/workspace/skills/game-playtester/scripts/game_playtester.py test-snake
# Expected: READY (score >= 80%)
```

### Phase 2 — Deploy Pipeline (requires Phase 1)
**Tasks:**
1. Проверить surge CLI установлен
2. Настроить SURGE_TOKEN или анонимный деплой
3. Fallback: копировать на Desktop при ошибке

**Validation:**
```bash
bash /root/.openclaw/workspace/skills/game-generator/scripts/deploy.sh /tmp/test-snake snake-test-$(date +%s)
# Expected output contains: GAME_URL:https://
```

### Phase 3 — Custom AI Generation (requires Phase 1)
**Tasks:**
1. Ветка `custom` в generate_game.py — вызов LLM
2. Промпт: write complete HTML5 game in one file, no external deps
3. Парсинг HTML из ответа + валидация

**Validation:**
```bash
python3 generate_game.py "custom" "Кот-Прыгун" minimal /tmp/custom
python3 game_playtester.py custom
# Expected: score >= 60%
```

### Phase 4 — Subagents (requires Phase 3)
**Tasks:**
1. 6 файлов агентов в `/root/.openclaw/workspace/agents/`
2. Обновить SOUL.md — инструкция по запуску субагентов

**Validation:**
```
Запрос → game-designer → [game-coder || game-asset-designer || game-audio-designer] → game-tester → game-deployer
Ссылка в VK < 120 сек
```

### Phase 5 — Self-Improvement (requires Phase 4)
**Tasks:**
1. generate-eval для game-generator
2. Настройка hooks: post-skill-eval.sh
3. /skill-health проверка

**Validation:**
```bash
cat /root/.openclaw/workspace/skills/game-generator/eval/eval.json
# Expected: >= 5 binary assertions
```

---

## 9. Risk Assessment

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| Free LLM rate limit | High | Critical | Шаблоны для 4 типов, LLM только для custom |
| surge.sh недоступен | Medium | High | Fallback: Desktop |
| LLM генерирует невалидный HTML | Medium | High | Retry с исправленным промптом |
| Python/JS `{}` конфликт | High | Medium | Решён: `.replace()` вместо `.format()` |
| VK token истёк | Low | High | Предупреждение при старте |

---

## 10. Agent Operating Rules

### ALLOWED (автономно)
- Читать файлы проекта
- Запускать python3 скрипты генерации
- Запускать bash deploy.sh
- Создавать папки в /games/
- Отправлять ответы в VK

### REQUIRES APPROVAL
- Изменять SOUL.md / SKILL.md
- Добавлять зависимости (npm, pip)
- Изменять openclaw.json

### FORBIDDEN
- Деплой без тестирования game_playtester.py
- Отправка PII пользователя в LLM
- Изменение настроек VK-аккаунта

---

## 11. Completion Checklist

- [ ] generate_game.py: snake READY >= 80%
- [ ] generate_game.py: tetris READY >= 80%
- [ ] generate_game.py: pong READY >= 80%
- [ ] generate_game.py: clicker READY >= 80%
- [ ] deploy.sh: возвращает GAME_URL строку
- [ ] custom генерация: READY >= 60%
- [ ] 6 субагентов: файлы созданы в /agents/
- [ ] SOUL.md: обновлён с инструкцией субагентов
- [ ] eval.json: создан для game-generator (>= 5 assertions)
- [ ] /skill-health: game-generator имеет score
- [ ] VK: бот отвечает ссылкой < 60 сек
