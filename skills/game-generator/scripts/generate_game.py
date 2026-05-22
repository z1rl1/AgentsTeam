#!/usr/bin/env python3
"""
GameForge ? LLM Game Generator v3
Usage: python3 generate_game.py "<description>" "<title>" "<theme>" "<output_dir>" [user_id]

Calls LLM API, extracts a single-file HTML5 game, runs strict quality checks,
and retries once with targeted feedback before accepting the result.
"""
import sys, os, json, re, time, subprocess
from pathlib import Path
import urllib.request, urllib.error
import socket

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]


def load_env_file(path):
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_env_file(WORKSPACE_ROOT / ".env")

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")
MODEL = os.environ.get("GAMEFORGE_MODEL", "MiniMax-M2.7")
MAX_TOKENS = int(os.environ.get("GAMEFORGE_MAX_TOKENS", "60000"))
QUALITY_THRESHOLD = int(os.environ.get("GAMEFORGE_QUALITY_THRESHOLD", "85"))
MAX_ATTEMPTS = int(os.environ.get("GAMEFORGE_MAX_ATTEMPTS", "2"))
MINIMAX_TIMEOUT_SECONDS = int(os.environ.get("MINIMAX_TIMEOUT_SECONDS", "180"))

THEME_COLORS = {
    "cyberpunk": {"bg": "#0a0010", "primary": "#ff00ff", "secondary": "#00ffff", "text": "#ffffff", "accent": "#ff006e"},
    "space": {"bg": "#000820", "primary": "#4488ff", "secondary": "#ffcc00", "text": "#ffffff", "accent": "#00aaff"},
    "retro": {"bg": "#1a0a00", "primary": "#ff6600", "secondary": "#cc4400", "text": "#ffcc00", "accent": "#ff9900"},
    "neon": {"bg": "#000000", "primary": "#00ff41", "secondary": "#00cc33", "text": "#00ff41", "accent": "#39ff14"},
    "minimal": {"bg": "#0d1117", "primary": "#ff4444", "secondary": "#cc0000", "text": "#ffffff", "accent": "#ff6666"},
}

BASE_PROMPT = """You are GameForge, a senior HTML5 arcade developer. Generate a unique complete game for this exact user request.

User request: {description}
Title: {title}
Theme: {theme}
Colors: bg={bg}, primary={primary}, secondary={secondary}, accent={accent}, text={text}

{user_constraints}
{prompt_improvements}
{retry_feedback}

Goal: a polished, varied, playable HTML5 arcade game. Do NOT make a tiny prototype or generic placeholder.

Hard requirements:
- Return one complete HTML file only, starting with <!DOCTYPE html>.
- Inline CSS and JavaScript only. No CDN, no external files, no alert/prompt/confirm.
- Canvas renderer, responsive full-screen presentation, internal resolution at least 960x540.
- requestAnimationFrame loop with deltaTime.
- Start screen, live HUD, score/objective, game over or win state, restart.
- Keyboard controls appropriate to the genre.
- Procedural visuals with layered background, styled sprites, animation, particles or hit effects.
- Real gameplay from the request: enemies/obstacles/goals/progression, not just movement.
- Tune the first 30 seconds to be playable, readable, and fun.
- Use Russian UI text if the user wrote Russian.
- Keep code compact but complete: usually 250-600 lines.

Genre requirements:
{genre_requirements}

Visual direction:
Use the theme colors, but avoid empty black space. The first screen must look like a real game.

Return ONLY HTML. No Markdown. No explanation. Do not include reasoning or analysis.
"""


def words(*items):
    return [item.encode("utf-8").decode("unicode_escape") for item in items]


def genre_requirements(description):
    d = description.lower()
    blocks = []
    platform_words = words("\\u043f\\u043b\\u0430\\u0442\\u0444\\u043e\\u0440\\u043c", "\\u0431\\u0430\\u043d\\u0434\\u0438\\u0442", "\\u0443\\u0434\\u0430\\u0440", "\\u0433\\u043e\\u0440\\u043e\\u0434", "\\u0433\\u0435\\u0440\\u043e\\u0439") + ["platform", "beat", "punch", "street", "hero"]
    snake_words = words("\\u0437\\u043c\\u0435\\u0439") + ["snake"]
    tetris_words = words("\\u0442\\u0435\\u0442\\u0440\\u0438\\u0441") + ["tetris"]
    shooter_words = words("\\u0441\\u0442\\u0440\\u0435\\u043b", "\\u0437\\u043e\\u043c\\u0431\\u0438") + ["shooter", "zombie", "shoot"]
    racing_words = words("\\u0433\\u043e\\u043d\\u043a", "\\u043c\\u0430\\u0448\\u0438\\u043d") + ["racing", "car"]
    clicker_words = words("\\u043a\\u043b\\u0438\\u043a\\u0435\\u0440") + ["clicker"]
    puzzle_words = words("\\u0433\\u043e\\u043b\\u043e\\u0432\\u043e\\u043b\\u043e\\u043c") + ["puzzle", "match", "2048"]

    if any(w in d for w in platform_words):
        blocks.append("""Platformer / beat-em-up:
- Side-scrolling city or level with camera following the player and a world wider than the viewport.
- Player can walk/run, jump/fall, and punch/attack with visible animation states.
- Multiple enemies with simple AI, hit points, knockback, attack cooldowns, and defeat feedback.
- Combat feedback: hit sparks, screen shake or flash, health/lives, score/combo rewards.
- Platforms/streets/rooftops/obstacles and at least several background details.""")
    if any(w in d for w in snake_words):
        blocks.append("""Snake:
- Large readable board, animated snake body, food pickup effects, speed progression, obstacles or powerups.""")
    if any(w in d for w in tetris_words):
        blocks.append("""Tetris:
- 10x20 board, falling pieces, rotation, line clearing, next preview, scoring, speed progression.""")
    if any(w in d for w in shooter_words):
        blocks.append("""Shooter:
- Moving enemies, projectiles, firing controls, health/ammo or cooldown, waves/spawns, particles.""")
    if any(w in d for w in racing_words):
        blocks.append("""Racing:
- Scrolling track/road, acceleration, steering physics, obstacles/opponents, distance/lap progress.""")
    if any(w in d for w in clicker_words):
        blocks.append("""Clicker:
- Upgrades, animated click feedback, auto-income/progression goals, satisfying UI.""")
    if any(w in d for w in puzzle_words):
        blocks.append("""Puzzle:
- Clear board state, valid move feedback, scoring/progress, win/loss conditions, tile animations.""")
    if not blocks:
        blocks.append("Infer the genre from the request and implement at least three concrete mechanics from the user's words.")
    return "\n\n".join(blocks)



def get_user_constraints(user_id):
    if not user_id:
        return ""
    script = WORKSPACE_ROOT / "skills/feedback/scripts/feedback.py"
    if not script.exists():
        return ""
    try:
        result = subprocess.run(["python3", str(script), "get", user_id], capture_output=True, text=True, timeout=5)
        out = result.stdout.strip()
        if out and out != "NO_CONSTRAINTS":
            return f"\nUser-specific constraints:\n{out}\n"
    except Exception:
        pass
    return ""


def get_prompt_improvements():
    script = WORKSPACE_ROOT / "skills/prompt-optimizer/scripts/prompt_optimizer.py"
    if not script.exists():
        return ""
    try:
        result = subprocess.run(["python3", str(script), "best-prompt"], capture_output=True, text=True, timeout=5)
        out = result.stdout.strip()
        if out and out != "NO_IMPROVEMENTS":
            return f"\nLearned improvements from previous games:\n{out}\n"
    except Exception:
        pass
    return ""


def minimax_model_name():
    model = os.environ.get("GAMEFORGE_MODEL") or os.environ.get("MINIMAX_TEXT_MODEL") or "MiniMax-M2.7"
    model = model.replace("minimax/", "")
    if model in {"MiniMax-Text-01", "MiniMax-Text"}:
        model = "MiniMax-M2.7"
    return model


def with_ipv4_dns(fn):
    original_getaddrinfo = socket.getaddrinfo

    def ipv4_getaddrinfo(*args, **kwargs):
        results = original_getaddrinfo(*args, **kwargs)
        ipv4 = [item for item in results if item[0] == socket.AF_INET]
        return ipv4 or results

    socket.getaddrinfo = ipv4_getaddrinfo
    try:
        return fn()
    finally:
        socket.getaddrinfo = original_getaddrinfo


def call_minimax(prompt):
    url = os.environ.get("MINIMAX_API_URL", "https://api.minimax.io/v1/chat/completions")
    data = json.dumps({
        "model": minimax_model_name(),
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": MAX_TOKENS,
        "temperature": 0.72,
        "stream": False,
        "reasoning_split": True,
    }).encode()
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json",
    })

    def do_request():
        with urllib.request.urlopen(req, timeout=MINIMAX_TIMEOUT_SECONDS) as r:
            return json.loads(r.read())

    resp = with_ipv4_dns(do_request)
    base_resp = resp.get("base_resp") or {}
    if base_resp.get("status_code") not in (None, 0):
        raise RuntimeError(f"MiniMax API error {base_resp.get('status_code')}: {base_resp.get('status_msg')}")
    choices = resp.get("choices") or []
    if not choices:
        raise RuntimeError(f"MiniMax response has no choices. Keys: {sorted(resp.keys())}")
    message = choices[0].get("message") or {}
    content = message.get("content") or ""
    if not content.strip():
        finish_reason = choices[0].get("finish_reason")
        details = (resp.get("usage") or {}).get("completion_tokens_details") or {}
        reasoning_tokens = details.get("reasoning_tokens", 0)
        raise RuntimeError(f"MiniMax returned empty content (finish={finish_reason}, reasoning_tokens={reasoning_tokens}, max_tokens={MAX_TOKENS})")
    return content, resp.get("usage", {})


def call_openrouter(prompt, model):
    url = "https://openrouter.ai/api/v1/chat/completions"
    data = json.dumps({
        "model": model.replace("openrouter/", ""),
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": MAX_TOKENS,
        "temperature": 0.72,
    }).encode()
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://gameforge.vk",
        "X-Title": "GameForge VK",
    })
    with urllib.request.urlopen(req, timeout=180) as r:
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
    match = re.search(r"```(?:html)?\s*(<!DOCTYPE.*?</html>)\s*```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r"(<!DOCTYPE html.*?</html>)", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1)
    if text.strip().lower().startswith("<!doctype"):
        return text.strip()
    return None


def log_generation(slug, model, usage, success, duration_sec, score=None):
    log_dir = WORKSPACE_ROOT / "hooks/logs"
    log_dir.mkdir(parents=True, exist_ok=True)
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
        "score": score,
        "duration_sec": round(duration_sec, 2),
    }
    date = datetime.now().strftime("%Y-%m-%d")
    with (log_dir / f"llm-usage-{date}.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def record_quality(slug, score, theme, game_type):
    script = WORKSPACE_ROOT / "skills/prompt-optimizer/scripts/prompt_optimizer.py"
    if script.exists():
        try:
            subprocess.run(["python3", str(script), "record", slug, str(score), theme, game_type], capture_output=True, timeout=5)
        except Exception:
            pass


def run_playtester(slug):
    playtester = WORKSPACE_ROOT / "skills/game-playtester/scripts/game_playtester.py"
    if not playtester.exists():
        return 0, "Playtester missing"
    result = subprocess.run(["python3", str(playtester), slug], capture_output=True, text=True, timeout=45)
    output = (result.stdout or "") + (result.stderr or "")
    m = re.search(r"\((\d+)%\)", output)
    return (int(m.group(1)) if m else 0), output


def write_metadata(output_dir, description, title, theme, user_id):
    metadata = {
        "description": description,
        "title": title,
        "theme": theme,
        "user_id": user_id,
        "created_at": int(time.time()),
        "quality_threshold": QUALITY_THRESHOLD,
    }
    Path(output_dir, "gameforge.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_prompt(description, title, theme, user_id=None, retry_feedback=""):
    colors = THEME_COLORS.get(theme, THEME_COLORS["minimal"])
    return BASE_PROMPT.format(
        description=description,
        title=title,
        theme=theme,
        user_constraints=get_user_constraints(user_id),
        prompt_improvements=get_prompt_improvements(),
        genre_requirements=genre_requirements(description),
        retry_feedback=retry_feedback,
        **colors,
    )


def generate(description, title, theme, output_dir, user_id=None):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    slug = output_path.name
    write_metadata(output_path, description, title, theme, user_id)

    print(f"Generating: {title} ({theme})")
    print(f"Description: {description}")
    print("-" * 50)

    best_score = -1
    best_html = None
    best_usage = {}
    retry_feedback = ""
    total_start = time.time()

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"Attempt {attempt}/{MAX_ATTEMPTS}")
        prompt = build_prompt(description, title, theme, user_id, retry_feedback)
        t0 = time.time()
        try:
            raw, usage = call_llm(prompt)
            html = extract_html(raw)
            duration = time.time() - t0
            if not html:
                preview = raw[:500].replace("\n", " ")
                print(f"  No complete HTML found. Response preview: {preview}")
                retry_feedback = "Previous attempt failed: response did not contain a complete <!DOCTYPE html> document. Return only one complete HTML file."
                log_generation(slug, minimax_model_name() if MINIMAX_API_KEY else MODEL, usage, False, duration, 0)
                continue

            out_file = output_path / "index.html"
            out_file.write_text(html, encoding="utf-8")
            score, report = run_playtester(slug)
            lines = html.count("\n")
            size_kb = out_file.stat().st_size // 1024
            print(f"  Size: {size_kb}KB | Lines: {lines} | Score: {score}% | Time: {duration:.1f}s")
            print(report)

            if score > best_score:
                best_score = score
                best_html = html
                best_usage = usage

            if score >= QUALITY_THRESHOLD:
                record_quality(slug, score, theme, description.split()[0] if description.split() else "custom")
                log_generation(slug, minimax_model_name() if MINIMAX_API_KEY else MODEL, usage, True, time.time() - total_start, score)
                print(f"ACCEPTED: {score}% >= {QUALITY_THRESHOLD}%")
                return True

            retry_feedback = (
                "Previous attempt was rejected by QA. Fix every issue below before returning the new HTML. "
                "Make the canvas larger, visuals richer, gameplay deeper, and genre mechanics explicit.\n"
                + report[-4000:]
            )
        except Exception as e:
            duration = time.time() - t0
            print(f"ERROR: {e}")
            retry_feedback = f"Previous attempt failed with runtime error: {e}. Return a complete robust HTML game."
            log_generation(slug, MODEL, {}, False, duration, 0)

    if best_html:
        (output_path / "index.html").write_text(best_html, encoding="utf-8")
    record_quality(slug, max(best_score, 0), theme, description.split()[0] if description.split() else "custom")
    log_generation(slug, minimax_model_name() if MINIMAX_API_KEY else MODEL, best_usage, False, time.time() - total_start, max(best_score, 0))
    print(f"REJECTED: best score {best_score}% < {QUALITY_THRESHOLD}%")
    return False


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python3 generate_game.py <description> <title> <theme> <output_dir> [user_id]")
        sys.exit(1)
    description, title, theme, output_dir = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    user_id = sys.argv[5] if len(sys.argv) > 5 else None
    ok = generate(description, title, theme, output_dir, user_id)
    sys.exit(0 if ok else 1)
