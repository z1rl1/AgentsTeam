#!/usr/bin/env python3
import sys, subprocess
from pathlib import Path

WORKSPACE = Path('/root/.openclaw/workspace')

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(WORKSPACE))
    return r.returncode, r.stdout.strip()

def main():
    msg = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else None
    if not msg:
        games = len(list((WORKSPACE/'games').iterdir())) if (WORKSPACE/'games').exists() else 0
        _, status = run(['git', 'status', '--short'])
        files = len([l for l in status.splitlines() if l.strip()])
        parts = []
        if games: parts.append(f'{games} game(s)')
        if files: parts.append(f'{files} file(s) changed')
        msg = 'feat: update ' + (', '.join(parts) or 'workspace')
    run(['git', 'add', '-A'])
    rc2, st = run(['git', 'status', '--short'])
    if not st: print('Nothing to commit'); sys.exit(0)
    rc, out = run(['git', 'commit', '-m', msg])
    if rc: print(f'ERROR: {out}'); sys.exit(1)
    print(out)
    _, log = run(['git', 'log', '--oneline', '-3'])
    print(log)

if __name__ == '__main__': main()
