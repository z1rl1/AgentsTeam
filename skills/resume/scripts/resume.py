#!/usr/bin/env python3
import os, json
from datetime import datetime, timezone
from pathlib import Path

GAMES_DIR = Path('/root/.openclaw/workspace/games')

def fmt_ago(s):
    if not s: return 'unknown'
    try:
        dt = datetime.fromisoformat(s.replace('Z', '+00:00'))
        diff = int((datetime.now(timezone.utc) - dt).total_seconds())
        if diff < 3600: return f'{diff//60}m ago'
        if diff < 86400: return f'{diff//3600}h ago'
        return f'{diff//86400}d ago'
    except Exception:
        return 'unknown'

def main():
    print('=== RESUME: Incomplete Games ===')
    if not GAMES_DIR.exists(): print('No games dir'); return
    found = []
    for d in sorted(GAMES_DIR.iterdir()):
        if not d.is_dir(): continue
        issues = []
        if not (d/'index.html').exists(): issues.append('no index.html')
        elif (d/'index.html').stat().st_size < 5000: issues.append('too small')
        gf = d/'gameforge.json'
        meta = {}
        if not gf.exists(): issues.append('no gameforge.json')
        else:
            try: meta = json.loads(gf.read_text())
            except Exception: issues.append('invalid gameforge.json')
        if not meta.get('qa_score'): issues.append('no qa_score')
        if not meta.get('deploy_url') and not meta.get('deployed'): issues.append('not deployed')
        if issues:
            found.append({'slug': d.name, 'issues': issues, 'created_at': meta.get('created_at', '')})
    if not found: print('All games complete!'); return
    for g in found:
        print(f"  {g['slug']:<35} {fmt_ago(g['created_at']):<12} {', '.join(g['issues'])}")

if __name__ == '__main__': main()
