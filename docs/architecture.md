# Архитектура GameForge

## Общая схема

```
VK Сообщение
     |
     v
OpenClaw Agent (Claude/MiniMax-M2.7)
     |
     |-- читает SOUL.md (инструкции поведения)
     |
     v
make_game.py / orchestrate.py
     |
     |-- определяет slug, theme, title из запроса
     |
     v
generate_game.py (главный движок)
     |
     |-- [параллельно]
     |   |-- MiniMax Image API -> player-idle.png, player-run.png,
     |   |                        player-jump.png, enemy.png, enemy2.png,
     |   |                        background.png, title.png
     |   |-- MiniMax Music API -> assets/theme.mp3
     |
     |-- [если image quota exhausted] -> canvas-only mode (рисует кодом)
     |
     |-- MiniMax-M2.7 Text API -> генерирует index.html (30-60k токенов)
     |
     v
game_playtester.py (QA Gate)
     |
     |-- статический анализ кода (27 regex-проверок)
     |-- браузерный тест (Playwright Chromium)
     |   |-- запуск в headless браузере
     |   |-- нажимает Enter/Space (старт игры)
     |   |-- проверяет canvas рендерит
     |   |-- проверяет анимацию (checksums)
     |   |-- ловит JS ошибки
     |
     |-- score >= 85% и нет required failures -> READY
     |-- score < 85% или есть required failures -> ISSUES/BROKEN
     |
     v
[если READY]
deploy.sh -> surge.sh -> https://{slug}.surge.sh
     |
     v
VK Ответ: "Играть: https://..."
```

## Компоненты

### make_game.py
Точка входа. Принимает описание от пользователя, определяет slug и theme по ключевым словам, вызывает generate_game.py.

Определение жанра (GAME_TYPES):
- "стрел", "зомби", "shooter" -> shooter
- "платформ", "прыг" -> platformer
- "гонк", "машин" -> racing
- "змей" -> snake
- "тетрис" -> tetris

Определение темы (THEMES):
- "киберпанк" -> cyberpunk
- "космос", "космич", "галакт" -> space
- "неон" -> neon
- "ретро" -> retro

### generate_game.py
Главный движок генерации. 940+ строк.

Ключевые функции:
- build_asset_pack() — генерация PNG/MP3 через MiniMax API параллельно
- is_quota_error() — детектирует исчерпание дневного лимита
- is_transient_error() — детектирует временные сетевые ошибки
- asset_instructions() — инструкции для LLM (с ассетами или canvas-only)
- build_prompt() — собирает промпт: описание + жанр + цвета + инструкции
- call_minimax() — вызов MiniMax text API
- run_playtester() — запускает QA
- update_qa_score() — сохраняет score в gameforge.json
- generate_locked() — основной цикл с retry (MAX_ATTEMPTS раз)

Цикл генерации (generate_locked):
1. Запускает генерацию ассетов в фоновом потоке
2. Пишет predicted_manifest в gameforge.json
3. Для каждой попытки (1..MAX_ATTEMPTS):
   a. Строит промпт с текущим asset_manifest
   b. Вызывает MiniMax для генерации HTML кода
   c. Ждёт завершения ассетов (если ещё не готовы)
   d. Запускает playtester
   e. Если score >= 85% -> ACCEPTED, return True
   f. Иначе строит retry_feedback с конкретными фиксами
4. Если все попытки провалились -> REJECTED, return False

### Умная обработка quota (is_quota_error)
Детектирует слова: "daily usage limit", "quota", "50/50", "plan limit"
При обнаружении:
- Отменяет все оставшиеся параллельные запросы к image API
- Устанавливает quota_exhausted=True в manifest
- Переключается в canvas-only режим
- asset_instructions() возвращает CANVAS_FALLBACK_INSTRUCTIONS
- QA снижает требования к ассетам с required до warning

### orchestrate.py
Многоагентный оркестратор. Шаги:
1. game-designer — LLM придумывает slug, тему, механики (JSON план)
2. generate_game.py — генерирует игру
3. game-enhancer — если score 75-84%, пытается улучшить
4. deploy.sh — деплоит если score >= 85%

### game_playtester.py
QA Gate. 27 проверок кода + браузерный тест.

Ключевые проверки (required = блокируют деплой):
- Complete HTML document
- Canvas renderer
- Large/responsive canvas (>= 900x500 или fullscreen)
- requestAnimationFrame loop
- Start/restart controls
- Game over state
- Score/objective UI
- Keyboard controls
- Substantial code size (>= 24KB или 350+ строк)
- Core gameplay depth (5+ механик: коллизии, физика, прогрессия, враги, частицы)
- Multiple entities/systems (12+ массивов/классов/объектов)
- Generated bitmap/image assets (если ассеты есть)
- Not rectangle-only actors (персонажи не просто fillRect)
- No distorted asset stretching
- Polished typography
- Designed UI composition
- No blocking dialogs (alert/prompt/confirm)
- No external dependencies (CDN)

Оценка: pct = passed / total * 100
Если есть required failures: pct = min(pct, 74) — жёсткий потолок
READY >= 85%, ISSUES 65-84%, BROKEN < 65%

## Агенты (agents/)

| Файл | Роль | Когда используется |
|---|---|---|
| game-designer.md | Придумывает план игры (JSON) | Шаг 1 в SOUL.md pipeline |
| game-coder.md | Пишет index.html по плану | Шаг 2 параллельно |
| game-asset-designer.md | Планирует ассеты для MiniMax | Шаг 2 параллельно |
| game-audio-designer.md | Генерирует музыку | Шаг 2 параллельно |
| game-tester.md | Запускает QA, при провале -> fix_bugs | Шаг 3 |
| game-deployer.md | Деплоит READY игры, отвечает в VK | Шаг 4 |

## Лимиты MiniMax (Plan Plus)

| API | Лимит | Период |
|---|---|---|
| Text Generation | 4500 единиц | 5-часовое окно |
| Image Generation | 50 изображений | Ежедневно (сброс 00:00 UTC) |
| Music Generation | 100 треков | Ежедневно |
| Speech Generation | 4000 единиц | Ежедневно |

ВАЖНО: max_tokens для text API — не более ~40000. Значение 200000 вызывает HTTP 400.