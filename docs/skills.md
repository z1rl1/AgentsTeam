# Скиллы GameForge

Каждый скилл — это папка в `skills/` с `SKILL.md` (инструкции) и `scripts/` (Python код).

## Основные (используются в pipeline)

### game-generator
**Скрипты:** generate_game.py, make_game.py, orchestrate.py, deploy.sh
**Роль:** Главный движок. Генерирует ассеты, вызывает LLM, запускает QA, деплоит.

```bash
# Простой запуск
python3 skills/game-generator/scripts/make_game.py "описание игры" "user_id"

# Многоагентный (с планированием)
python3 skills/game-generator/scripts/orchestrate.py "описание игры" "user_id"

# Деплой готовой игры
bash skills/game-generator/scripts/deploy.sh games/{slug} {slug}
```

### game-playtester
**Скрипты:** game_playtester.py, browser_test.js
**Роль:** QA Gate. 27 статических проверок + браузерный тест в Playwright.
Вердикт: READY (>=85%) / ISSUES (65-84%) / BROKEN (<65%)

```bash
python3 skills/game-playtester/scripts/game_playtester.py {slug}
# Или для всех игр сразу:
python3 skills/game-playtester/scripts/game_playtester.py
```

### game-bug-fixer
**Скрипты:** fix_bugs.py
**Роль:** Отправляет провалившую QA игру в LLM с описанием что именно сломано.
Пробует исправить автоматически.

```bash
python3 skills/game-bug-fixer/scripts/fix_bugs.py {slug}
```

### game-enhancer
**Скрипты:** enhance.py
**Роль:** Улучшает существующую игру. Режимы: visual, gameplay, audio, all.

```bash
python3 skills/game-enhancer/scripts/enhance.py {slug} visual
python3 skills/game-enhancer/scripts/enhance.py {slug} gameplay
python3 skills/game-enhancer/scripts/enhance.py {slug} audio
```

---

## Вспомогательные (утилиты)

### feedback
**Роль:** Хранит пользовательские ограничения и предпочтения.
```bash
python3 skills/feedback/scripts/feedback.py get {user_id}
python3 skills/feedback/scripts/feedback.py set {user_id} "без спойлеров"
```

### user-memory
**Роль:** Запоминает какие игры делал пользователь, любимые темы и жанры.
```bash
python3 skills/user-memory/scripts/memory.py save {user_id} {slug} {game_type} {theme}
python3 skills/user-memory/scripts/memory.py get {user_id}
```

### rate-limiter
**Роль:** Ограничивает частоту запросов от одного пользователя.
```bash
python3 skills/rate-limiter/scripts/rate_limit.py check {user_id}
python3 skills/rate-limiter/scripts/rate_limit.py release {user_id}
```

### prompt-optimizer
**Роль:** Накапливает статистику что работает, предлагает улучшения промпта.
```bash
python3 skills/prompt-optimizer/scripts/prompt_optimizer.py record {slug} {score} {theme} {type}
python3 skills/prompt-optimizer/scripts/prompt_optimizer.py best-prompt
python3 skills/prompt-optimizer/scripts/prompt_optimizer.py analyze
```

### observability
**Роль:** Статистика токенов, стоимости, успешности за день.
```bash
python3 skills/observability/scripts/stats.py today
python3 skills/observability/scripts/stats.py week
```

### game-library
**Роль:** Каталог всех сгенерированных игр. Поиск похожих.
```bash
python3 skills/game-library/scripts/library.py find "змейка киберпанк"
python3 skills/game-library/scripts/library.py add {slug} {title} {type} {theme} {score} {url}
```

### overnight
**Роль:** Ночное улучшение — берёт игры с score 70-84%, пробует починить через fix_bugs.
Запускается автоматически или вручную:
```bash
python3 skills/overnight/scripts/overnight.py
```

---

## Игровые утилиты (по запросу пользователя)

| Скилл | Команда | Что делает |
|---|---|---|
| game-difficulty | difficulty.py {slug} hard/easy | Регулирует сложность |
| theme-switcher | switch_theme.py {slug} cyberpunk | Меняет визуальную тему |
| mobile-optimizer | optimize_mobile.py {slug} | Добавляет тач-управление |
| game-leaderboard | leaderboard.py {slug} | Добавляет таблицу рекордов |
| game-tutorial | tutorial.py {slug} | Добавляет туториал |
| achievement-system | achievements.py {slug} | Добавляет ачивки |
| game-balancer | balance.py {slug} | Балансирует сложность |
| game-soundtrack | soundtrack.py {slug} | Добавляет/заменяет музыку |
| game-clone | clone.py {slug} {new_slug} | Клонирует игру |
| idea-generator | ideas.py [theme] | Генерирует идеи игр |
| game-randomizer | randomizer.py | Случайная механика/тема |