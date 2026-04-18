#!/usr/bin/env python3
"""
Rate Limiter — prevents generation spam per VK user
Usage:
  rate_limit.py check <user_id>    → 0=ok, 1=blocked
  rate_limit.py acquire <user_id>  → lock slot
  rate_limit.py release <user_id>  → unlock slot
  rate_limit.py status             → show all active locks
"""
import sys, os, json, time
from datetime import datetime

LOCK_DIR   = "/tmp/gameforge-locks"
COOLDOWN   = 60   # seconds between requests per user
MAX_ACTIVE = 5    # max concurrent generations total

os.makedirs(LOCK_DIR, exist_ok=True)

def get_lock_path(user_id):
    return f"{LOCK_DIR}/{user_id}.json"

def cmd_check(user_id):
    path = get_lock_path(user_id)
    # Check user cooldown
    if os.path.exists(path):
        data = json.load(open(path))
        age = time.time() - data["started"]
        if data["status"] == "generating":
            print(f"BLOCKED: {user_id} is already generating (started {int(age)}s ago)")
            return 1
        if data["status"] == "done" and age < COOLDOWN:
            wait = int(COOLDOWN - age)
            print(f"COOLDOWN: {user_id} must wait {wait}s")
            return 1
    # Check global concurrent limit
    active = [f for f in os.listdir(LOCK_DIR) if f.endswith(".json")]
    generating = 0
    for f in active:
        try:
            d = json.load(open(f"{LOCK_DIR}/{f}"))
            if d["status"] == "generating" and time.time() - d["started"] < 300:
                generating += 1
        except: pass
    if generating >= MAX_ACTIVE:
        print(f"BUSY: {generating} games generating, try again soon")
        return 1
    print(f"OK: {user_id} can generate")
    return 0

def cmd_acquire(user_id):
    path = get_lock_path(user_id)
    data = {"user_id": user_id, "status": "generating", "started": time.time(), "ts": datetime.now().isoformat()}
    with open(path, "w") as f:
        json.dump(data, f)
    print(f"Locked: {user_id}")

def cmd_release(user_id):
    path = get_lock_path(user_id)
    if os.path.exists(path):
        data = json.load(open(path))
        data["status"] = "done"
        data["finished"] = time.time()
        with open(path, "w") as f:
            json.dump(data, f)
    print(f"Released: {user_id}")

def cmd_status():
    files = [f for f in os.listdir(LOCK_DIR) if f.endswith(".json")]
    if not files:
        print("No active locks"); return
    print(f"\n  Active: {len(files)} users")
    for f in files:
        try:
            d = json.load(open(f"{LOCK_DIR}/{f}"))
            age = int(time.time() - d["started"])
            print(f"    {d['user_id']:20} {d['status']:12} {age}s ago")
        except: pass

cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
if cmd == "check"   and len(sys.argv) > 2: sys.exit(cmd_check(sys.argv[2]))
elif cmd == "acquire" and len(sys.argv) > 2: cmd_acquire(sys.argv[2])
elif cmd == "release" and len(sys.argv) > 2: cmd_release(sys.argv[2])
elif cmd == "status": cmd_status()
else: print(__doc__)
