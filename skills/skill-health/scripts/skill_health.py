#!/usr/bin/env python3
import os, json
from datetime import datetime

SKILLS_DIR = "/root/.openclaw/workspace/skills"
METRICS_DIR = "/root/.openclaw/workspace/hooks/metrics"

def get_score(name):
    p = os.path.join(METRICS_DIR, f"{name}.jsonl")
    if not os.path.exists(p): return None
    lines = [l for l in open(p) if l.strip()]
    if not lines: return None
    return json.loads(lines[-1]).get("score")

def has_eval(name):
    return os.path.exists(os.path.join(SKILLS_DIR, name, "eval", "eval.json"))

def has_scripts(name):
    return os.path.exists(os.path.join(SKILLS_DIR, name, "scripts"))

skills = sorted(os.listdir(SKILLS_DIR))
print("=" * 58)
print("  GAMEFORGE — SKILL HEALTH DASHBOARD")
print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("=" * 58)
print(f"  {'Скилл':<28} {'Eval':>5} {'Scripts':>8} {'Score':>8}")
print("-" * 58)

we, ws = 0, 0
for s in skills:
    ev, sc = has_eval(s), has_scripts(s)
    score = get_score(s)
    if ev: we += 1
    if sc: ws += 1
    print(f"  {s:<28} {'v' if ev else '-':>5} {'v' if sc else '-':>8} {str(round(score))+'%' if score else '-':>8}")

print("-" * 58)
print(f"  Total: {len(skills)} skills | Eval: {we}/{len(skills)} | Scripts: {ws}/{len(skills)}")
print("=" * 58)
