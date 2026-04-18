#!/usr/bin/env python3
"""
User Memory System — saves VK user preferences and game history
Usage:
  memory.py get <user_id>
  memory.py save <user_id> <slug> <game_type> <theme>
  memory.py find <user_id> <game_type>
  memory.py stats
"""
import sys, os, json
from datetime import datetime

MEMORY_DIR = "/root/.openclaw/workspace/memory/users"

def get_profile(user_id):
    path = f"{MEMORY_DIR}/{user_id}.json"
    if not os.path.exists(path):
        return {"user_id": user_id, "games": [], "favorite_theme": None, "favorite_type": None, "total_games": 0}
    return json.load(open(path))

def save_profile(profile):
    os.makedirs(MEMORY_DIR, exist_ok=True)
    uid = profile["user_id"]
    with open(f"{MEMORY_DIR}/{uid}.json", "w") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

def cmd_get(user_id):
    p = get_profile(user_id)
    print(f"User: {user_id}")
    print(f"  Total games: {p['total_games']}")
    print(f"  Favorite theme: {p['favorite_theme'] or 'not set'}")
    print(f"  Favorite type: {p['favorite_type'] or 'not set'}")
    if p["games"]:
        print(f"  Last games:")
        for g in p["games"][-3:]:
            print(f"    - {g['slug']} ({g['type']}/{g['theme']}) — {g['date'][:10]}")
    return p

def cmd_save(user_id, slug, game_type, theme):
    p = get_profile(user_id)
    entry = {"slug": slug, "type": game_type, "theme": theme, "date": datetime.now().isoformat(), "url": f"https://{slug}.surge.sh"}
    p["games"].append(entry)
    p["games"] = p["games"][-20:]  # keep last 20
    p["total_games"] += 1

    # Update favorites (most frequent)
    types  = [g["type"]  for g in p["games"]]
    themes = [g["theme"] for g in p["games"]]
    p["favorite_type"]  = max(set(types),  key=types.count)  if types  else None
    p["favorite_theme"] = max(set(themes), key=themes.count) if themes else None

    save_profile(p)
    print(f"Saved: {user_id} → {slug} ({game_type}/{theme})")
    print(f"Total games: {p['total_games']} | Favorite: {p['favorite_theme']}/{p['favorite_type']}")

def cmd_find(user_id, game_type):
    p = get_profile(user_id)
    matches = [g for g in p["games"] if g["type"] == game_type]
    if not matches:
        print(f"No previous {game_type} games for user {user_id}")
        return
    last = matches[-1]
    print(f"Found previous {game_type}: {last['slug']}")
    print(f"  URL: {last['url']}")
    print(f"  Theme: {last['theme']} | Date: {last['date'][:10]}")

def cmd_stats():
    if not os.path.exists(MEMORY_DIR):
        print("No users yet"); return
    users = os.listdir(MEMORY_DIR)
    total_games = 0
    type_counts, theme_counts = {}, {}
    for f in users:
        p = json.load(open(f"{MEMORY_DIR}/{f}"))
        total_games += p["total_games"]
        for g in p["games"]:
            type_counts[g["type"]] = type_counts.get(g["type"], 0) + 1
            theme_counts[g["theme"]] = theme_counts.get(g["theme"], 0) + 1
    print(f"Users: {len(users)} | Total games: {total_games}")
    if type_counts:
        top_type = max(type_counts, key=type_counts.get)
        print(f"  Most popular type: {top_type} ({type_counts[top_type]}x)")
    if theme_counts:
        top_theme = max(theme_counts, key=theme_counts.get)
        print(f"  Most popular theme: {top_theme} ({theme_counts[top_theme]}x)")

cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
if cmd == "get"   and len(sys.argv) > 2: cmd_get(sys.argv[2])
elif cmd == "save" and len(sys.argv) > 5: cmd_save(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
elif cmd == "find" and len(sys.argv) > 3: cmd_find(sys.argv[2], sys.argv[3])
elif cmd == "stats": cmd_stats()
else: print(__doc__)
