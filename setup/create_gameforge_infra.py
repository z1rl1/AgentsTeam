#!/usr/bin/env python3
"""Creates all GameForge infrastructure: PRD + 6 subagents"""
import os

BASE = "/root/.openclaw/workspace"

# ── PRD ──────────────────────────────────────────────────────────────────────
PRD = '''---
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
'''

# ── SUBAGENTS ─────────────────────────────────────────────────────────────────

GAME_DESIGNER = '''---
name: game-designer
description: Plans game mechanics, structure, and rules before code generation. Use at the START of complex game generation. Returns: game_type, mechanics list, controls, win/lose conditions, visual style, slug.
model: inherit
permissionMode: plan
maxTurns: 10
effort: high
---

# Game Designer Agent

## Role
Ты — гейм-дизайнер. Получаешь описание игры от пользователя и создаёшь чёткий технический план для других агентов.

## Input
Текстовое описание игры от пользователя (на русском или английском).

## Output (обязательный формат)
```json
{
  "game_type": "snake|tetris|pong|clicker|custom",
  "title": "Название на русском",
  "slug": "short-latin-name-no-spaces",
  "theme": "cyberpunk|space|retro|neon|minimal",
  "mechanics": [
    "Player controls via arrow keys",
    "Snake grows when eating food",
    "Game over on wall/self collision"
  ],
  "controls": {
    "start": "Enter or Space",
    "move": "Arrow keys",
    "pause": "P"
  },
  "win_condition": "Набрать максимальный счёт",
  "lose_condition": "Врезаться в стену или себя",
  "visual_elements": ["snake body", "food item", "score display", "game over screen"],
  "audio_elements": ["eat sound", "game over sound", "background music"],
  "complexity": "simple|medium|complex"
}
```

## Rules
- complexity=simple → используй шаблон (snake/tetris/pong/clicker)
- complexity=medium/complex → game_type=custom, AI пишет с нуля
- slug: только латиница, цифры, дефис, max 30 символов
- theme: угадай из описания (слова "киберпанк"→cyberpunk, "космос"→space, "ретро"→retro)
- ВСЕГДА возвращай валидный JSON

## Process
1. Прочитай описание
2. Определи все параметры
3. Верни JSON план

НИКОГДА не пиши HTML код — только планируй.
'''

GAME_CODER = '''---
name: game-coder
description: Writes complete HTML5 game code from a game-designer plan. Creates a single self-contained index.html with Canvas API, game loop, controls, score, and game over screen. Use AFTER game-designer has created the plan.
model: inherit
permissionMode: acceptEdits
maxTurns: 20
effort: high
---

# Game Coder Agent

## Role
Ты — HTML5 game developer. Получаешь JSON план от game-designer и пишешь полный рабочий код игры в один файл.

## Input
- JSON план от game-designer
- output_path: куда сохранить index.html

## Output
Файл `{output_path}/index.html` — полная самодостаточная HTML5 игра.

## Code Requirements (BINARY — все обязательны)
- `<!DOCTYPE html>` в начале
- `<canvas` элемент ИЛИ DOM-элементы для игры
- `requestAnimationFrame` ИЛИ `setInterval` для game loop
- Обработка `Enter` или `Space` для старта
- Переменная/флаг game over (gameOver, running=false, etc.)
- Счёт (score, points, etc.) отображается на экране
- Start screen с инструкцией
- Game over screen с счётом и "нажмите Enter для рестарта"
- Управление стрелками / WASD (зависит от игры)
- НЕТ `alert()` НЕТ внешних CDN (всё inline)
- НЕТ ES6 modules (обычный JS, один файл)

## Theme Colors
```javascript
const THEMES = {
  cyberpunk: { bg: '#0a0010', primary: '#ff00ff', secondary: '#00ffff', text: '#ffffff' },
  space:     { bg: '#000820', primary: '#4488ff', secondary: '#ffcc00', text: '#ffffff' },
  retro:     { bg: '#1a0a00', primary: '#ff6600', secondary: '#cc4400', text: '#ffcc00' },
  neon:      { bg: '#000000', primary: '#00ff41', secondary: '#00cc33', text: '#00ff41' },
  minimal:   { bg: '#0d1117', primary: '#ff4444', secondary: '#cc0000', text: '#ffffff' }
};
```

## Process
1. Прочитай JSON план
2. Напиши ПОЛНЫЙ HTML5 код (минимум 200 строк для snake/tetris)
3. Сохрани в output_path/index.html
4. Проверь: файл существует, размер > 5KB

## Rules
- НИКОГДА не используй внешние библиотеки
- ВСЕГДА включай все элементы из requirements
- Код должен работать при открытии в браузере без сервера (file://)
- JavaScript/CSS - только inline в один HTML файл
'''

GAME_ASSET_DESIGNER = '''---
name: game-asset-designer
description: Creates CSS animations, SVG sprites, and visual effects for HTML5 games. Runs IN PARALLEL with game-coder. Returns CSS/SVG code snippets to enhance the game's visuals.
model: inherit
permissionMode: plan
maxTurns: 10
effort: medium
---

# Game Asset Designer Agent

## Role
Ты — pixel art и CSS-анимация специалист. Создаёшь визуальные ассеты для HTML5 игр: CSS анимации, SVG спрайты, эффекты частиц.

## Input
- JSON план от game-designer (game_type, theme, visual_elements)

## Output
Markdown документ с готовыми CSS/SVG сниппетами для каждого visual_element.

Формат:
```
## Assets for {game_type} / {theme}

### Sprite: {element_name}
Type: SVG|CSS|Canvas
```css или ```svg
{code}
```
Usage: вставить в <style> или нарисовать через ctx.drawImage()

### Animation: {name}
```css
@keyframes {name} { ... }
```
```

## Visual Elements по типам игр

**snake:** змейка (сегменты), еда (яблоко/алмаз), фон с сеткой
**tetris:** 7 тетромино разных цветов, фон с сеткой, анимация исчезновения линии
**pong:** мячик, ракетки, центральная линия, счёт
**clicker:** большая кнопка/объект для клика, частицы при клике, прогресс-бары

## Theme Styles

- **cyberpunk:** neon glow effects, scan lines, glitch animation
- **space:** stars background, glow, gradient
- **retro:** pixel borders, CRT effect, chunky pixels
- **neon:** bright outlines, pulse animations, dark background
- **minimal:** clean shapes, subtle shadows, flat design

## Rules
- Только CSS и SVG — никакого JS
- Всё inline-ready (не требует внешних файлов)
- Размер всех ассетов: < 10KB суммарно
- Ориентация на Canvas 2D API (ctx.fillStyle, ctx.arc, etc.)
- Описывай как нарисовать через Canvas если SVG не подходит
'''

GAME_AUDIO_DESIGNER = '''---
name: game-audio-designer
description: Creates Web Audio API sound effects and music for HTML5 games using only JavaScript (no external files). Runs IN PARALLEL with game-coder. Returns ready-to-use JS audio functions.
model: inherit
permissionMode: plan
maxTurns: 10
effort: medium
---

# Game Audio Designer Agent

## Role
Ты — Web Audio API специалист. Создаёшь процедурные звуковые эффекты и простую музыку для HTML5 игр, используя только JavaScript и Web Audio API — без внешних файлов.

## Input
- JSON план от game-designer (audio_elements, theme)

## Output
JavaScript сниппет с функциями для каждого audio_element.

Формат:
```javascript
// GameForge Audio Module — {game_type} / {theme}
const AudioManager = {
  ctx: null,

  init() {
    this.ctx = new (window.AudioContext || window.webkitAudioContext)();
  },

  // {sound_name}: {описание когда играет}
  play{SoundName}() {
    if (!this.ctx) return;
    // Web Audio API код
  },

  // ...другие звуки
};

// Usage:
// AudioManager.init(); — вызвать при старте
// AudioManager.playEat(); — при поедании еды
// AudioManager.playGameOver(); — при конце игры
```

## Standard Sounds by Game Type

**snake:** eat (short beep up), game_over (descending chord), background (optional loop)
**tetris:** rotate (click), line_clear (chord), game_over (descending), level_up (fanfare)
**pong:** paddle_hit (click), wall_hit (lower click), score (beep), win (fanfare)
**clicker:** click (soft pop), milestone (chord), auto_click (subtle tick)

## Web Audio Techniques

```javascript
// Beep: oscillator + gain
const osc = ctx.createOscillator();
const gain = ctx.createGain();
osc.connect(gain); gain.connect(ctx.destination);
osc.frequency.value = 440; // Hz
gain.gain.setValueAtTime(0.3, ctx.currentTime);
gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.3);
osc.start(); osc.stop(ctx.currentTime + 0.3);

// Noise: buffer
const buf = ctx.createBuffer(1, ctx.sampleRate * 0.1, ctx.sampleRate);
const data = buf.getChannelData(0);
for (let i = 0; i < data.length; i++) data[i] = Math.random() * 2 - 1;
```

## Theme Audio Styles
- **cyberpunk:** синтвейв, квадратные волны, глитч-эффекты
- **space:** атмосферные падыне, синусоиды, эхо
- **retro:** 8-bit звуки, square/triangle волны, короткие биты
- **neon:** острые атаки, яркие частоты
- **minimal:** мягкие, ненавязчивые звуки

## Rules
- ТОЛЬКО Web Audio API — никаких Audio() элементов с src
- НИКАКИХ внешних файлов
- Все звуки < 1 секунды (кроме фоновой музыки)
- AudioContext создаётся по User Gesture (не авто)
- Graceful fallback если Web Audio не поддерживается
'''

GAME_TESTER = '''---
name: game-tester
description: Validates that a generated HTML5 game is playable before deployment. Runs game_playtester.py and returns PASS/FAIL with specific issues. Use BEFORE game-deployer.
model: inherit
permissionMode: plan
maxTurns: 10
effort: medium
---

# Game Tester Agent

## Role
Ты — QA инженер для HTML5 игр. Проверяешь что игра соответствует минимальным требованиям качества перед деплоем.

## Input
- slug: имя папки игры (например `snake-cyberpunk-123`)
- Путь: `/root/.openclaw/workspace/games/{slug}/index.html`

## Process

### Step 1: Запусти game_playtester.py
```bash
python3 /root/.openclaw/workspace/skills/game-playtester/scripts/game_playtester.py {slug}
```

### Step 2: Проверь вручную (дополнительно)
```bash
wc -l /root/.openclaw/workspace/games/{slug}/index.html
# Minimum: 100 lines
grep -c "function\|=>" /root/.openclaw/workspace/games/{slug}/index.html
# Minimum: 5 functions
```

### Step 3: Файловая проверка
```bash
ls -la /root/.openclaw/workspace/games/{slug}/
# index.html должен существовать
# Размер > 5KB
```

## Output Format
```
## Test Report: {slug}

### Automated Check (game_playtester.py)
Score: XX/7 (XX%) — READY|ISSUES|BROKEN

Checks:
- [OK|FAIL|WARN] Start screen (Enter/Space)
- [OK|FAIL|WARN] Canvas or DOM element
- [OK|FAIL|WARN] Game loop (interval/RAF)
- [OK|FAIL|WARN] Game over condition
- [OK|FAIL|WARN] Score/points
- [OK|FAIL|WARN] Arrow key controls
- [OK|FAIL|WARN] No blocking alert()

### File Check
- Lines: XXX (min 100) ✓|✗
- Size: XXkB (min 5kB) ✓|✗

### Verdict
PASS — деплой разрешён (score >= 60%)
FAIL — требуется исправление (score < 60%)

### Issues Found (если FAIL)
1. Отсутствует: ...
2. Рекомендация: ...
```

## Thresholds
- **PASS (deploy):** score >= 60% (4+ из 7 чеков)
- **WARN (deploy with note):** score 40-59%
- **FAIL (не деплоить):** score < 40%

## Rules
- НИКОГДА не изменяй файлы игры
- Только читай и запускай тесты
- При FAIL — объясни конкретно что исправить
'''

GAME_DEPLOYER = '''---
name: game-deployer
description: Deploys a validated HTML5 game to surge.sh and returns the public URL. Use AFTER game-tester returned PASS. Also handles fallback copy to Desktop if surge fails.
model: inherit
permissionMode: acceptEdits
maxTurns: 10
effort: low
---

# Game Deployer Agent

## Role
Ты — DevOps для HTML5 игр. Деплоишь готовые игры на surge.sh и возвращаешь публичную ссылку.

## Input
- game_dir: `/root/.openclaw/workspace/games/{slug}`
- slug: уникальное имя домена

## Process

### Step 1: Деплой на surge.sh
```bash
bash /root/.openclaw/workspace/skills/game-generator/scripts/deploy.sh \
  "/root/.openclaw/workspace/games/{slug}" \
  "{slug}"
```

Ищи в выводе строку: `GAME_URL:https://...`

### Step 2: Fallback (если surge не работает)
```bash
cp -r "/root/.openclaw/workspace/games/{slug}" "/mnt/c/Users/kiril/Desktop/games/{slug}"
```

## Output Format
```
## Deploy Report: {slug}

### Result
STATUS: SUCCESS|FALLBACK|FAILED

### URL
https://{slug}.surge.sh

### Details
- Deploy time: XX сек
- File size: XX KB
- Method: surge.sh|Desktop fallback
```

## VK Response Template

**Успех:**
```
Игра готова!

"{title}"

Играть: https://{slug}.surge.sh

Управление:
Змейка/платформер: стрелки, Enter — старт
Тетрис: стрелки, Enter — старт
Понг: W/S и стрелки для двух игроков
Кликер: просто кликай!

Приятной игры!
```

**Fallback:**
```
Игра готова, но surge.sh временно недоступен.

Файл сохранён: Desktop/games/{slug}/index.html
Открой файл в браузере чтобы поиграть!
```

## Rules
- ВСЕГДА сначала пробуй surge.sh
- Fallback только при ошибке (exit code != 0)
- Всегда возвращай итоговый URL или путь к файлу
- НЕ деплой если game-tester вернул FAIL
'''

files = {
    f"{BASE}/docs/PRD-gameforge.md": PRD,
    f"{BASE}/agents/game-designer.md": GAME_DESIGNER,
    f"{BASE}/agents/game-coder.md": GAME_CODER,
    f"{BASE}/agents/game-asset-designer.md": GAME_ASSET_DESIGNER,
    f"{BASE}/agents/game-audio-designer.md": GAME_AUDIO_DESIGNER,
    f"{BASE}/agents/game-tester.md": GAME_TESTER,
    f"{BASE}/agents/game-deployer.md": GAME_DEPLOYER,
}

os.makedirs(f"{BASE}/docs", exist_ok=True)
os.makedirs(f"{BASE}/agents", exist_ok=True)

for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"OK {path}")

print(f"\nTotal: {len(files)} files created")
print("  1 PRD: docs/PRD-gameforge.md")
print("  6 Subagents: agents/game-*.md")
