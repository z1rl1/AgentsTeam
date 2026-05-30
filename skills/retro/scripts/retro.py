#!/usr/bin/env python3
"""Retrospective analysis. Usage: python3 retro.py"""
import os, json, glob, urllib.request
from datetime import datetime, timezone, timedelta
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
    if not key: return '(API key not set)'
    payload = json.dumps({'model': os.environ.get('GAMEFORGE_MODEL','MiniMax-M2.7'),
        'messages': [{'role':'user','content':prompt}],
        'max_tokens': 3000, 'temperature': 0.6, 'stream': False
    }).encode()
    req = urllib.request.Request(API_URL, data=payload,
        headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.loads(r.read())
        return (data.get('choices') or [{}])[0].get('message', {}).get('content', '')
    except Exception as e:
        return f'(API error: {e})'

def main():
    games, scores, fixes = [], [], 0
    if GAMES_DIR.exists():
        for d in sorted(GAMES_DIR.iterdir()):
            if not d.is_dir(): continue
            gf = d/'gameforge.json'
            if not gf.exists(): continue
            try:
                m = json.loads(gf.read_text())
                games.append(m)
                s = m.get('qa_score')
                if s: scores.append(float(s))
                fixes += len(m.get('fix_history', []))
            except Exception:
                pass

    cost, tokens, calls = 0.0, 0, 0
    for f in glob.glob(str(LOGS_DIR/'llm-usage-*.jsonl')):
        try:
            for line in open(f):
                try:
                    e = json.loads(line)
                    cost += float(e.get('cost', 0) or 0)
                    tokens += int(e.get('total_tokens', 0) or 0)
                    calls += 1
                except Exception:
                    pass
        except Exception:
            pass

    avg = sum(scores)/len(scores) if scores else 0
    top5 = sorted(games, key=lambda g: float(g.get('qa_score',0) or 0), reverse=True)[:5]

    summary = (f'RETRO {datetime.now().strftime("%Y-%m-%d")}\n'
               f'Games: {len(games)}  Avg QA: {avg:.1f}  Fixes: {fixes}\n'
               f'LLM: {calls} calls  ${cost:.4f}  {tokens:,} tokens\n'
               f'Top games: {", ".join(g.get("_slug",g.get("slug","?"))+"="+str(g.get("qa_score","?")) for g in top5[:3])}')

    print(summary)
    print('\nGetting AI insights...')
    prompt = f'Given these game generation stats, what should we improve?\n\n{summary}\n\nGive 3 actionable recommendations.'
    insights = call_minimax(prompt)
    print('\n=== AI INSIGHTS ===')
    print(insights)

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    date = datetime.now().strftime('%Y-%m-%d')
    out = LOGS_DIR/f'retro-{date}.md'
    out.write_text(f'# Retro {date}\n\n## Stats\n```\n{summary}\n```\n\n## Insights\n{insights}\n')
    print(f'\nSaved: {out}')

if __name__ == '__main__': main()
