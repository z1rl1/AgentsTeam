#!/usr/bin/env python3
import sys, subprocess
from pathlib import Path

GAMES_DIR = Path('/root/.openclaw/workspace/games')
DEPLOY_SH = Path('/root/.openclaw/workspace/skills/game-generator/scripts/deploy.sh')

def main():
    if len(sys.argv) < 2: print('Usage: deploy.py <slug>'); sys.exit(1)
    slug = sys.argv[1]
    game_dir = GAMES_DIR/slug
    if not game_dir.exists(): print(f'ERROR: {game_dir}'); sys.exit(1)
    if not (game_dir/'index.html').exists(): print('ERROR: no index.html'); sys.exit(1)
    if not (game_dir/'gameforge.json').exists(): print('ERROR: no gameforge.json'); sys.exit(1)
    if not DEPLOY_SH.exists(): print(f'ERROR: {DEPLOY_SH}'); sys.exit(1)
    r = subprocess.run(['bash', str(DEPLOY_SH), str(game_dir), slug])
    sys.exit(r.returncode)

if __name__ == '__main__': main()
