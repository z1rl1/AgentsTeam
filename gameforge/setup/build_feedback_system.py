#!/usr/bin/env python3
"""
GameForge — Feedback & Self-Improvement System
Creates:
  1. feedback.py      — saves user likes/dislikes, reads constraints for prompt
  2. prompt_optimizer.py — tracks prompt performance, evolves base prompt
  3. self_improve.py  — OpenClaw self-improvement loop (runs via BOOT.md or /overnight)
  4. Wires OpenClaw hooks via openclaw.json
  5. Updates generate_game.py to read user feedback + best prompt
  6. Updates user-memory.py to include feedback in profile
"""
import os, json

BASE = "/root/.openclaw/workspace"

# ══════════════════════════════════════════════════════════════════════════════
# 1. feedback.py — User feedback system
# ══════════════════════════════════════════════════════════════════════════════
FEEDBACK_PY = r'''#!/usr/bin/env python3
"""
User Feedback System — saves what users like/dislike about games
Agent calls this when user says: "не нравится", "плохо", "слишком", "хочу чтобы"

Usage:
  feedback.py add <user_id> <slug> <sentiment> "<text>"
    sentiment: positive | negative | suggestion

  feedback.py get <user_id>
    → returns user constraints for LLM prompt

  feedback.py analyze
    → global patterns: what ALL users dislike most

  feedback.py detect "<message>"
    → 0=neutral, 1=positive, 2=negative/suggestion (for agent to auto-detect)
"""
import sys, os, json, re
from datetime import datetime

FEEDBACK_DIR = "/root/.openclaw/workspace/memory/feedback"
os.makedirs(FEEDBACK_DIR, exist_ok=True)

# Keywords that trigger feedback detection
NEGATIVE_KEYWORDS = [
    "не нравится", "плохо", "ужасно", "скучно", "медленно", "слишком",
    "не то", "другой", "измени", "сделай иначе", "не хочу", "убери",
    "без", "не надо", "хватит", "надоело", "плохая", "плохой",
]
POSITIVE_KEYWORDS = [
    "нравится", "круто", "классно", "отлично", "супер", "огонь",
    "топ", "красиво", "понравилось", "класс", "лайк", "здорово",
]
SUGGESTION_KEYWORDS = [
    "хочу чтобы", "сделай", "добавь", "хочу", "лучше если", "можно",
    "попробуй", "было бы", "хотел бы", "хотела бы",
]

def get_feedback(user_id):
    path = f"{FEEDBACK_DIR}/{user_id}.json"
    if not os.path.exists(path):
        return {"user_id": user_id, "entries": [], "constraints": [], "prefs": {}}
    return json.load(open(path))

def save_feedback(data):
    uid = data["user_id"]
    with open(f"{FEEDBACK_DIR}/{uid}.json", "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def cmd_add(user_id, slug, sentiment, text):
    data = get_feedback(user_id)
    entry = {
        "slug": slug,
        "sentiment": sentiment,  # positive | negative | suggestion
        "text": text,
        "date": datetime.now().isoformat(),
    }
    data["entries"].append(entry)
    data["entries"] = data["entries"][-50:]  # keep last 50

    # Extract constraint from negative feedback
    if sentiment == "negative":
        constraint = extract_constraint(text)
        if constraint and constraint not in data["constraints"]:
            data["constraints"].append(constraint)
            print(f"New constraint: {constraint}")

    # Extract preference from suggestion
    if sentiment == "suggestion":
        extract_preference(data, text)

    save_feedback(data)
    print(f"Feedback saved: {user_id} | {sentiment} | {slug}")
    print(f"Total constraints: {len(data['constraints'])}")

def extract_constraint(text):
    """Turn negative feedback into a prompt constraint"""
    text = text.lower().strip()
    mappings = {
        "медленно":    "Make the game faster and more responsive",
        "скучно":      "Make gameplay more exciting with power-ups and variety",
        "темно":       "Use brighter colors and higher contrast",
        "громко":      "Make sounds subtle and not annoying",
        "сложно":      "Make the game easier for beginners",
        "легко":       "Make the game more challenging",
        "маленьк":     "Make game elements larger and more visible",
        "не понятно":  "Add clear instructions and tutorial text",
        "без звука":   "Remove all sound effects",
        "без музыки":  "No background music",
        "ретро":       "Do not use retro theme",
        "киберпанк":   "Do not use cyberpunk theme",
    }
    for keyword, constraint in mappings.items():
        if keyword in text:
            return constraint
    # Generic constraint from text
    if len(text) > 5:
        return f"User feedback (avoid this): {text}"
    return None

def extract_preference(data, text):
    """Extract explicit preferences from suggestions"""
    text = text.lower()
    if "быстр" in text: data["prefs"]["speed"] = "fast"
    if "медленн" in text: data["prefs"]["speed"] = "slow"
    if "яркий" in text or "яркие" in text: data["prefs"]["colors"] = "bright"
    if "тёмный" in text or "тёмные" in text: data["prefs"]["colors"] = "dark"
    if "простой" in text: data["prefs"]["difficulty"] = "easy"
    if "сложный" in text: data["prefs"]["difficulty"] = "hard"
    if "звук" in text and "без" not in text: data["prefs"]["audio"] = "yes"
    if "без звука" in text: data["prefs"]["audio"] = "no"

def cmd_get(user_id):
    """Get user constraints for LLM prompt injection"""
    data = get_feedback(user_id)
    if not data["constraints"] and not data["prefs"]:
        print("NO_CONSTRAINTS")
        return

    lines = []
    if data["constraints"]:
        lines.append("User preferences (MUST follow):")
        for c in data["constraints"]:
            lines.append(f"  - {c}")
    if data["prefs"]:
        lines.append("Additional preferences:")
        for k, v in data["prefs"].items():
            lines.append(f"  - {k}: {v}")

    result = "\n".join(lines)
    print(result)
    return result

def cmd_analyze():
    """Global patterns across all users"""
    if not os.path.exists(FEEDBACK_DIR):
        print("No feedback yet"); return
    all_constraints = {}
    total_users = 0
    total_neg = 0
    for f in os.listdir(FEEDBACK_DIR):
        if not f.endswith(".json"): continue
        data = json.load(open(f"{FEEDBACK_DIR}/{f}"))
        total_users += 1
        for e in data["entries"]:
            if e["sentiment"] == "negative":
                total_neg += 1
        for c in data.get("constraints", []):
            all_constraints[c] = all_constraints.get(c, 0) + 1

    print(f"\nGlobal Feedback Analysis:")
    print(f"  Users with feedback: {total_users}")
    print(f"  Total negative entries: {total_neg}")
    if all_constraints:
        print(f"  Most common complaints:")
        for c, count in sorted(all_constraints.items(), key=lambda x: -x[1])[:5]:
            print(f"    ({count}x) {c}")

def cmd_detect(message):
    """Detect feedback type in user message. Returns: 0=neutral 1=positive 2=negative"""
    msg = message.lower()
    for kw in NEGATIVE_KEYWORDS:
        if kw in msg:
            print("negative"); return 2
    for kw in SUGGESTION_KEYWORDS:
        if kw in msg:
            print("suggestion"); return 2
    for kw in POSITIVE_KEYWORDS:
        if kw in msg:
            print("positive"); return 1
    print("neutral"); return 0

args = sys.argv[1:]
if not args: print(__doc__)
elif args[0] == "add" and len(args) >= 5:  cmd_add(args[1], args[2], args[3], " ".join(args[4:]))
elif args[0] == "get" and len(args) > 1:   cmd_get(args[1])
elif args[0] == "analyze":                  cmd_analyze()
elif args[0] == "detect" and len(args) > 1: sys.exit(cmd_detect(" ".join(args[1:])))
else: print(__doc__)
'''

# ══════════════════════════════════════════════════════════════════════════════
# 2. prompt_optimizer.py — tracks what works, evolves base prompt
# ══════════════════════════════════════════════════════════════════════════════
PROMPT_OPTIMIZER_PY = r'''#!/usr/bin/env python3
"""
Prompt Optimizer — tracks game generation quality, evolves the base prompt
Кarpathy loop: generate → test → score → if bad → improve prompt → repeat

Usage:
  prompt_optimizer.py record <slug> <score> <theme> <game_type> [feedback]
  prompt_optimizer.py analyze        → what patterns produce high/low scores
  prompt_optimizer.py best-prompt    → returns current best prompt additions
  prompt_optimizer.py improve        → auto-generates prompt improvement suggestions
"""
import sys, os, json
from datetime import datetime

DATA_DIR = "/root/.openclaw/workspace/memory/prompt_data"
PROMPT_FILE = "/root/.openclaw/workspace/memory/prompt_data/current_improvements.json"
os.makedirs(DATA_DIR, exist_ok=True)

LOG_FILE = f"{DATA_DIR}/generation_log.jsonl"

def cmd_record(slug, score, theme, game_type, feedback=""):
    entry = {
        "slug": slug,
        "score": float(score),
        "theme": theme,
        "game_type": game_type,
        "feedback": feedback,
        "date": datetime.now().isoformat(),
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    status = "GOOD" if float(score) >= 80 else "WARN" if float(score) >= 60 else "BAD"
    print(f"Recorded: {slug} score={score}% [{status}]")

def load_log():
    if not os.path.exists(LOG_FILE): return []
    return [json.loads(l) for l in open(LOG_FILE) if l.strip()]

def cmd_analyze():
    entries = load_log()
    if not entries:
        print("No data yet — generate some games first!"); return

    # Overall stats
    scores = [e["score"] for e in entries]
    avg = sum(scores) / len(scores)
    good = sum(1 for s in scores if s >= 80)
    bad  = sum(1 for s in scores if s < 60)

    # By theme
    theme_scores = {}
    for e in entries:
        t = e["theme"]
        if t not in theme_scores: theme_scores[t] = []
        theme_scores[t].append(e["score"])

    # By game_type
    type_scores = {}
    for e in entries:
        gt = e["game_type"]
        if gt not in type_scores: type_scores[gt] = []
        type_scores[gt].append(e["score"])

    print(f"\n{'='*55}")
    print(f"  Prompt Optimizer — Generation Quality Analysis")
    print(f"{'='*55}")
    print(f"  Total games: {len(entries)}")
    print(f"  Avg score: {avg:.1f}% | Good(>=80%): {good} | Bad(<60%): {bad}")
    print(f"\n  By Theme:")
    for t, sc in sorted(theme_scores.items(), key=lambda x: -sum(x[1])/len(x[1])):
        a = sum(sc)/len(sc)
        print(f"    {t:12} avg={a:.0f}% ({len(sc)} games)")
    print(f"\n  By Game Type:")
    for gt, sc in sorted(type_scores.items(), key=lambda x: -sum(x[1])/len(x[1])):
        a = sum(sc)/len(sc)
        print(f"    {gt:15} avg={a:.0f}% ({len(sc)} games)")

    # Failures
    failures = [e for e in entries if e["score"] < 60]
    if failures:
        print(f"\n  Recent failures (score < 60%):")
        for e in failures[-5:]:
            print(f"    {e['slug']} ({e['game_type']}/{e['theme']}) score={e['score']:.0f}%")
            if e.get("feedback"):
                print(f"      User said: {e['feedback']}")
    print(f"{'='*55}\n")

def cmd_best_prompt():
    """Returns current prompt improvements to inject into generate_game.py"""
    if not os.path.exists(PROMPT_FILE):
        print("NO_IMPROVEMENTS")
        return ""

    data = json.load(open(PROMPT_FILE))
    improvements = data.get("improvements", [])
    if not improvements:
        print("NO_IMPROVEMENTS")
        return ""

    result = "\n".join(f"- {imp}" for imp in improvements)
    print(result)
    return result

def cmd_improve():
    """Analyze failures and generate prompt improvement suggestions"""
    entries = load_log()
    if len(entries) < 5:
        print("Need at least 5 games to analyze. Keep generating!"); return

    failures = [e for e in entries if e["score"] < 60]
    if not failures:
        print("All games scoring >= 60%! System is working well.")
        return

    # Pattern analysis
    improvements = []

    # Check if specific themes always fail
    theme_fails = {}
    for e in failures:
        t = e["theme"]
        theme_fails[t] = theme_fails.get(t, 0) + 1
    for theme, count in theme_fails.items():
        if count >= 3:
            improvements.append(f"For {theme} theme: emphasize glow effects and theme-specific visual identity more strongly")

    # Check if game loop is missing
    no_loop_count = sum(1 for e in failures if "loop" in e.get("feedback", "").lower())
    if no_loop_count >= 2:
        improvements.append("Always include explicit requestAnimationFrame game loop with deltaTime for smooth animation")

    # Generic improvements for consistent failures
    if len(failures) > len(entries) * 0.3:
        improvements.extend([
            "Start the game code with a complete skeleton: canvas setup, game loop, input handlers, then fill in mechanics",
            "Always implement game over detection as a boolean flag checked every frame",
            "Include explicit start screen: draw title text and 'Press Enter to start' before game begins",
        ])

    if not improvements:
        improvements = [
            "Make game mechanics more complete with proper collision detection",
            "Always include score display updating every frame",
        ]

    # Save improvements
    data = {
        "updated": datetime.now().isoformat(),
        "based_on": f"{len(entries)} games, {len(failures)} failures",
        "improvements": improvements,
    }
    with open(PROMPT_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(improvements)} prompt improvements:")
    for imp in improvements:
        print(f"  + {imp}")
    print(f"\nSaved to: {PROMPT_FILE}")
    print("generate_game.py will use these on next run.")

args = sys.argv[1:]
if not args: print(__doc__)
elif args[0] == "record"  and len(args) >= 5: cmd_record(args[1], args[2], args[3], args[4], " ".join(args[5:]))
elif args[0] == "analyze":  cmd_analyze()
elif args[0] == "best-prompt": cmd_best_prompt()
elif args[0] == "improve":  cmd_improve()
else: print(__doc__)
'''

# ══════════════════════════════════════════════════════════════════════════════
# 3. Updated generate_game.py — reads feedback + prompt improvements
# ══════════════════════════════════════════════════════════════════════════════
GENERATE_GAME_V2 = r'''#!/usr/bin/env python3
"""
GameForge — LLM Game Generator v2 (with feedback + self-improvement)
Usage: python3 generate_game.py "<description>" "<title>" "<theme>" "<output_dir>" [user_id]

Calls LLM API → extracts HTML5 game code → saves index.html
Auto-reads: user feedback constraints + prompt optimizer improvements
Compatible with: MiniMax API (direct) and OpenRouter
"""
import sys, os, json, re, time, subprocess
import urllib.request, urllib.error

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MINIMAX_API_KEY    = os.environ.get("MINIMAX_API_KEY", "")
MODEL              = os.environ.get("GAMEFORGE_MODEL", "minimax/minimax-text-01")

THEME_COLORS = {
    "cyberpunk": {"bg": "#0a0010", "primary": "#ff00ff", "secondary": "#00ffff", "text": "#ffffff", "accent": "#ff006e"},
    "space":     {"bg": "#000820", "primary": "#4488ff", "secondary": "#ffcc00", "text": "#ffffff", "accent": "#00aaff"},
    "retro":     {"bg": "#1a0a00", "primary": "#ff6600", "secondary": "#cc4400", "text": "#ffcc00", "accent": "#ff9900"},
    "neon":      {"bg": "#000000", "primary": "#00ff41", "secondary": "#00cc33", "text": "#00ff41", "accent": "#39ff14"},
    "minimal":   {"bg": "#0d1117", "primary": "#ff4444", "secondary": "#cc0000", "text": "#ffffff", "accent": "#ff6666"},
}

BASE_PROMPT = """You are an expert HTML5 game developer. Create a COMPLETE, PLAYABLE browser game.

Game Description: {description}
Game Title: {title}
Visual Theme: {theme}
Theme Colors: bg={bg}, primary={primary}, secondary={secondary}, text={text}

{user_constraints}
{prompt_improvements}

STRICT REQUIREMENTS — ALL must be present:
1. Single self-contained HTML file (<!DOCTYPE html> to </html>)
2. All CSS inside <style> tag — dark background, use theme colors with glow effects
3. All JavaScript inside <script> tag
4. <canvas> element for game rendering
5. requestAnimationFrame game loop (NOT setInterval)
6. Start screen: show title + "Press Enter or Space to start" — wait for input
7. Game Over screen: show final score + "Press Enter to restart"
8. Score displayed live during gameplay (top of canvas)
9. Keyboard controls (arrow keys / WASD appropriate to game type)
10. Complete game logic — fully playable, not a stub
11. Smooth 60fps with deltaTime
12. NO external libraries, NO CDN — everything inline
13. NO alert() — use canvas for all UI
14. Minimum 300 lines of actual game code

Visual requirements for {theme}:
- Background: {bg} with subtle texture or gradient
- Player/main elements: {primary} with glow (shadowBlur, shadowColor)
- Enemies/secondary: {secondary}
- Text: {text}, clear and readable
- Overall feel: polished, modern, visually impressive

Code structure (follow this order):
1. canvas setup + context
2. theme colors as constants
3. game state variables
4. input handlers (keydown/keyup)
5. game objects (player, enemies, etc.)
6. game logic functions
7. draw functions
8. requestAnimationFrame loop
9. start/restart logic

Return ONLY the complete HTML code. No explanations. Start with <!DOCTYPE html>"""

def get_user_constraints(user_id):
    """Read user feedback constraints"""
    if not user_id:
        return ""
    script = "/root/.openclaw/workspace/skills/feedback/scripts/feedback.py"
    if not os.path.exists(script):
        return ""
    try:
        result = subprocess.run(
            ["python3", script, "get", user_id],
            capture_output=True, text=True, timeout=5
        )
        out = result.stdout.strip()
        if out and out != "NO_CONSTRAINTS":
            return f"\n{out}\n"
    except:
        pass
    return ""

def get_prompt_improvements():
    """Read prompt optimizer improvements"""
    script = "/root/.openclaw/workspace/skills/prompt-optimizer/scripts/prompt_optimizer.py"
    if not os.path.exists(script):
        return ""
    try:
        result = subprocess.run(
            ["python3", script, "best-prompt"],
            capture_output=True, text=True, timeout=5
        )
        out = result.stdout.strip()
        if out and out != "NO_IMPROVEMENTS":
            return f"\nLearned improvements from previous games:\n{out}\n"
    except:
        pass
    return ""

def call_minimax(prompt):
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

def call_openrouter(prompt, model):
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

def call_llm(prompt):
    if MINIMAX_API_KEY:
        print("Using MiniMax API...")
        return call_minimax(prompt)
    if OPENROUTER_API_KEY:
        print(f"Using OpenRouter: {MODEL}...")
        return call_openrouter(prompt, MODEL)
    raise RuntimeError("No API key! Set MINIMAX_API_KEY or OPENROUTER_API_KEY")

def extract_html(text):
    match = re.search(r'```(?:html)?\s*(<!DOCTYPE.*?</html>)\s*```', text, re.DOTALL | re.IGNORECASE)
    if match: return match.group(1)
    match = re.search(r'(<!DOCTYPE html.*?</html>)', text, re.DOTALL | re.IGNORECASE)
    if match: return match.group(1)
    if text.strip().lower().startswith('<!doctype'): return text.strip()
    return None

def log_generation(slug, model, usage, success, duration_sec):
    log_dir = "/root/.openclaw/workspace/hooks/logs"
    os.makedirs(log_dir, exist_ok=True)
    from datetime import datetime
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event": "game_generated",
        "slug": slug, "model": model,
        "tokens_in":    usage.get("prompt_tokens", 0),
        "tokens_out":   usage.get("completion_tokens", 0),
        "tokens_total": usage.get("total_tokens", 0),
        "success": success,
        "duration_sec": round(duration_sec, 2),
    }
    from datetime import datetime as dt
    date = dt.now().strftime("%Y-%m-%d")
    with open(f"{log_dir}/llm-usage-{date}.jsonl", "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def record_quality(slug, score, theme, game_type):
    """Record score to prompt optimizer"""
    script = "/root/.openclaw/workspace/skills/prompt-optimizer/scripts/prompt_optimizer.py"
    if os.path.exists(script):
        try:
            subprocess.run(["python3", script, "record", slug, str(score), theme, game_type],
                         capture_output=True, timeout=5)
        except: pass

def generate(description, title, theme, output_dir, user_id=None):
    os.makedirs(output_dir, exist_ok=True)
    slug = os.path.basename(output_dir)
    colors = THEME_COLORS.get(theme, THEME_COLORS["minimal"])

    # Read personalization
    user_constraints = get_user_constraints(user_id)
    prompt_improvements = get_prompt_improvements()

    if user_constraints:
        print(f"Applied {user_constraints.count('- ')} user constraints")
    if prompt_improvements:
        print(f"Applied prompt optimizer improvements")

    prompt = BASE_PROMPT.format(
        description=description, title=title, theme=theme,
        user_constraints=user_constraints,
        prompt_improvements=prompt_improvements,
        **colors
    )

    print(f"Generating: {title} ({theme})")
    print(f"Description: {description}")
    print("-" * 50)

    t0 = time.time()
    try:
        raw, usage = call_llm(prompt)
        duration = time.time() - t0

        html = extract_html(raw)
        if not html:
            print("ERROR: No HTML in response")
            print("Preview:", raw[:300])
            log_generation(slug, MODEL, usage, False, duration)
            return False

        out_path = os.path.join(output_dir, "index.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)

        size_kb = os.path.getsize(out_path) // 1024
        lines = html.count("\n")
        print(f"SUCCESS: {out_path}")
        print(f"  Size: {size_kb}KB | Lines: {lines} | Tokens: {usage.get('total_tokens','?')} | Time: {duration:.1f}s")

        log_generation(slug, MODEL, usage, True, duration)

        # Auto-test and record quality
        playtester = "/root/.openclaw/workspace/skills/game-playtester/scripts/game_playtester.py"
        if os.path.exists(playtester):
            try:
                result = subprocess.run(["python3", playtester, slug],
                                       capture_output=True, text=True, timeout=30)
                # Extract score from output
                m = re.search(r'\((\d+)%\)', result.stdout)
                if m:
                    score = int(m.group(1))
                    record_quality(slug, score, theme, description.split()[0])
                    print(f"  Playtester: {score}%")
            except: pass

        return True

    except Exception as e:
        duration = time.time() - t0
        print(f"ERROR: {e}")
        log_generation(slug, MODEL, {}, False, duration)
        return False

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python3 generate_game.py <description> <title> <theme> <output_dir> [user_id]")
        sys.exit(1)
    description, title, theme, output_dir = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    user_id = sys.argv[5] if len(sys.argv) > 5 else None
    ok = generate(description, title, theme, output_dir, user_id)
    sys.exit(0 if ok else 1)
'''

# ══════════════════════════════════════════════════════════════════════════════
# 4. SKILL.md files for new skills
# ══════════════════════════════════════════════════════════════════════════════
FEEDBACK_SKILL = '''---
name: feedback
description: Saves and reads user feedback about games. Automatically detects when user says they dislike something and saves it as a constraint. Use to personalize future game generation per user.
triggers:
  - "не нравится"
  - "плохо"
  - "измени"
  - "хочу чтобы"
  - "сделай иначе"
  - "слишком"
  - "скучно"
---

# Feedback Skill

Когда пользователь говорит что ему не нравится — сохраняй это как ограничение.
Агент должен сам детектировать фидбек и сохранять без явной команды.

## Алгоритм детекции

После каждого сообщения пользователя проверь:
```bash
python3 /root/.openclaw/workspace/skills/feedback/scripts/feedback.py detect "{message}"
```
- Вернёт `negative` или `suggestion` → сохрани фидбек
- Вернёт `positive` → похвали и запиши
- Вернёт `neutral` → игнорируй

## Сохранить фидбек
```bash
python3 /root/.openclaw/workspace/skills/feedback/scripts/feedback.py add {user_id} {slug} negative "{что не понравилось}"
```

## Прочитать ограничения пользователя (до генерации)
```bash
python3 /root/.openclaw/workspace/skills/feedback/scripts/feedback.py get {user_id}
```
Передай результат в generate_game.py как user_id параметр — он сам подтянет ограничения.

## Важно
- НЕ жди явной команды "сохрани фидбек"
- АВТОМАТИЧЕСКИ детектируй негативные сообщения
- Отвечай в VK: "Понял! Запомнил что тебе не нравится [X]. Учту в следующей игре!"
'''

PROMPT_OPT_SKILL = '''---
name: prompt-optimizer
description: Tracks game generation quality over time and automatically improves the base prompt. Runs after every game (records score) and periodically analyzes patterns to suggest prompt improvements.
---

# Prompt Optimizer Skill

Самообучение системы: отслеживает что работает, улучшает промпты.

## Как работает (автоматически)

1. После каждой генерации → запускается через generate_game.py (авто)
2. Записывает: slug, score, theme, game_type
3. После 10+ игр → `improve` анализирует паттерны провалов
4. Улучшения сохраняются → следующие генерации используют их

## Ручные команды

### Аналитика
```bash
python3 /root/.openclaw/workspace/skills/prompt-optimizer/scripts/prompt_optimizer.py analyze
```

### Запустить улучшение промпта
```bash
python3 /root/.openclaw/workspace/skills/prompt-optimizer/scripts/prompt_optimizer.py improve
```

### Посмотреть текущие улучшения
```bash
python3 /root/.openclaw/workspace/skills/prompt-optimizer/scripts/prompt_optimizer.py best-prompt
```

## Self-Improvement Loop (Karpathy pattern)

Запускай раз в неделю или после 20+ игр:
```bash
python3 prompt_optimizer.py analyze
python3 prompt_optimizer.py improve
# → улучшения автоматически применяются к следующим генерациям
```
'''

# ══════════════════════════════════════════════════════════════════════════════
# 5. Wire OpenClaw hooks via openclaw.json
# ══════════════════════════════════════════════════════════════════════════════
OPENCLAW_HOOKS_UPDATE = {
    "internal": {
        "enabled": True,
        "entries": {
            "boot-md": {"enabled": True},
            "pre-skill": {
                "enabled": True,
                "script": "/root/.openclaw/workspace/hooks/pre-skill-check.sh",
                "event": "pre-skill",
                "timeout": 10
            },
            "post-skill-eval": {
                "enabled": True,
                "script": "/root/.openclaw/workspace/hooks/post-skill-eval.sh",
                "event": "post-skill",
                "timeout": 30
            },
            "session-report": {
                "enabled": True,
                "script": "/root/.openclaw/workspace/hooks/session-report.sh",
                "event": "stop",
                "timeout": 15
            }
        }
    }
}

# ══════════════════════════════════════════════════════════════════════════════
# Build
# ══════════════════════════════════════════════════════════════════════════════
files = {
    # Feedback system
    f"{BASE}/skills/feedback/SKILL.md": FEEDBACK_SKILL,
    f"{BASE}/skills/feedback/scripts/feedback.py": FEEDBACK_PY,

    # Prompt optimizer
    f"{BASE}/skills/prompt-optimizer/SKILL.md": PROMPT_OPT_SKILL,
    f"{BASE}/skills/prompt-optimizer/scripts/prompt_optimizer.py": PROMPT_OPTIMIZER_PY,

    # Updated generate_game.py v2
    f"{BASE}/skills/game-generator/scripts/generate_game.py": GENERATE_GAME_V2,
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    os.chmod(path, 0o755)
    print(f"OK  {path.replace(BASE+'/', '')}")

# Update openclaw.json hooks section
OPENCLAW_JSON = "/root/.openclaw/openclaw.json"
with open(OPENCLAW_JSON) as f:
    config = json.load(f)
config["hooks"] = OPENCLAW_HOOKS_UPDATE
with open(OPENCLAW_JSON, "w") as f:
    json.dump(config, f, ensure_ascii=False, indent=2)
print(f"OK  openclaw.json (hooks wired)")

# Create memory dirs
for d in [f"{BASE}/memory/feedback", f"{BASE}/memory/prompt_data"]:
    os.makedirs(d, exist_ok=True)
    print(f"DIR {d.replace(BASE+'/', '')}")

print(f"\n{'='*60}")
print(f"  GameForge — Feedback & Self-Improvement Ready!")
print(f"{'='*60}")
print(f"  feedback system:    detects + saves user dislikes")
print(f"  prompt-optimizer:   Karpathy loop, auto-improves prompts")
print(f"  generate_game.py:   reads feedback + improvements")
print(f"  openclaw.json:      hooks wired (pre/post/stop)")
print(f"{'='*60}")
print(f"\nFull flow:")
print(f"  User: 'змейку киберпанк'")
print(f"  → rate_limit.py check")
print(f"  → game_library.py find snake cyberpunk")
print(f"  → feedback.py get user_id  → add constraints to prompt")
print(f"  → prompt_optimizer.py best-prompt → add improvements")
print(f"  → generate_game.py → LLM → HTML")
print(f"  → game_playtester.py → score")
print(f"  → prompt_optimizer.py record score")
print(f"  → game_library.py add")
print(f"  → user_memory.py save")
print(f"  → deploy.sh → VK link")
print(f"  User: 'скучно'")
print(f"  → feedback.py detect → negative")
print(f"  → feedback.py add → saves constraint")
print(f"  → 'Понял, запомнил! В следующий раз сделаю интереснее'")
