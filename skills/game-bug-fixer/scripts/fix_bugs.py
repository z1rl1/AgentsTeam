#!/usr/bin/env python3
"""
GameForge Bug Fixer — sends QA failures to LLM for fixing.
Usage: python3 fix_bugs.py <slug>
Exit: 0=fixed, 1=error, 2=no improvement
"""
import sys, os, json, re, subprocess, time, shutil, urllib.request, urllib.error
from datetime import datetime
from pathlib import Path

WORKSPACE  = Path('/root/.openclaw/workspace')
GAMES_DIR  = WORKSPACE / 'games'
PLAYTESTER = WORKSPACE / 'skills' / 'game-playtester' / 'scripts' / 'game_playtester.py'
API_URL    = os.environ.get('MINIMAX_API_URL', 'https://api.minimax.io/v1/chat/completions')


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
TIMEOUT         = int(os.environ.get('MINIMAX_TIMEOUT_SECONDS', '240'))
THRESHOLD       = int(os.environ.get('GAMEFORGE_QUALITY_THRESHOLD', '85'))


def call_minimax(prompt):
    if not MINIMAX_API_KEY:
        raise RuntimeError('MINIMAX_API_KEY not set')
    payload = json.dumps({
        'model': MODEL,
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': MAX_TOKENS,
        'temperature': 0.3,
        'stream': False,
        'reasoning_split': True,
    }, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(API_URL, data=payload, headers={
        'Authorization': f'Bearer {MINIMAX_API_KEY}',
        'Content-Type': 'application/json',
    })
    t0 = time.time()
    print(f'  Calling MiniMax ({MODEL})...')
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'HTTP {e.code}: {e.read().decode()[:300]}')
    elapsed = time.time() - t0
    base = data.get('base_resp') or {}
    if base.get('status_code') not in (None, 0):
        raise RuntimeError(f"MiniMax error: {base.get('status_msg')}")
    choices = data.get('choices') or []
    if not choices:
        raise RuntimeError('No choices in response')
    content = (choices[0].get('message') or {}).get('content', '')
    if not content.strip():
        raise RuntimeError('Empty response content')
    tok = data.get('usage', {})
    print(f'  Done in {elapsed:.1f}s | in={tok.get("prompt_tokens","?")} out={tok.get("completion_tokens","?")}')
    return content


def run_playtester(slug):
    try:
        r = subprocess.run(['python3', str(PLAYTESTER), slug],
                           capture_output=True, text=True, timeout=120)
        out = r.stdout + r.stderr
    except subprocess.TimeoutExpired:
        return None, [], 'TIMEOUT'
    m = re.search(r'Result:\s*\d+/\d+\s*\((\d+)%\)', out)
    score = int(m.group(1)) if m else None
    fails = [ln.strip() for ln in out.splitlines() if '[FAIL]' in ln]
    return score, fails, out


def extract_html(text):
    m = re.search(r'(<!DOCTYPE\s+html.*?</html>)', text, re.I | re.S)
    return m.group(1) if m else None


def read_meta(game_dir):
    p = game_dir / 'gameforge.json'
    try:
        return json.loads(p.read_text()) if p.exists() else {}
    except Exception:
        return {}


def write_meta(game_dir, meta):
    p = game_dir / 'gameforge.json'
    p.write_text(json.dumps(meta, indent=2, ensure_ascii=False))


def fix_game(slug):
    game_dir   = GAMES_DIR / slug
    index_path = game_dir / 'index.html'
    if not index_path.exists():
        print(f'ERROR: {index_path} not found'); return 1

    print(f'\n[fix_bugs] {slug}')
    print('[1/7] Running playtester...')
    score_before, fails, pt_out = run_playtester(slug)
    if score_before is None:
        meta = read_meta(game_dir)
        score_before = meta.get('qa_score')
        if score_before is None:
            print('Cannot determine score'); return 1
    print(f'  Score: {score_before}%  Fails: {len(fails)}')
    if score_before >= THRESHOLD:
        print(f'  Already passing ({score_before}%)'); return 0

    print('[2/7] Reading index.html...')
    html = index_path.read_text(encoding='utf-8', errors='ignore')

    fails_text = '\n'.join(f'  - {f}' for f in fails) if fails else '  (general quality issues)'
    prompt = (
        f"You are GameForge Bug Fixer. This HTML5 game scored {score_before}% "
        f"(threshold {THRESHOLD}%).\n\nFailing checks:\n{fails_text}\n\n"
        f"Fix ALL failures. Return ONE complete fixed HTML document starting with <!DOCTYPE html>.\n"
        f"Return ONLY HTML. No explanation, no markdown fences.\n\nCurrent HTML:\n{html[:180000]}"
    )

    print('[3/7] Calling LLM...')
    try:
        response = call_minimax(prompt)
    except Exception as e:
        print(f'  ERROR: {e}'); return 1

    print('[4/7] Extracting HTML...')
    fixed_html = extract_html(response)
    if not fixed_html:
        print('  ERROR: no complete HTML in response'); return 1
    print(f'  Got {len(fixed_html):,} chars')

    print('[5/7] Saving backup + writing fix...')
    backup = index_path.with_suffix('.html.bak')
    shutil.copy2(index_path, backup)
    index_path.write_text(fixed_html, encoding='utf-8')

    print('[6/7] Re-running playtester...')
    score_after, _, _ = run_playtester(slug)
    if score_after is None:
        print('  Could not parse new score, keeping fix')
        score_after = score_before
    print(f'  {score_before}% -> {score_after}%')

    if score_after > score_before:
        print(f'  IMPROVED +{score_after - score_before}%')
        backup.unlink(missing_ok=True)
        kept = True
    else:
        print('  No improvement, restoring backup')
        shutil.copy2(backup, index_path)
        kept = False

    print('[7/7] Updating gameforge.json...')
    meta = read_meta(game_dir)
    meta['qa_score']    = score_after if kept else score_before
    meta['fixed_at']    = datetime.utcnow().isoformat() + 'Z'
    meta['fix_kept']    = kept
    hist = meta.get('fix_history', [])
    hist.append({'fixed_at': meta['fixed_at'], 'score_before': score_before,
                 'score_after': score_after, 'kept': kept})
    meta['fix_history'] = hist
    write_meta(game_dir, meta)

    print(f'\n[fix_bugs] {"FIXED" if kept else "NO_IMPROVEMENT"} | {score_before}% -> {score_after}%')
    return 0 if kept else 2


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: python3 {sys.argv[0]} <slug>'); sys.exit(1)
    sys.exit(fix_game(sys.argv[1]))
