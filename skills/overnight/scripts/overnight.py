#!/usr/bin/env python3
"""GameForge Overnight Maintenance. Usage: python3 overnight.py"""
import sys, os, json, subprocess, time, re
from datetime import datetime
from pathlib import Path

WORKSPACE    = Path('/root/.openclaw/workspace')
GAMES_DIR    = WORKSPACE / 'games'
LOGS_DIR     = WORKSPACE / 'hooks' / 'logs'
SKILLS_DIR   = WORKSPACE / 'skills'
SELF_IMPROVE = SKILLS_DIR / 'self-improve'  / 'scripts' / 'self_improve.py'
FIX_BUGS     = SKILLS_DIR / 'game-bug-fixer' / 'scripts' / 'fix_bugs.py'
PLAYTESTER   = SKILLS_DIR / 'game-playtester' / 'scripts' / 'game_playtester.py'
STATS        = SKILLS_DIR / 'observability'  / 'scripts' / 'stats.py'
SALVAGE_MIN, SCORE_OK = 70, 85
LOGS_DIR.mkdir(parents=True, exist_ok=True)


def run(cmd, timeout=120):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout or '') + (r.stderr or '')
    except subprocess.TimeoutExpired:
        return -1, 'TIMEOUT'
    except Exception as e:
        return -2, str(e)


def playtester_score(slug):
    _, out = run(['python3', str(PLAYTESTER), slug], timeout=120)
    m = re.search(r'Result:\s*\d+/\d+\s*\((\d+)%\)', out)
    return int(m.group(1)) if m else None


def get_score(game_dir):
    p = game_dir / 'gameforge.json'
    try:
        return json.loads(p.read_text()).get('qa_score') if p.exists() else None
    except Exception:
        return None


def step1(report):
    print('\n[1/3] Self-improve all skills...')
    report.append('=== STEP 1: self-improve ===')
    if not SELF_IMPROVE.exists():
        print('  SKIP'); return
    rc, out = run(['python3', str(SELF_IMPROVE), 'all'], timeout=900)
    report.append(f'  exit={rc}')
    report += ['  ' + ln for ln in out.strip().splitlines()[-15:]]
    print(f'  Done (exit={rc})')


def step2(report):
    print('\n[2/3] Fix games 70-84%...')
    report.append('=== STEP 2: fix games ===')
    if not (FIX_BUGS.exists() and GAMES_DIR.exists()):
        report.append('  SKIP'); return {}
    cands = []
    for d in sorted(GAMES_DIR.iterdir()):
        if not (d.is_dir() and (d / 'index.html').exists()):
            continue
        s = get_score(d) or playtester_score(d.name)
        if s is not None and SALVAGE_MIN <= s < SCORE_OK:
            cands.append((d.name, s))
    if not cands:
        report.append('  Nothing in 70-84% range'); return {}
    results = {}
    for slug, before in cands:
        print(f'  Fixing {slug} ({before}%)...')
        rc, _ = run(['python3', str(FIX_BUGS), slug], timeout=600)
        after = get_score(GAMES_DIR / slug) or before
        sign = '+' if after >= before else ''
        report.append(f'  {slug}: {before}% -> {after}% ({sign}{after - before}%)')
        results[slug] = {'before': before, 'after': after}
    return results


def step3(report, fixes):
    date = datetime.now().strftime('%Y-%m-%d')
    md = LOGS_DIR / f'overnight-{date}.md'
    lines = [f'# Overnight {date}', '']
    if fixes:
        lines += ['| Slug | Before | After |', '|------|--------|-------|']
        for k, v in fixes.items():
            b, a = v['before'], v['after']
            lines.append(f'| {k} | {b}% | {a}% |')
    lines += ['', '## Log'] + report
    md.write_text('\n'.join(lines))
    print(f'  Report: {md}')
    if STATS.exists():
        _, out = run(['python3', str(STATS), 'week'], 30)
        print(out)


def main():
    print(f"GameForge Overnight - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print('=' * 60)
    r = []
    step1(r)
    fixes = step2(r)
    print('\n[3/3] Report...')
    step3(r, fixes)
    print('\nDone.')


if __name__ == '__main__':
    main()
