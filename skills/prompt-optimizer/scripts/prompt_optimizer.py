#!/usr/bin/env python3
"""
Prompt Optimizer — tracks game generation quality, evolves the base prompt
Кarpathy loop: generate → test → score → if bad → improve prompt → repeat

Usage:
  prompt_optimizer.py record <slug> <score> <theme> <game_type> [feedback]
  prompt_optimizer.py analyze        → what patterns produce high/low scores
  prompt_optimizer.py best-prompt    → returns current best prompt additions
  prompt_optimizer.py improve        → auto-generates prompt improvement suggestions
"""
import sys, os, json
from datetime import datetime

DATA_DIR = "/root/.openclaw/workspace/memory/prompt_data"
PROMPT_FILE = "/root/.openclaw/workspace/memory/prompt_data/current_improvements.json"
os.makedirs(DATA_DIR, exist_ok=True)

LOG_FILE = f"{DATA_DIR}/generation_log.jsonl"

def cmd_record(slug, score, theme, game_type, feedback=""):
    entry = {
        "slug": slug,
        "score": float(score),
        "theme": theme,
        "game_type": game_type,
        "feedback": feedback,
        "date": datetime.now().isoformat(),
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    status = "GOOD" if float(score) >= 80 else "WARN" if float(score) >= 60 else "BAD"
    print(f"Recorded: {slug} score={score}% [{status}]")

def load_log():
    if not os.path.exists(LOG_FILE): return []
    return [json.loads(l) for l in open(LOG_FILE) if l.strip()]

def cmd_analyze():
    entries = load_log()
    if not entries:
        print("No data yet — generate some games first!"); return

    # Overall stats
    scores = [e["score"] for e in entries]
    avg = sum(scores) / len(scores)
    good = sum(1 for s in scores if s >= 80)
    bad  = sum(1 for s in scores if s < 60)

    # By theme
    theme_scores = {}
    for e in entries:
        t = e["theme"]
        if t not in theme_scores: theme_scores[t] = []
        theme_scores[t].append(e["score"])

    # By game_type
    type_scores = {}
    for e in entries:
        gt = e["game_type"]
        if gt not in type_scores: type_scores[gt] = []
        type_scores[gt].append(e["score"])

    print(f"\n{'='*55}")
    print(f"  Prompt Optimizer — Generation Quality Analysis")
    print(f"{'='*55}")
    print(f"  Total games: {len(entries)}")
    print(f"  Avg score: {avg:.1f}% | Good(>=80%): {good} | Bad(<60%): {bad}")
    print(f"\n  By Theme:")
    for t, sc in sorted(theme_scores.items(), key=lambda x: -sum(x[1])/len(x[1])):
        a = sum(sc)/len(sc)
        print(f"    {t:12} avg={a:.0f}% ({len(sc)} games)")
    print(f"\n  By Game Type:")
    for gt, sc in sorted(type_scores.items(), key=lambda x: -sum(x[1])/len(x[1])):
        a = sum(sc)/len(sc)
        print(f"    {gt:15} avg={a:.0f}% ({len(sc)} games)")

    # Failures
    failures = [e for e in entries if e["score"] < 60]
    if failures:
        print(f"\n  Recent failures (score < 60%):")
        for e in failures[-5:]:
            print(f"    {e['slug']} ({e['game_type']}/{e['theme']}) score={e['score']:.0f}%")
            if e.get("feedback"):
                print(f"      User said: {e['feedback']}")
    print(f"{'='*55}\n")

def cmd_best_prompt():
    """Returns current prompt improvements to inject into generate_game.py"""
    if not os.path.exists(PROMPT_FILE):
        print("NO_IMPROVEMENTS")
        return ""

    data = json.load(open(PROMPT_FILE))
    improvements = data.get("improvements", [])
    if not improvements:
        print("NO_IMPROVEMENTS")
        return ""

    result = "\n".join(f"- {imp}" for imp in improvements)
    print(result)
    return result

def cmd_improve():
    """Analyze failures and generate prompt improvement suggestions"""
    entries = load_log()
    if len(entries) < 5:
        print("Need at least 5 games to analyze. Keep generating!"); return

    failures = [e for e in entries if e["score"] < 60]
    if not failures:
        print("All games scoring >= 60%! System is working well.")
        return

    # Pattern analysis
    improvements = []

    # Check if specific themes always fail
    theme_fails = {}
    for e in failures:
        t = e["theme"]
        theme_fails[t] = theme_fails.get(t, 0) + 1
    for theme, count in theme_fails.items():
        if count >= 3:
            improvements.append(f"For {theme} theme: emphasize glow effects and theme-specific visual identity more strongly")

    # Check if game loop is missing
    no_loop_count = sum(1 for e in failures if "loop" in e.get("feedback", "").lower())
    if no_loop_count >= 2:
        improvements.append("Always include explicit requestAnimationFrame game loop with deltaTime for smooth animation")

    # Generic improvements for consistent failures
    if len(failures) > len(entries) * 0.3:
        improvements.extend([
            "Start the game code with a complete skeleton: canvas setup, game loop, input handlers, then fill in mechanics",
            "Always implement game over detection as a boolean flag checked every frame",
            "Include explicit start screen: draw title text and 'Press Enter to start' before game begins",
        ])

    if not improvements:
        improvements = [
            "Make game mechanics more complete with proper collision detection",
            "Always include score display updating every frame",
        ]

    # Save improvements
    data = {
        "updated": datetime.now().isoformat(),
        "based_on": f"{len(entries)} games, {len(failures)} failures",
        "improvements": improvements,
    }
    with open(PROMPT_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(improvements)} prompt improvements:")
    for imp in improvements:
        print(f"  + {imp}")
    print(f"\nSaved to: {PROMPT_FILE}")
    print("generate_game.py will use these on next run.")

args = sys.argv[1:]
if not args: print(__doc__)
elif args[0] == "record"  and len(args) >= 5: cmd_record(args[1], args[2], args[3], args[4], " ".join(args[5:]))
elif args[0] == "analyze":  cmd_analyze()
elif args[0] == "best-prompt": cmd_best_prompt()
elif args[0] == "improve":  cmd_improve()
else: print(__doc__)
