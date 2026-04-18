#!/usr/bin/env python3
"""
State Manager — save/restore agent session context
Usage:
  state.py save <session_id> <context_json>
  state.py load <session_id>
  state.py list
  state.py clean   (remove states older than 7 days)
"""
import sys, os, json
from datetime import datetime, timedelta

STATE_DIR = "/root/.openclaw/workspace/state"
os.makedirs(STATE_DIR, exist_ok=True)

def cmd_save(session_id, context_raw):
    try:
        context = json.loads(context_raw)
    except:
        context = {"raw": context_raw}
    state = {
        "session_id": session_id,
        "saved_at": datetime.now().isoformat(),
        "context": context,
    }
    path = f"{STATE_DIR}/{session_id}.json"
    with open(path, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    print(f"State saved: {session_id}")

def cmd_load(session_id):
    path = f"{STATE_DIR}/{session_id}.json"
    if not os.path.exists(path):
        print(f"No state found: {session_id}"); return
    state = json.load(open(path))
    print(f"State: {session_id} (saved {state['saved_at'][:16]})")
    print(json.dumps(state["context"], ensure_ascii=False, indent=2))

def cmd_list():
    files = [f for f in os.listdir(STATE_DIR) if f.endswith(".json")]
    if not files:
        print("No saved states"); return
    print(f"Saved states ({len(files)}):")
    for f in sorted(files):
        state = json.load(open(f"{STATE_DIR}/{f}"))
        print(f"  {state['session_id']:30} saved: {state['saved_at'][:16]}")

def cmd_clean():
    cutoff = datetime.now() - timedelta(days=7)
    removed = 0
    for f in os.listdir(STATE_DIR):
        if not f.endswith(".json"): continue
        path = f"{STATE_DIR}/{f}"
        state = json.load(open(path))
        saved = datetime.fromisoformat(state["saved_at"])
        if saved < cutoff:
            os.remove(path)
            removed += 1
    print(f"Cleaned {removed} old states (> 7 days)")

cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
if cmd == "save" and len(sys.argv) > 3:  cmd_save(sys.argv[2], sys.argv[3])
elif cmd == "load" and len(sys.argv) > 2: cmd_load(sys.argv[2])
elif cmd == "list":  cmd_list()
elif cmd == "clean": cmd_clean()
else: print(__doc__)
