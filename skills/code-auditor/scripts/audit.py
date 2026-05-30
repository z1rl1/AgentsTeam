#!/usr/bin/env python3
import sys, re
from pathlib import Path

GAMES_DIR = Path('/root/.openclaw/workspace/games')

def main():
    if len(sys.argv) < 2: print('Usage: audit.py <slug>'); sys.exit(1)
    slug = sys.argv[1]
    idx = GAMES_DIR/slug/'index.html'
    if not idx.exists(): print(f'ERROR: {idx}'); sys.exit(1)
    content = idx.read_text(encoding='utf-8', errors='replace')
    lines = content.splitlines()
    size = idx.stat().st_size
    issues, warns = [], []
    for i, l in enumerate(lines):
        if re.search(r'eval\s*\(', l): issues.append(f'L{i+1}: eval() > {l.strip()[:50]}')
        if re.search(r'document\.write\s*\(', l): issues.append(f'L{i+1}: document.write() > {l.strip()[:50]}')
        if re.search(r'console\.log\s*\(', l): warns.append(f'L{i+1}: console.log (debug)')
        if re.search(r'//\s*TODO', l): warns.append(f'L{i+1}: TODO comment')
        if re.search(r'//\s*FIXME', l): warns.append(f'L{i+1}: FIXME comment')
    canvas = len(re.findall(r'ctx\.', content))
    raf = len(re.findall(r'requestAnimationFrame', content))
    print(f'=== AUDIT: {slug} ===')
    print(f'Size: {size//1024}KB  Lines: {len(lines)}  Canvas: {canvas}  rAF: {raf}')
    print(f'Issues ({len(issues)}):'); [print(f'  {i}') for i in issues] or print('  None')
    print(f'Warnings ({len(warns)}):'); [print(f'  {w}') for w in warns] or print('  None')
    result = 'FAIL' if issues else ('WARN' if warns else 'CLEAN')
    print(f'Result: {result}')
    sys.exit(1 if issues else 0)

if __name__ == '__main__': main()
