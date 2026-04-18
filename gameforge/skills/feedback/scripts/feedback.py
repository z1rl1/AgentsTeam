#!/usr/bin/env python3
"""
User Feedback System — saves what users like/dislike about games
Agent calls this when user says: "не нравится", "плохо", "слишком", "хочу чтобы"

Usage:
  feedback.py add <user_id> <slug> <sentiment> "<text>"
    sentiment: positive | negative | suggestion

  feedback.py get <user_id>
    → returns user constraints for LLM prompt

  feedback.py analyze
    → global patterns: what ALL users dislike most

  feedback.py detect "<message>"
    → 0=neutral, 1=positive, 2=negative/suggestion (for agent to auto-detect)
"""
import sys, os, json, re
from datetime import datetime

FEEDBACK_DIR = "/root/.openclaw/workspace/memory/feedback"
os.makedirs(FEEDBACK_DIR, exist_ok=True)

# Keywords that trigger feedback detection
NEGATIVE_KEYWORDS = [
    "не нравится", "плохо", "ужасно", "скучно", "медленно", "слишком",
    "не то", "другой", "измени", "сделай иначе", "не хочу", "убери",
    "без", "не надо", "хватит", "надоело", "плохая", "плохой",
]
POSITIVE_KEYWORDS = [
    "нравится", "круто", "классно", "отлично", "супер", "огонь",
    "топ", "красиво", "понравилось", "класс", "лайк", "здорово",
]
SUGGESTION_KEYWORDS = [
    "хочу чтобы", "сделай", "добавь", "хочу", "лучше если", "можно",
    "попробуй", "было бы", "хотел бы", "хотела бы",
]

def get_feedback(user_id):
    path = f"{FEEDBACK_DIR}/{user_id}.json"
    if not os.path.exists(path):
        return {"user_id": user_id, "entries": [], "constraints": [], "prefs": {}}
    return json.load(open(path))

def save_feedback(data):
    uid = data["user_id"]
    with open(f"{FEEDBACK_DIR}/{uid}.json", "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def cmd_add(user_id, slug, sentiment, text):
    data = get_feedback(user_id)
    entry = {
        "slug": slug,
        "sentiment": sentiment,  # positive | negative | suggestion
        "text": text,
        "date": datetime.now().isoformat(),
    }
    data["entries"].append(entry)
    data["entries"] = data["entries"][-50:]  # keep last 50

    # Extract constraint from negative feedback
    if sentiment == "negative":
        constraint = extract_constraint(text)
        if constraint and constraint not in data["constraints"]:
            data["constraints"].append(constraint)
            print(f"New constraint: {constraint}")

    # Extract preference from suggestion
    if sentiment == "suggestion":
        extract_preference(data, text)

    save_feedback(data)
    print(f"Feedback saved: {user_id} | {sentiment} | {slug}")
    print(f"Total constraints: {len(data['constraints'])}")

def extract_constraint(text):
    """Turn negative feedback into a prompt constraint"""
    text = text.lower().strip()
    mappings = {
        "медленно":    "Make the game faster and more responsive",
        "скучно":      "Make gameplay more exciting with power-ups and variety",
        "темно":       "Use brighter colors and higher contrast",
        "громко":      "Make sounds subtle and not annoying",
        "сложно":      "Make the game easier for beginners",
        "легко":       "Make the game more challenging",
        "маленьк":     "Make game elements larger and more visible",
        "не понятно":  "Add clear instructions and tutorial text",
        "без звука":   "Remove all sound effects",
        "без музыки":  "No background music",
        "ретро":       "Do not use retro theme",
        "киберпанк":   "Do not use cyberpunk theme",
    }
    for keyword, constraint in mappings.items():
        if keyword in text:
            return constraint
    # Generic constraint from text
    if len(text) > 5:
        return f"User feedback (avoid this): {text}"
    return None

def extract_preference(data, text):
    """Extract explicit preferences from suggestions"""
    text = text.lower()
    if "быстр" in text: data["prefs"]["speed"] = "fast"
    if "медленн" in text: data["prefs"]["speed"] = "slow"
    if "яркий" in text or "яркие" in text: data["prefs"]["colors"] = "bright"
    if "тёмный" in text or "тёмные" in text: data["prefs"]["colors"] = "dark"
    if "простой" in text: data["prefs"]["difficulty"] = "easy"
    if "сложный" in text: data["prefs"]["difficulty"] = "hard"
    if "звук" in text and "без" not in text: data["prefs"]["audio"] = "yes"
    if "без звука" in text: data["prefs"]["audio"] = "no"

def cmd_get(user_id):
    """Get user constraints for LLM prompt injection"""
    data = get_feedback(user_id)
    if not data["constraints"] and not data["prefs"]:
        print("NO_CONSTRAINTS")
        return

    lines = []
    if data["constraints"]:
        lines.append("User preferences (MUST follow):")
        for c in data["constraints"]:
            lines.append(f"  - {c}")
    if data["prefs"]:
        lines.append("Additional preferences:")
        for k, v in data["prefs"].items():
            lines.append(f"  - {k}: {v}")

    result = "\n".join(lines)
    print(result)
    return result

def cmd_analyze():
    """Global patterns across all users"""
    if not os.path.exists(FEEDBACK_DIR):
        print("No feedback yet"); return
    all_constraints = {}
    total_users = 0
    total_neg = 0
    for f in os.listdir(FEEDBACK_DIR):
        if not f.endswith(".json"): continue
        data = json.load(open(f"{FEEDBACK_DIR}/{f}"))
        total_users += 1
        for e in data["entries"]:
            if e["sentiment"] == "negative":
                total_neg += 1
        for c in data.get("constraints", []):
            all_constraints[c] = all_constraints.get(c, 0) + 1

    print(f"\nGlobal Feedback Analysis:")
    print(f"  Users with feedback: {total_users}")
    print(f"  Total negative entries: {total_neg}")
    if all_constraints:
        print(f"  Most common complaints:")
        for c, count in sorted(all_constraints.items(), key=lambda x: -x[1])[:5]:
            print(f"    ({count}x) {c}")

def cmd_detect(message):
    """Detect feedback type in user message. Returns: 0=neutral 1=positive 2=negative"""
    msg = message.lower()
    for kw in NEGATIVE_KEYWORDS:
        if kw in msg:
            print("negative"); return 2
    for kw in SUGGESTION_KEYWORDS:
        if kw in msg:
            print("suggestion"); return 2
    for kw in POSITIVE_KEYWORDS:
        if kw in msg:
            print("positive"); return 1
    print("neutral"); return 0

args = sys.argv[1:]
if not args: print(__doc__)
elif args[0] == "add" and len(args) >= 5:  cmd_add(args[1], args[2], args[3], " ".join(args[4:]))
elif args[0] == "get" and len(args) > 1:   cmd_get(args[1])
elif args[0] == "analyze":                  cmd_analyze()
elif args[0] == "detect" and len(args) > 1: sys.exit(cmd_detect(" ".join(args[1:])))
else: print(__doc__)
