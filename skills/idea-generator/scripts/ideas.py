#!/usr/bin/env python3
"""Generates game ideas. Usage: python3 ideas.py [theme] [count]"""
import sys, os, json, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path('/root/.openclaw/workspace')
GAMES_DIR = WORKSPACE / 'games'
LOGS_DIR  = WORKSPACE / 'hooks' / 'logs'
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
        'max_tokens': 4000, 'temperature': 0.8, 'stream': False
    }).encode()
    req = urllib.request.Request(API_URL, data=payload,
        headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read())
    return (data.get('choices') or [{}])[0].get('message', {}).get('content', '')

def existing_games():
    if not GAMES_DIR.exists(): return []
    return [d.name for d in GAMES_DIR.iterdir() if d.is_dir() and not d.name.startswith('_')]

def main():
    args = sys.argv[1:]
    count = 5
    theme = None
    if args:
        if args[-1].isdigit():
            count = int(args[-1])
            theme = ' '.join(args[:-1]) or None
        else:
            theme = ' '.join(args)
    existing = existing_games()
    existing_str = f'\n\nAlready existing (do NOT repeat): {", ".join(existing[:20])}' if existing else ''
    theme_str = f" with '{theme}' theme" if theme else ''
    prompt = (f'Generate {count} unique HTML5 game ideas{theme_str}.{existing_str}\n\n'
              f'For each provide:\n### N. Title\n**Genre:** genre\n**Description:** 2 sentences\n'
              f'**Mechanics:**\n- mechanic 1\n- mechanic 2\n\nMake ideas diverse and fun.')
    print(f'Generating {count} idea(s){theme_str}...')
    try:
        result = call_minimax(prompt)
    except Exception as e:
        print(f'ERROR: {e}'); sys.exit(1)
    print('\n' + '='*60)
    print(result)
    print('='*60)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    out = LOGS_DIR/f'ideas-{datetime.now().strftime("%Y-%m-%d")}.json'
    out.write_text(json.dumps({'generated_at': datetime.now(timezone.utc).isoformat(),
        'theme': theme, 'count': count, 'raw': result}, indent=2, ensure_ascii=False))
    print(f'Saved: {out}')

if __name__ == '__main__': main()
