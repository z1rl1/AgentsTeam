#!/usr/bin/env python3
"""
GameForge VK — Full System Build
Creates all missing components:
  1. generate_game.py — LLM-based (no templates)
  2. Memory/RAG — user preferences per VK user_id
  3. State management — pause/resume for sessions
  4. Observability — token + cost tracking
  5. Rate limiting — queue system per user
  6. Game library/cache — catalog with tags + search
"""
import os

BASE = "/root/.openclaw/workspace"

# ══════════════════════════════════════════════════════════════════════════════
# 1. generate_game.py — Pure LLM generation, no templates
# ══════════════════════════════════════════════════════════════════════════════
GENERATE_GAME = r'''#!/usr/bin/env python3
"""
GameForge — LLM Game Generator
Usage: python3 generate_game.py "<description>" "<title>" "<theme>" "<output_dir>"

Calls LLM API → extracts HTML5 game code → saves index.html
Compatible with: OpenRouter (MiniMax, Claude, GPT-4) and direct MiniMax API
"""
import sys, os, json, re, time
import urllib.request, urllib.error

# ── Config ────────────────────────────────────────────────────────────────────
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MINIMAX_API_KEY    = os.environ.get("MINIMAX_API_KEY", "")
MODEL              = os.environ.get("GAMEFORGE_MODEL", "openrouter/minimax/minimax-01")

THEME_COLORS = {
    "cyberpunk": {"bg": "#0a0010", "primary": "#ff00ff", "secondary": "#00ffff", "text": "#ffffff", "accent": "#ff006e"},
    "space":     {"bg": "#000820", "primary": "#4488ff", "secondary": "#ffcc00", "text": "#ffffff", "accent": "#00aaff"},
    "retro":     {"bg": "#1a0a00", "primary": "#ff6600", "secondary": "#cc4400", "text": "#ffcc00", "accent": "#ff9900"},
    "neon":      {"bg": "#000000", "primary": "#00ff41", "secondary": "#00cc33", "text": "#00ff41", "accent": "#39ff14"},
    "minimal":   {"bg": "#0d1117", "primary": "#ff4444", "secondary": "#cc0000", "text": "#ffffff", "accent": "#ff6666"},
}

GAME_PROMPT = """You are an expert HTML5 game developer. Create a COMPLETE, PLAYABLE browser game.

Game Description: {description}
Game Title: {title}
Visual Theme: {theme}
Theme Colors: bg={bg}, primary={primary}, secondary={secondary}, text={text}

STRICT REQUIREMENTS — ALL must be present:
1. Single self-contained HTML file (<!DOCTYPE html> to </html>)
2. All CSS inside <style> tag — dark background, use theme colors
3. All JavaScript inside <script> tag
4. <canvas> element OR DOM-based game area
5. requestAnimationFrame OR setInterval for game loop
6. Start screen: show title + "Press Enter or Space to start"
7. Game Over screen: show final score + "Press Enter to restart"
8. Score/points displayed during gameplay
9. Keyboard controls (arrow keys / WASD / Space / Enter as appropriate)
10. Complete game logic — not a stub, fully playable
11. NO external libraries, NO CDN links — everything inline
12. NO alert() calls — use canvas/DOM for all UI
13. Smooth 60fps gameplay
14. Minimum 300 lines of code

Visual Style for {theme} theme:
- Background: {bg}
- Primary color (player, important elements): {primary}
- Secondary color (enemies, accents): {secondary}
- Text color: {text}
- Add glow effects using CSS box-shadow or canvas shadowBlur
- Make it look BEAUTIFUL and polished

Return ONLY the complete HTML code. No explanations. Start with <!DOCTYPE html>"""

# ── LLM Call ──────────────────────────────────────────────────────────────────
def call_openrouter(prompt, model):
    """Call OpenRouter API"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    data = json.dumps({
        "model": model.replace("openrouter/", ""),
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 8000,
        "temperature": 0.7,
    }).encode()
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://gameforge.vk",
        "X-Title": "GameForge VK",
    })
    with urllib.request.urlopen(req, timeout=120) as r:
        resp = json.loads(r.read())
    return resp["choices"][0]["message"]["content"], resp.get("usage", {})

def call_minimax(prompt):
    """Call MiniMax API directly"""
    url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
    data = json.dumps({
        "model": "MiniMax-Text-01",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 8000,
        "temperature": 0.7,
    }).encode()
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=120) as r:
        resp = json.loads(r.read())
    return resp["choices"][0]["message"]["content"], resp.get("usage", {})

def call_llm(prompt):
    """Try available APIs in order"""
    if MINIMAX_API_KEY:
        print("Using MiniMax API...")
        return call_minimax(prompt)
    if OPENROUTER_API_KEY:
        print(f"Using OpenRouter: {MODEL}...")
        return call_openrouter(prompt, MODEL)
    raise RuntimeError(
        "No API key found! Set MINIMAX_API_KEY or OPENROUTER_API_KEY.\n"
        "Example: MINIMAX_API_KEY=xxx python3 generate_game.py ..."
    )

# ── HTML Extraction ────────────────────────────────────────────────────────────
def extract_html(text):
    """Extract HTML from LLM response"""
    # Try markdown code block first
    match = re.search(r'```(?:html)?\s*(<!DOCTYPE.*?</html>)\s*```', text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1)
    # Try raw HTML
    match = re.search(r'(<!DOCTYPE html.*?</html>)', text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1)
    # If it starts with DOCTYPE, take everything
    if text.strip().lower().startswith('<!doctype'):
        return text.strip()
    return None

# ── Observability ─────────────────────────────────────────────────────────────
def log_generation(slug, model, usage, success, duration_sec):
    """Log LLM usage to observability system"""
    log_dir = "/root/.openclaw/workspace/hooks/logs"
    os.makedirs(log_dir, exist_ok=True)
    from datetime import datetime
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event": "game_generated",
        "slug": slug,
        "model": model,
        "tokens_in": usage.get("prompt_tokens", 0),
        "tokens_out": usage.get("completion_tokens", 0),
        "tokens_total": usage.get("total_tokens", 0),
        "success": success,
        "duration_sec": round(duration_sec, 2),
    }
    date = datetime.now().strftime("%Y-%m-%d")
    with open(f"{log_dir}/llm-usage-{date}.jsonl", "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# ── Main ──────────────────────────────────────────────────────────────────────
def generate(description, title, theme, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    slug = os.path.basename(output_dir)
    colors = THEME_COLORS.get(theme, THEME_COLORS["minimal"])

    prompt = GAME_PROMPT.format(
        description=description,
        title=title,
        theme=theme,
        **colors
    )

    print(f"Generating: {title} ({theme} theme)")
    print(f"Description: {description}")
    print("-" * 50)

    t0 = time.time()
    try:
        raw, usage = call_llm(prompt)
        duration = time.time() - t0

        html = extract_html(raw)
        if not html:
            print("ERROR: LLM response did not contain valid HTML")
            print("Raw response preview:", raw[:500])
            log_generation(slug, MODEL, usage, False, duration)
            return False

        out_path = os.path.join(output_dir, "index.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)

        size_kb = os.path.getsize(out_path) // 1024
        lines = html.count("\n")
        tokens_used = usage.get("total_tokens", "?")

        print(f"SUCCESS: {out_path}")
        print(f"  Size: {size_kb}KB | Lines: {lines} | Tokens: {tokens_used} | Time: {duration:.1f}s")

        log_generation(slug, MODEL, usage, True, duration)
        return True

    except Exception as e:
        duration = time.time() - t0
        print(f"ERROR: {e}")
        log_generation(slug, MODEL, {}, False, duration)
        return False

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python3 generate_game.py <description> <title> <theme> <output_dir>")
        print("Example: python3 generate_game.py 'snake game' 'Змейка' cyberpunk /tmp/snake")
        sys.exit(1)

    description, title, theme, output_dir = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    ok = generate(description, title, theme, output_dir)
    sys.exit(0 if ok else 1)
'''

# ══════════════════════════════════════════════════════════════════════════════
# 2. Memory/RAG — user preferences
# ══════════════════════════════════════════════════════════════════════════════
USER_MEMORY_SKILL = '''---
name: user-memory
description: Remembers VK user preferences, favorite themes, past games, and personalizes game generation. Use before generating a game to get user context, and after to save the result.
---

# User Memory Skill

Сохраняй и читай предпочтения пользователей для персонализации игр.

## Хранилище
`/root/.openclaw/workspace/memory/users/{user_id}.json`

## Команды

### Прочитать профиль пользователя перед генерацией
```bash
python3 /root/.openclaw/workspace/skills/user-memory/scripts/memory.py get {user_id}
```
Вернёт: любимая тема, любимый тип игры, последние 5 игр.

### Сохранить результат после генерации
```bash
python3 /root/.openclaw/workspace/skills/user-memory/scripts/memory.py save {user_id} {slug} {game_type} {theme}
```

### Найти похожую игру в истории пользователя
```bash
python3 /root/.openclaw/workspace/skills/user-memory/scripts/memory.py find {user_id} {game_type}
```

## Как использовать

1. До генерации: `memory.py get {user_id}` — узнай предпочтения
2. Если у пользователя есть favorite_theme — используй его если он не указал другой
3. После генерации: `memory.py save ...` — обнови профиль
4. Если пользователь часто просит snake — предложи вариации: snake с боссами, snake RPG и т.д.
'''

USER_MEMORY_SCRIPT = r'''#!/usr/bin/env python3
"""
User Memory System — saves VK user preferences and game history
Usage:
  memory.py get <user_id>
  memory.py save <user_id> <slug> <game_type> <theme>
  memory.py find <user_id> <game_type>
  memory.py stats
"""
import sys, os, json
from datetime import datetime

MEMORY_DIR = "/root/.openclaw/workspace/memory/users"

def get_profile(user_id):
    path = f"{MEMORY_DIR}/{user_id}.json"
    if not os.path.exists(path):
        return {"user_id": user_id, "games": [], "favorite_theme": None, "favorite_type": None, "total_games": 0}
    return json.load(open(path))

def save_profile(profile):
    os.makedirs(MEMORY_DIR, exist_ok=True)
    uid = profile["user_id"]
    with open(f"{MEMORY_DIR}/{uid}.json", "w") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

def cmd_get(user_id):
    p = get_profile(user_id)
    print(f"User: {user_id}")
    print(f"  Total games: {p['total_games']}")
    print(f"  Favorite theme: {p['favorite_theme'] or 'not set'}")
    print(f"  Favorite type: {p['favorite_type'] or 'not set'}")
    if p["games"]:
        print(f"  Last games:")
        for g in p["games"][-3:]:
            print(f"    - {g['slug']} ({g['type']}/{g['theme']}) — {g['date'][:10]}")
    return p

def cmd_save(user_id, slug, game_type, theme):
    p = get_profile(user_id)
    entry = {"slug": slug, "type": game_type, "theme": theme, "date": datetime.now().isoformat(), "url": f"https://{slug}.surge.sh"}
    p["games"].append(entry)
    p["games"] = p["games"][-20:]  # keep last 20
    p["total_games"] += 1

    # Update favorites (most frequent)
    types  = [g["type"]  for g in p["games"]]
    themes = [g["theme"] for g in p["games"]]
    p["favorite_type"]  = max(set(types),  key=types.count)  if types  else None
    p["favorite_theme"] = max(set(themes), key=themes.count) if themes else None

    save_profile(p)
    print(f"Saved: {user_id} → {slug} ({game_type}/{theme})")
    print(f"Total games: {p['total_games']} | Favorite: {p['favorite_theme']}/{p['favorite_type']}")

def cmd_find(user_id, game_type):
    p = get_profile(user_id)
    matches = [g for g in p["games"] if g["type"] == game_type]
    if not matches:
        print(f"No previous {game_type} games for user {user_id}")
        return
    last = matches[-1]
    print(f"Found previous {game_type}: {last['slug']}")
    print(f"  URL: {last['url']}")
    print(f"  Theme: {last['theme']} | Date: {last['date'][:10]}")

def cmd_stats():
    if not os.path.exists(MEMORY_DIR):
        print("No users yet"); return
    users = os.listdir(MEMORY_DIR)
    total_games = 0
    type_counts, theme_counts = {}, {}
    for f in users:
        p = json.load(open(f"{MEMORY_DIR}/{f}"))
        total_games += p["total_games"]
        for g in p["games"]:
            type_counts[g["type"]] = type_counts.get(g["type"], 0) + 1
            theme_counts[g["theme"]] = theme_counts.get(g["theme"], 0) + 1
    print(f"Users: {len(users)} | Total games: {total_games}")
    if type_counts:
        top_type = max(type_counts, key=type_counts.get)
        print(f"  Most popular type: {top_type} ({type_counts[top_type]}x)")
    if theme_counts:
        top_theme = max(theme_counts, key=theme_counts.get)
        print(f"  Most popular theme: {top_theme} ({theme_counts[top_theme]}x)")

cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
if cmd == "get"   and len(sys.argv) > 2: cmd_get(sys.argv[2])
elif cmd == "save" and len(sys.argv) > 5: cmd_save(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
elif cmd == "find" and len(sys.argv) > 3: cmd_find(sys.argv[2], sys.argv[3])
elif cmd == "stats": cmd_stats()
else: print(__doc__)
'''

# ══════════════════════════════════════════════════════════════════════════════
# 3. Observability — token + cost tracking
# ══════════════════════════════════════════════════════════════════════════════
OBSERVABILITY_SKILL = '''---
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
'''

OBSERVABILITY_SCRIPT = r'''#!/usr/bin/env python3
"""
Observability — LLM usage stats for GameForge
Usage: stats.py today|week|top|all
"""
import sys, os, json, glob
from datetime import datetime, timedelta

LOGS_DIR = "/root/.openclaw/workspace/hooks/logs"

# Model pricing per 1M tokens (input/output) in USD
MODEL_PRICES = {
    "minimax":         {"in": 0.20, "out": 1.10},
    "minimax-text-01": {"in": 0.20, "out": 1.10},
    "claude-3-haiku":  {"in": 0.25, "out": 1.25},
    "claude-3-sonnet": {"in": 3.00, "out": 15.0},
    "gpt-4o-mini":     {"in": 0.15, "out": 0.60},
    "default":         {"in": 0.50, "out": 1.50},
}

def get_price(model, tokens_in, tokens_out):
    key = "default"
    for k in MODEL_PRICES:
        if k in model.lower():
            key = k; break
    p = MODEL_PRICES[key]
    return (tokens_in * p["in"] + tokens_out * p["out"]) / 1_000_000

def load_entries(days=1):
    entries = []
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        path = f"{LOGS_DIR}/llm-usage-{date}.jsonl"
        if os.path.exists(path):
            for line in open(path):
                if line.strip():
                    try: entries.append(json.loads(line))
                    except: pass
    return entries

def print_stats(entries, label):
    if not entries:
        print(f"No data for {label}"); return
    total_in  = sum(e.get("tokens_in", 0)  for e in entries)
    total_out = sum(e.get("tokens_out", 0) for e in entries)
    total_tok = sum(e.get("tokens_total", 0) for e in entries)
    success   = sum(1 for e in entries if e.get("success"))
    total_cost = sum(get_price(e.get("model","default"), e.get("tokens_in",0), e.get("tokens_out",0)) for e in entries)
    avg_time  = sum(e.get("duration_sec", 0) for e in entries) / len(entries)

    print(f"\n{'='*50}")
    print(f"  GameForge Observability — {label}")
    print(f"{'='*50}")
    print(f"  Requests:     {len(entries)} total | {success} OK | {len(entries)-success} failed")
    print(f"  Tokens:       {total_in:,} in + {total_out:,} out = {total_tok:,} total")
    print(f"  Cost:         ${total_cost:.4f} USD")
    print(f"  Avg time:     {avg_time:.1f} sec/game")
    print(f"  Cost/game:    ${total_cost/len(entries):.4f} USD avg")
    models = list(set(e.get("model","?") for e in entries))
    print(f"  Models:       {', '.join(models)}")
    print(f"{'='*50}\n")

def cmd_today():
    print_stats(load_entries(1), "Today")

def cmd_week():
    print_stats(load_entries(7), "Last 7 days")

def cmd_top():
    entries = load_entries(30)
    by_cost = sorted(entries, key=lambda e: get_price(e.get("model","default"), e.get("tokens_in",0), e.get("tokens_out",0)), reverse=True)
    print("\n  Top 5 most expensive generations:")
    for e in by_cost[:5]:
        cost = get_price(e.get("model","default"), e.get("tokens_in",0), e.get("tokens_out",0))
        print(f"    {e.get('slug','?')} | {e.get('tokens_total',0):,} tokens | ${cost:.4f} | {e.get('duration_sec',0):.1f}s")

cmd = sys.argv[1] if len(sys.argv) > 1 else "today"
if cmd == "today": cmd_today()
elif cmd == "week": cmd_week()
elif cmd == "top":  cmd_top()
elif cmd == "all":
    cmd_today(); cmd_week(); cmd_top()
else: print(__doc__)
'''

# ══════════════════════════════════════════════════════════════════════════════
# 4. Rate Limiting — per-user queue
# ══════════════════════════════════════════════════════════════════════════════
RATE_LIMIT_SCRIPT = r'''#!/usr/bin/env python3
"""
Rate Limiter — prevents generation spam per VK user
Usage:
  rate_limit.py check <user_id>    → 0=ok, 1=blocked
  rate_limit.py acquire <user_id>  → lock slot
  rate_limit.py release <user_id>  → unlock slot
  rate_limit.py status             → show all active locks
"""
import sys, os, json, time
from datetime import datetime

LOCK_DIR   = "/tmp/gameforge-locks"
COOLDOWN   = 60   # seconds between requests per user
MAX_ACTIVE = 5    # max concurrent generations total

os.makedirs(LOCK_DIR, exist_ok=True)

def get_lock_path(user_id):
    return f"{LOCK_DIR}/{user_id}.json"

def cmd_check(user_id):
    path = get_lock_path(user_id)
    # Check user cooldown
    if os.path.exists(path):
        data = json.load(open(path))
        age = time.time() - data["started"]
        if data["status"] == "generating":
            print(f"BLOCKED: {user_id} is already generating (started {int(age)}s ago)")
            return 1
        if data["status"] == "done" and age < COOLDOWN:
            wait = int(COOLDOWN - age)
            print(f"COOLDOWN: {user_id} must wait {wait}s")
            return 1
    # Check global concurrent limit
    active = [f for f in os.listdir(LOCK_DIR) if f.endswith(".json")]
    generating = 0
    for f in active:
        try:
            d = json.load(open(f"{LOCK_DIR}/{f}"))
            if d["status"] == "generating" and time.time() - d["started"] < 300:
                generating += 1
        except: pass
    if generating >= MAX_ACTIVE:
        print(f"BUSY: {generating} games generating, try again soon")
        return 1
    print(f"OK: {user_id} can generate")
    return 0

def cmd_acquire(user_id):
    path = get_lock_path(user_id)
    data = {"user_id": user_id, "status": "generating", "started": time.time(), "ts": datetime.now().isoformat()}
    with open(path, "w") as f:
        json.dump(data, f)
    print(f"Locked: {user_id}")

def cmd_release(user_id):
    path = get_lock_path(user_id)
    if os.path.exists(path):
        data = json.load(open(path))
        data["status"] = "done"
        data["finished"] = time.time()
        with open(path, "w") as f:
            json.dump(data, f)
    print(f"Released: {user_id}")

def cmd_status():
    files = [f for f in os.listdir(LOCK_DIR) if f.endswith(".json")]
    if not files:
        print("No active locks"); return
    print(f"\n  Active: {len(files)} users")
    for f in files:
        try:
            d = json.load(open(f"{LOCK_DIR}/{f}"))
            age = int(time.time() - d["started"])
            print(f"    {d['user_id']:20} {d['status']:12} {age}s ago")
        except: pass

cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
if cmd == "check"   and len(sys.argv) > 2: sys.exit(cmd_check(sys.argv[2]))
elif cmd == "acquire" and len(sys.argv) > 2: cmd_acquire(sys.argv[2])
elif cmd == "release" and len(sys.argv) > 2: cmd_release(sys.argv[2])
elif cmd == "status": cmd_status()
else: print(__doc__)
'''

# ══════════════════════════════════════════════════════════════════════════════
# 5. Game Library/Cache — catalog with tags + search
# ══════════════════════════════════════════════════════════════════════════════
GAME_LIBRARY_SKILL = '''---
name: game-library
description: Searchable catalog of all generated games with tags, themes, and scores. Use BEFORE generating a new game to check if a similar game already exists and can be reused or modified.
---

# Game Library Skill

Каталог всех созданных игр с тегами и поиском.
Перед генерацией новой игры — проверь библиотеку, вдруг уже есть похожая!

## Команды

### Найти похожую игру
```bash
python3 /root/.openclaw/workspace/skills/game-library/scripts/library.py find "snake cyberpunk"
# или:
python3 /root/.openclaw/workspace/skills/game-library/scripts/library.py find snake --theme cyberpunk
```

### Добавить игру в каталог после генерации
```bash
python3 /root/.openclaw/workspace/skills/game-library/scripts/library.py add {slug} "{title}" {game_type} {theme} {score} "{url}"
```

### Показать весь каталог
```bash
python3 /root/.openclaw/workspace/skills/game-library/scripts/library.py list
```

### Топ игр по рейтингу
```bash
python3 /root/.openclaw/workspace/skills/game-library/scripts/library.py top
```

## Логика кеша

Если пользователь просит "змейку в стиле neон" и такая уже есть с score >= 80%:
→ Верни существующую ссылку (быстро, бесплатно)
→ Или предложи: "У меня уже есть такая! Хочешь новую или вот старая: [ссылка]?"

Если score < 60% — генерируй заново, кеш не использовать.
'''

GAME_LIBRARY_SCRIPT = r'''#!/usr/bin/env python3
"""
Game Library — searchable catalog of generated games
Storage: /root/.openclaw/workspace/games/_catalog.json

Usage:
  library.py list
  library.py find <query> [--theme <theme>]
  library.py add <slug> <title> <game_type> <theme> <score> <url>
  library.py top [N]
  library.py stats
"""
import sys, os, json
from datetime import datetime

CATALOG = "/root/.openclaw/workspace/games/_catalog.json"
GAMES_DIR = "/root/.openclaw/workspace/games"

def load():
    if not os.path.exists(CATALOG):
        return {"games": [], "version": "1.0"}
    return json.load(open(CATALOG))

def save(data):
    with open(CATALOG, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def cmd_add(slug, title, game_type, theme, score, url):
    data = load()
    # Remove old entry for same slug
    data["games"] = [g for g in data["games"] if g["slug"] != slug]
    entry = {
        "slug": slug,
        "title": title,
        "type": game_type,
        "theme": theme,
        "score": float(score),
        "url": url,
        "created": datetime.now().isoformat(),
        "tags": [game_type, theme, slug.split("-")[0]],
    }
    data["games"].append(entry)
    save(data)
    print(f"Added to library: {slug} ({game_type}/{theme}) score={score}%")

def cmd_find(query, theme_filter=None):
    data = load()
    query_words = query.lower().split()
    results = []
    for g in data["games"]:
        score_match = 0
        searchable = f"{g['slug']} {g['title']} {g['type']} {g['theme']} {' '.join(g.get('tags',[]))}".lower()
        for word in query_words:
            if word in searchable:
                score_match += 1
        if score_match > 0:
            if theme_filter and g["theme"] != theme_filter:
                continue
            results.append((score_match, g))
    results.sort(key=lambda x: (-x[0], -x[1]["score"]))

    if not results:
        print(f"No games found for: {query}")
        return
    print(f"\nFound {len(results)} game(s) for '{query}':")
    for relevance, g in results[:5]:
        print(f"  [{g['score']:.0f}%] {g['slug']} — {g['title']}")
        print(f"         Type: {g['type']} | Theme: {g['theme']} | URL: {g['url']}")
        print(f"         Created: {g['created'][:10]}")

def cmd_list():
    data = load()
    if not data["games"]:
        print("Library is empty — no games yet"); return
    print(f"\n{'='*60}")
    print(f"  Game Library — {len(data['games'])} games")
    print(f"{'='*60}")
    for g in sorted(data["games"], key=lambda x: x["created"], reverse=True):
        print(f"  {g['score']:3.0f}% | {g['type']:10} | {g['theme']:10} | {g['slug']}")
    print(f"{'='*60}\n")

def cmd_top(n=10):
    data = load()
    top = sorted(data["games"], key=lambda x: x["score"], reverse=True)[:n]
    print(f"\n  Top {n} games by score:")
    for i, g in enumerate(top, 1):
        print(f"  {i:2}. [{g['score']:.0f}%] {g['title']} → {g['url']}")

def cmd_stats():
    data = load()
    games = data["games"]
    if not games:
        print("No games yet"); return
    avg_score = sum(g["score"] for g in games) / len(games)
    types = {}
    themes = {}
    for g in games:
        types[g["type"]] = types.get(g["type"], 0) + 1
        themes[g["theme"]] = themes.get(g["theme"], 0) + 1
    print(f"\n  Library Stats:")
    print(f"  Total games: {len(games)} | Avg score: {avg_score:.1f}%")
    print(f"  Top type:  {max(types, key=types.get)} ({max(types.values())}x)")
    print(f"  Top theme: {max(themes, key=themes.get)} ({max(themes.values())}x)")
    good = sum(1 for g in games if g["score"] >= 80)
    print(f"  Quality: {good}/{len(games)} games score >= 80%")

args = sys.argv[1:]
if not args or args[0] == "list":   cmd_list()
elif args[0] == "find":  cmd_find(" ".join(args[1:]))
elif args[0] == "add" and len(args) >= 7: cmd_add(*args[1:7])
elif args[0] == "top":   cmd_top(int(args[1]) if len(args) > 1 else 10)
elif args[0] == "stats": cmd_stats()
else: print(__doc__)
'''

# ══════════════════════════════════════════════════════════════════════════════
# 6. State Management — STATE.md for session continuity
# ══════════════════════════════════════════════════════════════════════════════
STATE_SCRIPT = r'''#!/usr/bin/env python3
"""
State Manager — save/restore agent session context
Usage:
  state.py save <session_id> <context_json>
  state.py load <session_id>
  state.py list
  state.py clean   (remove states older than 7 days)
"""
import sys, os, json
from datetime import datetime, timedelta

STATE_DIR = "/root/.openclaw/workspace/state"
os.makedirs(STATE_DIR, exist_ok=True)

def cmd_save(session_id, context_raw):
    try:
        context = json.loads(context_raw)
    except:
        context = {"raw": context_raw}
    state = {
        "session_id": session_id,
        "saved_at": datetime.now().isoformat(),
        "context": context,
    }
    path = f"{STATE_DIR}/{session_id}.json"
    with open(path, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    print(f"State saved: {session_id}")

def cmd_load(session_id):
    path = f"{STATE_DIR}/{session_id}.json"
    if not os.path.exists(path):
        print(f"No state found: {session_id}"); return
    state = json.load(open(path))
    print(f"State: {session_id} (saved {state['saved_at'][:16]})")
    print(json.dumps(state["context"], ensure_ascii=False, indent=2))

def cmd_list():
    files = [f for f in os.listdir(STATE_DIR) if f.endswith(".json")]
    if not files:
        print("No saved states"); return
    print(f"Saved states ({len(files)}):")
    for f in sorted(files):
        state = json.load(open(f"{STATE_DIR}/{f}"))
        print(f"  {state['session_id']:30} saved: {state['saved_at'][:16]}")

def cmd_clean():
    cutoff = datetime.now() - timedelta(days=7)
    removed = 0
    for f in os.listdir(STATE_DIR):
        if not f.endswith(".json"): continue
        path = f"{STATE_DIR}/{f}"
        state = json.load(open(path))
        saved = datetime.fromisoformat(state["saved_at"])
        if saved < cutoff:
            os.remove(path)
            removed += 1
    print(f"Cleaned {removed} old states (> 7 days)")

cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
if cmd == "save" and len(sys.argv) > 3:  cmd_save(sys.argv[2], sys.argv[3])
elif cmd == "load" and len(sys.argv) > 2: cmd_load(sys.argv[2])
elif cmd == "list":  cmd_list()
elif cmd == "clean": cmd_clean()
else: print(__doc__)
'''

# ══════════════════════════════════════════════════════════════════════════════
# Build everything
# ══════════════════════════════════════════════════════════════════════════════
files = {
    # 1. Core generator — rewritten for LLM
    f"{BASE}/skills/game-generator/scripts/generate_game.py": GENERATE_GAME,

    # 2. Memory/RAG
    f"{BASE}/skills/user-memory/SKILL.md": USER_MEMORY_SKILL,
    f"{BASE}/skills/user-memory/scripts/memory.py": USER_MEMORY_SCRIPT,

    # 3. Observability
    f"{BASE}/skills/observability/SKILL.md": OBSERVABILITY_SKILL,
    f"{BASE}/skills/observability/scripts/stats.py": OBSERVABILITY_SCRIPT,

    # 4. Rate limiting
    f"{BASE}/skills/rate-limiter/scripts/rate_limit.py": RATE_LIMIT_SCRIPT,

    # 5. Game library/cache
    f"{BASE}/skills/game-library/SKILL.md": GAME_LIBRARY_SKILL,
    f"{BASE}/skills/game-library/scripts/library.py": GAME_LIBRARY_SCRIPT,

    # 6. State management
    f"{BASE}/skills/pause/scripts/state.py": STATE_SCRIPT,
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    os.chmod(path, 0o755)
    print(f"OK  {path.replace(BASE+'/', '')}")

# Create memory and state dirs
for d in [f"{BASE}/memory/users", f"{BASE}/state"]:
    os.makedirs(d, exist_ok=True)
    print(f"DIR {d.replace(BASE+'/', '')}")

print(f"\n{'='*55}")
print(f"  GameForge — Full System Ready!")
print(f"{'='*55}")
print(f"  generate_game.py  → LLM-based, no templates")
print(f"  user-memory       → RAG per VK user_id")
print(f"  observability     → token + cost tracking")
print(f"  rate-limiter      → {60}s cooldown, max {5} concurrent")
print(f"  game-library      → catalog + search + cache")
print(f"  state manager     → pause/resume sessions")
print(f"{'='*55}")
print(f"\nNext step: set MINIMAX_API_KEY and test!")
print(f"  export MINIMAX_API_KEY=your_key")
print(f"  python3 {BASE}/skills/game-generator/scripts/generate_game.py 'snake game' 'Змейка' cyberpunk /tmp/test")
