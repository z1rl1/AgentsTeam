# GameForge — Система генерации HTML5 игр

GameForge принимает текстовый запрос от пользователя в VK и за 5-10 минут генерирует готовую HTML5 игру, деплоит её на surge.sh и отвечает публичной ссылкой.

## Как это работает

Пользователь: "сделай змейку в стиле киберпанк"
1. Агент генерирует картинки (MiniMax image API) — фон, персонажи, тайтл
2. Агент генерирует музыку (MiniMax music API)
3. LLM пишет полный HTML5 код игры (MiniMax-M2.7, до 40k токенов)
4. QA проверка: статический анализ кода + реальный браузер (Playwright)
5. Деплой на surge.sh
6. Бот отвечает ссылкой в VK

## Зависимости

### Обязательные
- Python 3.10+
- Node.js 18+ (браузерный QA через Playwright)
- surge CLI: npm install -g surge
- MiniMax API ключ

### Установка Playwright
```bash
cd /root/.openclaw/workspace/skills/game-playtester
npm install playwright
npx playwright install chromium
```

## Быстрый старт

```bash
# Скопируй и заполни .env
cp .env.example .env

# Сгенерировать игру
python3 skills/game-generator/scripts/make_game.py "змейка киберпанк" "user123"

# Или через оркестратор (планировщик + генератор + деплой)
python3 skills/game-generator/scripts/orchestrate.py "платформер с роботами" "user123"
```

## Переменные окружения

| Переменная | Значение | Описание |
|---|---|---|
| MINIMAX_API_KEY | — | Обязательно |
| GAMEFORGE_MODEL | MiniMax-M2.7 | LLM для кода |
| GAMEFORGE_GENERATE_ASSETS | 1 | Генерировать PNG/MP3 |
| GAMEFORGE_REQUIRE_GENERATED_ASSETS | 0 | Блокировать без ассетов |
| GAMEFORGE_MAX_TOKENS | 40000 | Лимит токенов (MiniMax принимает до ~40k) |
| GAMEFORGE_MAX_ATTEMPTS | 4 | Попытки при провале QA |
| MINIMAX_TIMEOUT_SECONDS | 180 | Таймаут text API |
| MINIMAX_ASSET_TIMEOUT_SECONDS | 240 | Таймаут image/music API |

## Структура проекта

```
workspace/
├── SOUL.md              # Главные инструкции агента
├── PIPELINE.md          # Краткий пайплайн (резерв)
├── AGENTS.md            # Описание субагентов
├── agents/              # Субагенты (game-designer, game-coder, ...)
├── skills/              # Python-скрипты скиллов
│   ├── game-generator/  # Главный генератор
│   ├── game-playtester/ # QA gate
│   ├── game-bug-fixer/  # Авточинка через LLM
│   ├── game-enhancer/   # Улучшение визуала
│   └── ...              # 25+ других
├── games/               # Сгенерированные игры
├── memory/              # Память о пользователях
├── hooks/               # Логи и метрики
└── docs/                # Документация
```