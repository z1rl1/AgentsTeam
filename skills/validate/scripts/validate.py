#!/usr/bin/env python3
import sys, re, json
from pathlib import Path

GAMES_DIR = Path('/root/.openclaw/workspace/games')

def main():
    if len(sys.argv) < 2: print('Usage: validate.py <slug>'); sys.exit(1)
    slug = sys.argv[1]
    game_dir = GAMES_DIR/slug
    idx = game_dir/'index.html'
    gf_path = game_dir/'gameforge.json'
    problems = []
    if not idx.exists():
        problems.append('no index.html')
    else:
        size = idx.stat().st_size
        if size < 10240: problems.append(f'too small ({size}B < 10KB)')
        html = idx.read_text(encoding='utf-8', errors='replace')
        if not html.strip().upper().startswith('<!DOCTYPE'): problems.append('no DOCTYPE')
        if not re.search(r'</html>', html, re.I): problems.append('no </html>')
        if not re.search(r'<canvas', html, re.I): problems.append('no <canvas>')
        if not re.search(r'<script', html, re.I): problems.append('no <script>')
    if not gf_path.exists():
        problems.append('no gameforge.json')
    else:
        try:
            d = json.loads(gf_path.read_text())
            for f in ('title', 'description', 'slug'):
                if not d.get(f): problems.append(f'missing {f} in gameforge.json')
        except Exception as e:
            problems.append(f'invalid gameforge.json: {e}')
    if problems:
        print(f'INVALID ({len(problems)}):')
        for p in problems: print(f'  - {p}')
        sys.exit(1)
    print('VALID')

if __name__ == '__main__': main()
