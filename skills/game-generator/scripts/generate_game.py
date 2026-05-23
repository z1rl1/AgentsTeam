#!/usr/bin/env python3
"""
GameForge ? LLM Game Generator v3
Usage: python3 generate_game.py "<description>" "<title>" "<theme>" "<output_dir>" [user_id]

Calls LLM API, extracts a single-file HTML5 game, runs strict quality checks,
and retries once with targeted feedback before accepting the result.
"""
import sys, os, json, re, time, subprocess, base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import urllib.request, urllib.error
import socket
import fcntl
from contextlib import contextmanager

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
MINIMAX_ASSET_TIMEOUT_SECONDS = int(os.environ.get("MINIMAX_ASSET_TIMEOUT_SECONDS", "240"))
GENERATE_ASSETS = os.environ.get("GAMEFORGE_GENERATE_ASSETS", "1").lower() not in {"0", "false", "no", "off"}
REQUIRE_GENERATED_ASSETS = os.environ.get("GAMEFORGE_REQUIRE_GENERATED_ASSETS", "1").lower() not in {"0", "false", "no", "off"}
ASSET_WORKERS = int(os.environ.get("GAMEFORGE_ASSET_WORKERS", "4"))
GENERATION_LOCK_TIMEOUT_SECONDS = int(os.environ.get("GAMEFORGE_LOCK_TIMEOUT_SECONDS", "900"))
if REQUIRE_GENERATED_ASSETS and not GENERATE_ASSETS:
    print("GAMEFORGE_GENERATE_ASSETS=0 ignored because generated assets are required")
    GENERATE_ASSETS = True

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
{asset_instructions}

Goal: a polished, varied, playable HTML5 arcade game. Do NOT make a tiny prototype or generic placeholder.

Hard requirements:
- Return one complete index.html document only, starting with <!DOCTYPE html>.
- Inline CSS and JavaScript. Local generated files under assets/ are allowed and expected. No CDN, no remote URLs, no alert/prompt/confirm.
- Canvas renderer, responsive full-screen presentation, internal resolution at least 960x540.
- requestAnimationFrame loop with deltaTime.
- Start screen, live HUD, score/objective, game over or win state, restart.
- Keyboard controls appropriate to the genre.
- Generated bitmap assets must be used for the main background, title/menu art, player, enemies, vehicles, props, or other primary visible subjects when asset files are provided.
- Procedural visuals may add particles, lighting, UI, hit effects, and fallback details, but primary actors must not be simple colored rectangles.
- Build a rich scene, not a sparse prototype: detailed background, foreground details, multiple object types, visual polish, and no large empty margins.
- Real gameplay from the request: enemies/obstacles/goals/progression, not just movement.
- If the user asks for a game like a known title, implement the core mechanics and feel in an original way; do not make a shallow visual imitation.
- Include multiple interacting systems: player input, physics/movement, collisions, scoring, progression, feedback effects, and several entities.
- Tune the first 30 seconds to be playable, readable, and fun.
- Use Russian UI text if the user wrote Russian.
- Keep code complete and substantial: usually 450-1000 lines for visual arcade games. Do not optimize by removing polish.

Genre requirements:
{genre_requirements}

Art direction and layout rules:
- Treat MiniMax images as art assets, not wallpaper to stretch blindly. Preserve aspect ratio with cover/crop math, parallax layers, camera-aware positioning, or cropped sprite regions.
- Do NOT stretch `assets/background.png` or `assets/title.png` to arbitrary canvas dimensions with distorted proportions. If drawing full-screen, implement a drawCover/drawContain helper that computes source/destination rectangles correctly.
- Do NOT place raw generated key art behind unreadable text without dark overlays, contrast panels, or composition-safe placement.
- Do NOT use ugly all-caps pixel/monospace text for the whole UI unless the request explicitly asks for strict pixel art. Retro style can use arcade accents, but HUD/menu text must be clean, readable, aligned, and proportionate.
- Use modern readable typography: system-ui, Segoe UI, Inter/Arial/sans-serif style, consistent sizes, text shadows/outlines only where they improve contrast.
- Build real UI composition: title screen, HUD, buttons/prompts, progress panels, health/score/lives indicators with spacing, padding, hierarchy, and no overlap.
- Keep visual style coherent: generated art, sprites, particles, UI colors, and text should look like one designed game, not unrelated pasted pieces.
- Avoid neon-green/debug-magenta UI unless it is a deliberate small accent. Do not draw giant magenta borders, wireframe rectangles, debug grids, hitbox-looking panels, or crude strokeRect HUD boxes.
- Do not make a collage of random square crops from generated art. Sprite-sheet cropping must be semantic: named crop regions for player/enemy/vehicle/prop states, with consistent scale and silhouette.
- Use sprite-sheet cropping for actors and props; if the sheet is imperfect, request/repair better assets or crop larger coherent regions rather than pasting tiny unrelated fragments.
- HUD panels should be designed with filled translucent panels, rounded corners, spacing, icons/bars, and hierarchy; avoid raw outlined boxes with huge labels.
- The first viewport must look like a finished game screen: attractive background, clear focal point, readable controls, and no distorted assets.

Visual direction:
Use the theme colors, but avoid empty black space. The first screen must look like a real finished web game with a large playable area, rich scenery, readable HUD, and polished objects.

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


def truthy_env(name, default="1"):
    return os.environ.get(name, default).lower() not in {"0", "false", "no", "off"}


def post_json(url, payload, timeout):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json",
    })

    def do_request():
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())

    resp = with_ipv4_dns(do_request)
    base_resp = resp.get("base_resp") or {}
    if base_resp.get("status_code") not in (None, 0):
        raise RuntimeError(f"MiniMax API error {base_resp.get('status_code')}: {base_resp.get('status_msg')}")
    return resp


def collect_strings(value):
    found = []
    if isinstance(value, str):
        found.append(value)
    elif isinstance(value, list):
        for item in value:
            found.extend(collect_strings(item))
    elif isinstance(value, dict):
        for item in value.values():
            found.extend(collect_strings(item))
    return found


def decode_image_string(value):
    raw = value.strip()
    if raw.startswith("data:image") and "," in raw:
        raw = raw.split(",", 1)[1]
    if len(raw) < 1000 or not re.fullmatch(r"[A-Za-z0-9+/=\s]+", raw):
        return None
    try:
        data = base64.b64decode(re.sub(r"\s+", "", raw), validate=True)
    except Exception:
        return None
    if data.startswith((b"\x89PNG\r\n\x1a\n", b"\xff\xd8\xff", b"RIFF")):
        return data
    return None


def download_binary(url, timeout):
    req = urllib.request.Request(url, headers={"User-Agent": "GameForge/1.0"})

    def do_request():
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()

    return with_ipv4_dns(do_request)


def generate_image_asset(assets_dir, filename, prompt, aspect_ratio):
    url = os.environ.get("MINIMAX_IMAGE_API_URL", "https://api.minimax.io/v1/image_generation")
    payload = {
        "model": os.environ.get("MINIMAX_IMAGE_MODEL", "image-01"),
        "prompt": prompt[:1500],
        "aspect_ratio": aspect_ratio,
        "response_format": "base64",
        "n": 1,
        "prompt_optimizer": True,
    }
    resp = post_json(url, payload, MINIMAX_ASSET_TIMEOUT_SECONDS)
    out_path = assets_dir / filename
    for value in collect_strings(resp.get("data", resp)):
        if value.startswith("http://") or value.startswith("https://"):
            data = download_binary(value, MINIMAX_ASSET_TIMEOUT_SECONDS)
            if len(data) > 1000:
                out_path.write_bytes(data)
                return {"type": "image", "path": f"assets/{filename}", "prompt": prompt, "source": "minimax-url"}
        data = decode_image_string(value)
        if data:
            out_path.write_bytes(data)
            return {"type": "image", "path": f"assets/{filename}", "prompt": prompt, "source": "minimax-base64"}
    raise RuntimeError("image response did not contain downloadable image data")


def generate_music_asset(assets_dir, filename, prompt):
    url = os.environ.get("MINIMAX_MUSIC_API_URL", "https://api.minimax.io/v1/music_generation")
    payload = {
        "model": os.environ.get("MINIMAX_MUSIC_MODEL", "music-2.6"),
        "prompt": prompt[:2000],
        "is_instrumental": True,
        "output_format": "hex",
        "audio_setting": {"sample_rate": 44100, "bitrate": 256000, "format": "mp3"},
    }
    resp = post_json(url, payload, MINIMAX_ASSET_TIMEOUT_SECONDS)
    data = resp.get("data") or {}
    out_path = assets_dir / filename
    audio = data.get("audio")
    if isinstance(audio, str) and len(audio) > 100:
        try:
            out_path.write_bytes(bytes.fromhex(re.sub(r"\s+", "", audio)))
            return {"type": "music", "path": f"assets/{filename}", "prompt": prompt, "source": "minimax-hex"}
        except ValueError:
            pass
    for value in collect_strings(data):
        if value.startswith("http://") or value.startswith("https://"):
            audio_data = download_binary(value, MINIMAX_ASSET_TIMEOUT_SECONDS)
            if len(audio_data) > 1000:
                out_path.write_bytes(audio_data)
                return {"type": "music", "path": f"assets/{filename}", "prompt": prompt, "source": "minimax-url"}
    raise RuntimeError("music response did not contain audio data")


def manifest_files_exist(output_path, manifest):
    images = manifest.get("images") or []
    audio = manifest.get("audio") or []
    image_ok = sum(1 for asset in images if (output_path / asset.get("path", "")).exists()) >= 2
    audio_ok = not audio or any((output_path / asset.get("path", "")).exists() for asset in audio)
    return image_ok and audio_ok


def load_existing_asset_pack(output_path):
    manifest_path = output_path / "assets" / "manifest.json"
    if not manifest_path.exists():
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if manifest.get("enabled") and manifest_files_exist(output_path, manifest):
        manifest["reused"] = True
        return manifest
    return None


def build_asset_pack(output_path, description, title, theme):
    manifest = {"enabled": False, "required": REQUIRE_GENERATED_ASSETS, "images": [], "audio": [], "errors": []}
    existing = load_existing_asset_pack(output_path)
    if existing:
        print("Reusing existing MiniMax assets from assets/manifest.json")
        return existing
    if not GENERATE_ASSETS:
        manifest["errors"].append("GAMEFORGE_GENERATE_ASSETS disabled")
        if REQUIRE_GENERATED_ASSETS:
            raise RuntimeError("Generated assets are required; GAMEFORGE_GENERATE_ASSETS=0 is not allowed")
        return manifest
    if not MINIMAX_API_KEY:
        manifest["errors"].append("MINIMAX_API_KEY missing; cannot generate bitmap/music assets")
        if REQUIRE_GENERATED_ASSETS:
            raise RuntimeError("Generated assets are required but MINIMAX_API_KEY is missing")
        return manifest

    assets_dir = output_path / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    common_style = (
        f"Game title: {title}. User request: {description}. Theme: {theme}. "
        "High quality game art, clear readable shapes, no UI text, no watermarks."
    )
    image_jobs = [
        ("background.png", "16:9", "wide gameplay background with depth, environment layers, cinematic composition, rich details, usable behind a canvas game. " + common_style),
        ("sprites.png", "1:1", "sprite sheet concept art containing the main playable character plus enemies/objects from the request, full body, readable silhouettes, multiple poses, game-ready. " + common_style),
        ("title.png", "16:9", "dramatic title/menu key art for the game, clean focal composition, no text, attractive first screen. " + common_style),
    ]
    music_prompt = (
        f"Instrumental looping game soundtrack for {title}. {description}. "
        f"Theme {theme}. Energetic, polished, suitable for browser arcade gameplay, no vocals."
    )

    print(f"Generating MiniMax image/music assets in parallel ({ASSET_WORKERS} workers)...")
    futures = {}
    with ThreadPoolExecutor(max_workers=max(1, ASSET_WORKERS)) as pool:
        for filename, aspect, prompt in image_jobs:
            futures[pool.submit(generate_image_asset, assets_dir, filename, prompt, aspect)] = ("image", filename)
        futures[pool.submit(generate_music_asset, assets_dir, "theme.mp3", music_prompt)] = ("music", "theme.mp3")
        for future in as_completed(futures):
            kind, filename = futures[future]
            try:
                asset = future.result()
                manifest["images" if kind == "image" else "audio"].append(asset)
                print(f"  Asset {kind}: {asset['path']}")
            except Exception as exc:
                msg = f"{filename}: {exc}"
                manifest["errors"].append(msg)
                print(f"  Asset {kind} failed: {msg}")

    manifest["images"].sort(key=lambda item: item.get("path", ""))
    manifest["audio"].sort(key=lambda item: item.get("path", ""))
    manifest["enabled"] = bool(manifest["images"] or manifest["audio"])
    (assets_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if REQUIRE_GENERATED_ASSETS and len(manifest["images"]) < 2:
        raise RuntimeError("Generated bitmap assets are required; fewer than 2 MiniMax image assets were created")
    return manifest
def asset_instructions(manifest):
    if not manifest or not manifest.get("enabled"):
        return ""
    lines = [
        "Generated asset pipeline:",
        "The following MiniMax-generated local assets already exist beside index.html and will be deployed with the game.",
    ]
    for asset in manifest.get("images", []):
        lines.append(f"- Image: {asset['path']}")
    for asset in manifest.get("audio", []):
        lines.append(f"- Music: {asset['path']}")
    lines.extend([
        "Asset usage requirements:",
        "- Preload and draw generated PNG assets with Image() and ctx.drawImage().",
        "- Use assets/background.png or assets/title.png as the visible menu/game background, not a flat color field.",
        "- Use assets/sprites.png for the main character, enemies, vehicles, bosses, props, or other primary subjects. Crop regions from the sheet if needed.",
        "- Do not render primary actors as colored fillRect/strokeRect blocks. Rectangles are allowed only for collision math, UI bars, particles, or minor props.",
        "- If assets/theme.mp3 exists, create an Audio object or <audio> element, start it after the user's start action, loop it, and add volume control/mute handling.",
        "- WebAudio sound effects are still expected for hits, jumps, pickups, crashes, shots, or UI feedback.",
        "- Use generated images with aspect-ratio-safe cover/contain/crop helpers; never distort full-screen art by blindly stretching it to canvas dimensions.",
        "- Do not create random square-crop collages from generated art. Use named semantic sprite crops with consistent scale and silhouettes.",
        "- Do not draw debug-magenta frames, wireframes, hitbox-looking rectangles, or crude outlined HUD boxes.",
        "- Put readable UI over designed panels/overlays. Do not use crude all-caps pixel text as the whole interface unless explicitly requested.",
        "- If a generated asset fails to load at runtime, use a graceful fallback, but the normal path must visibly use the generated assets.",
    ])
    return "\n".join(lines) + "\n"


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


@contextmanager
def generation_lock(output_path):
    lock_path = output_path / ".gameforge.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_file = lock_path.open("w", encoding="utf-8")
    start = time.time()
    announced = False
    try:
        while True:
            try:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                lock_file.seek(0)
                lock_file.truncate()
                lock_file.write(f"pid={os.getpid()} started={int(time.time())}\n")
                lock_file.flush()
                return_value = yield
                return return_value
            except BlockingIOError:
                if not announced:
                    print(f"Another generation is already running for {output_path.name}; waiting instead of starting a duplicate.")
                    announced = True
                if time.time() - start > GENERATION_LOCK_TIMEOUT_SECONDS:
                    raise RuntimeError(f"Timed out waiting for generation lock: {lock_path}")
                time.sleep(3)
    finally:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        except Exception:
            pass
        lock_file.close()


def existing_game_ready(output_path):
    if not (output_path / "index.html").exists() or not (output_path / "gameforge.json").exists():
        return False
    score, report = run_playtester(output_path.name)
    if score >= QUALITY_THRESHOLD:
        print(f"Existing game already READY: {score}% >= {QUALITY_THRESHOLD}%")
        print(report)
        return True
    return False


def write_metadata(output_dir, description, title, theme, user_id, asset_manifest=None):
    metadata = {
        "description": description,
        "title": title,
        "theme": theme,
        "user_id": user_id,
        "created_at": int(time.time()),
        "quality_threshold": QUALITY_THRESHOLD,
        "assets": asset_manifest or {},
    }
    Path(output_dir, "gameforge.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_prompt(description, title, theme, user_id=None, retry_feedback="", asset_manifest=None):
    colors = THEME_COLORS.get(theme, THEME_COLORS["minimal"])
    return BASE_PROMPT.format(
        description=description,
        title=title,
        theme=theme,
        user_constraints=get_user_constraints(user_id),
        prompt_improvements=get_prompt_improvements(),
        genre_requirements=genre_requirements(description),
        retry_feedback=retry_feedback,
        asset_instructions=asset_instructions(asset_manifest),
        **colors,
    )


def generate(description, title, theme, output_dir, user_id=None):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    with generation_lock(output_path):
        if existing_game_ready(output_path):
            return True
        return generate_locked(description, title, theme, output_path, user_id)


def generate_locked(description, title, theme, output_path, user_id=None):
    slug = output_path.name
    asset_manifest = build_asset_pack(output_path, description, title, theme)
    write_metadata(output_path, description, title, theme, user_id, asset_manifest)

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
        prompt = build_prompt(description, title, theme, user_id, retry_feedback, asset_manifest)
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
            log_generation(slug, minimax_model_name() if MINIMAX_API_KEY else MODEL, {}, False, duration, 0)

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
