#!/usr/bin/env python3
"""Game Balancer. Usage: python3 balance.py <slug> [issue_description]"""
import sys, os, json, re, time, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path('/root/.openclaw/workspace')
GAMES_DIR = WORKSPACE / 'games'
API_URL   = 'https://api.minimaxi.chat/v1/text/chatcompletion_v2'

def load_env():
    p = WORKSPACE/'.env'
    if not p.exists(): return
    for raw in p.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line: continue
        k, v = line.split('=', 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and k not in os.environ: os.environ[k] = v

load_env()

def call_minimax(prompt):
    key = os.environ.get('MINIMAX_API_KEY', '')
    if not key: raise RuntimeError('MINIMAX_API_KEY not set')
    payload = json.dumps({'model': os.environ.get('GAMEFORGE_MODEL','MiniMax-M2.7'),
        'messages': [{'role':'user','content':prompt}],
        'max_tokens': 40000, 'temperature': 0.35, 'stream': False
    }).encode()
    req = urllib.request.Request(API_URL, data=payload,
        headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=240) as r:
        data = json.loads(r.read())
    print(f'  Done in {time.time()-t0:.1f}s')
    choices = data.get('choices') or []
    if not choices: raise RuntimeError('No choices')
    return (choices[0].get('message') or {}).get('content', '')

def extract_html(text):
    m = re.search(r'(<!DOCTYPE\s+html.*?</html>)', text, re.I|re.S)
    return m.group(1) if m else None

def main():
    if len(sys.argv) < 2: print('Usage: balance.py <slug> [issue]'); sys.exit(1)
    slug = sys.argv[1]
    issue = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else 'The game feels unbalanced. Add progressive difficulty.'
    game_dir = GAMES_DIR/slug
    idx = game_dir/'index.html'
    if not idx.exists(): print(f'ERROR: {idx}'); sys.exit(1)
    html = idx.read_text(encoding='utf-8')
    print(f'[balance] {slug}: {issue}')
    prompt = (f'Rebalance this HTML5 game. Issue: {issue}\n'
              f'Adjust: enemy speed, spawn rates, player HP, score multipliers.\n'
              f'Return ONLY complete fixed HTML.\n\n{html[:180000]}')
    try:
        response = call_minimax(prompt)
    except Exception as e:
        print(f'ERROR: {e}'); sys.exit(1)
    new_html = extract_html(response)
    if not new_html: print('ERROR: no HTML in response'); sys.exit(1)
    ts = datetime.now().strftime('%Y%m%d%H%M%S')
    backup = game_dir/f'index.backup.{ts}.html'
    backup.write_text(html, encoding='utf-8')
    idx.write_text(new_html, encoding='utf-8')
    gf = game_dir/'gameforge.json'
    if gf.exists():
        d = json.loads(gf.read_text())
        d['balanced_at'] = datetime.now(timezone.utc).isoformat()
        d['balance_notes'] = issue
        gf.write_text(json.dumps(d, indent=2, ensure_ascii=False))
    print(f'[balance] Done. Backup: {backup.name}')

if __name__ == '__main__': main()
