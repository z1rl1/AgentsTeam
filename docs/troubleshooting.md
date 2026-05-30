# Troubleshooting — Частые проблемы и решения

## Игры всегда 74% и не деплоятся

**Симптом:** все игры получают ровно 74%, статус ISSUES, деплоя нет.

**Причина:** 74% это жёсткий потолок при наличии required failures в QA.
`if required_failed: pct = min(pct, 74)`

**Диагностика:**
```bash
python3 skills/game-playtester/scripts/game_playtester.py {slug}
```
Смотри строки с `[FAIL]` — это required failures.

**Частые required failures и фиксы:**

| Failure | Причина | Фикс |
|---|---|---|
| Not rectangle-only actors | LLM рисует персонажей через fillRect | Усилить запрет в BASE_PROMPT |
| Generated bitmap/image assets | Ассеты не загружаются в код | Проверить manifest.json в assets/ |
| Rich scene density | Мало draw calls или visual_terms | Снизить порог в playtester (40 вместо 55) |
| No debug neon frames | Magenta #ff00ff + strokeRect | Перевести в warning |

---

## HTTP Error 400: Bad Request от MiniMax

**Симптом:** `ERROR: HTTP Error 400: Bad Request` в логах, tokens_in=0.

**Причина:** GAMEFORGE_MAX_TOKENS слишком большое. MiniMax принимает максимум ~40000.

**Фикс:**
```bash
# В .env
GAMEFORGE_MAX_TOKENS=40000
```

---

## Картинки не генерируются, quota exhausted

**Симптом:** `MiniMax API error 2056: usage limit exceeded, daily usage limit reached (50/50 used)`

**Это нормально** — дневной лимит image API исчерпан (50 картинок в день).

**Система автоматически:**
1. Детектирует quota error
2. Отменяет оставшиеся запросы к image API
3. Переключается в canvas-only режим
4. Передаёт LLM инструкции рисовать через Canvas API

**Если автопереключение не работает:**
```bash
# В .env
GAMEFORGE_REQUIRE_GENERATED_ASSETS=0
```

**Сброс лимита:** 00:00 UTC ежедневно (~03:00 по Москве).

---

## Агент не пишет ответ в VK после ошибки

**Симптом:** бот написал "Делаю, подожди" и замолчал.

**Причина:** в SOUL.md не было правила писать в VK при ошибках API.

**Фикс добавлен:** секция 2.1 в SOUL.md с шаблонами для каждого типа ошибки:
- Лимит картинок: "Картинки закончились, делаю без них, подожди"
- Лимит токенов: "Лимит запросов, подожди минуту"
- Таймаут: "Генерация зависла, запускаю заново"
- Ошибка деплоя: "Игра готова, surge не ответил"

---

## Агент предлагает OpenRouter когда не надо

**Симптом:** бот пишет "Попробую через OpenRouter" когда лимит только на картинки.

**Причина:** image API и text API — разные лимиты. Когда кончились картинки,
text API (для кода игры) продолжает работать.

**Фикс:** в SOUL.md секция 2.1 теперь явно говорит:
"Лимит картинок != лимит кода. НЕ предлагай OpenRouter, просто делай canvas-mode."

---

## Дублирующиеся генерации одного slug

**Симптом:** в логах 2-3 записи одного slug подряд с малым интервалом.

**Причина:** fcntl.flock не работает надёжно в WSL2 между процессами.

**Фикс:** не запускать несколько экземпляров make_game.py параллельно для одной игры.

---

## Агент застрял, ничего не происходит

**Диагностика:**
```bash
# Смотри запущенные процессы
ps aux | grep -E "python3|make_game|generate_game" | grep -v grep

# Смотри последние логи
tail -5 /root/.openclaw/workspace/hooks/logs/llm-usage-$(date +%Y-%m-%d).jsonl

# Смотри папку активной генерации
ls -la /root/.openclaw/workspace/games/{slug}/
```

**Если застрял:**
```bash
# Убить зависший процесс
kill {PID}

# Удалить незавершённую папку (снимет lock)
rm -rf /root/.openclaw/workspace/games/{slug}
```

---

## Тема игры определяется неправильно

**Симптом:** "космический шутер" получает тему retro вместо space.

**Причина:** make_game.py ищет точные подстроки ("космос"), а слова типа
"космический", "космических" не совпадают.

**Фикс добавлен:** в THEMES добавлено "космич" -> space, "галакт" -> space.

---

## git push не работает из WSL

**Причина:** WSL2 NAT не видит Windows-прокси. GitHub недоступен из WSL.

**Фикс:** пушить из Windows PowerShell через git bundle:
```powershell
# В Windows PowerShell
wsl -u root git -C /root/.openclaw/workspace bundle create /mnt/c/Users/.../gameforge.bundle --all
$tmpDir = "$env:TEMP\gameforge_push"
git clone "$env:TEMP\gameforge.bundle" $tmpDir
git -C $tmpDir remote set-url origin https://github.com/user/repo.git
git -C $tmpDir push origin gameforge --force
```

---

## self_improve показывает 100% но ничего не улучшается

**Причина:** self_improve.py проверяет качество запуском `generate_game.py status`,
который возвращает "GameForge generator OK" — это всегда 100%.

**Реальные метрики** смотри в:
```bash
tail -20 hooks/logs/llm-usage-$(date +%Y-%m-%d).jsonl
python3 skills/observability/scripts/stats.py today
```

---

## Игра задеплоена но без ссылки в surge.sh

**Симптом:** deploy.sh отработал но GAME_URL не появился.

**Диагностика:**
```bash
bash skills/game-generator/scripts/deploy.sh games/{slug} {slug}
# Ищи строку: GAME_URL:https://...
```

**Если FALLBACK_PATH:** surge завис, игра скопирована на Desktop.
Открой /mnt/c/Users/kiril/Desktop/games/{slug}/index.html локально.