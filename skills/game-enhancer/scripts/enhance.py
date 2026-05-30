#!/usr/bin/env python3
"""
GameForge Game Enhancer — polishes existing games via LLM.
Usage: python3 enhance.py <slug> [visual|gameplay|audio|all]
"""
import sys, os, json, re, subprocess, shutil, time, urllib.request, urllib.error
from datetime import datetime
from pathlib import Path

WORKSPACE  = Path('/root/.openclaw/workspace')
GAMES_DIR  = WORKSPACE / 'games'
PLAYTESTER = WORKSPACE / 'skills' / 'game-playtester' / 'scripts' / 'game_playtester.py'
API_URL    = os.environ.get('MINIMAX_API_URL', 'https://api.minimax.io/v1/chat/completions')

MODES = {
    'visual':   'Improve graphics: richer backgrounds, better particles, smoother animations, polished UI panels.',
    'gameplay': 'Deepen gameplay: add progression system, more enemy/obstacle types, power-ups, combo system.',
    'audio':    'Add rich Web Audio API sounds: looping background music, hit/pickup/jump/gameover sounds.',
}


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
MAX_TOKENS      = int(os.environ.get('GAMEFORGE_MAX_TOKENS', '200000'))
API_TIMEOUT     = int(os.environ.get('MINIMAX_TIMEOUT_SECONDS', '240'))


def call_minimax(prompt):
    if not MINIMAX_API_KEY:
        raise RuntimeError('MINIMAX_API_KEY not set')
    payload = json.dumps({
        'model': MODEL, 'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': MAX_TOKENS, 'temperature': 0.6,
        'stream': False, 'reasoning_split': True,
    }, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(API_URL, data=payload, headers={
        'Authorization': f'Bearer {MINIMAX_API_KEY}',
        'Content-Type': 'application/json',
    })
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=API_TIMEOUT) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'HTTP {e.code}: {e.read().decode()[:300]}')
    base = data.get('base_resp') or {}
    if base.get('status_code') not in (None, 0):
        raise RuntimeError(f"MiniMax error: {base.get('status_msg')}")
    choices = data.get('choices') or []
    if not choices:
        raise RuntimeError('No choices in response')
    content = (choices[0].get('message') or {}).get('content', '')
    if not content.strip():
        raise RuntimeError('Empty response content')
    print(f'  Done in {time.time()-t0:.1f}s')
    return content


def extract_html(text):
    text = text.strip()
    m = re.search(r'```(?:html)?\s*\n(<!DOCTYPE.*?</html>)\s*```', text, re.I | re.S)
    if m:
        return m.group(1)
    m = re.search(r'(<!DOCTYPE\s+html.*?</html>)', text, re.I | re.S)
    return m.group(1) if m else None


def run_playtester(slug):
    if not PLAYTESTER.exists():
        return None
    try:
        r = subprocess.run(['python3', str(PLAYTESTER), slug],
                           capture_output=True, text=True, timeout=120)
        out = r.stdout + r.stderr
        m = re.search(r'Result:\s*\d+/\d+\s*\((\d+)%\)', out)
        return int(m.group(1)) if m else None
    except Exception:
        return None


def read_meta(slug):
    p = GAMES_DIR / slug / 'gameforge.json'
    try:
        return json.loads(p.read_text()) if p.exists() else {}
    except Exception:
        return {}


def write_meta(slug, meta):
    p = GAMES_DIR / slug / 'gameforge.json'
    p.write_text(json.dumps(meta, indent=2, ensure_ascii=False))


def enhance(slug, mode='all'):
    game_dir   = GAMES_DIR / slug
    index_path = game_dir / 'index.html'
    if not index_path.exists():
        print(f'ERROR: {index_path} not found'); return False

    print(f'[enhance] {slug}  mode={mode}')
    html = index_path.read_text(encoding='utf-8')

    score_before = run_playtester(slug)
    print(f'  Score before: {score_before}%' if score_before else '  Score before: unknown')

    modes_to_run = list(MODES.keys()) if mode == 'all' else [mode]
    current_html = html
    changed = False

    for m in modes_to_run:
        instruction = MODES[m]
        prompt = (
            f"{instruction}\n\n"
            "Rules: return ONLY complete HTML, no explanation, no markdown fences.\n"
            "Keep all game logic intact. No external CDN dependencies.\n\n"
            f"Current HTML:\n{current_html[:180000]}"
        )
        print(f'  Running {m} enhancement...')
        try:
            response = call_minimax(prompt)
            new_html = extract_html(response)
            if new_html and len(new_html) > 500 and '</html>' in new_html.lower():
                current_html = new_html
                changed = True
                print(f'  {m}: OK ({len(new_html):,} chars)')
            else:
                print(f'  {m}: skipped (invalid response)')
        except Exception as e:
            print(f'  {m}: ERROR {e}')

    if not changed:
        print('  No enhancements applied'); return False

    backup = index_path.with_suffix('.html.enh_bak')
    shutil.copy2(index_path, backup)
    index_path.write_text(current_html, encoding='utf-8')

    score_after = run_playtester(slug)
    print(f'  Score after: {score_after}%' if score_after else '  Score after: unknown')

    if score_after is not None and score_before is not None and score_after < score_before:
        print('  Score dropped, reverting')
        shutil.copy2(backup, index_path)
        backup.unlink(missing_ok=True)
        return False

    backup.unlink(missing_ok=True)
    meta = read_meta(slug)
    meta['enhanced_at'] = datetime.utcnow().isoformat() + 'Z'
    enhs = meta.get('enhancements', [])
    enhs.append({'mode': mode, 'timestamp': meta['enhanced_at'],
                 'score_before': score_before, 'score_after': score_after})
    meta['enhancements'] = enhs
    if score_after:
        meta['qa_score'] = score_after
    write_meta(slug, meta)
    print('[enhance] Done')
    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 enhance.py <slug> [visual|gameplay|audio|all]'); sys.exit(1)
    slug = sys.argv[1]
    mode = sys.argv[2].lower() if len(sys.argv) > 2 else 'all'
    if mode not in ('visual', 'gameplay', 'audio', 'all'):
        print(f'Unknown mode: {mode}'); sys.exit(1)
    ok = enhance(slug, mode)
    sys.exit(0 if ok else 1)
