#!/usr/bin/env python3
"""
GameForge Difficulty Adjuster — patches numeric params via regex, no LLM.
Usage: python3 difficulty.py <slug> <easy|normal|hard|extreme>
"""
import sys, json, re, shutil
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/root/.openclaw/workspace')
GAMES_DIR = WORKSPACE / 'games'

LEVELS = {
    'easy':    {'speed': 0.7,  'damage': 0.5,  'hp': 0.7,  'spawn': 0.6},
    'normal':  {'speed': 1.0,  'damage': 1.0,  'hp': 1.0,  'spawn': 1.0},
    'hard':    {'speed': 1.4,  'damage': 1.5,  'hp': 1.5,  'spawn': 1.6},
    'extreme': {'speed': 2.0,  'damage': 2.5,  'hp': 2.0,  'spawn': 2.5},
}

# (category, regex pattern with 2 groups: prefix, number)
PATTERNS = [
    ('speed',  r'((?:SPEED|speed|playerSpeed|moveSpeed|velocity|PLAYER_SPEED|MOVE_SPEED|BULLET_SPEED|bulletSpeed)\s*[=:]\s*)([0-9]+(?:\.[0-9]+)?)'),
    ('damage', r'((?:DAMAGE|damage|attackDamage|dmg|PLAYER_DAMAGE|bulletDamage|BULLET_DAMAGE)\s*[=:]\s*)([0-9]+(?:\.[0-9]+)?)'),
    ('damage', r'((?:this\.damage|this\.dmg)\s*=\s*)([0-9]+(?:\.[0-9]+)?)'),
    ('hp',     r'((?:HP|MAX_HP|maxHp|health|MAX_HEALTH|maxHealth|ENEMY_HP|enemyHp)\s*[=:]\s*)([0-9]+(?:\.[0-9]+)?)'),
    ('hp',     r'((?:this\.hp|this\.health|this\.maxHealth)\s*=\s*)([0-9]+(?:\.[0-9]+)?)'),
    ('spawn',  r'((?:SPAWN_RATE|spawnRate|SPAWN_INTERVAL|spawnInterval|ENEMY_COUNT|enemyCount|MAX_ENEMIES|maxEnemies|WAVE_SIZE|waveSize)\s*[=:]\s*)([0-9]+(?:\.[0-9]+)?)'),
]


def fmt_num(v):
    return str(int(v)) if v == int(v) else f'{v:.4f}'.rstrip('0').rstrip('.')


def net_mult(old_lv, new_lv, cat):
    o = LEVELS.get(old_lv, LEVELS['normal'])[cat]
    n = LEVELS[new_lv][cat]
    return n / o if o else n


def patch(html, old_lv, new_lv):
    total = 0
    for cat, pat in PATTERNS:
        mult = net_mult(old_lv, new_lv, cat)
        if abs(mult - 1.0) < 1e-9:
            continue

        def repl(m, mult=mult):
            prefix = m.group(1)
            try:
                num = float(m.group(2))
            except ValueError:
                return m.group(0)
            if num == 0:
                return m.group(0)
            return prefix + fmt_num(num * mult)

        new_html, cnt = re.subn(pat, repl, html)
        if cnt:
            print(f'  [{cat}] {cnt}x  x{mult:.3f}')
            html = new_html
            total += cnt
    return html, total


def read_meta(slug):
    p = GAMES_DIR / slug / 'gameforge.json'
    try:
        return json.loads(p.read_text()) if p.exists() else {}
    except Exception:
        return {}


def write_meta(slug, meta):
    (GAMES_DIR / slug / 'gameforge.json').write_text(
        json.dumps(meta, indent=2, ensure_ascii=False))


def adjust(slug, new_lv):
    if new_lv not in LEVELS:
        print(f'Unknown level: {new_lv}. Use: {", ".join(LEVELS)}'); return False
    index_path = GAMES_DIR / slug / 'index.html'
    if not index_path.exists():
        print(f'ERROR: {index_path} not found'); return False

    meta   = read_meta(slug)
    old_lv = meta.get('difficulty', 'normal')
    if old_lv not in LEVELS:
        old_lv = 'normal'
    if old_lv == new_lv:
        print(f'Already at "{new_lv}"'); return True

    print(f'[difficulty] {slug}: {old_lv} -> {new_lv}')
    html = index_path.read_text(encoding='utf-8')

    backup = index_path.with_suffix('.html.diff_bak')
    shutil.copy2(index_path, backup)

    html, total = patch(html, old_lv, new_lv)
    if total == 0:
        print('  No matching params found (game may use different variable names)')
        backup.unlink(missing_ok=True)
    else:
        index_path.write_text(html, encoding='utf-8')
        print(f'  {total} total patches written')

    meta['difficulty']          = new_lv
    meta['difficulty_changed_at'] = datetime.utcnow().isoformat() + 'Z'
    write_meta(slug, meta)
    print('[difficulty] Done.')
    return True


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f'Usage: python3 difficulty.py <slug> <{"|".join(LEVELS)}>'); sys.exit(1)
    ok = adjust(sys.argv[1], sys.argv[2].lower())
    sys.exit(0 if ok else 1)
