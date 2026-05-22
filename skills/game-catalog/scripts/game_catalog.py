#!/usr/bin/env python3
import os
from datetime import datetime

GAMES_DIR = "/root/.openclaw/workspace/games"

if not os.path.exists(GAMES_DIR) or not os.listdir(GAMES_DIR):
    print("No games yet.")
    exit()

games = sorted(os.listdir(GAMES_DIR))
print("=" * 52)
print("  GAMEFORGE — CREATED GAMES")
print("=" * 52)
for i, slug in enumerate(games, 1):
    html = os.path.join(GAMES_DIR, slug, "index.html")
    if not os.path.exists(html): continue
    date = datetime.fromtimestamp(os.path.getmtime(html)).strftime("%d.%m.%Y")
    size = os.path.getsize(html) // 1024
    print(f"  {i}. {slug}")
    print(f"     https://{slug}.surge.sh  [{date}, {size}KB]")
print("-" * 52)
print(f"  Total: {len(games)} games")
print("=" * 52)
