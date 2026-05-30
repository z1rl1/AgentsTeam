#!/usr/bin/env python3
"""Code review via LLM. Usage: python3 review.py <slug>"""
import sys, os, json, time, urllib.request
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
        'max_tokens': 6000, 'temperature': 0.3, 'stream': False
    }).encode()
    req = urllib.request.Request(API_URL, data=payload,
        headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read())
    return (data.get('choices') or [{}])[0].get('message', {}).get('content', '')

def main():
    if len(sys.argv) < 2: print('Usage: review.py <slug>'); sys.exit(1)
    slug = sys.argv[1]
    idx = GAMES_DIR/slug/'index.html'
    if not idx.exists(): print(f'ERROR: {idx}'); sys.exit(1)
    html = idx.read_text(encoding='utf-8')
    lines = len(html.splitlines())
    print(f'Reviewing {slug} ({lines} lines)...')
    prompt = (f'Review this HTML5 game code. Find bugs, performance issues, UX problems.\n'
              f'Format:\n## Bugs\n## Performance\n## UX\n## Suggestions\n## Summary\n\n{html[:80000]}')
    try:
        result = call_minimax(prompt)
    except Exception as e:
        print(f'ERROR: {e}'); sys.exit(1)
    print('\n' + '='*60)
    print(f'REVIEW: {slug}')
    print('='*60)
    print(result)
    review_file = GAMES_DIR/slug/'review.md'
    review_file.write_text(f'# Review: {slug}\n\n{result}\n', encoding='utf-8')
    print(f'\nSaved: {review_file}')

if __name__ == '__main__': main()
