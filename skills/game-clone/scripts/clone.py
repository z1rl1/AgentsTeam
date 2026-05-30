#!/usr/bin/env python3
import sys, os, shutil, json, random, string
from datetime import datetime, timezone
from pathlib import Path

GAMES_DIR = Path('/root/.openclaw/workspace/games')

def gen_slug(src):
    v2 = src + '-v2'
    if not (GAMES_DIR/v2).exists(): return v2
    return src + '-' + ''.join(random.choices(string.digits, k=4))

def main():
    if len(sys.argv) < 2: print('Usage: clone.py <source> [new_slug]'); sys.exit(1)
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else ''
    src_dir = GAMES_DIR/src
    if not src_dir.exists(): print(f'ERROR: {src_dir}'); sys.exit(1)
    if not dst: dst = gen_slug(src); print(f'Auto slug: {dst}')
    dst_dir = GAMES_DIR/dst
    if dst_dir.exists(): print(f'ERROR: {dst_dir} exists'); sys.exit(1)
    shutil.copytree(src_dir, dst_dir)
    gf = dst_dir/'gameforge.json'
    if gf.exists():
        d = json.loads(gf.read_text())
        d['slug'] = dst
        d['cloned_from'] = src
        d['created_at'] = datetime.now(timezone.utc).isoformat()
        gf.write_text(json.dumps(d, indent=2, ensure_ascii=False))
    print(f'Cloned {src} -> {dst}')

if __name__ == '__main__': main()
