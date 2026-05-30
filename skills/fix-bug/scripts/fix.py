#!/usr/bin/env python3
"""Fix specific bug. Usage: python3 fix.py <slug> "<bug_description>"""
import sys, os, json, re, time, urllib.request
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
        'max_tokens': 40000, 'temperature': 0.2, 'stream': False
    }).encode()
    req = urllib.request.Request(API_URL, data=payload,
        headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=240) as r:
        data = json.loads(r.read())
    print(f'  Done in {time.time()-t0:.1f}s')
    return (data.get('choices') or [{}])[0].get('message', {}).get('content', '')

def extract_html(text):
    m = re.search(r'(<!DOCTYPE\s+html.*?</html>)', text, re.I|re.S)
    return m.group(1) if m else None

def main():
    if len(sys.argv) < 3: print('Usage: fix.py <slug> "<bug>"'); sys.exit(1)
    slug = sys.argv[1]
    bug = ' '.join(sys.argv[2:])
    idx = GAMES_DIR/slug/'index.html'
    if not idx.exists(): print(f'ERROR: {idx}'); sys.exit(1)
    html = idx.read_text(encoding='utf-8')
    print(f'[fix-bug] {slug}: {bug}')
    prompt = (f'Fix this specific bug: {bug}\n'
              f'Fix ONLY the described bug. Return ONLY complete HTML.\n\n{html[:180000]}')
    try:
        response = call_minimax(prompt)
    except Exception as e:
        print(f'ERROR: {e}'); sys.exit(1)
    new_html = extract_html(response)
    if not new_html: print('ERROR: no HTML'); sys.exit(1)
    ts = datetime.now().strftime('%Y%m%d%H%M%S')
    backup = GAMES_DIR/slug/f'index.backup.{ts}.html'
    backup.write_text(html, encoding='utf-8')
    idx.write_text(new_html, encoding='utf-8')
    gf = GAMES_DIR/slug/'gameforge.json'
    if gf.exists():
        d = json.loads(gf.read_text())
        hist = d.get('fix_history', [])
        hist.append({'ts': datetime.now(timezone.utc).isoformat(), 'bug': bug, 'backup': backup.name})
        d['fix_history'] = hist
        d['last_fixed_at'] = datetime.now(timezone.utc).isoformat()
        gf.write_text(json.dumps(d, indent=2, ensure_ascii=False))
    print(f'[fix-bug] Done. Backup: {backup.name}')

if __name__ == '__main__': main()
