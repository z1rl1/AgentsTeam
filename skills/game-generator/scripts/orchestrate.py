#!/usr/bin/env python3
"""
orchestrate.py — Multi-agent GameForge pipeline.
Usage: python3 orchestrate.py "<description>" [user_id]

Pipeline:
  1. game-designer  — LLM planning call → structured JSON plan
  2. game-generator — generate_game.py subprocess (includes assets + audio parallel)
  3. game-enhancer  — if score 75-84%, auto-enhance visual quality
  4. game-deployer  — deploy.sh if score >= threshold
"""
import sys, os, json, re, time, subprocess, random, urllib.request, urllib.error
from datetime import datetime
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
WORKSPACE   = SCRIPTS_DIR.parents[2]   # skills/game-generator/scripts -> workspace
GAMES_DIR   = WORKSPACE / 'games'
GENERATE_PY = SCRIPTS_DIR / 'generate_game.py'
ENHANCE_PY  = WORKSPACE / 'skills' / 'game-enhancer' / 'scripts' / 'enhance.py'
DEPLOY_SH   = SCRIPTS_DIR / 'deploy.sh'
API_URL     = os.environ.get('MINIMAX_API_URL', 'https://api.minimax.io/v1/chat/completions')

THRESHOLD_DEPLOY  = 85
THRESHOLD_ENHANCE = 75
GENERATE_TIMEOUT  = 600
ENHANCE_TIMEOUT   = 300
DEPLOY_TIMEOUT    = 120


def load_env():
    p = WORKSPACE / '.env'
    if not p.exists():
        return
    for raw in p.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v

load_env()

MINIMAX_API_KEY = os.environ.get('MINIMAX_API_KEY', '')
MODEL           = os.environ.get('GAMEFORGE_MODEL', 'MiniMax-M2.7').replace('minimax/', '')


def ts():
    return datetime.now().strftime('%H:%M:%S')


def log(step, msg):
    print(f'[{ts()}] [{step}] {msg}', flush=True)


# ── Step 1: game-designer ──────────────────────────────────────────────────

DESIGNER_PROMPT = """\
You are a game designer. Given this user request, output a JSON game plan.
User request: {description}

Return ONLY valid JSON (no markdown, no explanation):
{{
  "title": "...",
  "slug": "game_type-theme-NNNN",
  "game_type": "platformer|shooter|racing|snake|tetris|puzzle|clicker",
  "theme": "cyberpunk|space|retro|neon|minimal",
  "mechanics": ["...", "..."],
  "controls": "Arrow keys + Space",
  "complexity": "simple|medium|complex"
}}"""


def call_minimax_small(prompt):
    if not MINIMAX_API_KEY:
        raise RuntimeError('MINIMAX_API_KEY not set')
    payload = json.dumps({
        'model': MODEL,
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': 512,
        'temperature': 0.5,
        'stream': False,
    }, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(API_URL, data=payload, headers={
        'Authorization': f'Bearer {MINIMAX_API_KEY}',
        'Content-Type': 'application/json',
    })
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
    choices = data.get('choices') or []
    if not choices:
        raise RuntimeError('No choices in planning response')
    return (choices[0].get('message') or {}).get('content', '')


def extract_json(text):
    text = re.sub(r'```(?:json)?', '', text).strip('` \n')
    m = re.search(r'\{.*\}', text, re.S)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    raise ValueError('No valid JSON in response')


def fallback_plan(description):
    desc = description.lower()
    game_type = next((t for t in ('platformer','shooter','racing','snake','tetris','puzzle','clicker') if t in desc), 'platformer')
    theme     = next((t for t in ('cyberpunk','space','retro','neon','minimal') if t in desc), 'retro')
    slug      = f'{game_type}-{theme}-{random.randint(1000,9999)}'
    return {'title': description[:60].title(), 'slug': slug,
            'game_type': game_type, 'theme': theme,
            'mechanics': ['movement', 'collision'],
            'controls': 'Arrow keys + Space', 'complexity': 'simple'}


def plan_game(description):
    log('game-designer', 'Planning...')
    try:
        raw  = call_minimax_small(DESIGNER_PROMPT.format(description=description))
        plan = extract_json(raw)
        log('game-designer', f"slug={plan.get('slug')}  type={plan.get('game_type')}  theme={plan.get('theme')}")
        return plan
    except Exception as e:
        log('game-designer', f'LLM failed ({e}), using fallback')
        plan = fallback_plan(description)
        log('game-designer', f"fallback slug={plan['slug']}")
        return plan


# ── Step 2: generate_game.py ───────────────────────────────────────────────

def run_generate(description, plan, user_id):
    slug     = plan['slug']
    game_dir = str(GAMES_DIR / slug)
    cmd = [sys.executable, str(GENERATE_PY),
           description, plan.get('title', description[:60]),
           plan.get('theme', 'retro'), game_dir, user_id]
    log('game-generator', 'Starting generate_game.py...')
    t0 = time.time()
    try:
        r = subprocess.run(cmd, timeout=GENERATE_TIMEOUT, cwd=str(SCRIPTS_DIR))
        log('game-generator', f'Done in {time.time()-t0:.0f}s  exit={r.returncode}')
        return r
    except subprocess.TimeoutExpired:
        log('game-generator', f'TIMEOUT after {GENERATE_TIMEOUT}s')
        return None


# ── Score reading ──────────────────────────────────────────────────────────

def read_score(slug):
    p = GAMES_DIR / slug / 'gameforge.json'
    try:
        return json.loads(p.read_text()).get('qa_score') if p.exists() else None
    except Exception:
        return None


# ── Step 3: enhance ────────────────────────────────────────────────────────

def run_enhance(slug):
    if not ENHANCE_PY.exists():
        log('game-enhancer', 'enhance.py not found, skipping')
        return False
    log('game-enhancer', f'Enhancing {slug}...')
    try:
        r = subprocess.run([sys.executable, str(ENHANCE_PY), slug, 'visual'],
                           timeout=ENHANCE_TIMEOUT, capture_output=True, text=True)
        print(r.stdout)
        return r.returncode == 0
    except subprocess.TimeoutExpired:
        log('game-enhancer', 'TIMEOUT')
        return False


# ── Step 4: deploy ─────────────────────────────────────────────────────────

def run_deploy(slug):
    if not DEPLOY_SH.exists():
        log('game-deployer', 'deploy.sh not found, skipping')
        return False
    log('game-deployer', f'Deploying {slug}...')
    game_dir = str(GAMES_DIR / slug)
    try:
        r = subprocess.run(['bash', str(DEPLOY_SH), game_dir, slug],
                           timeout=DEPLOY_TIMEOUT)
        if r.returncode == 0:
            log('game-deployer', f'Deployed: https://{slug}.surge.sh')
            return True
        log('game-deployer', f'deploy.sh exit={r.returncode}')
        return False
    except subprocess.TimeoutExpired:
        log('game-deployer', 'TIMEOUT')
        return False


# ── Main orchestrator ──────────────────────────────────────────────────────

def orchestrate(description, user_id='anon'):
    t_start = time.time()
    errors  = []
    log('orchestrator', '=== GameForge Pipeline START ===')
    log('orchestrator', f'description={description!r}  user={user_id}')

    # Step 1
    plan = plan_game(description)
    slug = plan['slug']

    # Step 2
    gen = run_generate(description, plan, user_id)
    if gen is None or gen.returncode != 0:
        errors.append(f'generate_game.py failed (exit={getattr(gen,"returncode","TIMEOUT")})')

    # Read score
    score = read_score(slug)
    log('orchestrator', f'Score after generation: {score}%' if score else 'Score: unknown')

    # Step 3 — enhance if in 75-84% range
    if score is not None and THRESHOLD_ENHANCE <= score < THRESHOLD_DEPLOY:
        log('orchestrator', f'{score}% in enhancement range, trying enhance...')
        if run_enhance(slug):
            new_score = read_score(slug)
            if new_score:
                log('orchestrator', f'Score after enhance: {new_score}%')
                score = new_score

    # Step 4 — deploy
    deployed = False
    if score is not None and score >= THRESHOLD_DEPLOY:
        deployed = run_deploy(slug)
    else:
        log('orchestrator', f'Score {score}% < {THRESHOLD_DEPLOY}%, NOT deploying')
        errors.append(f'Score {score}% below threshold')

    elapsed = time.time() - t_start
    log('orchestrator', '=== COMPLETE ===')
    log('orchestrator', f'slug={slug}  score={score}%  deployed={deployed}  time={elapsed:.0f}s')
    if errors:
        log('orchestrator', 'Issues: ' + ' | '.join(errors))

    return {'slug': slug, 'score': score, 'deployed': deployed, 'errors': errors}


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 orchestrate.py "<description>" [user_id]')
        sys.exit(1)
    result = orchestrate(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else 'anon')
    sys.exit(0 if result['deployed'] else (2 if result['score'] else 1))
