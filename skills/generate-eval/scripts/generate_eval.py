#!/usr/bin/env python3
import sys, os, json

def gen(skill_name):
    skill_path = f"/root/.openclaw/workspace/skills/{skill_name}/SKILL.md"
    if not os.path.exists(skill_path):
        print(f"Skill not found: {skill_name}"); return
    content = open(skill_path).read()
    eval_dir = f"/root/.openclaw/workspace/skills/{skill_name}/eval"
    os.makedirs(eval_dir, exist_ok=True)

    assertions = [
        {"id": "non_empty",    "type": "non_empty",    "description": "Output not empty"},
        {"id": "no_error",     "type": "not_contains", "pattern": "ошибка|error|failed", "description": "No errors", "case_insensitive": True},
    ]
    if "game" in skill_name:
        assertions.append({"id": "has_link", "type": "contains", "pattern": "surge.sh", "description": "Has surge link"})
        assertions.append({"id": "has_emoji", "type": "contains", "pattern": "OK|ready|готова", "description": "Has status"})

    data = {"skill": skill_name, "version": "1.0", "assertions": assertions}
    out = os.path.join(eval_dir, "eval.json")
    json.dump(data, open(out, "w"), ensure_ascii=False, indent=2)
    print(f"OK {skill_name}: {len(assertions)} assertions -> {out}")

if len(sys.argv) > 1:
    gen(sys.argv[1])
else:
    d = "/root/.openclaw/workspace/skills"
    for s in sorted(os.listdir(d)):
        if not os.path.exists(f"{d}/{s}/eval/eval.json"):
            gen(s)
