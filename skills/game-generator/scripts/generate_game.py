#!/usr/bin/env python3
"""
GameForge — LLM Game Generator v2 (with feedback + self-improvement)
Usage: python3 generate_game.py "<description>" "<title>" "<theme>" "<output_dir>" [user_id]

Calls LLM API → extracts HTML5 game code → saves index.html
Auto-reads: user feedback constraints + prompt optimizer improvements
Compatible with: MiniMax API (direct) and OpenRouter
"""
import sys, os, json, re, time, subprocess
import urllib.request, urllib.error

OPENROUTER_API_KEY = os.environ.get(OPENROUTER_API_KEY, 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)
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
