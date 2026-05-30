#!/usr/bin/env python3
import os, json, glob
from pathlib import Path

WORKSPACE = Path('/root/.openclaw/workspace')
GAMES_DIR = WORKSPACE / 'games'
LOGS_DIR  = WORKSPACE / 'hooks' / 'logs'

def bar(v, mx, w=15):
    f = int(round(v/mx*w)) if mx else 0
    return '[' + '#'*f + ' '*(w-f) + ']'

def main():
    games, scores, themes = [], [], {}
    if GAMES_DIR.exists():
        for d in sorted(GAMES_DIR.iterdir()):
            if not d.is_dir(): continue
            gf = d/'gameforge.json'
            if not gf.exists(): continue
            try:
                m = json.loads(gf.read_text())
                m['_slug'] = d.name
                games.append(m)
                s = m.get('qa_score')
                if s: scores.append(float(s))
                t = str(m.get('theme', '')).lower()
                if t: themes[t] = themes.get(t, 0) + 1
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
    mx = max(scores) if scores else 0
    top = sorted(games, key=lambda g: float(g.get('qa_score', 0) or 0), reverse=True)[:10]

    print('='*60)
    print('  GAMEFORGE ANALYTICS')
    print('='*60)
    print(f'  Games: {len(games)}  Avg QA: {avg:.1f}  Top: {mx}')
    print(f'  LLM: {calls} calls  {tokens:,} tokens  ${cost:.4f}')
    print()
    print('  Top games by QA score:')
    for g in top:
        s = float(g.get('qa_score', 0) or 0)
        dep = 'deployed' if g.get('deploy_url') or g.get('deployed') else 'local'
        print(f'  {g["_slug"]:<35} {s:5.1f}  {bar(s,mx)}  {dep}')
    print()
    print('  Themes:')
    for t, c in sorted(themes.items(), key=lambda x: x[1], reverse=True)[:8]:
        print(f'  {t:<20} {c:3d}  {bar(c, max(themes.values()) if themes else 1)}')
    print('='*60)

if __name__ == '__main__': main()
