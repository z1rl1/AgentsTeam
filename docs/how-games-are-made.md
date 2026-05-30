# Как создаётся игра — полный путь

## От запроса до ссылки

### 1. Пользователь пишет в VK
"Неоновый космический шутер. Вид сверху. Три типа врагов, боссы, параллакс."

### 2. OpenClaw читает SOUL.md и запускает pipeline

Агент определяет что это запрос на игру и вызывает make_game.py или orchestrate.py.

### 3. make_game.py определяет параметры

```python
slug  = "shooter-space-4521"    # game_type + theme + 4 цифры
title = "Неоновый Космический Шутер"
theme = "space"                  # определяется по ключевым словам
```

### 4. generate_game.py — параллельная фаза ассетов + кода

**Параллельно запускаются:**

Поток 1 — MiniMax Image API (4 worker'а):
```
player-idle.png  — персонаж стоит
player-run.png   — персонаж бежит (для платформеров)
player-jump.png  — персонаж прыгает
player-shoot.png — персонаж стреляет (для шутеров)
enemy.png        — враг тип 1
enemy2.png       — враг тип 2 / босс
background.png   — фон с параллаксом
title.png        — тайтл-скрин
```

Поток 2 — MiniMax Music API:
```
theme.mp3 — инструментальная музыка под тему игры
```

Если image quota исчерпана (50/50) — переключается в canvas-only режим,
отменяет остальные запросы, рисует всё через Canvas API.

### 5. LLM генерирует HTML5 код (MiniMax-M2.7)

Промпт содержит:
- Описание игры от пользователя
- Жанровые требования (для шутера: волны врагов, снаряды, здоровье)
- Цветовую схему темы (space: #000820, #4488ff, #ffcc00)
- Инструкции по использованию ассетов (или canvas fallback)
- Строгие QA требования (минимум draw calls, структура кода)
- Feedback от предыдущей попытки (если retry)

Результат: index.html, обычно 30,000-40,000 токенов, 400-1000 строк кода.

### 6. QA Gate (game_playtester.py)

Статические проверки (27 штук):
- Структура HTML: DOCTYPE, canvas, rAF loop
- Геймплей: старт, game over, score, управление
- Визуал: размер canvas, плотность draw calls, частицы, эффекты
- Качество: нет CDN, нет alert/confirm, нет debug цветов
- Ассеты: используются ли загруженные PNG

Браузерный тест (Playwright):
- Загружает игру в headless Chromium
- Нажимает Enter (старт) и Space
- Делает 3 скриншота с интервалом 500мс
- Проверяет анимацию (checksums должны меняться)
- Ловит JS ошибки

Score < 85% или есть required failures -> retry с feedback.

### 7. Retry (если нужно)

Feedback строится из конкретных провалов:
```
RETRY — scored below 85%. Fix these issues FIRST:

MUST FIX: particle system with 20+ arc() particles,
gradient background, shadowBlur glow, screen shake.
Use variables: particles, gradient, shadow, glow, shake.

Full QA report:
[FAIL] Rich scene density
[FAIL] Not rectangle-only actors
```

### 8. Деплой (deploy.sh)

1. Запускает playtester ещё раз (финальная проверка)
2. Если READY: `surge {game_dir} {slug}.surge.sh`
3. Если surge упал: копирует в Desktop как fallback

### 9. Ответ в VK

```
🔥 Готово! Неоновый Космический Шутер

Играть: https://shooter-space-4521.surge.sh

Управление: стрелки или WASD + пробел.
```

---

## Спрайты — как работает per-state система

Вместо одного sprites.png (который резался на случайные куски),
теперь каждое состояние персонажа — отдельный файл:

```javascript
// Загрузка
const sprites = {};
const SPRITE_FILES = [
  ['idle',   'assets/player-idle.png'],
  ['run',    'assets/player-run.png'],
  ['jump',   'assets/player-jump.png'],
  ['enemy',  'assets/enemy.png'],
  ['enemy2', 'assets/enemy2.png'],
  ['bg',     'assets/background.png'],
];
SPRITE_FILES.forEach(([key, src]) => {
  const img = new Image();
  img.onload = () => sprites[key] = img;
  img.onerror = () => sprites[key] = null;  // graceful fallback
  img.src = src;
});

// Рисование с переключением состояний
function drawPlayer(p) {
  let key = p.onGround ? (p.vx !== 0 ? 'run' : 'idle') : 'jump';
  const img = sprites[key] || sprites['idle'];
  ctx.drawImage(img, p.x, p.y, p.w, p.h);
}
```

---

## Canvas-only режим (когда картинки недоступны)

LLM получает инструкции рисовать всё через Canvas API:

```
PLAYER — compound canvas path:
  ctx.beginPath(); ctx.moveTo(0,-h/2); ctx.lineTo(w/2,h/2);
  ctx.lineTo(0,h/3); ctx.lineTo(-w/2,h/2); ctx.closePath();
  ctx.fillStyle = PRIMARY_COLOR; ctx.shadowBlur=15; ctx.fill();
  // Engine glow: two arc() pulsing with Math.sin(Date.now()/100)

ENEMIES — each type unique shape:
  Fast: ellipse(), color #ff4444
  Heavy: hexagon via lineTo() x6, color #ff8800
  Boss: bezierCurveTo() multi-part body, color #aa00ff

PARTICLES (20+ per explosion):
  ctx.globalAlpha = p.life/p.maxLife;
  ctx.arc(p.x, p.y, p.size*(p.life/p.maxLife), 0, Math.PI*2);
  ctx.shadowBlur=8; ctx.shadowColor=p.color; ctx.fill();
```

---

## Стоимость генерации

Из observability (данные за 2026-05-30):
- Средняя длительность: ~131 секунда на игру
- Средняя стоимость: ~$0.005 на игру
- Успешных: ~14% (6 из 81 попытки)
- Токенов среднее: 77k input + 358k output = 436k total за день

Основные причины неуспеха (до исправлений):
1. MAX_TOKENS=200000 -> HTTP 400 от MiniMax API
2. Противоречие промпт vs QA (sprites.png запрещён но QA требует drawImage)
3. orchestrate.py деплоил при score=None (qa_score не писался в gameforge.json)