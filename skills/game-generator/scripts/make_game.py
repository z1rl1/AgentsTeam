#!/usr/bin/env python3
"""
Simple wrapper for game generation — no shell tricks needed.
Usage: python3 make_game.py "<description>" "<user_id>"
OpenClaw calls this with two simple args, slug is generated internally.
"""
import sys, os, random, re, subprocess
from pathlib import Path

WORKSPACE = Path('/root/.openclaw/workspace')
GENERATE  = WORKSPACE / 'skills/game-generator/scripts/generate_game.py'
GAMES_DIR = WORKSPACE / 'games'

GAME_TYPES = {
    'шутер': 'shooter', 'shooter': 'shooter', 'стрел': 'shooter',
    'платформ': 'platformer', 'platform': 'platformer', 'прыг': 'platformer',
    'гонк': 'racing', 'машин': 'racing', 'racing': 'racing', 'car': 'racing',
    'змей': 'snake', 'snake': 'snake',
    'тетрис': 'tetris', 'tetris': 'tetris',
    'кликер': 'clicker', 'clicker': 'clicker',
    'головолом': 'puzzle', 'puzzle': 'puzzle',
    'зомби': 'zombie', 'zombie': 'zombie',
    'танк': 'tank', 'tank': 'tank',
}

THEMES = {
    'киберпанк': 'cyberpunk', 'cyberpunk': 'cyberpunk', 'неон': 'neon', 'neon': 'neon',
    'космос': 'space', 'космич': 'space', 'space': 'space', 'галакт': 'space',
    'ретро': 'retro', 'retro': 'retro',
    'зомби': 'retro', 'zombie': 'retro',
    'неонов': 'neon', 'киберпанков': 'cyberpunk',
}

def make_slug(description):
    d = description.lower()
    game_type = 'game'
    for kw, t in GAME_TYPES.items():
        if kw in d:
            game_type = t
            break
    theme = 'retro'
    for kw, t in THEMES.items():
        if kw in d:
            theme = t
            break
    digits = str(random.randint(1000, 9999))
    return f'{game_type}-{theme}-{digits}'

def make_title(description):
    words = description.strip().split()[:5]
    return ' '.join(w.capitalize() for w in words)

def main():
    if len(sys.argv) < 2:
        print('Usage: python3 make_game.py "<description>" [user_id]')
        sys.exit(1)

    description = sys.argv[1]
    user_id = sys.argv[2] if len(sys.argv) > 2 else 'anonymous'
    slug = make_slug(description)
    title = make_title(description)

    # Determine theme
    d = description.lower()
    theme = 'retro'
    for kw, t in THEMES.items():
        if kw in d:
            theme = t
            break

    game_dir = str(GAMES_DIR / slug)
    print(f'[make_game] slug={slug} title={title} theme={theme}')

    result = subprocess.run(
        ['python3', str(GENERATE), description, title, theme, game_dir, user_id],
        timeout=600
    )
    sys.exit(result.returncode)

if __name__ == '__main__':
    main()
