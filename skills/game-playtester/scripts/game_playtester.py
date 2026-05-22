#!/usr/bin/env python3
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path('/root/.openclaw/workspace')
GAMES_DIR = ROOT / 'games'


def read_metadata(game_dir):
    path = game_dir / 'gameforge.json'
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {}


def has(pattern, code):
    return bool(re.search(pattern, code, re.I | re.S))


def words(*items):
    return [item.encode("utf-8").decode("unicode_escape") for item in items]


def canvas_large_or_responsive(code):
    explicit_large = False
    canvas_tag = re.search(r'<canvas[^>]*>', code, re.I)
    if canvas_tag:
        width = re.search(r'width=["\']?(\d+)', canvas_tag.group(0), re.I)
        height = re.search(r'height=["\']?(\d+)', canvas_tag.group(0), re.I)
        if width and height:
            explicit_large = int(width.group(1)) >= 900 and int(height.group(1)) >= 500

    width_assigns = [int(n) for n in re.findall(r'canvas\.width\s*=\s*(\d+)', code, re.I)]
    height_assigns = [int(n) for n in re.findall(r'canvas\.height\s*=\s*(\d+)', code, re.I)]
    if width_assigns and height_assigns:
        explicit_large = explicit_large or max(width_assigns) >= 900 and max(height_assigns) >= 500

    responsive = has(r'innerWidth|innerHeight|devicePixelRatio|resizeCanvas|addEventListener\(["\']resize', code)
    css_large = has(r'100vw|100vh|80vh|90vh|min\(|max-width\s*:\s*100vw|max-height\s*:\s*100vh|max-width\s*:\s*1280|width\s*:\s*100%', code)
    return explicit_large or (responsive and css_large)


def count_draw_calls(code):
    return len(re.findall(r'ctx\.(fillRect|strokeRect|arc|ellipse|lineTo|quadraticCurveTo|bezierCurveTo|drawImage|fillText|strokeText|createLinearGradient|createRadialGradient)', code))


def count_arrays_and_entities(code):
    array_defs = len(re.findall(r'\b(?:const|let|var)\s+\w+\s*=\s*\[', code))
    pushes = len(re.findall(r'\.push\s*\(', code))
    classes = len(re.findall(r'\bclass\s+\w+', code))
    object_literals = len(re.findall(r'\{\s*(?:x|y|vx|vy|width|height|hp|health|type)\s*:', code))
    return array_defs + pushes + classes + object_literals


def has_rich_scene(code):
    visual_terms = len(re.findall(r'gradient|shadow|particle|spark|debris|trail|glow|shake|flash|explosion|parallax|background|building|cloud|star|window|tree|mountain|city|wave|dust|smoke', code, re.I))
    return visual_terms >= 12 and count_draw_calls(code) >= 55


def has_core_gameplay_depth(code):
    mechanics = [
        r'collision|intersect|overlap|distance',
        r'gravity|velocity|vx|vy|accel|friction|bounce',
        r'level|wave|round|stage|progress|nextLevel',
        r'enem|target|obstacle|goal|food|block|projectile|bullet',
        r'health|hp|lives|damage|score|combo|ammo|shots',
        r'particle|debris|spark|explosion|shake|flash|trail',
    ]
    return sum(1 for pat in mechanics if has(pat, code)) >= 5


def genre_checks(description, slug, code):
    d = f'{description} {slug}'.lower()
    checks = []
    platform_words = words('\u043f\u043b\u0430\u0442\u0444\u043e\u0440\u043c', '\u0431\u0430\u043d\u0434\u0438\u0442', '\u0443\u0434\u0430\u0440', '\u0433\u043e\u0440\u043e\u0434', '\u0433\u0435\u0440\u043e\u0439') + ['platform', 'beat', 'punch', 'street', 'hero']
    snake_words = words('\u0437\u043c\u0435\u0439') + ['snake']
    tetris_words = words('\u0442\u0435\u0442\u0440\u0438\u0441') + ['tetris']
    shooter_words = words('\u0441\u0442\u0440\u0435\u043b', '\u0437\u043e\u043c\u0431\u0438') + ['shooter', 'zombie', 'shoot']

    if any(w in d for w in platform_words):
        checks.extend([
            ('Platform physics (gravity/jump/velocity)', r'gravity|vy|velocity|jump|grounded|onGround', True, False),
            ('Scrolling camera / wider level', r'camera|scroll|offsetX|worldWidth|levelWidth|translate\(', True, False),
            ('Enemies with behavior', r'enem(y|ies)|bandit|thug|patrol|chase|ai|attackCooldown', True, False),
            ('Combat / hit detection', r'punch|attack|hitbox|damage|knockback|combo|cooldown', True, False),
            ('Health/lives bars', r'health|hp|lives|barWidth|drawHealth', True, False),
            ('City/platform scenery', r'building|city|window|street|platform|rooftop|sign|lamp', False, False),
        ])
    if any(w in d for w in snake_words):
        checks.extend([
            ('Snake growth', r'snake|grow|food', True, False),
            ('Progression or obstacles', r'obstacle|level|speed|power|bonus', False, False),
        ])
    if any(w in d for w in tetris_words):
        checks.extend([
            ('Tetris board/grid', r'grid|board|matrix|tetromino|piece', True, False),
            ('Line clearing', r'clearLines|lineClear|lines|rows', True, False),
            ('Next/hold preview', r'next|preview|hold|ghost', False, False),
        ])
    if any(w in d for w in shooter_words):
        checks.extend([
            ('Projectiles/weapons', r'bullet|projectile|shoot|fire|ammo', True, False),
            ('Enemy waves/spawning', r'spawn|wave|zombie|enemy', True, False),
        ])
    return checks
def test_game(slug):
    game_dir = GAMES_DIR / slug
    path = game_dir / 'index.html'
    if not path.exists():
        print(f'Not found: {path}')
        return 1
    code = path.read_text(encoding='utf-8', errors='ignore')
    meta = read_metadata(game_dir)
    description = meta.get('description', '')

    checks = [
        ('Complete HTML document', r'<!DOCTYPE html.*</html>', True, False),
        ('Canvas renderer', r'<canvas', True, False),
        ('Large/responsive canvas', None, True, False),
        ('requestAnimationFrame loop', r'requestAnimationFrame', True, False),
        ('Delta-time or frame timing', r'delta|dt|lastTime|timestamp|performance\.now', True, False),
        ('Start/restart controls', r'Enter|Space|start|restart', True, False),
        ('Game over or win state', r'game.?over|state\s*=\s*["\'](?:gameover|win)|running\s*=\s*false|victory', True, False),
        ('Score/objective UI', r'score|points|objective', True, False),
        ('Keyboard controls', r'ArrowUp|ArrowLeft|KeyA|KeyD|KeyW|KeyS|keydown', True, False),
        ('GameForge metadata', None, True, False),
        ('Substantial code size', None, True, False),
        ('Rich scene density', None, True, False),
        ('Core gameplay depth', None, True, False),
        ('Multiple entities/systems', None, True, False),
        ('Rich canvas drawing', None, True, False),
        ('Animated visual effects', r'particle|spark|shake|flash|trail|glow|shadowBlur|animation|frame|pulse', False, False),
        ('No blocking dialogs', r'alert\s*[(]|prompt\s*[(]|confirm\s*[(]', True, True),
        ('No external dependencies', r'https?://|cdn\.|<script\s+src=|<link\s+[^>]*href=', True, True),
    ]
    checks.extend(genre_checks(description, slug, code))

    print(f'\nTesting: {slug}\n' + '=' * 58)
    passed = 0
    required_failed = []
    for name, pat, required, invert in checks:
        if name == 'Large/responsive canvas':
            found = canvas_large_or_responsive(code)
        elif name == 'GameForge metadata':
            found = bool(meta.get('description')) and bool(meta.get('title'))
        elif name == 'Substantial code size':
            found = len(code.encode('utf-8')) >= 32000 or code.count('\n') >= 450
        elif name == 'Rich scene density':
            found = has_rich_scene(code)
        elif name == 'Core gameplay depth':
            found = has_core_gameplay_depth(code)
        elif name == 'Multiple entities/systems':
            found = count_arrays_and_entities(code) >= 12
        elif name == 'Rich canvas drawing':
            found = count_draw_calls(code) >= 55
        else:
            found = has(pat, code)
        ok = (not found) if invert else found
        if ok:
            passed += 1
        elif required:
            required_failed.append(name)
        icon = 'OK' if ok else ('FAIL' if required else 'WARN')
        print(f'  [{icon}] {name}')

    pct = int(passed / len(checks) * 100)
    if required_failed:
        pct = min(pct, 74)
    status = 'READY' if pct >= 85 and not required_failed else 'ISSUES' if pct >= 65 else 'BROKEN'
    print('-' * 58)
    print(f'  Result: {passed}/{len(checks)} ({pct}%) - {status}')
    if required_failed:
        print('  Required failures: ' + ', '.join(required_failed))
    print('=' * 58)
    return 0 if status == 'READY' else 1


if __name__ == '__main__':
    slug = sys.argv[1] if len(sys.argv) > 1 else None
    if slug:
        sys.exit(test_game(slug))
    if GAMES_DIR.exists():
        code = 0
        for game in sorted(p.name for p in GAMES_DIR.iterdir() if p.is_dir()):
            code = max(code, test_game(game))
        sys.exit(code)
