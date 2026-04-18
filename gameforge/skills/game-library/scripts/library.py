#!/usr/bin/env python3
"""
Game Library — searchable catalog of generated games
Storage: /root/.openclaw/workspace/games/_catalog.json

Usage:
  library.py list
  library.py find <query> [--theme <theme>]
  library.py add <slug> <title> <game_type> <theme> <score> <url>
  library.py top [N]
  library.py stats
"""
import sys, os, json
from datetime import datetime

CATALOG = "/root/.openclaw/workspace/games/_catalog.json"
GAMES_DIR = "/root/.openclaw/workspace/games"

def load():
    if not os.path.exists(CATALOG):
        return {"games": [], "version": "1.0"}
    return json.load(open(CATALOG))

def save(data):
    with open(CATALOG, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def cmd_add(slug, title, game_type, theme, score, url):
    data = load()
    # Remove old entry for same slug
    data["games"] = [g for g in data["games"] if g["slug"] != slug]
    entry = {
        "slug": slug,
        "title": title,
        "type": game_type,
        "theme": theme,
        "score": float(score),
        "url": url,
        "created": datetime.now().isoformat(),
        "tags": [game_type, theme, slug.split("-")[0]],
    }
    data["games"].append(entry)
    save(data)
    print(f"Added to library: {slug} ({game_type}/{theme}) score={score}%")

def cmd_find(query, theme_filter=None):
    data = load()
    query_words = query.lower().split()
    results = []
    for g in data["games"]:
        score_match = 0
        searchable = f"{g['slug']} {g['title']} {g['type']} {g['theme']} {' '.join(g.get('tags',[]))}".lower()
        for word in query_words:
            if word in searchable:
                score_match += 1
        if score_match > 0:
            if theme_filter and g["theme"] != theme_filter:
                continue
            results.append((score_match, g))
    results.sort(key=lambda x: (-x[0], -x[1]["score"]))

    if not results:
        print(f"No games found for: {query}")
        return
    print(f"\nFound {len(results)} game(s) for '{query}':")
    for relevance, g in results[:5]:
        print(f"  [{g['score']:.0f}%] {g['slug']} — {g['title']}")
        print(f"         Type: {g['type']} | Theme: {g['theme']} | URL: {g['url']}")
        print(f"         Created: {g['created'][:10]}")

def cmd_list():
    data = load()
    if not data["games"]:
        print("Library is empty — no games yet"); return
    print(f"\n{'='*60}")
    print(f"  Game Library — {len(data['games'])} games")
    print(f"{'='*60}")
    for g in sorted(data["games"], key=lambda x: x["created"], reverse=True):
        print(f"  {g['score']:3.0f}% | {g['type']:10} | {g['theme']:10} | {g['slug']}")
    print(f"{'='*60}\n")

def cmd_top(n=10):
    data = load()
    top = sorted(data["games"], key=lambda x: x["score"], reverse=True)[:n]
    print(f"\n  Top {n} games by score:")
    for i, g in enumerate(top, 1):
        print(f"  {i:2}. [{g['score']:.0f}%] {g['title']} → {g['url']}")

def cmd_stats():
    data = load()
    games = data["games"]
    if not games:
        print("No games yet"); return
    avg_score = sum(g["score"] for g in games) / len(games)
    types = {}
    themes = {}
    for g in games:
        types[g["type"]] = types.get(g["type"], 0) + 1
        themes[g["theme"]] = themes.get(g["theme"], 0) + 1
    print(f"\n  Library Stats:")
    print(f"  Total games: {len(games)} | Avg score: {avg_score:.1f}%")
    print(f"  Top type:  {max(types, key=types.get)} ({max(types.values())}x)")
    print(f"  Top theme: {max(themes, key=themes.get)} ({max(themes.values())}x)")
    good = sum(1 for g in games if g["score"] >= 80)
    print(f"  Quality: {good}/{len(games)} games score >= 80%")

args = sys.argv[1:]
if not args or args[0] == "list":   cmd_list()
elif args[0] == "find":  cmd_find(" ".join(args[1:]))
elif args[0] == "add" and len(args) >= 7: cmd_add(*args[1:7])
elif args[0] == "top":   cmd_top(int(args[1]) if len(args) > 1 else 10)
elif args[0] == "stats": cmd_stats()
else: print(__doc__)
