#!/usr/bin/env python3
import sys, re, json
from pathlib import Path

GAMES_DIR = Path('/root/.openclaw/workspace/games')

def main():
    if len(sys.argv) < 2: print('Usage: perf.py <slug>'); sys.exit(1)
    slug = sys.argv[1]
    idx = GAMES_DIR/slug/'index.html'
    if not idx.exists(): print(f'ERROR: {idx}'); sys.exit(1)
    html = idx.read_text(encoding='utf-8')
    changes = []

    if re.search(r'drawImage', html) and not re.search(r'imageSmoothingEnabled', html):
        def add_smooth(m):
            changes.append('imageSmoothingEnabled=false')
            return m.group(0) + '\n  ctx.imageSmoothingEnabled = false;'
        html = re.sub(r'((?:const|let|var)\s+ctx\s*=\s*canvas\.getContext\s*\([^)]+\);)', add_smooth, html, 1)

    if html.count('canvas.width') > 2 and not re.search(r'const W\s*=\s*canvas\.width', html):
        def add_cache(m):
            changes.append('canvas size cache (W,H)')
            return m.group(0) + '\n    const W = canvas.width, H = canvas.height;'
        html = re.sub(r'(function\s+(?:gameLoop|update|draw|render|loop|tick)\s*\([^)]*\)\s*\{)', add_cache, html, 1)

    if changes:
        idx.write_text(html, encoding='utf-8')
        print('Applied: ' + ', '.join(changes))
    else:
        print('No optimizations applicable')

    gf = GAMES_DIR/slug/'gameforge.json'
    if gf.exists():
        d = json.loads(gf.read_text())
        d['performance_optimized'] = True
        d['performance_changes'] = changes
        gf.write_text(json.dumps(d, indent=2, ensure_ascii=False))

if __name__ == '__main__': main()
