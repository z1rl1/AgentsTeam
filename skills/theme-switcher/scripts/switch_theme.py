#!/usr/bin/env python3
"""
GameForge Theme Switcher — swaps color palette without LLM.
Usage: python3 switch_theme.py <slug> <cyberpunk|space|retro|neon|minimal>
"""
import sys, json, re
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('/root/.openclaw/workspace')
GAMES_DIR = WORKSPACE / 'games'

THEMES = {
    'cyberpunk': {'bg':'#0a0010','primary':'#ff00ff','secondary':'#00ffff','accent':'#ff006e','text':'#ffffff'},
    'space':     {'bg':'#000820','primary':'#4488ff','secondary':'#ffcc00','accent':'#00aaff','text':'#ffffff'},
    'retro':     {'bg':'#1a0a00','primary':'#ff6600','secondary':'#cc4400','accent':'#ff9900','text':'#ffcc00'},
    'neon':      {'bg':'#000000','primary':'#00ff41','secondary':'#00cc33','accent':'#39ff14','text':'#00ff41'},
    'minimal':   {'bg':'#0d1117','primary':'#ff4444','secondary':'#cc0000','accent':'#ff6666','text':'#ffffff'},
}


def hex_variants(h):
    h = h.lstrip('#')
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return [
        '#' + h.lower(), '#' + h.upper(),
        f'rgb({r},{g},{b})', f'rgb({r}, {g}, {b})',
        f'rgba({r},{g},{b},1)', f'rgba({r},{g},{b},1.0)',
    ]


def replace_colors(html, old_pal, new_pal):
    total = 0
    for role in ('bg', 'primary', 'secondary', 'accent', 'text'):
        old_hex, new_hex = old_pal[role], new_pal[role]
        if old_hex.lower() == new_hex.lower():
            continue
        for variant in hex_variants(old_hex):
            cnt = html.count(variant)
            if cnt:
                html = html.replace(variant, new_hex)
                total += cnt
                print(f'  [{role}] {cnt}x "{variant}" -> "{new_hex}"')
    return html, total


def css_override(pal):
    return (
        f'\n<style>\n/* theme-switcher override */\n'
        f':root{{--bg:{pal["bg"]};--primary:{pal["primary"]};'
        f'--secondary:{pal["secondary"]};--accent:{pal["accent"]};--text:{pal["text"]};}}\n'
        f'body{{background:{pal["bg"]} !important;color:{pal["text"]} !important;}}\n'
        f'canvas{{background:{pal["bg"]} !important;}}\n</style>\n'
    )


def inject_override(html, pal):
    closes = [m.start() for m in re.finditer(r'</style>', html, re.I)]
    block  = css_override(pal)
    if closes:
        pos = closes[-1]
        inner = block.replace('<style>', '').replace('</style>', '')
        return html[:pos] + inner + html[pos:]
    m = re.search(r'</head>', html, re.I)
    if m:
        return html[:m.start()] + block + html[m.start():]
    return block + html


def read_meta(slug):
    p = GAMES_DIR / slug / 'gameforge.json'
    try:
        return json.loads(p.read_text()) if p.exists() else {}
    except Exception:
        return {}


def write_meta(slug, meta):
    (GAMES_DIR / slug / 'gameforge.json').write_text(
        json.dumps(meta, indent=2, ensure_ascii=False))


def switch_theme(slug, new_theme):
    if new_theme not in THEMES:
        print(f'Unknown theme: {new_theme}. Use: {", ".join(THEMES)}'); return False
    index_path = GAMES_DIR / slug / 'index.html'
    if not index_path.exists():
        print(f'ERROR: {index_path} not found'); return False

    meta      = read_meta(slug)
    old_theme = meta.get('theme', 'minimal')
    if old_theme not in THEMES:
        old_theme = 'minimal'
    if old_theme == new_theme:
        print(f'Already using theme "{new_theme}"'); return True

    print(f'[theme-switcher] {slug}: {old_theme} -> {new_theme}')
    html = index_path.read_text(encoding='utf-8')
    html, n = replace_colors(html, THEMES[old_theme], THEMES[new_theme])
    if n == 0:
        print('  No hex matches, injecting CSS override')
        html = inject_override(html, THEMES[new_theme])
    else:
        print(f'  {n} total replacements')
    index_path.write_text(html, encoding='utf-8')

    meta['theme']            = new_theme
    meta['theme_changed_at'] = datetime.utcnow().isoformat() + 'Z'
    write_meta(slug, meta)
    print('[theme-switcher] Done.')
    return True


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f'Usage: python3 switch_theme.py <slug> <{"|".join(THEMES)}>'); sys.exit(1)
    ok = switch_theme(sys.argv[1], sys.argv[2].lower())
    sys.exit(0 if ok else 1)
